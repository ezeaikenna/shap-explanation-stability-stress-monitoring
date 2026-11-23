# Global and Participant-Level SHAP Explanation Stability in Longitudinal Stress Prediction

This repository contains privacy-minimised computational materials for the separate SSAQS and RELAX analyses reported in the associated manuscript. The datasets were analysed independently. No model, prediction or explanation was transferred between datasets, and no external validation was performed.

## Contents

- `SSAQS_Global_SHAP/`: SSAQS global SHAP notebook, fold-level and aggregate summaries, metadata and figures.
- `RELAX_Global_SHAP/`: RELAX global SHAP results and numerical reproduction results.
- `RELAX_Participant_Level/`: RELAX participant-level analysis and table-construction scripts, requirements, fold-level preprocessing summaries, aggregate stability results and figures.
- `RESULTS_INDEX.txt`: principal estimates and numerical reproduction results.
- `README_Computational_Materials.txt`: detailed scope, inputs, methods and limitations.
- `PUBLIC_RELEASE_EXCLUSIONS.txt`: files intentionally omitted from this repository.
- `generate_sha256_manifest.py`: regenerates `SHA256SUMS.txt` for the current repository contents.
- `check_public_release.py`: checks known restricted paths and sensitive-looking fields in CSV, TSV, JSON and JSONL data files before release.

## Data access and source licences

- SSAQS dataset record: https://doi.org/10.5281/zenodo.18706837 (dataset descriptor: https://doi.org/10.1038/s41597-026-07085-7). The dataset is identified as CC BY 4.0 in the source record.
- RELAX dataset concept DOI: https://doi.org/10.5281/zenodo.18693288 (dataset descriptor: https://doi.org/10.1038/s41597-026-07711-4). The Zenodo Version 2 record inspected for this repository is https://zenodo.org/records/20701999; its Rights panel identifies the dataset licence as Creative Commons Attribution 4.0 International (CC BY 4.0).

The original SSAQS and RELAX datasets and the RELAX questionnaire workbook are not redistributed here. Obtain them from their source repositories and follow the source providers' access conditions and licences. The analysis scripts require the corresponding source inputs; this repository does not contain every input needed for a complete end-to-end rerun. The RELAX record's displayed licence does not authorise publication of participant-linked analysis outputs or other restricted research records.

## Privacy and release scope

Observation-level predictions and SHAP exports, participant-coded local-stability records, participant-level SHAP arrays and related row-level files are excluded to reduce disclosure risk. Notebook cell outputs were cleared while executable source cells were retained. See `PUBLIC_RELEASE_EXCLUSIONS.txt`.

**Local execution can generate restricted files.** In particular, the RELAX table-construction script creates `RELAX_next_morning_stress_dataset.csv`; the participant-level script writes row-level and participant-coded exports under its `outputs/` directory; and the SSAQS/RELAX notebooks create held-out predictions, SHAP exports and local run workspaces. These files must remain outside version control unless a documented privacy and disclosure review authorises their release. The research-specific rules in `.gitignore` exclude the known generated paths.

Before committing or packaging changes, run:

```bash
python check_public_release.py
python -m unittest discover -s tests -v
git status --short
git diff --cached --name-status
```

When run inside a Git worktree, `check_public_release.py` also inspects staged file paths and staged CSV/TSV/JSON/JSONL content. Use `python check_public_release.py --require-git` to require a Git worktree, and `python check_public_release.py --history` to inspect reachable local Git history for known restricted paths and sensitive-looking fields in historical CSV/TSV/JSON/JSONL blobs. Fetch remote branches first; only refs present in the local clone are scanned.

The checker is a supplementary safeguard. It checks working-tree paths and structured CSV/TSV/JSON/JSONL content, staged paths and staged structured content, and (with `--history`) every path in reachable local Git commit trees plus structured-content blobs. Unreadable or invalidly encoded structured files are reported as findings rather than silently skipped. It does not inspect all binary formats, unreachable objects, unfetched remote refs or semantic disclosure risk. It is not a substitute for reviewing staged changes and checking source-data access conditions, privacy obligations and disclosure risks. See `PUBLIC_RELEASE_EXCLUSIONS.txt` for the complete list of known exclusions.

## Important interpretation limits

The reported SHAP values are predictive attributions, not causal effects. The analyses do not establish clinical validity, external generalisability, or robustness to arbitrary input perturbations. The RELAX local-stability analysis compares the same observations across repeated participant-grouped model fits; it is not a measure of within-model explainer stochasticity.

## Licences

- Original software code authored for this repository is licensed under the MIT License; see `LICENSE`.
- Original documentation and other original non-software text authored for this repository are licensed under CC BY 4.0; see `LICENSE-DOCUMENTATION.txt`.

These licences do not apply to third-party datasets, source materials, third-party code, or restricted participant-linked and observation-level research records. Those materials remain subject to their own rights, licences, access conditions and applicable requirements. In particular, neither licence grants permission to redistribute the SSAQS or RELAX source datasets or restricted research records.

## Citation

A `CITATION.cff` file provides the software title and author metadata. No version-specific software DOI has been assigned. A version-specific citation can be added after a release has been archived in Zenodo and its DOI has been verified.
