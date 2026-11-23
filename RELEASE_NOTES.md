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


## Privacy-safeguard maintenance — 2026-11-22

- Added research-specific `.gitignore` rules for known restricted SSAQS and RELAX generated outputs and local notebook workspaces.
- Added `check_public_release.py` as a supplementary pre-release check for known restricted paths and sensitive-looking structured-data fields.
- Expanded `PUBLIC_RELEASE_EXCLUSIONS.txt` and updated the README instructions to explain safe local execution and pre-commit review.
- No analysis code, numerical result tables, figures, or manuscript figures were changed in this maintenance update.
- At this maintenance stage, the checker covered known restricted paths only. Later hardening entries below describe the subsequent staged-content and Git-history checks. The checker is not a privacy certification; institutional/privacy clearance and manual release review remain necessary.


## Release-safeguard hardening — 2026-11-22

- Reviewed `RELAX_global_SHAP_run_metadata.json` and retained it as aggregate reproducibility metadata; it contains no participant identifiers, row-level records, timestamps or local filesystem paths.
- Extended `check_public_release.py` to inspect known restricted paths in the working tree and staged Git additions, modifications, renames and copies when run inside a Git worktree.
- Added regression tests for restricted participant-level output directories, local notebook workspaces, reviewed aggregate metadata, safe aggregate files and staged-index detection.
- Updated release instructions to run the checker and regression tests before committing.
- No research scripts, notebooks, numerical results, figures or manuscript content were changed.


## Content and Git-history safeguard update — 2026-11-22

- Expanded the release checker to inspect CSV/TSV headers and JSON keys for sensitive-looking participant, subject, user, record, timestamp and row-index fields, including staged Git blob content.
- Extended optional `--history` scanning to inspect reachable local Git refs for known restricted paths and sensitive-looking fields in historical CSV/TSV/JSON blobs. Fetch remote branches before scanning; unfetched refs and other binary formats are outside scope.
- Removed generated Python bytecode/cache directories from the distributable archive.
- Added a regression test for sensitive structured content committed under a generic filename and later deleted.
- Expanded regression coverage from five to eight tests, including generic-filename structured-content detection and historical restricted-path detection.
- Updated release documentation to state supported formats and remaining limitations.
- No scientific analysis, numerical result, figure or manuscript content was changed.


## Structured-field detection refinement — 2026-11-22

- Extended sensitive-field matching to recognise common camelCase variants such as `participantId` and `rowIndex`, in addition to underscore-, hyphen- and space-separated forms.
- Removed the 2 MB truncation of JSON input before parsing, which could cause larger valid JSON files to be skipped when the truncated text was invalid.
- Added regression tests for camelCase field names and JSON files larger than 2 MB.
- These checks remain heuristic and do not inspect arbitrary values, all binary formats, or semantic disclosure risk. Manual privacy and disclosure review remains necessary.

## JSONL inspection correction — 2026-11-23

- Extended structured-content inspection to JSON Lines (.jsonl), parsing each nonblank record independently, detecting sensitive-looking fields in later records, and reporting malformed records as findings rather than silently ignoring them. Added regression tests for both behaviours.


## JSON and CSV safeguard correction — 2026-11-23

- Changed malformed JSON handling to report invalid JSON documents as findings instead of silently skipping structured-content inspection.
- Corrected CSV regression fixtures to use actual newline characters and added explicit tests for multiline sensitive headers and malformed JSON.
- Updated the checker status message to include JSONL in the supported historical structured-content formats.
