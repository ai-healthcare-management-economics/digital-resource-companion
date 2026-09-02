# Chapter 11: Evidence, Validation, and Real-World Evaluation

**Part IV — Governance, Evidence, and Lifecycle Decision-Making**

This folder contains the canonical resources aligned principally with Chapter 11. The chapter establishes the governing conceptual and methodological context; the companion resources support structured application, documentation, analysis, teaching, and local adaptation.

Resources should be selected according to the decision being addressed. No favourable score or computational result overrides a mandatory legal, clinical, ethical, privacy, cybersecurity, quality, equity, procurement, or institutional safeguard.

## Worked examples

- [AIHE-CASE11 — Local Validation and Causal Evaluation of a Readmission Model](../../worked_examples/AIHE-CASE11_local_validation_and_causal_evaluation_of_readmission_model) — Does local performance and observed service change support adoption, and what can reasonably be attributed to the AI-enabled pathway?

## Reference guides

- [AIHE-RG02 — Reporting and Appraisal Tool Selection Guide](guides/AIHE-RG02) — Match evidence type and study stage to current reporting and appraisal instruments without treating checklist completion as proof of validity, effectiveness, or regulatory conformity.
- [AIHE-RG06 — Diagnostic and Predictive Evidence Appraisal Checklist](guides/AIHE-RG06) — Appraise reference standards, index tests, data partitions, calibration, diagnostic accuracy, bias, subgroup performance, clinical utility, and downstream resource consequences.

## Python analytical modules

- [AIHE-PY04 — Predictive model development: logistic regression and random forest](python_analytics/PY04_model_dev) — Builds two baseline classifiers, compares test performance, and exports predictions for later validation modules.
- [AIHE-PY05 — Model performance, threshold trade-offs, and calibration](python_analytics/PY05_performance) — Calculates ROC AUC, Brier score, confusion-matrix measures across thresholds, calibration intercept and slope, and calibration bins.
- [AIHE-PY24 — Implementation evaluation with interrupted time series and control charts](python_analytics/PY24_impl_eval) — Evaluates change after an AI implementation using segmented regression, run charts, control limits, uptake, and balancing measures.
- [AIHE-PY30 — Random-effects meta-analysis and forest plot](python_analytics/PY30_meta_analysis) — Pools study-level effects using inverse-variance fixed and DerSimonian-Laird random-effects methods, quantifies heterogeneity, and creates forest and funnel plots.
- [AIHE-PY31 — Difference-in-differences evaluation](python_analytics/PY31_diff_in_diff) — Estimates the effect of AI implementation by comparing change over time in an intervention group with change in a comparison group.
- [AIHE-PY32 — Time-to-event and survival analysis](python_analytics/PY32_survival) — Estimates Kaplan-Meier survival curves and compares event timing between AI and comparator groups using a log-rank test.

## Supplemental specialist resources

Additional specialist resources are stored within the relevant core-resource folders. They preserve stable resource identifiers and provide more focused records, exercises, reference material, or structured data where a decision requires greater detail.

## Chapter process

- [Chapter 11 process map](flow/PROCESS_FLOW.md)

## Use and version control

- Release: **V1.0**
- Book alignment: **Chapter 11: Evidence, Validation, and Real-World Evaluation**
- Cite stable chapter, figure, table, case, and resource identifiers rather than printed page numbers.
- Record the evidence cut-off, intervention version, accountable owner, review date, and local modifications in any institutional use.
- Worked examples and bundled demonstration data are synthetic unless explicitly stated otherwise.

See the [Master Resource Catalogue](../../catalogs/MASTER_RESOURCE_CATALOG.xlsx) and the [Web Companion](../../docs/chapters/11.html) for additional navigation.
