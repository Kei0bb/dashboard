from pathlib import Path

import pandas as pd
import streamlit as st


@st.cache_data
def load_prod(csv_path: str) -> list[str]:
    p = Path(csv_path)
    if not p.exists():
        return []
    df = pd.read_csv(p, encoding="utf-8")
    col = "product" if "Product" in df.columns else df.columns[0]
    return df[col].dropna().map(str.strip).unique().tolist()


def render_sidebar(csv_path: str, *, key_prefix: str = "var") -> str:
    prod = load_prod(csv_path)
    if not prod:
        st.sidebar.error(f"No varieties found in {csv_path}")
        return ""

    with st.sidebar:
        selected = (
            st.selectbox("Product Name", prod, key=f"{key_prefix}_select", index=None)
            or ""
        )
        return selected
