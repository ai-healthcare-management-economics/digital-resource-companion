# AIHE-PY15 — Probabilistic sensitivity analysis, CEAC, and EVPI

**Version:** V1.0 
**Primary chapter:** 8. Decision Modelling, Simulation, and the Value of Information 
**Additional chapter alignment:** 8 
**Related companion resources:** AIHE-B05, AIHE-RG05 
**Data classification:** Synthetic example data only

## Purpose

Propagates uncertainty in incremental costs and effects through Monte Carlo simulation, estimates cost-effectiveness probabilities across thresholds, and computes expected value of perfect information.

## Choose an execution route

### Standard Python script

Use the script when you need a repeatable analysis, an IDE-based workflow, or a command that can be incorporated into a governed pipeline.

```bash
python python/15_probabilistic_sensitivity_ceac_evpi.py
```

The actual script retains its stable numeric filename inside the `python/` folder. A Windows and a Unix launcher are provided at the application root.

### Jupyter notebook

Use the notebook when you prefer a stepwise, inspectable workflow for learning, review, or exploratory analysis. Open the `.ipynb` file in JupyterLab, VS Code, or Google Colab. The notebook and script call the same implementation in `src/`.

## Inputs

`Parameters` sheet with means, standard deviations, correlation, number of simulations, and threshold range.

- `data/xlsx/` contains the canonical Excel example and blank template.
- `data/ods/` V1.0 OpenDocument files are retained in the migration archive.
- All supplied data are synthetic and should be replaced only in a governed project copy.

## Outputs

Simulation draws, cost-effectiveness plane, CEAC, EVPI by threshold, probability of cost-effectiveness, and reproducible seed metadata.

- `outputs/example/` contains representative synthetic results.
- `outputs/generated/` is reserved for local runs and should not be committed when it contains confidential data.

## Recommended workflow

1. Read the aligned chapter and related companion records.
2. Run the supplied synthetic example without modification.
3. Review assumptions, calculations, outputs, and limitations.
4. Copy the blank input template and document local changes.
5. Run the analysis in a controlled environment.
6. Preserve the input version, software environment, random seed, output location, evidence cut-off, analyst, reviewer, and decision context.

## Limitations

This application is an educational and decision-support example. It is not a validated clinical, legal, regulatory, procurement, accreditation, cybersecurity, quality-certification, or health technology assessment instrument. Institutional use requires local verification, validation, responsible ownership, data protection, and an auditable decision record.
