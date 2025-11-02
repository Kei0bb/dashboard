# GEMINI.md - Project Context for Gemini

## Project Overview

This project is a web-based dashboard for visualizing and analyzing semiconductor manufacturing data, specifically wafer yield and Wafer Acceptance Test (WAT) Statistical Process Control (SPC) data.

-   **Framework**: Python with Streamlit
-   **Core Libraries**: Pandas for data manipulation, Plotly for charting, and `oracledb` for database connectivity.
-   **Architecture**: The application is modular, with a clear separation of concerns:
    -   `main.py`: Application entry point (homepage).
    -   `pages/`: Contains the UI definition for each dashboard page. It uses a naming convention to distinguish between production (`_Prod.py`) and development (`_Dev.py`) versions.
    -   `src/modules/`: Houses the core application logic, including database utilities, charting functions, and sidebar components.
    -   `data/`: Contains sample CSV files for local development and, importantly, **the specification (`specs.csv`) files for all modes**.
-   **Key Architectural Pattern**: A significant design choice is the hybrid data source model and the "long-to-wide" data transformation pipeline.
    -   **Yield and WAT data** are fetched from the database in a normalized "long" format.
    -   **Specification data (`specs`)** is always loaded from a local CSV file (`data/<product>/specs.csv`).
    -   The long-format data from the DB is then dynamically transformed into a "wide" format within `src/modules/db_utils.py` using `pandas.pivot_table`. This decouples the database schema from the data structures required by the frontend charting components.

## Building and Running

1.  **Install Dependencies**:
    The project uses `uv` for package management (inferred from `uv.lock`).
    ```bash
    # Assuming requirements.txt is generated from pyproject.toml
    uv pip install -r requirements.txt
    ```

2.  **Configure Database (Production Mode)**:
    Create a `secrets.toml` file inside the `.streamlit` directory with Oracle DB credentials. This file is git-ignored.
    ```toml
    # .streamlit/secrets.toml
    [database]
    username = "your_username"
    password = "your_password"
    dsn = "your_oracle_host:1521/your_service_name"
    ```

3.  **Run the Application**:
    ```bash
    streamlit run main.py
    ```

## Development Conventions

-   **Data Source**: The app uses a hybrid data source model:
    -   **Yield/WAT Data**: Loaded from an Oracle database in production mode, or from CSVs in the `data/` directory in development mode. All database queries are configured to fetch data from the last 6 months.
    -   **Specs Data**: **Always** loaded from a local CSV file located at `data/<product_name>/specs.csv`, regardless of the mode.
-   **SQL Query Management**:
    -   All SQL queries are centralized in `src/modules/sql_queries.py`. They are written for an Oracle DB and assume a specific schema (e.g., tables like `YOUR_SCHEMA.SEMI_CP_HEADER`, `YOUR_SCHEMA.WAT_HEADER`).
    -   Queries are designed to fetch data in a **long format**, but with a key exception for CPY Yield data.
    -   **Yield Queries**: Two types of queries are used:
        1.  **Standard Yield**: Fetches raw, long-format data with one row per die, identified by a `Bin` column.
        2.  **CPY Yield**: Fetches data that is pre-aggregated by bin, providing a `BinCount` column directly from the database.
    -   A dictionary map (`YIELD_QUERY_MAP`) is used to dynamically select the appropriate yield query based on the product name.
-   **Data Transformation**:
    -   The core transformation logic resides in `load_data_from_db` within `src/modules/db_utils.py`.
    -   **Yield Data**: The transformation logic dynamically adapts based on the input data format. It checks for the existence of a `BinCount` column:
        -   If `BinCount` **exists** (CPY data), the `pivot_table` function uses this column for its values, effectively pivoting the pre-aggregated data.
        -   If `BinCount` **does not exist** (Standard data), the `pivot_table` function uses `aggfunc="count"` to count die per bin for each wafer.
    -   **WAT Data**: Fetched with `Parameter` and `Value` columns. The `pivot_table` function is used to pivot the parameters into distinct columns.
-   **Configuration**:
    -   **Credentials**: Managed via `.streamlit/secrets.toml`.
    -   **App Theme**: Managed via `.streamlit/config.toml`.
-   **State Management**: The application uses Streamlit's caching mechanisms (`@st.cache_resource` for the DB connection, `@st.cache_data` for data loading) to optimize performance. Data is loaded only when the "Run Analysis" button is clicked.
