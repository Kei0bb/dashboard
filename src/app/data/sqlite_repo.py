"""ローカル開発向けSQLiteデータリポジトリ。"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timedelta

import pandas as pd

from ..config import AppConfig


class SQLiteRepository:
    PASS_BIN_CODE = 1

    def __init__(self, config: AppConfig) -> None:
        self.config = config
        self._conn = sqlite3.connect(self.config.database.sqlite_path or "data/test.db")

    def load_yield_overview(self, product_name: str, stage: str = "CP") -> pd.DataFrame:
        stage_upper = stage.upper()
        if stage_upper not in {"CP", "FT"}:
            raise ValueError(f"Unsupported stage: {stage}")

        metadata = self._build_lot_metadata(product_name)
        df_bins = self._load_bin_distribution(product_name, stage_upper)
        if df_bins.empty:
            return df_bins
        df = df_bins.merge(metadata, on=["Product", "LotID"], how="left")
        df["Stage"] = stage_upper
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        return df

    def _build_lot_metadata(self, product_name: str) -> pd.DataFrame:
        query = """
            SELECT product AS Product, lot_id AS LotID
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
        return df

    def _load_bin_distribution(self, product_name: str, stage: str) -> pd.DataFrame:
        query = """
            SELECT
                product AS Product,
                lot_id AS LotID,
                stage AS Stage,
                bin_code AS BinCode,
                bin_name AS BinName,
                bin_count AS BinCount,
                effective_num AS EffectiveNum
            FROM bin_data
            WHERE product = ?
              AND stage = ?
            ORDER BY lot_id, bin_code
        """
        df = pd.read_sql_query(query, self._conn, params=(product_name, stage))
        if df.empty:
            return df
        df["BinLabel"] = (
            pd.to_numeric(df["BinCode"], errors="coerce")
            .astype("Int64")
            .astype(str)
            .str.zfill(2)
        )
        df["BinLabel"] = (
            df["BinLabel"] + "_" + df["BinName"].fillna("").astype(str).str.strip()
        ).str.rstrip("_")
        pass_rows = df[pd.to_numeric(df["BinCode"], errors="coerce") == self.PASS_BIN_CODE]
        pass_label = pass_rows["BinLabel"].iloc[0] if not pass_rows.empty else None
        value_cols = ["Product", "LotID", "BinLabel"]
        pivot = (
            df.pivot_table(
                index=["Product", "LotID"],
                columns="BinLabel",
                values="BinCount",
                aggfunc="sum",
                fill_value=0,
            )
            .reset_index()
        )
        eff = (
            df[["Product", "LotID", "EffectiveNum"]]
            .drop_duplicates(["Product", "LotID"])
            .rename(columns={"EffectiveNum": "EffectiveNum"})
        )
        pivot = pivot.merge(eff, on=["Product", "LotID"], how="left")
        rename_map: dict[str, str] = {}
        fail_cols: list[str] = []
        bin_columns = [c for c in pivot.columns if c not in {"Product", "LotID", "EffectiveNum"}]
        for col in bin_columns:
            if pass_label and col == pass_label:
                rename_map[col] = "0_PASS"
            else:
                new_name = f"FAIL_BIN_{col}"
                rename_map[col] = new_name
                fail_cols.append(new_name)
        pivot = pivot.rename(columns=rename_map)
        denom = pivot["EffectiveNum"].replace(0, pd.NA)
        all_rate_cols = fail_cols + (["0_PASS"] if "0_PASS" in pivot.columns else [])
        for col in all_rate_cols:
            pivot[col] = pivot[col].div(denom) * 100
        return pivot.drop(columns=["EffectiveNum"])

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
