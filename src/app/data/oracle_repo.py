"""Oracle本番接続向けリポジトリ。"""

from __future__ import annotations

import pandas as pd

from ..config import AppConfig

try:
    import oracledb
except ImportError:  # pragma: no cover
    oracledb = None


class OracleRepository:
    def __init__(self, config: AppConfig) -> None:
        if oracledb is None:
            raise RuntimeError("oracle backend requested but python-oracledb is未インストール")
        self.config = config
        self._conn = oracledb.connect(
            user=self.config.database.oracle_username,
            password=self.config.database.oracle_password,
            dsn=self.config.database.oracle_dsn,
        )

    def load_yield_overview(self, product_name: str, stage: str = "CP") -> pd.DataFrame:
        params = {"product_name": product_name}
        df_long = pd.read_sql_query(YIELD_QUERY, self._conn, params=params)
        if df_long.empty:
            return df_long

        index_cols = ["Product", "LotID", "WaferID", "Time"]
        valid_index = [c for c in index_cols if c in df_long.columns]
        pivot_value = "BinCount" if "BinCount" in df_long.columns else "WaferID"
        aggfunc = "sum" if pivot_value == "BinCount" else "count"
        df = df_long.pivot_table(
            index=valid_index,
            columns="Bin",
            values=pivot_value,
            aggfunc=aggfunc,
            fill_value=0,
        )
        df = df.rename(columns={1: "0_PASS"})
        df = df.rename(
            columns={c: f"FAIL_BIN_{c}" for c in df.columns if c != "0_PASS"}
        ).reset_index()
        return df

    def load_wat_measurements(self, product_name: str) -> pd.DataFrame:
        params = {"product_name": product_name}
        df_long = pd.read_sql_query(WAT_QUERY, self._conn, params=params)
        if df_long.empty:
            return df_long

        pivot_index = [
            "Product",
            "BulkID",
            "WaferID",
            "DieX",
            "DieY",
            "Site",
            "Time",
        ]
        valid_index = [c for c in pivot_index if c in df_long.columns]
        df = df_long.pivot_table(index=valid_index, columns="Parameter", values="Value").reset_index()
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        return df


YIELD_QUERY = """
SELECT
    t1.PRODUCT_ID AS "Product",
    t1.LOT_ID AS "LotID",
    t1.WAFER_ID AS "WaferID",
    t1.REGIST_DATE AS "Time",
    t2.BIN_CODE AS "Bin",
    t2.BIN_COUNT AS "BinCount"
FROM YOUR_SCHEMA.SEMI_CP_HEADER t1
LEFT OUTER JOIN YOUR_SCHEMA.SEMI_CP_BIN_SUM t2 ON t1.CREATE_DATE = t2.CREATE_DATE
WHERE t1.PRODUCT_ID = :product_name
  AND t1.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY t1.REGIST_DATE ASC
"""

WAT_QUERY = """
SELECT
    t1.PRODUCT_ID AS "Product",
    t1.SUBSTRATE_ID AS "BulkID",
    t2.WAFER_ID AS "WaferID",
    t2.DIE_X AS "DieX",
    t2.DIE_Y AS "DieY",
    t2.SITE_NO AS "Site",
    t1.REGIST_DATE AS "Time",
    t2.ITEM_NAME AS "Parameter",
    t2.MEAS_DATA AS "Value"
FROM YOUR_SCHEMA.WAT_HEADER t1
LEFT OUTER JOIN YOUR_SCHEMA.WAT_DETAIL t2 ON t2.LOT_ID = t1.LOT_ID
WHERE t1.PRODUCT_ID = :product_name
  AND t1.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
"""
