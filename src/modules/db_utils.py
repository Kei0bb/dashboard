"""
データベース接続とデータ読み込みのためのユーティリティ関数を提供します。
"""
import oracledb
import pandas as pd
import streamlit as st

from . import sql_queries


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
    """指定された製品のデータをデータベースから読み込みます。

    Args:
        _conn: oracledb.Connection オブジェクト
        product_name: 取得対象の製品名

    Returns:
        sort, wat, specs のデータフレームを含む辞書。
        エラー発生時は空の辞書を返します。
    """
    if not _conn:
        st.error("データベース接続がありません。")
        return {}

    try:
        # パラメータを指定してSQLを実行 (SQLインジェクション対策)
        params = {"product_name": product_name}

        df_sort = pd.read_sql_query(sql_queries.YIELD_QUERY, _conn, params=params)
        df_wat = pd.read_sql_query(sql_queries.WAT_QUERY, _conn, params=params)
        df_specs = pd.read_sql_query(sql_queries.SPECS_QUERY, _conn, params=params)

        return {"sort": df_sort, "wat": df_wat, "specs": df_specs}

    except Exception as e:
        st.error(f"データベースからのデータ読み込み中にエラーが発生しました: {e}")
        return {}
