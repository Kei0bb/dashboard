"""Spec CSVを読み込むユーティリティ。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import streamlit as st


@lru_cache(maxsize=32)
def load_specs(product_id: str, base_dir: str = "data") -> pd.DataFrame | None:
    specs_path = Path(base_dir) / product_id / "specs.csv"
    if not specs_path.exists():
        st.warning(f"Specs file not found: {specs_path}")
        return None
    df = pd.read_csv(specs_path)
    df.columns = df.columns.str.strip()
    return df


def extract_limits(spec_df: pd.DataFrame | None, parameter: str) -> tuple[float | None, float | None]:
    if spec_df is None or spec_df.empty:
        return None, None
    match = spec_df[spec_df["parameter"] == parameter]
    if match.empty:
        return None, None
    usl = match["USL"].iloc[0] if "USL" in match else None
    lsl = match["LSL"].iloc[0] if "LSL" in match else None
    return usl, lsl
