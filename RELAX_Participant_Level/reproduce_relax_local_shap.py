#!/usr/bin/env python
"""Reproduce RELAX participant-level local SHAP stability.

Usage:
    python reproduce_relax_local_shap.py \
        --data RELAX_next_morning_stress_dataset.csv \
        --output outputs

The script follows the previously documented model and explanation configuration. It does not perform
cross-dataset transfer or external validation.
"""
from pathlib import Path
import argparse, hashlib, json, platform, sys, itertools
import numpy as np
import pandas as pd
import scipy, sklearn, shap
from scipy.stats import spearmanr
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor

SEED = 20261013
REPEATS = 5
FOLDS = 5
BOOTSTRAPS = 10000
RF = dict(n_estimators=400, min_samples_leaf=5, max_features=0.8, n_jobs=-1)

def participant_equal_weights(groups):
    groups = np.asarray(groups).astype(str)
    counts = pd.Series(groups).value_counts()
    w = np.array([1.0 / counts[g] for g in groups], dtype=float)
    return w / w.mean()

def shap_values_2d(model, X):
    # Follows the previously documented SHAP configuration; no explicit background data are passed.
    vals = shap.TreeExplainer(model).shap_values(X, check_additivity=False)
    vals = np.asarray(vals)
    if vals.ndim == 3:
        vals = vals[..., 0]
    if vals.ndim != 2:
        raise ValueError(f"Unexpected SHAP array shape: {vals.shape}")
    return vals

def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="RELAX_next_morning_stress_dataset.csv")
    ap.add_argument("--output", default="outputs")
    args = ap.parse_args()
    data_path = Path(args.data)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(data_path)
    df["participant_id"] = df["participant_id"].astype(str)
    df["target_timestamp"] = pd.to_datetime(df["target_timestamp"], errors="coerce")
    df = df.dropna(subset=["participant_id", "target_stress_expectation_1_7"]).reset_index(drop=True)
    target = "target_stress_expectation_1_7"
    excluded = {"participant_id", "target_timestamp", target}
    features = [c for c in df.columns if c not in excluded]
    X = df[features].apply(pd.to_numeric, errors="coerce")
    y = pd.to_numeric(df[target], errors="coerce").to_numpy(float)
    groups = df["participant_id"].to_numpy(str)
    if not np.isfinite(y).all():
        raise ValueError("Target contains non-finite values after filtering.")

    # Build a common SHAP feature space, but determine missingness indicators
    # independently from each training fold. Indicators absent from a fold's
    # training-derived schema receive zero attribution in the aligned vector.
    base_feature_names = list(features)
    X_local = X.apply(pd.to_numeric, errors="coerce")

    unique_groups = np.array(sorted(np.unique(groups)))
    fold_specs = []
    rng = np.random.default_rng(SEED)
    indicator_union = set()
    for r in range(REPEATS):
        perm = rng.permutation(unique_groups)
        group_fold = {str(pid): (i % FOLDS) for i, pid in enumerate(perm)}
        row_fold = np.array([group_fold[str(pid)] for pid in groups])
        for f in range(FOLDS):
            train_idx = np.where(row_fold != f)[0]
            train_missing = [c for c in base_feature_names if X_local.iloc[train_idx][c].isna().any()]
            indicator_union.update(train_missing)
            fold_specs.append((r, f, row_fold, train_idx, train_missing))

    indicator_names = [f"missing__{c}" for c in base_feature_names if c in indicator_union]
    feature_names = base_feature_names + indicator_names
    feature_index = {name: j for j, name in enumerate(feature_names)}
    shap_all = np.full((REPEATS, len(df), len(feature_names)), np.nan, dtype=np.float32)
    fold_log = []

    for r, f, row_fold, train_idx, train_missing in fold_specs:
        test_idx = np.where(row_fold == f)[0]
        imputer = SimpleImputer(strategy="median", keep_empty_features=True)
        X_train_base = imputer.fit_transform(X_local.iloc[train_idx])
        X_test_base = imputer.transform(X_local.iloc[test_idx])

        if train_missing:
            X_train_ind = X_local.iloc[train_idx][train_missing].isna().to_numpy(dtype=float)
            X_test_ind = X_local.iloc[test_idx][train_missing].isna().to_numpy(dtype=float)
            X_train = np.column_stack([X_train_base, X_train_ind])
            X_test = np.column_stack([X_test_base, X_test_ind])
        else:
            X_train, X_test = X_train_base, X_test_base

        model = RandomForestRegressor(**RF, random_state=SEED + r * 100 + f)
        model.fit(X_train, y[train_idx], sample_weight=participant_equal_weights(groups[train_idx]))
        sv = shap_values_2d(model, X_test)

        # Align this fold's SHAP values to the union schema without using
        # held-out missingness to decide which indicator columns exist.
        fold_names = base_feature_names + [f"missing__{c}" for c in train_missing]
        aligned = np.zeros((len(test_idx), len(feature_names)), dtype=np.float32)
        for j, name in enumerate(fold_names):
            aligned[:, feature_index[name]] = sv[:, j].astype(np.float32)
        shap_all[r, test_idx, :] = aligned

        fold_log.append({
            "repeat": r + 1, "fold": f + 1,
            "train_participants": int(len(np.unique(groups[train_idx]))),
            "test_participants": int(len(np.unique(groups[test_idx]))),
            "train_rows": int(len(train_idx)), "test_rows": int(len(test_idx)),
            "n_training_selected_missingness_indicators": len(train_missing),
            "training_selected_missingness_indicators": ";".join(train_missing),
            "n_estimators": RF["n_estimators"],
            "random_state": SEED + r * 100 + f
        })
        if f == FOLDS - 1:
            print(f"Completed repetition {r + 1}/{REPEATS}", flush=True)

    if not np.isfinite(shap_all).all():
        raise RuntimeError("Some observation-feature SHAP values are missing or non-finite.")

    obs = []
    for i in range(len(df)):
        values = shap_all[:, i, :]
        rank_scores, cosine_scores = [], []
        for a, b in itertools.combinations(range(REPEATS), 2):
            va, vb = values[a], values[b]
            rank_scores.append(spearmanr(np.abs(va), np.abs(vb)).statistic)
            denom = np.linalg.norm(va) * np.linalg.norm(vb)
            cosine_scores.append(float(np.dot(va, vb) / denom) if denom > 0 else np.nan)
        obs.append({
            "row_index": i, "participant_id": groups[i],
            "target_timestamp": str(df.loc[i, "target_timestamp"]),
            "n_repeat_pairs": len(rank_scores),
            "mean_abs_SHAP_rank_spearman": float(np.nanmean(rank_scores)),
            "mean_signed_SHAP_cosine_similarity": float(np.nanmean(cosine_scores))
        })
    obs_df = pd.DataFrame(obs)
    participant = (obs_df.groupby("participant_id")
        .agg(n_target_rows=("row_index", "count"),
             mean_row_rank_spearman=("mean_abs_SHAP_rank_spearman", "mean"),
             median_row_rank_spearman=("mean_abs_SHAP_rank_spearman", "median"),
             mean_signed_SHAP_cosine=("mean_signed_SHAP_cosine_similarity", "mean"),
             median_signed_SHAP_cosine=("mean_signed_SHAP_cosine_similarity", "median"))
        .reset_index())

    rng_boot = np.random.default_rng(SEED + 1)
    summaries = []
    for col in ["mean_row_rank_spearman", "mean_signed_SHAP_cosine"]:
        vals = participant[col].dropna().to_numpy(float)
        boots = np.array([
            rng_boot.choice(vals, size=len(vals), replace=True).mean()
            for _ in range(BOOTSTRAPS)
        ])
        summaries.append({
            "metric": col, "n_participants": len(vals),
            "mean": float(np.mean(vals)), "median": float(np.median(vals)),
            "participant_bootstrap_95CI_low": float(np.quantile(boots, .025)),
            "participant_bootstrap_95CI_high": float(np.quantile(boots, .975)),
            "min": float(np.min(vals)), "max": float(np.max(vals))
        })
    summary = pd.DataFrame(summaries)

    # Pseudonymise participant identifiers in exported derived files.
    codes = {pid: f"P{i+1:02d}" for i, pid in enumerate(sorted(np.unique(groups)))}
    obs_export = obs_df.copy()
    obs_export["participant_code"] = obs_export["participant_id"].map(codes)
    obs_export = obs_export.drop(columns=["participant_id"])
    part_export = participant.copy()
    part_export["participant_code"] = part_export["participant_id"].map(codes)
    part_export = part_export.drop(columns=["participant_id"])

    obs_export.to_csv(out / "RELAX_local_SHAP_observation_stability_anonymised.csv", index=False)
    part_export.to_csv(out / "RELAX_local_SHAP_participant_stability_anonymised.csv", index=False)
    pd.DataFrame(fold_log).to_csv(out / "RELAX_local_SHAP_fold_allocation_summary.csv", index=False)
    pd.DataFrame({"aligned_feature": feature_names}).to_csv(out / "RELAX_local_SHAP_feature_schema.csv", index=False)
    summary.to_csv(out / "RELAX_local_SHAP_stability_summary.csv", index=False)
    np.save(out / "RELAX_local_SHAP_values.npy", shap_all)

    # Runtime-resolved SHAP mode: no data argument means tree-path-dependent mode.
    explainer = shap.TreeExplainer(model)
    metadata = {
        "analysis": "RELAX participant-level local SHAP stability independent reproduction",
        "source_file": data_path.name, "source_sha256": sha256(data_path),
        "n_observations": len(df), "n_participants": len(unique_groups),
        "n_predictors_before_missing_indicators": len(features),
        "n_features_in_shap_vectors": len(feature_names),
        "missingness_indicator_selection": "Selected independently within each training fold; held-out data are used only to calculate indicators for columns selected from that fold's training partition.",
        "common_shap_feature_alignment": "Union of training-selected indicator features across folds; indicators not selected in a given fold are assigned zero attribution in that fold's aligned vector.",
        "repetitions": REPEATS, "folds_per_repetition": FOLDS, "model_fits": len(fold_log),
        "random_forest": RF, "seed": SEED,
        "bootstrap_resamples": BOOTSTRAPS, "bootstrap_seed": SEED + 1,
        "shap_call": "shap.TreeExplainer(model).shap_values(X_test, check_additivity=False)",
        "shap_feature_perturbation": explainer.feature_perturbation,
        "shap_background_data": "No separate background dataset supplied; tree_path_dependent mode uses fitted-tree path statistics.",
        "runtime": {
            "python": platform.python_version(), "numpy": np.__version__,
            "pandas": pd.__version__, "scikit_learn": sklearn.__version__,
            "shap": shap.__version__, "scipy": scipy.__version__
        },
        "integrity": {
            "all_shap_values_finite": bool(np.isfinite(shap_all).all()),
            "fold_records": len(fold_log), "participants": len(participant),
            "observations": len(obs_df)
        }
    }
    (out / "run_metadata.json").write_text(json.dumps(metadata, indent=2))
    print(summary.to_string(index=False))

if __name__ == "__main__":
    main()
