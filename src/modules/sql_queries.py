"""
このモジュールには、データベースからデータを取得するためのSQLクエリが
文字列定数として格納されています。
"""

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

WAT_QUERY = """
-- 製品名を指定してWATデータを取得します。
-- YOUR_WAT_TABLE を実際のテーブル名に、各列名も実際の列名に合わせてください。
SELECT
    PRODUCT_NAME AS "Product",
    LOT_ID AS "BulkID", -- BulkIDとしてロットIDを使用する例
    WAFER_ID AS "WaferID",
    DIE_X AS "DieX",
    DIE_Y AS "DieY",
    TEST_SITE AS "Site",
    TEST_TIMESTAMP AS "Time",
    -- 以下に、測定パラメータの列を記述します。
    PARAM_VTH AS "VTH",
    PARAM_ID_SAT AS "IDSAT"
    -- ... 必要なパラメータの分だけ追加 ...
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
