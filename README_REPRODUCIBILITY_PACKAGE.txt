# Computational Research Materials

This repository contains computational materials supporting the separate SSAQS and RELAX analyses reported in the associated research. It includes analysis scripts and notebooks, software and model metadata, fold-level and aggregate results, figures, and numerical comparison results.

## Organisation

1. `SSAQS_Global_SHAP/` — materials for the SSAQS global SHAP explanation-stability analysis.
2. `RELAX_Global_SHAP/` — materials for the RELAX global SHAP explanation-stability analysis, including numerical reproduction results.
3. `RELAX_Participant_Level/` — materials for the RELAX participant-level local explanation-stability analysis.

The materials support examination of the analytical procedures and reported findings, and numerical reproduction where the required source inputs are available. The original SSAQS and RELAX datasets and the original RELAX questionnaire workbook are not redistributed. Users should obtain source materials from the cited repositories and follow the providers' access conditions and licences.

Observation-level prediction and SHAP exports, participant-coded local-stability records, and participant-level SHAP value arrays are not included. Aggregate results and supporting documentation are provided.

For analytical methods, computational environments, source-data requirements and reproduction limitations, consult `README_Computational_Materials.txt`. The categories of excluded data products are described in `PUBLIC_RELEASE_EXCLUSIONS.txt`.

## Data generated during analysis

Execution of the notebooks and scripts may generate observation-level or participant-linked files that are not part of this public repository. Such files include reconstructed modelling tables, held-out predictions, individual SHAP values and participant-coded stability records. They should be handled as restricted research data and should not be redistributed as part of this archive.

## Interpretation

SHAP values are predictive attributions and should not be interpreted as causal effects. The SSAQS and RELAX analyses were conducted independently; no cross-dataset model or explanation transfer or external validation was performed. The analyses do not establish clinical validity or unrestricted generalisability.
