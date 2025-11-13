"""Streamlitの再利用可能なパーツ。"""

from __future__ import annotations

from typing import Iterable, Sequence

import streamlit as st

from ..products import ProductDefinition


def sidebar_product_selector(products: Iterable[ProductDefinition]) -> ProductDefinition | None:
    st.sidebar.subheader("Product")
    items: Sequence[ProductDefinition] = list(products)
    if not items:
        st.sidebar.info("`data/` に製品ディレクトリがありません。")
        return None
    return st.sidebar.selectbox(
        "Select Product",
        options=items,
        format_func=lambda p: p.label,
    )


def sidebar_run_button(label: str = "Run Analysis") -> bool:
    return st.sidebar.button(label, type="primary")
