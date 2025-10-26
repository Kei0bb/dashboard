"""
Module for common utility functions, including data loading.
"""
import os

import pandas as pd
import streamlit as st

# db_utilsから必要な関数をインポート
from src.modules.db_utils import get_db_connection
from src.modules.db_utils import load_data_from_db as fetch_data_from_db_tables


@st.cache_data
def load_specs_from_csv(product_id: str) -> pd.DataFrame | None:
    """指定された製品の規格(specs)データをCSVから読み込みます。

    Args:
        product_id: 製品ID (例: 'SCP117A')

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


def load_data_from_csv(product_id: str) -> dict[str, pd.DataFrame] | None:
    """Loads all data for a given product from local CSV files.

    Args:
        product_id: The identifier for the product (e.g., 'SCP117A').

    Returns:
        A dictionary containing 'sort', 'wat', and 'specs' pandas DataFrames,
        or None if data cannot be loaded.
    """
    st.info(f"Loading data for product '{product_id}' from CSV files...")
    data_dir = os.path.join("data", product_id)
    if not os.path.isdir(data_dir):
        st.error(f"Data directory not found for product: {product_id}")
        return None

    try:
        sort_df = pd.read_csv(os.path.join(data_dir, "sort.csv"))
        wat_df = pd.read_csv(os.path.join(data_dir, "wat.csv"))
        specs_df = load_specs_from_csv(product_id) # 新しい関数を利用

        if specs_df is None:
            return None # specsが見つからない場合はエラー

        # Strip column names
        sort_df.columns = sort_df.columns.str.strip()
        wat_df.columns = wat_df.columns.str.strip()

        st.success("Successfully loaded data from CSV.")
        return {"sort": sort_df, "wat": wat_df, "specs": specs_df}
    except FileNotFoundError as e:
        st.error(f"Missing a data file in '{data_dir}': {e.filename}")
        return None


def load_data_from_db(product_id: str) -> dict[str, pd.DataFrame] | None:
    """Loads all data for a given product from the database.

    Args:
        product_id: The identifier for the product to load.

    Returns:
        A dictionary containing dataframes, or None if connection fails.
    """
    st.info(f"Loading data for product '{product_id}' from database...")
    db_engine = get_db_connection()

    if db_engine:
        data = fetch_data_from_db_tables(db_engine, product_id)
        if not data or any(df.empty for df in data.values()):
            st.error(f"Could not find or load data for product '{product_id}' from the database.")
            return None
        st.success("Successfully loaded data from database.")
        return data
    else:
        st.error("Database connection is not configured. Please check your .streamlit/secrets.toml file.")
        return None