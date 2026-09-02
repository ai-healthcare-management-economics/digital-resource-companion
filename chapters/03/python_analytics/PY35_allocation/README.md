# AIHE-PY35 — Constrained resource-allocation optimization

**Version:** V1.0 
**Primary chapter:** 3. Human–AI Decision Systems and Managerial Action 
**Additional chapter alignment:** 3, 8, 13 
**Related companion resources:** AIHE-B05 
**Data classification:** Synthetic example data only

## Purpose

Selects an allocation across candidate AI or service options to maximize expected value subject to budget, workforce, capacity, and minimum-service constraints.

## Choose an execution route

### Standard Python script

Use the script when you need a repeatable analysis, an IDE-based workflow, or a command that can be incorporated into a governed pipeline.

```bash
python python/35_resource_allocation_optimization.py
```

The actual script retains its stable numeric filename inside the `python/` folder. A Windows and a Unix launcher are provided at the application root.

### Jupyter notebook

Use the notebook when you prefer a stepwise, inspectable workflow for learning, review, or exploratory analysis. Open the `.ipynb` file in JupyterLab, VS Code, or Google Colab. The notebook and script call the same implementation in `src/`.

## Inputs

`Options` sheet with option, unit_cost, value_per_unit, maximum_units, workforce_hours_per_unit, capacity_units_per_unit, and minimum_units; `Parameters` sheet with budget, workforce hours, and capacity available.

- `data/xlsx/` contains the canonical Excel example and blank template.
- `data/ods/` V1.0 OpenDocument files are retained in the migration archive.
- All supplied data are synthetic and should be replaced only in a governed project copy.

## Outputs

Optimal units, resource use, expected value, binding constraints, comparison with simple ranking, and allocation chart.

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
