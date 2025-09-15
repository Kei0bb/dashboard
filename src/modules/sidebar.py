from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_prod() -> list[str]:
    csv_path = "data/products.csv"
    p = Path(csv_path)
    if not p.exists():
        return []
    df = pd.read_csv(p, encoding="utf-8")
    df.columns = [c.lower() for c in df.columns]
    col = "product" if "product" in df.columns else df.columns[0]
    return df[col].dropna().map(str.strip).unique().tolist()


def product_selector(*, key_prefix: str = "var") -> str:
    st.title("Product Selection")
    prod = load_prod()
    if not prod:
        st.sidebar.error("No varieties found in data/products.csv")
        return ""

    with st.sidebar:
        selected = (
            st.selectbox("Product Name", prod, key=f"{key_prefix}_select", index=None)
            or ""
        )
        return selected