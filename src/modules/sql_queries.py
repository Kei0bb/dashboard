"""
このモジュールには、データベースからデータを取得するためのSQLクエリが
文字列定数として格納されています。
"""

# --- 標準的な歩留まりクエリ (CP) ---
YIELD_QUERY = """
-- 製品名を指定して歩留まりデータを取得します (縦積み形式)。
-- 1行が1ダイのテスト結果を表すことを想定しています。
-- YOUR_YIELD_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "LotID",
    WAFER_ID AS "WaferID",
    TEST_TIMESTAMP AS "Time",
    TEST_BIN AS "Bin" -- テスト結果のBIN番号 (e.g., 1, 2, 3, ...)
FROM
    YOUR_YIELD_TABLE
WHERE
    PRODUCT_NAME = :product_name
"""

# --- Fail-Stop用の歩留まりクエリ (CPY) ---
CPY_YIELD_QUERY = """
-- Fail-Stop試験の製品向けに歩留まりデータを取得します (縦積み形式)。
-- CPYデータは通常、PASSしたダイの情報のみを持つため、
-- ここではBIN番号として常に「1」(良品)を返す例を示します。
-- YOUR_CPY_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "LotID",
    WAFER_ID AS "WaferID",
    TEST_TIMESTAMP AS "Time",
    1 AS "Bin" -- 1行 = 1 PASSダイとみなし、BIN番号「1」を割り当てる
FROM
    YOUR_CPY_TABLE
WHERE
    PRODUCT_NAME = :product_name
"""


# --- 製品名と歩留まりクエリのマッピング ---
# ここで指定されていない製品は、自動的にデフォルトのYIELD_QUERYが使用されます。
YIELD_QUERY_MAP = {
    # 'PRODUCT_FAIL_STOP': CPY_YIELD_QUERY, # CPYを使用する製品をここに登録
    'DEFAULT': YIELD_QUERY,
}


# --- WAT/SPECS クエリ (変更なし) ---
WAT_QUERY = """
-- 製品名を指定してWATデータを取得します (縦積みデータ形式)。
-- この形式は、1行に1つのパラメータ測定値が含まれることを想定しています。
-- YOUR_WAT_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "BulkID",
    WAFER_ID AS "WaferID",
    DIE_X AS "DieX",
    DIE_Y AS "DieY",
    TEST_SITE AS "Site",
    TEST_TIMESTAMP AS "Time",
    PARAMETER_NAME_COLUMN AS "Parameter", -- パラメータ名が入っている列
    VALUE_COLUMN AS "Value"              -- 測定値が入っている列
FROM
    YOUR_WAT_TABLE
WHERE
    PRODUCT_NAME = :product_name
"""


