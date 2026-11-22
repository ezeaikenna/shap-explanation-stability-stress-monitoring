# SHAP Explanation Stability — Computational Materials

This repository provides computational materials supporting the separate SSAQS and RELAX analyses reported in the associated research manuscript. It contains analysis scripts and notebooks, software and model metadata, fold-level and aggregate results, figures, and numerical comparison documentation.

The repository is organised into three principal analysis components:

1. `SSAQS_Global_SHAP/` — materials for the SSAQS global SHAP explanation-stability analysis.
2. `RELAX_Global_SHAP/` — materials for the RELAX global SHAP explanation-stability analysis, including notebook-based numerical reproduction and comparison results.
3. `RELAX_Participant_Level/` — materials for the RELAX participant-level local explanation-stability analysis.

The supplied materials support inspection of the analysis procedures, examination of reported results and numerical reproduction where the required source inputs are available. The original SSAQS and RELAX datasets and the original RELAX questionnaire workbook are not redistributed in this repository. Consequently, the repository does not contain every original input required for a complete end-to-end rerun of all analyses. Users must obtain the relevant source materials separately and comply with their access conditions and licences.

Observation-level prediction and SHAP exports, participant-coded local-stability records and participant-level SHAP value arrays have been excluded to reduce disclosure risk. Aggregate results and supporting documentation are retained.

For detailed descriptions of the analysis materials, software environments, source-data requirements and reproduction limitations, consult `README_Computational_Materials.txt`. For the specific files excluded from the repository, consult `PUBLIC_RELEASE_EXCLUSIONS.txt`.
