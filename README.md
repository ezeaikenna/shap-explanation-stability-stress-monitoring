# Global and Participant-Level SHAP Explanation Stability in Longitudinal Stress Prediction

This repository contains privacy-minimised computational materials for the separate SSAQS and RELAX analyses reported in the associated manuscript. The datasets were analysed independently. No model, prediction or explanation was transferred between datasets, and no external validation was performed.

## Contents

- `SSAQS_Global_SHAP/`: SSAQS global SHAP notebook, fold-level and aggregate summaries, metadata and figures.
- `RELAX_Global_SHAP/`: RELAX global SHAP results and numerical reproduction results.
- `RELAX_Participant_Level/`: RELAX participant-level analysis and table-construction scripts, requirements, fold-level preprocessing summaries, aggregate stability results and figures.
- `RESULTS_INDEX.txt`: principal estimates and reproduction notes.
- `README_Computational_Materials.txt`: detailed scope, inputs, methods and limitations.
- `PUBLIC_RELEASE_EXCLUSIONS.txt`: records intentionally omitted from this public copy.
- `SHA256SUMS.txt`: file-integrity manifest.

## Data access

- SSAQS dataset record: https://doi.org/10.5281/zenodo.18706837 (dataset descriptor: https://doi.org/10.1038/s41597-026-07085-7).
- RELAX dataset record cited in the published Data Descriptor: https://doi.org/10.5281/zenodo.18693288 (dataset descriptor: https://doi.org/10.1038/s41597-026-07711-4). This is the source-record identifier used here; do not substitute a separately indexed or later linked record unless the exact downloaded input version is verified against it.

The original SSAQS and RELAX datasets and the RELAX questionnaire workbook are not redistributed here. Obtain them from their source repositories and follow the source providers' access conditions and licences. The analysis scripts require the corresponding source inputs; this repository does not contain every input needed for a complete end-to-end rerun.

## Privacy and release scope

Observation-level predictions and SHAP exports, participant-coded local-stability records, participant-level SHAP arrays and related row-level files are intentionally excluded. Notebook cell outputs were cleared while executable source cells were retained. See `PUBLIC_RELEASE_EXCLUSIONS.txt`. This is a privacy-minimised research-code and results collection. Confirm that retained materials comply with source-data providers’ redistribution terms and applicable institutional requirements before public distribution. Running the participant-level script generates row-level outputs that are not part of this public package; do not commit those generated outputs.

## Important interpretation limits

The reported SHAP values are predictive attributions, not causal effects. The analyses do not establish clinical validity, external generalisability, or robustness to arbitrary input perturbations. The RELAX local-stability analysis compares the same observations across repeated participant-grouped model fits; it is not a measure of within-model explainer stochasticity.

## Citation

A `CITATION.cff` file is provided with the software title and author metadata. The repository release has not yet been published and no software DOI is assigned. After a public GitHub release is created and archived in Zenodo, update the citation metadata and manuscript Data Availability Statement with the verified version-specific archive DOI. Do not cite a DOI until Zenodo has minted and verified it.
