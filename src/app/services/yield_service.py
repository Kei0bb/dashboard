"""Yieldページ向けのデータ加工ロジック。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pandas as pd

from ..data import DatabaseRepository


@dataclass
class YieldService:
    repo: DatabaseRepository

    STAGES: ClassVar[tuple[str, str]] = ("CP", "FT")

    def get_products(self, data_dir: str = "data") -> list[str]:
        """data/配下のフォルダ名を品種リストとして返す。"""
        from pathlib import Path

        path = Path(data_dir)
        if not path.exists():
            return []
        return sorted([p.name for p in path.iterdir() if p.is_dir()])

    def load_dataset(self, product_name: str, stage: str = "CP") -> pd.DataFrame:
        stage_upper = stage.upper()
        if stage_upper not in self.STAGES:
            raise ValueError(f"Unsupported stage: {stage}")
        df = self.repo.load_yield_overview(product_name, stage_upper)
        if df.empty:
            return df
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df["Stage"] = stage_upper
        return df

    def load_all_stages(self, product_name: str) -> dict[str, pd.DataFrame]:
        """CP/FT両方のDataFrameを返す。"""
        return {stage: self.load_dataset(product_name, stage) for stage in self.STAGES}

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
