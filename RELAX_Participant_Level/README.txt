RELAX PARTICIPANT-LEVEL ANALYSIS MATERIALS

This folder contains the table-construction script, participant-level analysis script, requirements, metadata, fold-level preprocessing summaries, aggregate stability summaries and figures. Observation-level and participant-coded SHAP exports are excluded from this repository. Use reproduce_relax_local_shap.py for the reported analysis.

SOURCE DATA
The original RELAX questionnaire response workbook and analysis-ready CSV are not redistributed. Obtain the source workbook from the original RELAX repository/data descriptor: https://doi.org/10.1038/s41597-026-07711-4. The associated Zenodo record is https://doi.org/10.5281/zenodo.18693288. Use is subject to provider access conditions and rights. The workbook should contain MFB, IFB and AFB worksheets.

RECONSTRUCT THE ANALYSIS TABLE
Install dependencies in requirements.txt, then run: python build_relax_analysis_table.py --responses questionnaire_responses.xlsx --out RELAX_next_morning_stress_dataset.csv

RUN THE PARTICIPANT-LEVEL ANALYSIS
Run: python reproduce_relax_local_shap.py --data RELAX_next_morning_stress_dataset.csv --output outputs
Missingness-indicator selection and median-imputation values are determined independently within each training fold. The training-derived transformation is applied unchanged to the corresponding held-out observations. The analysis uses five repetitions of five participant-grouped folds (25 Random Forest fits). Model settings, seeds and software versions are recorded in analysis_metadata.json.

RESULTS
Mean absolute-SHAP rank agreement was 0.938533 (95% participant-bootstrap CI 0.935732–0.941442), and mean signed-SHAP cosine similarity was 0.906385 (95% participant-bootstrap CI 0.896173–0.915704). The same 25 missingness indicators were selected in all 25 training folds. This was an observed result of fold-specific selection. Fold-level preprocessing details are provided in RELAX_local_SHAP_repeated_fold_preprocessing.csv. Selection was performed independently within each training fold.

The source workbook is required for reconstruction. The supplied code and aggregate outputs support inspection and reproduction when the source input is obtained from its repository; they do not make the original source data redistributable. The exact recorded environment for this analysis was Python 3.13.16, pandas 2.2.3, scikit-learn 1.6.1 and SHAP 0.54.1. Other package versions should be taken from the run record only where explicitly documented.

PRIVACY AND HANDLING OF GENERATED FILES
This repository excludes observation-level and participant-coded outputs. Executing reproduce_relax_local_shap.py creates row-level outputs under the selected output directory. Do not publish those generated files. Retain them in restricted storage unless an appropriate privacy and disclosure review authorises release.
