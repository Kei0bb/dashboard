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

    def load_yield_overview(self, product_name: str) -> pd.DataFrame:
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
        df["Time"] = [
            base_time - timedelta(days=idx)
            for idx in range(len(df))
        ]
        df["WaferID"] = df["LotID"]
        df["BulkID"] = df["LotID"]
        df["SortNo"] = 1
        df["Tester"] = "MOCK"
        df["TP"] = "DEV"
        df["0_PASS"] = df["PassRate"]
        df["FAIL_BIN_1"] = (100 - df["PassRate"]).clip(lower=0)
        return df.drop(columns=["PassRate"])

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
