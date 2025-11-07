import streamlit as st

from src.app.charts import (
    build_distribution_chart,
    build_failure_mode_chart,
    build_yield_combo_chart,
)
from src.app.config import load_config
from src.app.data import create_repository
from src.app.services import YieldService
from src.app.ui import sidebar_product_selector, sidebar_run_button

st.set_page_config(page_title="Yield Analysis", layout="wide")


def main() -> None:
    config = load_config()
    repo = create_repository(config)
    service = YieldService(repo)

    st.title("Yield Analysis")
    products = service.get_products()
    selected_product = sidebar_product_selector(products)
    run_analysis = sidebar_run_button()

    SESSION_KEY = "yield_page_state"
    state = st.session_state.get(SESSION_KEY)
    if state and selected_product and state.get("product") != selected_product:
        state = None

    if not run_analysis and not state:
        st.info("サイドバーから Run Analysis を押してデータを読込んでください。")
        return

    if not selected_product:
        st.warning("品種を選択してください。")
        return

    if run_analysis:
        df = service.load_dataset(selected_product)
        if df.empty:
            st.warning(f"{selected_product} のデータが見つかりません。")
            return
        st.session_state[SESSION_KEY] = {"product": selected_product, "data": df}
        state = st.session_state[SESSION_KEY]
        st.success(f"{selected_product} のデータを読み込みました。")
    elif state:
        df = state["data"]
        st.info(f"{selected_product} のキャッシュ済みデータを使用しています。")
    else:
        st.warning("データが存在しません。Run Analysis を実行してください。")
        return

    agg_period = st.radio(
        "集計粒度",
        options=["Daily", "Weekly", "Monthly", "Quarterly", "BulkID"],
        horizontal=True,
    )
    df_summary = service.build_summary(df, agg_period)
    st.plotly_chart(build_yield_combo_chart(df_summary), use_container_width=True)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Lot別分布")
        st.plotly_chart(build_distribution_chart(df), use_container_width=True)
    with col2:
        st.markdown("#### 不良モード構成比")
        fig_failure = build_failure_mode_chart(df)
        if fig_failure.data:
            st.plotly_chart(fig_failure, use_container_width=True)
        else:
            st.info("FAIL_BIN_* カラムが存在しません。")


if __name__ == "__main__":
    main()
