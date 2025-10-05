# 半導体ダッシュボード

## 1. 概要

このプロジェクトは、Streamlitで構築されたファブレス半導体企業向けのWebベースのダッシュボードです。ウェーハの歩留まりやウェーハ受け入れテスト（WAT）の統計的プロセス制御（SPC）データなど、製造データを可視化・分析するための使いやすいインターフェースを提供します。このアプリケーションは、モジュール化され、メンテナンスしやすいように設計されています。

## 2. 主な機能

*   **インタラクティブなダッシュボード**: Streamlitで構築された、シンプルでクリーンなUI。
*   **階層的なデータ分析**: 全体トレンドのサマリーから、特定のロットやウェーハへのドリルダウン分析が可能。
*   **明示的なデータ更新**: サイドバーの「Run Analysis」ボタンにより、ユーザーが明示的に指示するまでデータ処理やグラフ描画は実行されません。
*   **動的な製品選択**: `data`ディレクトリのフォルダ構成に基づき、サイドバーから製品を簡単に切り替え可能。
*   **セキュアな接続情報管理**: StreamlitのSecrets management機能 (`.streamlit/secrets.toml`) を利用してデータベース接続情報を安全に管理します。
*   **モジュール化アーキテクチャ**: UI、データ処理、チャート作成などの機能がモジュールとして整理されており、高いメンテナンス性と拡張性を持ちます。

## 3. ディレクトリ構成

```
/
├── .streamlit/          # Streamlit設定
├── data/                # ローカルテスト用CSVデータ
├── pages/               # アプリケーションページ
│   ├── 1_Yield_Dev.py   # 開発用 歩留まりページ
│   ├── 1_Yield_Prod.py  # 本番用 歩留まりページ
│   ├── 2_WAT_SPC_Dev.py # 開発用 WAT/SPCページ
│   └── 2_WAT_SPC_Prod.py# 本番用 WAT/SPCページ
├── src/                 # ソースコード
├── main.py              # アプリケーションのホームページ
├── project.md           # このプロジェクト説明ファイル
└── ...
```

(一部抜粋・簡略化)

## 5. 実行方法

以下のコマンドで、Streamlitアプリケーションを直接起動します。

```bash
streamlit run main.py
```

起動後、サイドバーに各ページの開発版（Dev）と本番版（Prod）が表示されます。目的に応じて、表示したいページを直接選択してください。

*   **`_Prod`ページ**: データベースからのデータ読み込みを前提としています。
*   **`_Dev`ページ**: データベースとローカルCSVファイルの両方からデータ読み込みを選択できます。


## 6. 使い方

1.  サイドバーで製品を選択します。
2.  実行したいデータソースに対応する「Run Analysis」ボタンをクリックします。（本番モードではボタンは1つです）
3.  各ページで分析結果を確認します。

## 7. モジュールの概要

*   **`src/modules/utils.py`**: `load_data_from_db` と `load_data_from_csv` という、データソースごとに独立したデータ読み込み関数を格納します。
*   **`src/modules/sidebar.py`**: `data`ディレクトリのフォルダ構成をスキャンし、製品選択サイドバーを動的に描画します。
*   **`src/modules/spc_charts.py`**: SPC関連のチャートを作成する汎用的な関数を格納します。
*   **`src/modules/yield_charts.py`**: 歩留まりページ (`1_Yield.py`) で使用されるチャート作成関数を格納します。
*   **`src/modules/db_utils.py`**: `.streamlit/secrets.toml` の設定に基づき、データベースへの接続を確立する `get_db_connection` 関数などを提供します。

## 8. データソースの管理

### 8.1. 開発モード (CSV)

開発モードでは、「Run Analysis (CSV)」ボタンを使用することで、`data/`ディレクトリ内のCSVファイルをデータソースとして利用できます。

### 8.2. 本番モード (Oracle DB)

本番モードでは、アプリケーションは `.streamlit/secrets.toml` ファイルに定義された情報を使ってOracleデータベースに接続します。このファイルが存在しない、または情報が不完全な場合はエラーが表示されます。

```toml
# .streamlit/secrets.toml

[database]
username = "your_actual_username"
password = "your_actual_password"
dsn = "your_oracle_host:1521/your_service_name"
```

**重要:** この `secrets.toml` ファイルは `.gitignore` によってバージョン管理から除外されています。絶対にリポジトリにコミットしないでください。

### 8.3. データベース連携 SQLガイド

本番用のデータベースと連携する際には、ダッシュボードが必要とするデータ構造に合わせてSQLクエリを準備する必要があります。以下に、`src/modules/db_utils.py` の `load_data_from_db` 関数に実装すべきSQLクエリのテンプレートを示します。

#### A. 歩留まりデータ (Yield / Sort)

ウェーハのテスト結果（どのダイが良品で、どの不良ビンに分類されたか）を取得します。

-   **目的**: 歩留まりの集計、不良モードの分析
-   **必要な列**: 製品名, ロットID, ウェーハID, テスト日時, **良品/不良品情報**

```sql
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
```

#### B. WATデータ (Wafer Acceptance Test)

ウェーハの電気特性（パラメータ）測定値を取得します。

-   **目的**: 電気特性の分布、トレンド、ウェーハマップの表示
-   **必要な列**: 製品名, ロットID, ウェーハID, 座標(X,Y), **各種測定パラメータ**

```sql
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
```

#### C. 規格値データ (Specs)

WATパラメータの規格値（USL/LSL）を取得します。

-   **目的**: WATデータの規格上限(USL)・下限(LSL)の表示
-   **必要な列**: 製品名, パラメータ名, **USL**, **LSL**

```sql
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
```


## 9. 設定 (Configuration)

### 9.1. 動作モードの切り替え

アプリケーションの動作モードは、環境変数 `APP_MODE` で制御します。

*   **`production`**: 本番モード。データベース接続が必須となり、CSV関連のUIは非表示になります。
*   **`development`** (または未設定): 開発モード。DBとCSVの両方のオプションが利用可能です。

### 9.2. テーマ (Theme)

アプリケーションのテーマは、`.streamlit/config.toml`ファイルでライトテーマに固定されています。

## 10. 今後のロードマップ (Future Roadmap)

（変更なし）
