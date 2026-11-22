#!/usr/bin/env python3
"""
Reconstruct the 1,148-row RELAX next-morning analysis table.

This script implements the preprocessing/data-construction procedure retained
in RELAX_questionnaire_longitudinal.py. It expects the original RELAX
questionnaire response workbook, which is not redistributed in this package.

Usage:
    python build_relax_analysis_table.py \
        --responses questionnaire_responses.xlsx \
        --out RELAX_next_morning_stress_dataset.csv

The expected SHA-256 is recorded below and in run_metadata.json. A matching
hash confirms byte-for-byte agreement with the analysis-ready input used for
the reported participant-level local-SHAP analysis.
"""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import pandas as pd

MFB_MAP = {
    "mfb_prev_mood": "answers/mfb-1-1",
    "mfb_prev_feeling_excited_calm": "answers/mfb-2-1",
    "mfb_prev_sleep_quality": "answers/mfb-4-1",
    "mfb_prev_night_waking": "answers/mfb-5-1",
}
IFB_MAP = {
    "ifb_prev_mood": "answers/ifb-1-1",
    "ifb_prev_feeling_excited_calm": "answers/ifb-2-1",
    "ifb_prev_work_time": "answers/ifb-3-1",
    "ifb_prev_duties_leisure": "answers/ifb-4-1",
    "ifb_prev_routine_extraordinary": "answers/ifb-5-1",
    "ifb_prev_physical_exertion": "answers/ifb-6-1",
    "ifb_prev_mental_effort": "answers/ifb-7-1",
    "ifb_prev_mood_recalled": "answers/ifb-11-1",
    "ifb_prev_feeling_recalled": "answers/ifb-12-1",
    "ifb_prev_physical_exertion_recalled": "answers/ifb-13-1",
    "ifb_prev_mental_effort_recalled": "answers/ifb-14-1",
}
AFB_MAP = {
    "afb_prev_mood": "answers/afb-1-1",
    "afb_prev_feeling_excited_calm": "answers/afb-2-1",
    "afb_prev_happy_unhappy": "answers/afb-3-1",
    "afb_prev_working_day": "answers/afb-4-1",
    "afb_prev_physical_exertion": "answers/afb-7-1",
    "afb_prev_mental_effort": "answers/afb-6a-1",
    "afb_prev_low_satisfaction_distress": "answers/afb-8-1",
    "afb_prev_overwhelm_distress": "answers/afb-9-1",
    "afb_prev_lack_of_control_distress": "answers/afb-10-1",
    "afb_prev_cannot_relax_distress": "answers/afb-11-1",
    "afb_prev_negative_mood_distress": "answers/afb-12-1",
}
TARGET = "answers/mfb-3-1"
EXPECTED_SHA256 = "864b0c9b52f123088f46d932b2daf5bb7410c7932fb5e0e233d6e5c51c5ee5ac"


def prep(df):
    df = df.copy()
    df["dt"] = pd.to_datetime(df["readable_date"], errors="coerce")
    df = df.dropna(subset=["user", "dt"]).sort_values(
        ["user", "dt"]
    ).reset_index(drop=True)
    return df


def build_table(responses_path):
    sheets = pd.read_excel(responses_path, sheet_name=None)
    for needed in ["mfb", "ifb", "afb"]:
        if needed not in sheets:
            raise ValueError(f"Required worksheet missing: {needed}")

    mfb, ifb, afb = (
        prep(sheets["mfb"]),
        prep(sheets["ifb"]),
        prep(sheets["afb"]),
    )
    mfb[TARGET] = pd.to_numeric(mfb[TARGET], errors="coerce")

    for frame, mapping in [(mfb, MFB_MAP), (ifb, IFB_MAP), (afb, AFB_MAP)]:
        for column in mapping.values():
            if column in frame:
                frame[column] = pd.to_numeric(frame[column], errors="coerce")

    # Reverse negatively oriented AFB distress items to a common direction.
    for column in [
        "answers/afb-8-1", "answers/afb-9-1", "answers/afb-10-1",
        "answers/afb-11-1", "answers/afb-12-1",
    ]:
        afb[column] = 8 - pd.to_numeric(afb[column], errors="coerce")

    by_user = {}
    for name, frame in [("mfb", mfb), ("ifb", ifb), ("afb", afb)]:
        by_user[name] = {
            uid: subset.sort_values("dt").reset_index(drop=True)
            for uid, subset in frame.groupby("user", sort=False)
        }

    rows = []
    for uid, target_group in mfb.groupby("user", sort=False):
        target_group = target_group.sort_values("dt")
        pm = by_user["mfb"].get(uid)
        pi = by_user["ifb"].get(uid, pd.DataFrame())
        pa = by_user["afb"].get(uid, pd.DataFrame())
        if pm is None:
            continue

        mt = pm["dt"].to_numpy(dtype="datetime64[ns]")
        it = pi["dt"].to_numpy(dtype="datetime64[ns]") if len(pi) else np.array([], dtype="datetime64[ns]")
        at = pa["dt"].to_numpy(dtype="datetime64[ns]") if len(pa) else np.array([], dtype="datetime64[ns]")

        for _, target in target_group.iterrows():
            y = pd.to_numeric(pd.Series([target[TARGET]]), errors="coerce").iloc[0]
            if pd.isna(y):
                continue

            target_time = np.datetime64(target["dt"])
            mi = int(np.searchsorted(mt, target_time, side="left"))
            history = pm.iloc[:mi]
            if history.empty:
                continue

            previous = history.iloc[-1]
            row = {
                "participant_id": uid,
                "target_timestamp": target["dt"],
                "target_stress_expectation_1_7": float(y),
                "hours_since_previous_mfb": (
                    target["dt"] - previous["dt"]
                ).total_seconds() / 3600,
                "previous_mfb_stress_expectation": pd.to_numeric(
                    previous[TARGET], errors="coerce"
                ),
                "previous_3_mfb_stress_mean": pd.to_numeric(
                    history[TARGET].tail(3), errors="coerce"
                ).mean(),
                "previous_mfb_count": len(history),
            }

            for name, column in MFB_MAP.items():
                row[name] = pd.to_numeric(previous.get(column, np.nan), errors="coerce")

            ii = int(np.searchsorted(it, target_time, side="left")) if len(it) else 0
            row["has_prior_ifb"] = int(ii > 0)
            row["hours_since_previous_ifb"] = np.nan
            for name in IFB_MAP:
                row[name] = np.nan
            if ii > 0:
                previous_ifb = pi.iloc[ii - 1]
                row["hours_since_previous_ifb"] = (
                    target["dt"] - previous_ifb["dt"]
                ).total_seconds() / 3600
                for name, column in IFB_MAP.items():
                    row[name] = pd.to_numeric(previous_ifb.get(column, np.nan), errors="coerce")

            ai = int(np.searchsorted(at, target_time, side="left")) if len(at) else 0
            row["has_prior_afb"] = int(ai > 0)
            row["hours_since_previous_afb"] = np.nan
            for name in AFB_MAP:
                row[name] = np.nan
            if ai > 0:
                previous_afb = pa.iloc[ai - 1]
                row["hours_since_previous_afb"] = (
                    target["dt"] - previous_afb["dt"]
                ).total_seconds() / 3600
                for name, column in AFB_MAP.items():
                    row[name] = pd.to_numeric(previous_afb.get(column, np.nan), errors="coerce")

            rows.append(row)

    data = pd.DataFrame(rows).sort_values(
        ["participant_id", "target_timestamp"]
    ).reset_index(drop=True)
    if data.empty:
        raise ValueError("No eligible next-response rows were created.")
    return data


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--responses", required=True, help="Original RELAX questionnaire_responses.xlsx")
    parser.add_argument("--out", default="RELAX_next_morning_stress_dataset.csv")
    args = parser.parse_args()

    data = build_table(args.responses)
    data.to_csv(args.out, index=False)
    digest = hashlib.sha256(Path(args.out).read_bytes()).hexdigest()

    print(f"Created: {args.out}")
    print(f"Rows: {len(data)}")
    print(f"Participants: {data['participant_id'].nunique()}")
    print(f"Columns: {len(data.columns)}")
    print(f"SHA-256: {digest}")
    if digest == EXPECTED_SHA256:
        print("VERIFIED: exact byte-for-byte match to the analysis-ready input used in the reported analysis.")
    else:
        print("WARNING: hash differs from the recorded analysis-ready input; investigate source workbook,")
        print("software versions, date parsing and CSV serialization before using this file for reproduction.")


if __name__ == "__main__":
    main()
