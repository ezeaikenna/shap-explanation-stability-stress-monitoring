# Research Materials Release Notes

## Version 1.0.0 — Research materials

Published 23 November 2026. The versioned research-materials archive is available at https://doi.org/10.5281/zenodo.24465081.

This release presents the computational materials supporting the separate SSAQS and RELAX analyses of global and participant-level SHAP explanation stability.

### Included materials

- SSAQS global SHAP analysis notebook, metadata, fold-level and aggregate summaries, and figures.
- RELAX global SHAP analysis results and numerical reproduction materials.
- RELAX participant-level analysis and table-construction scripts, metadata, fold-level preprocessing summaries, aggregate stability summaries, and figures.
- Computational environment information, source-data requirements, and methodological documentation.
- Aggregate numerical comparisons and a SHA-256 file manifest.

### Data availability

The original SSAQS and RELAX datasets and the original RELAX questionnaire workbook are not redistributed. They should be obtained from their source repositories, subject to the providers' access conditions and licences. The repository does not contain every original input required for a complete end-to-end rerun of all analyses.

Observation-level predictions and SHAP exports, participant-coded local-stability records, and participant-level SHAP arrays are excluded. See `PUBLIC_RELEASE_EXCLUSIONS.txt` for a description of these materials.

### Analytical scope

The SSAQS and RELAX datasets were analysed independently. No model, prediction or explanation was transferred between datasets, and no external validation was performed. SHAP values are predictive attributions, not causal effects. The analyses do not establish clinical validity or unrestricted generalisability.

### Computational reproduction

The RELAX global numerical reproduction includes 16 predefined numerical consistency checks. The archived and reproduced attribution, fold-level importance, aggregate feature summaries and pairwise stability results agreed under the stated comparison criteria. The original NumPy and SciPy versions were not documented, so complete identity with the historical computational environment cannot be established.

### Licences and citation

Original software code authored for this repository is licensed under MIT. Original documentation and other original non-software text are licensed under CC BY 4.0. These licences do not extend to third-party datasets, source materials or restricted research records.

Version 1.0.0 citation: https://doi.org/10.5281/zenodo.24465081. Please also cite the associated research manuscript when using these materials.
