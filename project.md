# 半導体ダッシュボード

## 1. 概要

このプロジェクトは、Streamlitで構築されたファブレス半導体企業向けのWebベースのダッシュボードです。ウェーハの歩留まりやウェーハ受け入れテスト（WAT）の統計的プロセス制御（SPC）データなど、製造データを可視化・分析するための使いやすいインターフェースを提供します。このアプリケーションは、モジュール化され、メンテナンスしやすいように設計されています。

## 2. 主な機能

*   **インタラクティブなダッシュボード**: Streamlitで構築された、シンプルでクリーンなUI。
*   **歩留まり分析**: 選択した製品の歩留まりトレンドを可視化します。
*   **WAT SPC分析**: 主要なWATパラメータの管理図（Iチャート）を、管理限界線（UCL/LCL）や規格限界線（USL/LSL）と共に表示します。
*   **製品選択**: サイドバーから簡単に異なる製品を切り替えることができます。
*   **モジュール化アーキテクチャ**: コードは、データベース操作、UIコンポーネント、チャート作成のための再利用可能なモジュールに整理されています。
*   **柔軟なデータソース**: 本番環境向けのOracleと、ローカルテスト向けのSQLiteの両方をサポートします。

## 3. ディレクトリ構成

```
/
├── data/
│   ├── products.csv       # サイドバーの製品選択リスト
│   ├── specs.csv          # WATパラメータのUSL/LSL規格限界
│   └── WAT.csv            # (現在未使用)
├── pages/
│   ├── 1_Yield.py         # 歩留まり分析ページのStreamlitスクリプト
│   └── 2_WAT_SPC.py       # WAT SPC分析ページのStreamlitスクリプト
├── src/
│   └── modules/
│       ├── database.py    # データベース接続とデータ取得を処理
│       ├── sidebar.py     # 製品選択サイドバーの描画
│       └── spc_charts.py  # SPCチャート作成用の関数
├── .python-version        # Pythonのバージョンを指定 (3.13)
├── main.py                # Streamlitアプリケーションのホームページ
├── project.md             # このプロジェクト説明ファイル
├── pyproject.toml         # プロジェクトのメタデータと依存関係
└── uv.lock                # uvのロックファイル
```

## 4. セットアップとインストール

### 4.1. 前提条件

*   Python 3.13
*   `uv` (プロジェクトおよび仮想環境管理用)

### 4.2. インストール手順

1.  **リポジトリをクローン:**
    ```bash
    git clone <repository-url>
    cd dashboard
    ```

2.  **仮想環境の作成と依存関係のインストール:**
    `uv`は自動的に仮想環境を作成し、`pyproject.toml`にリストされているパッケージをインストールします。
    ```bash
    uv sync
    ```

### 4.3. データベースのセットアップ

このアプリケーションは、テストおよび開発用にローカルのSQLiteデータベースを使用します。

1.  **テストデータベースの初期化:**
    プロジェクトのルートディレクトリから以下のコマンドを実行します。これにより、`data/test.db`ファイルが作成され、歩留まりとWAT測定のサンプルデータが投入されます。
    ```bash
    python -m src.modules.database init
    ```

## 5. 実行方法

Streamlitアプリケーションを起動するには、プロジェクトのルートディレクトリから以下のコマンドを実行します。

```bash
streamlit run main.py
```

ウェブブラウザで `http://localhost:8501` にアクセスすると、アプリケーションが表示されます。

## 6. 使い方

### 6.1. ホームページ

メインページには、利用可能な製品の簡単な概要が表示されます。

### 6.2. 歩留まりページ (Yield)

1.  ナビゲーションメニューから **Yield** ページに移動します。
2.  **Product Selection** サイドバーで製品を選択します。
3.  ページには、選択した製品の歩留まりデータとトレンドチャートが表示されます。

### 6.3. WAT SPCページ

1.  **WAT SPC** ページに移動します。
2.  サイドバーから製品を選択します。
3.  ページには、生のWATデータと、`param1`および`param2`のIチャートが表示されます。
4.  チャートには、計算された管理限界線（UCL/LCL）と、`data/specs.csv`から読み込まれた規格限界線（USL/LSL）が含まれます。

## 7. モジュールの概要

*   **`src/modules/database.py`**:
    *   `create_test_db_engine()`: SQLiteテストデータベースへの接続エンジンを作成します。
    *   `init_test_db()`: テストデータベースにサンプルデータを投入します。
    *   `fetch_data()`: SQLクエリを実行し、Pandas DataFrameを返す汎用関数です。
    *   `get_engine()`: Oracleデータベース（本番用）への接続エンジンを作成します。

*   **`src/modules/sidebar.py`**:
    *   `product_selector()`: `data/products.csv`からデータを読み込み、製品選択のドロップダウンをサイドバーに描画します。

*   **`src/modules/spc_charts.py`**:
    *   `load_spec_limits()`: 指定された製品とパラメータのUSL/LSLを`data/specs.csv`から読み込みます。
    *   `create_individual_chart()`: PlotlyのIチャートを作成します。
    *   `create_xbar_r_chart()`: PlotlyのX-bar Rチャートを作成します（現在はUIでは未使用）。

## 8. データファイル

`data/`ディレクトリには、アプリケーションの動的コンテンツを駆動するCSVファイルが含まれています。

*   **`products.csv`**: 製品名の単純なリストです。ヘッダーは `product_name` である必要があります。
    ```csv
    product_name
    ProductA
    ProductB
    ProductC
    ```
*   **`specs.csv`**: 製品ごと、パラメータごとの上限および下限規格値を定義します。
    ```csv
    product,parameter,USL,LSL
    ProductA,param1,1.5,0.9
    ProductA,param2,15,9
    ProductB,param1,1.0,0.6
    ProductB,param2,10,6
    ProductC,param1,1.2,0.8
    ProductC,param2,12,8
    ```

## 9. 設定 (Configuration)

### 9.1. テーマ (Theme)

アプリケーションのテーマは、`.streamlit/config.toml`ファイルで設定されています。デフォルトではライトテーマに固定されています。

```toml
[theme]
base="light"
```

ダークテーマに変更したい場合は、`base`の値を`"dark"`に変更してください。