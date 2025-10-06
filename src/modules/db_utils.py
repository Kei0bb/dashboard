"""
Database utility functions.

This module provides functions to connect to a database using credentials
stored in Streamlit's secrets management.
"""
import pandas as pd
import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


def get_db_connection() -> Engine | None:
    """Establishes a database connection using credentials from st.secrets.

    Returns:
        An SQLAlchemy Engine object if credentials are found, otherwise None.
    """
    if "database" in st.secrets and all(
        k in st.secrets["database"] for k in ["username", "password", "dsn"]
    ):
        creds = st.secrets["database"]
        try:
            print("Attempting to connect to Oracle DB using st.secrets...")
            engine = create_engine(
                f"oracle+oracledb://{creds['username']}:{creds['password']}@{creds['dsn']}",
                pool_pre_ping=True,
                pool_recycle=1800,
            )
            # You can uncomment the following lines to test the connection upon creation
            # with engine.connect() as connection:
            #     print("Successfully connected to Oracle DB!")
            return engine
        except Exception as e:
            st.error(f"Error connecting to Oracle DB: {e}")
            return None
    else:
        # This case means the app will run in local CSV mode.
        return None


import oracledb
import pandas as pd
import streamlit as st

from . import sql_queries


@st.cache_resource
def get_db_connection():
    """StreamlitのSecretsを使用してOracleデータベースへの接続を確立する"""
    try:
        return oracledb.connect(
            user=st.secrets["database"]["username"],
            password=st.secrets["database"]["password"],
            dsn=st.secrets["database"]["dsn"],
        )
    except oracledb.DatabaseError as e:
        st.error(f"データベース接続エラー: {e}")
        return None
    except Exception as e:
        st.error(f"予期せぬエラーが発生しました: {e}")
        return None


@st.cache_data
def load_data_from_db(_conn, product_name: str) -> dict:
    """指定された製品のデータをデータベースから読み込む"""
    if not _conn:
        st.error("データベース接続がありません。")
        return {}

    try:
        # パラメータを指定してSQLを実行
        params = {"product_name": product_name}
        df_sort = pd.read_sql_query(sql_queries.YIELD_QUERY, _conn, params=params)
        df_wat = pd.read_sql_query(sql_queries.WAT_QUERY, _conn, params=params)
        df_specs = pd.read_sql_query(sql_queries.SPECS_QUERY, _conn, params=params)

        return {"sort": df_sort, "wat": df_wat, "specs": df_specs}

    except Exception as e:
        st.error(f"データベースからのデータ読み込み中にエラーが発生しました: {e}")
        return {}


if __name__ == "__main__":
    print(
        "This script is not meant to be run directly. "
        "It provides utility functions for the Streamlit app."
    )