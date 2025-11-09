"""ローカル開発向けSQLiteデータリポジトリ。"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pandas as pd

from ..config import AppConfig


class SQLiteRepository:
    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._conn = sqlite3.connect(self.config.database.sqlite_path or "data/test.db")

    def load_yield_overview(self, product_name: str, stage: str = "CP") -> pd.DataFrame:
        stage_upper = stage.upper()
        if stage_upper not in {"CP", "FT"}:
            raise ValueError(f"Unsupported stage: {stage}")

        df_cp = self._build_cp_frame(product_name)
        if df_cp.empty:
            return df_cp

        if stage_upper == "CP":
            df_stage = df_cp.copy()
        else:
            df_stage = self._build_ft_frame(df_cp)

        df_stage["Stage"] = stage_upper
        return df_stage

    def _build_cp_frame(self, product_name: str) -> pd.DataFrame:
        query = """
            SELECT product AS Product, lot_id AS LotID, yield AS PassRate
            FROM yields
            WHERE product = ?
            ORDER BY lot_id
        """
        df = pd.read_sql_query(query, self._conn, params=(product_name,))
        if df.empty:
            return df

        base_time = datetime.utcnow()
        df["Time"] = [base_time - timedelta(days=idx) for idx in range(len(df))]
        df["WaferID"] = df["LotID"]
        df["BulkID"] = df["LotID"]
        df["SortNo"] = 1
        df["Tester"] = "MOCK"
        df["TP"] = "DEV"
        df["0_PASS"] = df["PassRate"]
        df["FAIL_BIN_1"] = (100 - df["PassRate"]).clip(lower=0)
        return df.drop(columns=["PassRate"])

    def _build_ft_frame(self, df_cp: pd.DataFrame) -> pd.DataFrame:
        df = df_cp.copy()
        offsets = pd.Series(range(len(df)), index=df.index, dtype=float)
        degradation = 1.5 + (offsets % 5) * 0.4
        df["0_PASS"] = (df["0_PASS"] - degradation).clip(lower=60.0)
        fail_cols = [c for c in df.columns if c.startswith("FAIL_BIN_")]
        if fail_cols:
            remaining = (100 - df["0_PASS"]).clip(lower=0)
            per_col = remaining / len(fail_cols)
            for col in fail_cols:
                df[col] = per_col
        else:
            df["FAIL_BIN_1"] = (100 - df["0_PASS"]).clip(lower=0)
        df["Time"] = df["Time"] + timedelta(hours=12)
        return df

    def load_wat_measurements(self, product_name: str) -> pd.DataFrame:
        query = """
            SELECT product, lot_id, subgroup, param1, param2
            FROM wat_data
            WHERE product = ?
            ORDER BY lot_id, subgroup
        """
        df = pd.read_sql_query(query, self._conn, params=(product_name,))
        if df.empty:
            return df

        df = df.rename(columns={"product": "Product"})
        df["BulkID"] = df["lot_id"]
        df["WaferID"] = df["lot_id"].astype(str) + "_" + df["subgroup"].astype(str)
        df["DieX"] = df["subgroup"] % 10
        df["DieY"] = df["subgroup"] // 10
        df["Site"] = df["subgroup"]
        df["Time"] = pd.to_datetime(datetime.utcnow()) - pd.to_timedelta(df["subgroup"], unit="D")
        df = df.drop(columns=["lot_id", "subgroup"])
        ordered_cols = [
            "Product",
            "BulkID",
            "WaferID",
            "DieX",
            "DieY",
            "Site",
            "Time",
        ]
        remaining_cols = [c for c in df.columns if c not in ordered_cols]
        return df[ordered_cols + remaining_cols]
