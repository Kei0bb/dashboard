"""Yieldページ向けのデータ加工ロジック。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pandas as pd

from ..data import DatabaseRepository
from ..products import ProductDefinition, find_product_definition, list_products


@dataclass
class YieldService:
    repo: DatabaseRepository

    STAGES: ClassVar[tuple[str, str]] = ("CP", "FT")

    def get_products(self, data_dir: str = "data") -> list[ProductDefinition]:
        """設定ファイル優先で品種リストを取得する。"""
        return list_products(data_dir=data_dir)

    def _resolve_source_name(self, product: ProductDefinition | str) -> str:
        if isinstance(product, ProductDefinition):
            return product.source_name
        definition = find_product_definition(product)
        return definition.source_name if definition else str(product)

    def load_dataset(self, product: ProductDefinition | str, stage: str = "CP") -> pd.DataFrame:
        stage_upper = stage.upper()
        if stage_upper not in self.STAGES:
            raise ValueError(f"Unsupported stage: {stage}")
        source_name = self._resolve_source_name(product)
        df = self.repo.load_yield_overview(source_name, stage_upper)
        if df.empty:
            return df
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df["Stage"] = stage_upper
        return df

    def load_all_stages(self, product: ProductDefinition | str) -> dict[str, pd.DataFrame]:
        """CP/FT両方のDataFrameを返す。"""
        return {stage: self.load_dataset(product, stage) for stage in self.STAGES}

    @staticmethod
    def build_summary(df: pd.DataFrame, agg: str) -> pd.DataFrame:
        if df.empty:
            return df
        df = df.copy()
        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        if agg != "BulkID":
            freq_map = {
                "Daily": "D",
                "Weekly": "W",
                "Monthly": "M",
                "Quarterly": "Q",
            }
            df["Period"] = df["Time"].dt.to_period(freq_map[agg])
            group_col = "Period"
        else:
            group_col = "BulkID"

        metric_cols = [c for c in df.columns if c.startswith("FAIL_BIN_") or c == "0_PASS"]
        agg_dict = {c: "mean" for c in metric_cols}
        out = (
            df.groupby(group_col)
            .agg(agg_dict)
            .sort_index()
            .reset_index()
        )
        if agg == "Weekly":
            period_ts = out["Period"].dt.to_timestamp()
            iso = period_ts.dt.isocalendar()
            out["Category"] = (
                iso["year"].astype(str)
                + "WW"
                + iso["week"].astype(str).str.zfill(2)
            )
        elif agg == "Monthly":
            out["Category"] = out["Period"].dt.month.astype(str) + "月"
        else:
            out["Category"] = out[group_col].astype(str)
        return out
