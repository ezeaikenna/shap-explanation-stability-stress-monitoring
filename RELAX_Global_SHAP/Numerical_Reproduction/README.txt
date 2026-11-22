RELAX GLOBAL SHAP — NUMERICAL REPRODUCTION

This directory documents the notebook-based numerical reproduction of the RELAX global SHAP analysis. The notebook follows the global-analysis method in PHASE_III_Model_Aligned_SHAP_Stability_FIXED.ipynb and uses the frozen analysis-ready input identified by SHA-256 in RELAX_global_SHAP_run_metadata.json. The original source dataset is not redistributed; obtain source materials from the original repository and follow its access conditions and licence.

The reproduction used Python 3.13.18, NumPy 2.4.6, pandas 3.1.1, SciPy 1.16.3, scikit-learn 1.9.1 and SHAP 0.54.1. Python, pandas, scikit-learn and SHAP match the versions recorded for the original global analysis. The original NumPy and SciPy versions were not documented.

All 16 predefined numerical consistency checks passed. The reproduced held-out SHAP attribution values (1,148 rows × 59 features) match the archived attribution values exactly. The five fold allocations and fold-specific seeds match. All 295 fold-feature importance comparisons, all 59 aggregated feature summaries and all 10 pairwise stability comparisons match the archived references. Prediction outputs differ by at most 1.7763568394002505e-15.

Archived stability estimates: mean pairwise Spearman = 0.9652504850938761; mean Kendall = 0.8689356257953765; mean top-five Jaccard = 0.5095238095238095.

The archived reference files in the parent RELAX_Global_SHAP directory have been retained unchanged. This reproduction demonstrates agreement with the recorded software versions and archived numerical outputs, but does not establish complete identity of the historical environment because the original NumPy and SciPy versions were not recorded.
