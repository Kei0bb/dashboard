"""Streamlitの再利用可能なパーツ。"""

from __future__ import annotations

from typing import Iterable

import streamlit as st


def sidebar_product_selector(products: Iterable[str]) -> str:
    st.sidebar.subheader("Product")
    if not products:
        st.sidebar.info("`data/` に製品ディレクトリがありません。")
        return ""
    return st.sidebar.selectbox("Select Product", options=list(products))


def sidebar_run_button(label: str = "Run Analysis") -> bool:
    return st.sidebar.button(label, type="primary")
