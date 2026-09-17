# AIHE-PY28 — Workflow time, capacity, productivity, and benefit realization

**Version:** V1.0 
**Primary chapter:** 4. Productivity, Work Redesign, and Implementation 
**Additional chapter alignment:** 4, 6 
**Related companion resources:** AIHE-B03 
**Data classification:** Synthetic example data only

## Purpose

Translates gross task-time savings into net time, usable capacity, realized output, quality-adjusted productivity, and economic value.

## Choose an execution route

### Standard Python script

Use the script when you need a repeatable analysis, an IDE-based workflow, or a command that can be incorporated into a governed pipeline.

```bash
python python/28_workflow_productivity.py
```

The actual script retains its stable numeric filename inside the `python/` folder. A Windows and a Unix launcher are provided at the application root.

### Jupyter notebook

Use the notebook when you prefer a stepwise, inspectable workflow for learning, review, or exploratory analysis. Open the `.ipynb` file in JupyterLab, VS Code, or Google Colab. The notebook and script call the same implementation in `src/`.

## Inputs

`Tasks` sheet with task, baseline minutes, AI minutes, review minutes, correction minutes, annual volume, redeployable fraction, quality factor, and staff cost per hour; `Parameters` sheet with capacity utilization assumption.

- `data/xlsx/` contains the canonical Excel example and blank template.
- All supplied data are synthetic and should be replaced only in a governed project copy.

## Outputs

Gross and net time savings, released and used capacity, labor-value estimate, quality-adjusted productivity, task comparison chart, and common-error flags.

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

## Notebook and hosted use

Open `notebook/28_workflow_productivity.ipynb` from this module in JupyterLab, VS Code, or Google Colab. Retain the complete module folder so that the notebook, input data, environment files, and `src/` implementation remain together.

For a local environment, run the following from this module folder:

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r environment/requirements.txt
```

Use an installed notebook interface, run the supplied synthetic example, and inspect `outputs/generated/`. The notebook uses the same implementation used by the Python entry point. Preserve input versions, the environment, and outputs before any local adaptation.

[Repository notebook](https://github.com/ai-healthcare-management-economics/digital-resource-companion/blob/main/chapters/04/python_analytics/PY28_productivity/notebook/28_workflow_productivity.ipynb) · [Open in Google Colab](https://colab.research.google.com/github/ai-healthcare-management-economics/digital-resource-companion/blob/main/chapters/04/python_analytics/PY28_productivity/notebook/28_workflow_productivity.ipynb)

Do not upload patient identifiers, credentials, private keys, confidential contracts, or restricted institutional information to a public notebook service.
