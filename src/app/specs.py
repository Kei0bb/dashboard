"""Spec設定をYAMLファイルから読み込むユーティリティ。"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
import yaml

from .products import DEFAULT_SPEC_DIR, find_product_definition


@lru_cache(maxsize=1)
def _read_specs_file(relative_path: str) -> pd.DataFrame | None:
    spec_path = DEFAULT_SPEC_DIR / relative_path
    if not spec_path.exists():
        return None
    with spec_path.open(encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    specs = data.get("specs")
    if not specs:
        return None
    df = pd.DataFrame(specs)
    if df.empty:
        return None
    df.columns = df.columns.str.strip()
    return df


@lru_cache(maxsize=32)
def load_specs(product_id: str) -> pd.DataFrame | None:
    """config/products.yaml で指定された spec_file を読み込む。"""
    definition = find_product_definition(product_id)
    if definition is None:
        return None
    if definition.spec_file:
        df = _read_specs_file(definition.spec_file)
        if df is not None:
            return df
    if definition.specs:
        df = pd.DataFrame(definition.specs)
        if df.empty:
            return None
        df.columns = df.columns.str.strip()
        return df
    return None


def extract_limits(spec_df: pd.DataFrame | None, parameter: str) -> tuple[float | None, float | None]:
    if spec_df is None or spec_df.empty:
        return None, None
    match = spec_df[spec_df["parameter"] == parameter]
    if match.empty:
        return None, None
    usl = match["USL"].iloc[0] if "USL" in spec_df.columns else None
    lsl = match["LSL"].iloc[0] if "LSL" in spec_df.columns else None
    return usl, lsl
