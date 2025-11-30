"""Oracle本番接続向けリポジトリ。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar

import pandas as pd

from ..config import AppConfig

try:
    import oracledb
except ImportError:  # pragma: no cover
    oracledb = None


@dataclass(frozen=True)
class YieldQueryConfig:
    """品種ごとの歩留まりクエリ設定。"""

    sql: str
    process_override: str | None = None


CP_STANDARD_QUERY = """
SELECT
    h.PRODUCT_ID AS "Product",
    h.SUBSTRATE_ID AS "BulkID",
    h.LOT_ID AS "LotID",
    h.WAFER_ID AS "WaferID",
    h.REGIST_DATE AS "Time",
    h.PROCESS AS "Process",
    h.EFFECTIVE_NUM AS "EffectiveNum",
    r.BIN_CODE AS "Bin",
    r.BIN_NAME AS "BinName"
FROM SONAR.SEMI_CP_HEADER h
LEFT JOIN SONAR.SEMI_CP_RESULT r
  ON h.SUBSTRATE_ID = r.SUBSTRATE_ID
 AND h.WAFER_ID = r.WAFER_ID
 AND h.PRODUCT_ID = r.PRODUCT_ID
 AND h.REWORK_NEW = r.REWORK_NEW
WHERE UPPER(h.PRODUCT_ID) = :product_name
  AND h.PROCESS = :process
  AND NVL(r.REWORK_NEW, 0) = 0
  AND h.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY h.REGIST_DATE ASC, h.LOT_ID, h.WAFER_ID, r.BIN_CODE
"""

CP_CPY_QUERY = """
SELECT
    h.PRODUCT_ID AS "Product",
    h.SUBSTRATE_ID AS "BulkID",
    h.LOT_ID AS "LotID",
    h.WAFER_ID AS "WaferID",
    h.REGIST_DATE AS "Time",
    h.PROCESS AS "Process",
    h.EFFECTIVE_NUM AS "EffectiveNum",
    b.BIN_CODE AS "Bin",
    b.BIN_COUNT AS "BinCount",
    b.BIN_NAME AS "BinName"
FROM SONAR.SEMI_CP_HEADER h
LEFT JOIN SONAR.SEMI_CP_BIN_SUM b
  ON h.SUBSTRATE_ID = b.SUBSTRATE_ID
 AND h.WAFER_ID = b.WAFER_ID
 AND h.PRODUCT_ID = b.PRODUCT_ID
 AND h.PROCESS = b.PROCESS
 AND h.REWORK_NEW = b.REWORK_NEW
WHERE UPPER(h.PRODUCT_ID) = :product_name
  AND h.PROCESS = :process
  AND b.REWORK_NEW = 0
  AND h.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY h.REGIST_DATE ASC, h.LOT_ID, h.WAFER_ID, b.BIN_CODE
"""

FT_BIN_SUM_QUERY = """
SELECT
    h.PRODUCT_ID AS "Product",
    h.ASSY_LOT_ID AS "BulkID",
    h.ASSY_LOT_ID AS "LotID",
    h.WAFER_ID AS "WaferID",
    h.REGIST_DATE AS "Time",
    h.PROCESS AS "Process",
    h.EFFECTIVE_NUM AS "EffectiveNum",
    b.BIN_CODE AS "Bin",
    b.BIN_COUNT AS "BinCount",
    b.BIN_NAME AS "BinName"
FROM SONAR.SEMI_FT_HEADER h
LEFT JOIN SONAR.SEMI_FT_BIN_SUM b
  ON h.ASSY_LOT_ID = b.ASSY_LOT_ID
 AND NVL(h.WAFER_ID, -1) = NVL(b.WAFER_ID, -1)
 AND h.PRODUCT_ID = b.PRODUCT_ID
 AND h.PROCESS = b.PROCESS
 AND h.REWORK_NEW = b.REWORK_NEW
WHERE UPPER(h.PRODUCT_ID) = :product_name
  AND h.PROCESS = :process
  AND NVL(b.REWORK_NEW, 0) = 0
  AND h.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY h.REGIST_DATE ASC, h.ASSY_LOT_ID, b.BIN_CODE
"""

CP_QUERY_DEFAULT = YieldQueryConfig(sql=CP_STANDARD_QUERY)
CP_QUERY_MAP: dict[str, YieldQueryConfig] = {
    # CPY (Fail-Stop) のようにBinCount付きデータを使用したい品種はここで指定
    "scp117a": YieldQueryConfig(sql=CP_CPY_QUERY, process_override="CPY"),
}

FT_QUERY_DEFAULT = YieldQueryConfig(sql=FT_BIN_SUM_QUERY)
FT_QUERY_MAP: dict[str, YieldQueryConfig] = {}

WAT_QUERY = """
SELECT
    h.PRODUCT_ID AS "Product",
    h.SUBSTRATE_ID AS "BulkID",
    d.WAFER_ID AS "WaferID",
    d.DIE_X AS "DieX",
    d.DIE_Y AS "DieY",
    d.SITE_NO AS "Site",
    h.REGIST_DATE AS "Time",
    d.ITEM_NAME AS "Parameter",
    d.MEAS_DATA AS "Value"
FROM SONAR.WAT_HEADER h
LEFT JOIN SONAR.WAT_DETAIL d ON d.LOT_ID = h.LOT_ID
WHERE UPPER(h.PRODUCT_ID) = :product_name
  AND h.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
"""


class OracleRepository:
    """Oracle本番DBからYield/WATデータを取得するリポジトリ。"""

    PASS_BIN_CODE: ClassVar[int] = 1
    CP_DEFAULT: ClassVar[YieldQueryConfig] = CP_QUERY_DEFAULT
    CP_QUERY_MAP: ClassVar[dict[str, YieldQueryConfig]] = CP_QUERY_MAP
    FT_DEFAULT: ClassVar[YieldQueryConfig] = FT_QUERY_DEFAULT
    FT_QUERY_MAP: ClassVar[dict[str, YieldQueryConfig]] = FT_QUERY_MAP

    def __init__(self, config: AppConfig) -> None:
        if oracledb is None:
            raise RuntimeError("oracle backend requested but python-oracledb is未インストール")
        self.config = config
        self._conn = oracledb.connect(
            user=self.config.database.oracle_username,
            password=self.config.database.oracle_password,
            dsn=self.config.database.oracle_dsn,
        )

    def _resolve_yield_query(self, product_name: str, stage: str) -> tuple[str, dict[str, str], str]:
        stage_upper = stage.upper()
        params: dict[str, str] = {"product_name": product_name.upper()}
        if stage_upper == "FT":
            query_cfg = self.FT_QUERY_MAP.get(product_name.lower(), self.FT_DEFAULT)
        else:
            query_cfg = self.CP_QUERY_MAP.get(product_name.lower(), self.CP_DEFAULT)
        params["process"] = query_cfg.process_override or stage_upper
        return query_cfg.sql, params, stage_upper

    def load_yield_overview(self, product_name: str, stage: str = "CP") -> pd.DataFrame:
        query, params, stage_label = self._resolve_yield_query(product_name, stage)
        df_long = pd.read_sql_query(query, self._conn, params=params)
        if df_long.empty:
            return df_long
        df_long["BinLabel"] = pd.to_numeric(df_long["Bin"], errors="coerce").astype("Int64").astype(str).str.zfill(2)
        if "BinName" in df_long.columns:
            df_long["BinLabel"] = (
                df_long["BinLabel"]
                + "_"
                + df_long["BinName"].fillna("").astype(str).str.strip()
            ).str.rstrip("_")
        pass_label = None
        pass_rows = df_long[pd.to_numeric(df_long["Bin"], errors="coerce") == self.PASS_BIN_CODE]
        if not pass_rows.empty:
            pass_label = pass_rows["BinLabel"].iloc[0]
        index_cols = ["Product", "BulkID", "LotID", "WaferID", "Time"]
        if "EffectiveNum" in df_long.columns:
            df_long["EffectiveNum"] = pd.to_numeric(df_long["EffectiveNum"], errors="coerce")
            index_cols.append("EffectiveNum")
        valid_index = [c for c in index_cols if c in df_long.columns]
        pivot_value = "BinCount" if "BinCount" in df_long.columns else "WaferID"
        aggfunc = "sum" if pivot_value == "BinCount" else "count"
        df = df_long.pivot_table(
            index=valid_index,
            columns="BinLabel",
            values=pivot_value,
            aggfunc=aggfunc,
            fill_value=0,
        ).reset_index()
        rename_map: dict[str, str] = {}
        fail_columns: list[str] = []
        bin_columns = [c for c in df.columns if c not in valid_index]
        for col in bin_columns:
            if pass_label and col == pass_label:
                rename_map[col] = "0_PASS"
            else:
                new_name = f"FAIL_BIN_{col}"
                rename_map[col] = new_name
                fail_columns.append(new_name)
        df = df.rename(columns=rename_map)
        pass_column = "0_PASS" if "0_PASS" in df.columns else None
        effective_col = "EffectiveNum" if "EffectiveNum" in df.columns else None
        if effective_col:
            denom = df[effective_col].replace(0, pd.NA)
            if fail_columns:
                df[fail_columns] = df[fail_columns].div(denom, axis=0) * 100
            if pass_column:
                df[pass_column] = df[pass_column].div(denom, axis=0) * 100
        if "Time" in df.columns:
            df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df["Stage"] = stage_label
        return df

    def load_wat_measurements(self, product_name: str) -> pd.DataFrame:
        params = {"product_name": product_name.upper()}
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
