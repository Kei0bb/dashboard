"""
このモジュールには、データベースからデータを取得するためのSQLクエリが
文字列定数として格納されています。
"""

# --- 標準的な歩留まりクエリ (CP) ---
YIELD_QUERY = """
-- 製品名を指定して歩留まりデータを取得します。
-- YOUR_YIELD_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "LotID",
    WAFER_ID AS "WaferID",
    TEST_TIMESTAMP AS "Time",
    -- スキーマに合わせてCASE文を修正してください。
    CASE WHEN TEST_BIN = 1 THEN 1 ELSE 0 END AS "0_PASS",
    CASE WHEN TEST_BIN = 2 THEN 1 ELSE 0 END AS "FAIL_BIN_2",
    CASE WHEN TEST_BIN = 3 THEN 1 ELSE 0 END AS "FAIL_BIN_3"
    -- ... 必要な不良BINの分だけ追加 ...
FROM
    YOUR_YIELD_TABLE
WHERE
    PRODUCT_NAME = :product_name
"""

# --- Fail-Stop用の歩留まりクエリ (CPY) ---
CPY_YIELD_QUERY = """
-- Fail-Stop試験の製品向けに歩留まりデータを取得します。
-- CPYデータは通常、PASSしたダイの情報のみを持つため、
-- ここでは単純に1行を1PASSとしてカウントする例を示します。
-- YOUR_CPY_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "LotID",
    WAFER_ID AS "WaferID",
    TEST_TIMESTAMP AS "Time",
    1 AS "0_PASS", -- 1行 = 1 PASSダイ
    0 AS "FAIL_BIN_2" -- Fail-Stopなので不良BINは存在しない想定
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

SPECS_QUERY = """
-- 製品名を指定して規格値を取得します。
-- YOUR_SPECS_TABLE を実際の規格値マスタテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    PARAMETER_NAME AS "Parameter",
    UPPER_SPEC_LIMIT AS "USL",
    LOWER_SPEC_LIMIT AS "LSL"
FROM
    YOUR_SPECS_TABLE
WHERE
    PRODUCT_NAME = :product_name
"""
