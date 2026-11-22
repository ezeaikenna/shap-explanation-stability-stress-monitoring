# Release Notes

## Version 1.0.0 — release candidate

This is the proposed first versioned release of the privacy-minimised computational materials supporting the separate SSAQS and RELAX analyses. It is a release candidate pending final privacy, source-rights, and public-availability review; no public release or software DOI has yet been created.

### Included materials

- Separate SSAQS global SHAP, RELAX global SHAP, and RELAX participant-level local-stability analysis materials.
- Executable notebooks and scripts, software-version metadata, fold-level and aggregate results, figures, and numerical comparison results.
- A SHA-256 manifest covering the repository files (excluding the manifest itself).
- Documentation of source-data requirements, analysis scope, and interpretation limits.

### Data, licences, and exclusions

- The original SSAQS and RELAX datasets and the RELAX questionnaire workbook are not redistributed.
- The SSAQS source record is identified as CC BY 4.0.
- The RELAX dataset concept DOI is https://doi.org/10.5281/zenodo.18693288; the inspected Zenodo Version 2 record is https://zenodo.org/records/20701999 and displays CC BY 4.0.
- Original repository software code is licensed under MIT; original repository documentation is licensed under CC BY 4.0. These licences do not extend to third-party datasets or restricted research records.
- Observation-level predictions and SHAP exports, pseudonymised participant-level outputs, and participant-level SHAP arrays are excluded to reduce disclosure risk. See `PUBLIC_RELEASE_EXCLUSIONS.txt`.
- No version-specific software DOI has been assigned. A DOI should be added to `CITATION.cff` only after the corresponding Zenodo archive has been created and verified.

### Interpretation limits

The analyses are separate within-dataset studies. They do not involve cross-dataset model or explanation transfer, or external validation. SHAP values are predictive attributions, not causal effects. The materials do not establish clinical validity or unrestricted generalisability.

### Final package-audit correction

The release review identified that the RELAX table-construction script can generate
a row-level analysis table containing participant identifiers, timestamps and
observed target values. This generated file and the participant-level script
outputs are explicitly identified as restricted in `PUBLIC_RELEASE_EXCLUSIONS.txt`.
Protective `.gitignore` rules were added to reduce the risk of accidental commits.
These safeguards do not replace a manual review of generated files before any upload.
