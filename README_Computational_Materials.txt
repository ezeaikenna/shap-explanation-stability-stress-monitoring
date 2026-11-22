# Computational Materials

## Global and Participant-Level SHAP Explanation Stability in Longitudinal Stress Prediction

### Purpose
These materials contain analysis notebooks and scripts, model and software-version information, fold-level and aggregate results, figures, and documentation for the separate SSAQS and RELAX analyses. The datasets were analysed independently. No model, prediction or explanation was transferred between datasets, and no external validation was performed.

### Privacy-Related Exclusions
The repository excludes observation-level prediction and SHAP exports, observation-level local-stability records, participant-coded local-stability records, and the participant-level SHAP value array. These files contained row-level or participant-linked information, including participant identifiers or codes, row indices, timestamps, observed targets, predictions, or individual attribution vectors. Aggregate participant-level stability estimates are retained because they do not contain the excluded observation-level or participant-coded records. Notebook cell outputs were cleared while executable source cells were retained.

### Contents
1. `SSAQS_Global_SHAP/` — analysis notebook, metadata, fold-level and aggregate SHAP summaries, pairwise stability estimates and figures.
2. `RELAX_Global_SHAP/` — fold summaries, fold-level feature-importance summaries, pairwise stability estimates and figures. `Numerical_Reproduction/` contains the notebook-based numerical reproduction and comparison results.
3. `RELAX_Participant_Level/` — analysis and table-construction scripts, requirements, metadata, fold summaries, preprocessing summaries, aggregate stability estimates and figures.
4. `RESULTS_INDEX.txt` — principal estimates and numerical reproduction results.

### Data Access and Source Licences
The original SSAQS and RELAX datasets and the original RELAX questionnaire workbook are not redistributed. Obtain the source materials from the repositories identified in the article and follow their access conditions and licences.

- SSAQS dataset record: https://doi.org/10.5281/zenodo.18706837. The source record identifies the dataset as CC BY 4.0.
- RELAX dataset concept DOI: https://doi.org/10.5281/zenodo.18693288. The inspected Zenodo Version 2 record is https://zenodo.org/records/20701999, whose Rights panel identifies Creative Commons Attribution 4.0 International (CC BY 4.0).

The SSAQS notebook requires the version-matched source archive containing the frozen modelling table and primary out-of-fold predictions. The RELAX table-construction script requires the original questionnaire workbook with MFB, IFB and AFB worksheets. The supplied code and aggregate outputs support inspection and reproduction when the corresponding source inputs are available. This repository does not contain all original inputs required for a complete end-to-end rerun.

### SSAQS Analysis
The SSAQS analysis includes 35 participants and 3,098 eligible next-observed questionnaire stress observations. Five participant-held-out folds were used with a 300-tree Random Forest (minimum leaf size 5; `max_features=0.8`; random state 20261009). Numeric predictors were median-imputed, augmented with missingness indicators and standardised; categorical predictors were imputed using the most frequent category and one-hot encoded. The fold sizes were 627, 634, 602, 627 and 608.

### RELAX Global Analysis
The RELAX global analysis includes 31 participants and 1,148 observations. Global SHAP rankings were compared across five participant-held-out folds using a 400-tree Random Forest.

The numerical reproduction used Python 3.13.18, NumPy 2.4.6, pandas 3.1.1, SciPy 1.16.3, scikit-learn 1.9.1 and SHAP 0.54.1. Python, pandas, scikit-learn and SHAP match the versions recorded for the original analysis; the original NumPy and SciPy versions were not documented.

All 16 predefined numerical consistency checks passed. The archived and reproduced SHAP attribution and stability results agreed according to the predefined comparison criteria. This supports numerical reproduction under the recorded software versions but does not establish complete identity with the historical computational environment.

### RELAX Participant-Level Analysis
The participant-level analysis comprises five repetitions of five participant-grouped folds (25 Random Forest fits, 400 trees per fit). The final analysis used Python 3.13.16, pandas 2.2.3, scikit-learn 1.6.1 and SHAP 0.54.1 (see the analysis metadata). This environment differs from the separate RELAX global numerical-reproduction environment documented above.

Missingness-indicator selection and median imputation were performed independently within each training fold. SHAP values were calculated using TreeExplainer with tree-path-dependent feature perturbation and no separately supplied background dataset. Absolute-SHAP rank agreement and signed-SHAP cosine similarity were calculated for the same observations across repeated fits and summarised within participants. The participant-level bootstrap used 10,000 resamples. Aggregate estimates are retained; row-level and participant-coded exports are excluded.

### Reported RELAX Local Estimates
Mean absolute-SHAP rank agreement was 0.938533 (95% participant-bootstrap CI 0.935732–0.941442), and mean signed-SHAP cosine similarity was 0.906385 (95% participant-bootstrap CI 0.896173–0.915704).

The same 25 missingness indicators were selected in all 25 folds in this analysis, although selection was performed independently within each training fold.

### Release Scope
This repository is a privacy-minimised research-code and results collection. Before public distribution, confirm that retained materials comply with source-data providers' redistribution terms and applicable institutional requirements. The source dataset licences do not authorise publication of participant-linked analysis outputs or other restricted research records.
