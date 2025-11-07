"""Yieldページ向けのデータ加工ロジック。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..data import DatabaseRepository


@dataclass
class YieldService:
    repo: DatabaseRepository

    def get_products(self, data_dir: str = "data") -> list[str]:
        """data/配下のフォルダ名を品種リストとして返す。"""
        from pathlib import Path

        path = Path(data_dir)
        if not path.exists():
            return []
        return sorted([p.name for p in path.iterdir() if p.is_dir()])

    def load_dataset(self, product_name: str) -> pd.DataFrame:
        return self.repo.load_yield_overview(product_name)

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
        out["Category"] = out[group_col].astype(str)
        return out
