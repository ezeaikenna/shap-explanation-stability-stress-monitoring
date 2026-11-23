# Global and Participant-Level SHAP Explanation Stability in Longitudinal Stress Prediction

This repository contains computational materials for the separate SSAQS and RELAX analyses reported in the associated research. The datasets were analysed independently. No model, prediction or explanation was transferred between datasets, and no external validation was performed.

## Contents

- `SSAQS_Global_SHAP/`: SSAQS global SHAP notebook, fold-level and aggregate summaries, metadata and figures.
- `RELAX_Global_SHAP/`: RELAX global SHAP results and numerical reproduction materials.
- `RELAX_Participant_Level/`: RELAX participant-level analysis and table-construction scripts, software requirements, fold-level preprocessing summaries, aggregate stability results and figures.
- `RESULTS_INDEX.txt`: principal estimates and numerical reproduction results.
- `README_Computational_Materials.txt`: analytical scope, inputs, methods and limitations.
- `PUBLIC_RELEASE_EXCLUSIONS.txt`: description of source and generated materials not distributed in this repository.
- `RELEASE_NOTES.md`: description of the research materials included in this version.
- `SHA256SUMS.txt`: file checksums.

## Data access and source licences

- SSAQS dataset record: https://doi.org/10.5281/zenodo.18706837 (dataset descriptor: https://doi.org/10.1038/s41597-026-07085-7). The source record identifies the dataset as CC BY 4.0.
- RELAX dataset concept DOI: https://doi.org/10.5281/zenodo.18693288 (dataset descriptor: https://doi.org/10.1038/s41597-026-07711-4). The inspected Zenodo Version 2 record is https://zenodo.org/records/20701999; its Rights panel identifies the dataset licence as CC BY 4.0.

The original SSAQS and RELAX datasets and the RELAX questionnaire workbook are not redistributed. Obtain them from their source repositories and follow the source providers' access conditions and licences. The analysis scripts require the corresponding source inputs; this repository does not contain every input needed for a complete end-to-end rerun. The RELAX record's displayed licence does not authorise publication of participant-linked analysis outputs or other restricted research records.

## Data availability and privacy

Observation-level predictions and SHAP exports, participant-coded local-stability records, participant-level SHAP arrays and related row-level files are excluded to reduce disclosure risk. Notebook cell outputs have been cleared while executable source cells have been retained. See `PUBLIC_RELEASE_EXCLUSIONS.txt` for details.

Execution of the notebooks and scripts may generate observation-level or participant-linked files that are not distributed here. Such files should be handled as restricted research data and should not be redistributed as part of this archive.

## Interpretation limits

The reported SHAP values are predictive attributions, not causal effects. The analyses do not establish clinical validity, external generalisability, or robustness to arbitrary input perturbations. The RELAX local-stability analysis compares the same observations across repeated participant-grouped model fits; it is not a measure of within-model explainer stochasticity.

## Licences

- Original software code authored for this repository is licensed under the MIT License; see `LICENSE`.
- Original documentation and other original non-software text authored for this repository are licensed under CC BY 4.0; see `LICENSE-DOCUMENTATION.txt`.

These licences do not apply to third-party datasets, source materials, third-party code, or restricted participant-linked and observation-level research records. Those materials remain subject to their own rights, licences, access conditions and applicable requirements.

## Citation

This repository's version 1.0.0 software archive is available from Zenodo:

https://doi.org/10.5281/zenodo.24465081

The `CITATION.cff` file provides the version-specific citation metadata. Please also cite the associated research manuscript when using these materials.
