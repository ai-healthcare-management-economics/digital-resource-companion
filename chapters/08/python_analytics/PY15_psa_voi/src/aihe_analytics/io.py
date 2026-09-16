
from __future__ import annotations
import json, platform, sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable
import pandas as pd

def ensure_output_dir(path: str | Path) -> Path:
    out = Path(path).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    return out

def read_sheet(path: str | Path, sheet_name: str) -> pd.DataFrame:
    file_path = Path(path).expanduser().resolve()
    if not file_path.exists():
        raise FileNotFoundError(
            f"Input wb not found: {file_path}\n"
            "Use the sample wb supplied with the module, or copy the blank template."
        )
    try:
        return pd.read_excel(file_path, sheet_name=sheet_name)
    except ValueError as exc:
        available = pd.ExcelFile(file_path).sheet_names
        raise ValueError(
            f"Worksheet '{sheet_name}' is missing from {file_path.name}. "
            f"Available worksheets: {available}"
        ) from exc

def require_columns(frame: pd.DataFrame, columns: Iterable[str], sheet_name: str) -> None:
    missing = [c for c in columns if c not in frame.columns]
    if missing:
        raise ValueError(
            f"Worksheet '{sheet_name}' is missing required columns {missing}. "
            f"Available columns: {list(frame.columns)}"
        )

def write_metadata(output_dir: str | Path, module_id: str, input_path: str | Path, extra: dict | None = None) -> None:
    out = ensure_output_dir(output_dir)
    payload = {
        "module_id": module_id,
        "input_file": str(Path(input_path).expanduser().resolve()),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": sys.version,
        "platform": platform.platform(),
        "synthetic_example": True,
    }
    if extra:
        payload.update(extra)
    (out / "run_metadata.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
