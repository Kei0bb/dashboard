"""Streamlitの再利用可能なパーツ。"""

from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Sequence

import streamlit as st

from ..config import AppConfig
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


def sidebar_backend_selector(config: AppConfig) -> AppConfig:
    """DBバックエンドをUIから上書き選択できるようにする。"""
    st.sidebar.subheader("Database Backend")
    backends = ["sqlite", "oracle"]
    try:
        default_index = backends.index(config.database.backend)
    except ValueError:
        default_index = 0
    selected = st.sidebar.radio(
        "接続先を選択",
        options=backends,
        index=default_index,
        key="db_backend_selector",
        horizontal=True,
    )
    if selected == config.database.backend:
        return config
    new_db = replace(config.database, backend=selected)
    st.sidebar.warning(f"DBバックエンドを {selected} に切り替えました。再読込してください。")
    return replace(config, database=new_db)
