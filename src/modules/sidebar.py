from pathlib import Path

import streamlit as st


def load_prod() -> list[str]:
    """Scans the data directory to find product folders."""
    data_dir = Path("data")
    if not data_dir.is_dir():
        return []
    
    product_folders = [p.name for p in data_dir.iterdir() if p.is_dir()]
    return sorted(product_folders)


def product_selector(*, key_prefix: str = "var") -> str:
    prod = load_prod()
    if not prod:
        st.sidebar.error("No product data found in `data` directory.")
        return ""

    selected = (
        st.sidebar.selectbox("Product Name", prod, key=f"{key_prefix}_select", index=None)
        or ""
    )
    return selected
