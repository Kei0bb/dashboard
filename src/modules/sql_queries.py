"""
このモジュールには、データベースからデータを取得するためのSQLクエリが
文字列定数として格納されています。
"""

# --- 標準的な歩留まりクエリ (CP) ---
YIELD_QUERY = """
-- 標準的なCP(Chip Probe)テスト向けのクエリ。
-- 1行が1ダイのテスト結果を表す「縦長形式」のデータを取得することを想定しています。
-- db_utils.py側で、このBin列を使ってpivot_tableで集計が行われます。
SELECT
    t1.PRODUCT_ID AS "Product",
    t1.LOT_ID AS "LotID",
    t1.WAFER_ID AS "WaferID",
    t1.REGIST_DATE AS "Time",
    t2.BIN_CODE AS "Bin" -- ダイのテスト結果(Bin)
FROM
    YOUR_SCHEMA.SEMI_CP_HEADER t1
LEFT OUTER JOIN
    YOUR_SCHEMA.SEMI_CP_RESULT t2 ON t1.CREATE_DATE = t2.CREATE_DATE
WHERE
    t1.PRODUCT_ID = :product_name
    AND t2.REWORK_NEW = 0
    AND t1.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY
    t1.REGIST_DATE ASC
"""

# --- CPY (Fail-Stop)用の歩留まりクエリ ---
CPY_YIELD_QUERY = """
-- CPY (Chip Probe Yield) データ用のクエリ。
-- このクエリは、各ウェーハ・各Binあたりのダイ数を集計済み(BinCount)の形で取得します。
-- db_utils.py側で、このBinCount列を使って横持ちデータが作成されます。
SELECT
    t1.PRODUCT_ID AS "Product",
    t1.LOT_ID AS "LotID",
    t1.WAFER_ID AS "WaferID",
    t1.REGIST_DATE AS "Time",
    t2.BIN_CODE AS "Bin",
    t2.BIN_COUNT AS "BinCount"
FROM
    YOUR_SCHEMA.SEMI_CP_HEADER t1
LEFT OUTER JOIN
    YOUR_SCHEMA.SEMI_CP_BIN_SUM t2 ON t1.CREATE_DATE = t2.CREATE_DATE
WHERE
    t1.PRODUCT_ID = :product_name
    AND t1.PROCESS = 'CPY'
    AND t2.REWORK_NEW = 0
    AND t1.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
ORDER BY
    t1.REGIST_DATE ASC
"""


# --- 製品名と歩留まりクエリのマッピング ---
# ここで指定されていない製品は、自動的にデフォルトのYIELD_QUERYが使用されます。
YIELD_QUERY_MAP = {
    'productA': CPY_YIELD_QUERY,  # productA は集計済みのCPYクエリを使用
    'DEFAULT': YIELD_QUERY,
}


# --- WAT/SPECS クエリ (変更なし) ---
WAT_QUERY = """
-- WAT (Wafer Acceptance Test) データ用のクエリ。
-- 1行に1つのパラメータ測定値が含まれる「縦長形式」のデータを取得します。
-- db_utils.py側で、このデータを使ってpivot_tableで横持ちデータが作成されます。
SELECT
    t1.PRODUCT_ID AS "Product",
    t1.SUBSTRATE_ID AS "BulkID",
    t2.WAFER_ID AS "WaferID",
    t2.SITE_No AS "Site",
    t1.REGIST_DATE AS "Time",
    t2.ITEM_NAME AS "Parameter",
    t2.MEAS_DATA AS "Value"
FROM
    YOUR_SCHEMA.WAT_HEADER t1
LEFT OUTER JOIN
    YOUR_SCHEMA.WAT_DETAIL t2 ON t2.LOT_ID = t1.LOT_ID
WHERE
    t1.PRODUCT_ID = :product_name
    AND t1.REGIST_DATE >= ADD_MONTHS(SYSDATE, -6)
"""