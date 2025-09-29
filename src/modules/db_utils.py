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


def load_data_from_db(engine: Engine, product_id: str) -> dict[str, pd.DataFrame]:
    """Loads sort, wat, and specs data for a given product from the database.

    Args:
        engine: The SQLAlchemy Engine to use for the connection.
        product_id: The identifier for the product to load.

    Returns:
        A dictionary containing 'sort', 'wat', and 'specs' pandas DataFrames.
        Returns an empty dictionary if any table fails to load.
    """
    data = {}
    tables = ["sort", "wat", "specs"]
    try:
        with engine.connect() as connection:
            for table in tables:
                # Assuming a 'product_id' column exists in each table
                query = f"SELECT * FROM {table} WHERE product_id = :product_id"
                df = pd.read_sql(query, connection, params={"product_id": product_id})
                df.columns = df.columns.str.strip()
                data[table] = df
        return data
    except Exception as e:
        st.error(f"Error loading data from database for product '{product_id}': {e}")
        return {}


if __name__ == "__main__":
    print(
        "This script is not meant to be run directly. "
        "It provides utility functions for the Streamlit app."
    )