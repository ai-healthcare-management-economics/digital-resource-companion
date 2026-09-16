"""Self-contained runner: ROI, net benefit, and benefit-realization analysis.

The default command uses the supplied synthetic workbook and writes to outputs/generated.
Use --input and --output to select governed local files and a different result directory.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from aihe_analytics.module_11_roi_benefit_realization import run_analysis


def main() -> None:
    default_input = ROOT / "data" / "xlsx" / "11_roi_benefit_realization_sample.xlsx"
    default_output = ROOT / "outputs" / "generated"
    parser = argparse.ArgumentParser(description='ROI, net benefit, and benefit-realization analysis')
    parser.add_argument(
        "--input",
        default=str(default_input),
        help="Path to the Excel input workbook. Defaults to the supplied synthetic example.",
    )
    parser.add_argument(
        "--output",
        default=str(default_output),
        help="Folder for generated results. Defaults to outputs/generated.",
    )
    parser.add_argument("--seed", type=int, default=2026, help="Random seed for stochastic methods.")
    args = parser.parse_args()
    try:
        result = run_analysis(Path(args.input), Path(args.output), seed=args.seed)
    except Exception as exc:
        raise SystemExit(f"ERROR: {exc}") from exc
    print(f"Completed: ROI, net benefit, and benefit-realization analysis")
    print(f"Input: {Path(args.input).resolve()}")
    print(f"Output: {Path(args.output).resolve()}")
    if result is not None:
        print(f"Returned: {result}")


if __name__ == "__main__":
    main()
