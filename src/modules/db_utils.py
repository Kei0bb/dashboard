"""
データベース接続とデータ読み込みのためのユーティリティ関数を提供します。
"""
import os
import oracledb
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from . import sql_queries

load_dotenv()  # .envファイルから環境変数を読み込む


@st.cache_data
def load_specs_from_csv(product_id: str) -> pd.DataFrame | None:
    """指定された製品の規格(specs)データをCSVから読み込みます。

    Args:
        product_id: 製品ID (例: 'productA')

    Returns:
        規格データを含むDataFrame。見つからない場合はNone。
    """
    specs_path = os.path.join("data", product_id, "specs.csv")
    try:
        df = pd.read_csv(specs_path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        st.warning(f"Specs file not found at: {specs_path}")
        return None


@st.cache_resource
def get_db_connection():
    """StreamlitのSecretsを使用してOracleデータベースへの接続を確立します。

    接続オブジェクトはStreamlitのキャッシュ機能により、アプリ全体で再利用されます。
    """
    try:
        conn = oracledb.connect(
            user=os.environ.get("DB_USERNAME"),
            password=os.environ.get("DB_PASSWORD"),
            dsn=os.environ.get("DB_DSN"),
        )
        print("Successfully connected to Oracle DB!")
        return conn
    except oracledb.DatabaseError as e:
        st.error(f"データベース接続エラー: {e}")
        return None
    except KeyError:
        st.warning("データベースの接続情報が環境変数に設定されていません。")
        return None
    except Exception as e:
        st.error(f"データベース接続中に予期せぬエラーが発生しました: {e}")
        return None


@st.cache_data
def load_yield_data(_conn, product_name: str) -> pd.DataFrame:
    """指定された製品の歩留まりデータをDBから読み込み、変換します。"""
    df_sort = pd.DataFrame()
    try:
        params = {"product_name": product_name}
        yield_query = sql_queries.YIELD_QUERY_MAP.get(
            product_name, sql_queries.YIELD_QUERY_MAP["DEFAULT"]
        )
        df_sort_long = pd.read_sql_query(yield_query, _conn, params=params)

        if not df_sort_long.empty:
            index_cols = ["Product", "LotID", "WaferID", "Time"]
            valid_index_cols = [c for c in index_cols if c in df_sort_long.columns]

            if "BinCount" in df_sort_long.columns:
                df_sort = df_sort_long.pivot_table(
                    index=valid_index_cols,
                    columns="Bin",
                    values="BinCount",
                    aggfunc="sum",
                    fill_value=0,
                )
            else:
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
        return df_sort

    except Exception as e:
        st.warning(f"歩留まりデータの読み込みに失敗しました: {e}")
        return df_sort


@st.cache_data
def load_wat_data(_conn, product_name: str) -> pd.DataFrame:
    """指定された製品のWATデータをDBから読み込み、変換します。"""
    df_wat = pd.DataFrame()
    try:
        params = {"product_name": product_name}
        df_wat_long = pd.read_sql_query(sql_queries.WAT_QUERY, _conn, params=params)
        if not df_wat_long.empty:
            pivot_index = [
                "Product", "BulkID", "WaferID", "DieX", "DieY", "Site", "Time"
            ]
            valid_pivot_index = [c for c in pivot_index if c in df_wat_long.columns]

            df_wat = df_wat_long.pivot_table(
                index=valid_pivot_index, columns="Parameter", values="Value",
            ).reset_index()
        return df_wat

    except Exception as e:
        st.warning(f"WATデータの読み込みに失敗しました: {e}")
        return df_wat