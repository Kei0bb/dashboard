"""WAT/SPCページ向けのデータ加工。"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from ..data import DatabaseRepository


@dataclass
class WATService:
    repo: DatabaseRepository

    def load_dataset(self, product_name: str) -> pd.DataFrame:
        return self.repo.load_wat_measurements(product_name)

    @staticmethod
    def available_parameters(df: pd.DataFrame) -> list[str]:
        if df.empty:
            return []
        id_cols = {"Product", "BulkID", "WaferID", "DieX", "DieY", "Site", "Time"}
        return [c for c in df.columns if c not in id_cols]

    @staticmethod
    def list_wafers(df: pd.DataFrame) -> list[str]:
        if df.empty or "WaferID" not in df.columns:
            return []
        return sorted(df["WaferID"].dropna().unique())

    @staticmethod
    def filter_by_wafer(df: pd.DataFrame, wafer_id: str) -> pd.DataFrame:
        if df.empty or "WaferID" not in df.columns:
            return pd.DataFrame()
        return df[df["WaferID"] == wafer_id]

    @staticmethod
    def parameter_range(df: pd.DataFrame, parameter: str) -> tuple[float | None, float | None]:
        if df.empty or parameter not in df.columns:
            return (None, None)
        series = pd.to_numeric(df[parameter], errors="coerce").dropna()
        if series.empty:
            return (None, None)
        return (float(series.min()), float(series.max()))

    @staticmethod
    def aggregate_bulk_trend(df: pd.DataFrame, parameter: str) -> pd.DataFrame:
        if df.empty or parameter not in df.columns:
            return pd.DataFrame()
        agg = (
            df.groupby("BulkID")
            .agg(mean_val=(parameter, "mean"), Time=("Time", "first"))
            .sort_values("Time")
            .reset_index()
        )
        agg["moving_avg"] = agg["mean_val"].rolling(window=3, min_periods=1).mean()
        return agg
