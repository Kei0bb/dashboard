"""
データベース接続とデータ読み込みのためのユーティリティ関数を提供します。
"""
import oracledb
import pandas as pd
import streamlit as st

from . import sql_queries
from .utils import load_specs_from_csv # specs読み込み関数をインポート


@st.cache_resource
def get_db_connection():
    """StreamlitのSecretsを使用してOracleデータベースへの接続を確立します。

    接続オブジェクトはStreamlitのキャッシュ機能により、アプリ全体で再利用されます。
    """
    try:
        conn = oracledb.connect(
            user=st.secrets["database"]["username"],
            password=st.secrets["database"]["password"],
            dsn=st.secrets["database"]["dsn"],
        )
        print("Successfully connected to Oracle DB!")
        return conn
    except oracledb.DatabaseError as e:
        st.error(f"データベース接続エラー: {e}")
        return None
    except KeyError:
        st.warning("データベースの接続情報が secrets.toml に設定されていません。")
        return None
    except Exception as e:
        st.error(f"データベース接続中に予期せぬエラーが発生しました: {e}")
        return None


@st.cache_data
def load_data_from_db(_conn, product_name: str) -> dict[str, pd.DataFrame]:
    """指定された製品のデータを読み込み、適切な形式に変換します。

    - 歩留まり(Yield): DBから取得 -> pivot_tableで集計 -> 横持ち
    - 電気特性(WAT): DBから取得 -> pivot_tableで変換 -> 横持ち
    - 規格値(Specs): CSVから取得
    """
    if not _conn:
        st.error("データベース接続がありません。")
        return {}

    try:
        params = {"product_name": product_name}

        # 1. 歩留まりデータの取得と変換
        yield_query = sql_queries.YIELD_QUERY_MAP.get(
            product_name, sql_queries.YIELD_QUERY_MAP["DEFAULT"]
        )
        df_sort_long = pd.read_sql_query(yield_query, _conn, params=params)

        if not df_sort_long.empty:
            index_cols = ["Product", "LotID", "WaferID", "Time"]
            valid_index_cols = [c for c in index_cols if c in df_sort_long.columns]

            df_sort = df_sort_long.pivot_table(
                index=valid_index_cols, columns="Bin", values="WaferID",
                aggfunc="count", fill_value=0,
            )

            bin_rename_map = {1: "0_PASS"}
            df_sort = df_sort.rename(columns=bin_rename_map)
            df_sort = df_sort.rename(
                columns={c: f"FAIL_BIN_{c}" for c in df_sort.columns if c != "0_PASS"}
            )
            df_sort = df_sort.reset_index()
        else:
            df_sort = pd.DataFrame()

        # 2. WATデータの取得と変換
        df_wat_long = pd.read_sql_query(sql_queries.WAT_QUERY, _conn, params=params)
        if not df_wat_long.empty:
            pivot_index = [
                "Product", "BulkID", "WaferID", "DieX", "DieY", "Site", "Time"
            ]
            valid_pivot_index = [c for c in pivot_index if c in df_wat_long.columns]

            df_wat = df_wat_long.pivot_table(
                index=valid_pivot_index, columns="Parameter", values="Value",
            ).reset_index()
        else:
            df_wat = pd.DataFrame()

        # 3. 規格値データのCSVからの取得
        df_specs = load_specs_from_csv(product_name)
        if df_specs is None:
            # specsがない場合は空のDataFrameを許容する
            df_specs = pd.DataFrame()

        return {"sort": df_sort, "wat": df_wat, "specs": df_specs}

    except Exception as e:
        st.error(f"データベースからのデータ処理中にエラーが発生しました: {e}")
        return {}
