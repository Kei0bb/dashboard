import pandas as pd
import streamlit as st

from src.app.charts import (
    build_distribution_chart,
    build_failure_mode_chart,
    build_yield_combo_chart,
)
from src.app.config import load_config
from src.app.data import create_repository
from src.app.services import YieldService
from src.app.ui import (
    sidebar_backend_selector,
    sidebar_product_selector,
    sidebar_run_button,
)

st.set_page_config(page_title="Yield Analysis", layout="wide")


def main() -> None:
    config = load_config()
    config = sidebar_backend_selector(config)
    repo = create_repository(config)
    service = YieldService(repo)
    current_backend = config.database.backend

    st.title("Yield Analysis")
    st.caption(f"DB Backend: {current_backend.upper()}")
    products = service.get_products()
    selected_product = sidebar_product_selector(products)
    run_analysis = sidebar_run_button()

    SESSION_KEY = "yield_page_state"
    state = st.session_state.get(SESSION_KEY)
    if state and state.get("backend") != current_backend:
        state = None
    if state and selected_product and state.get("product") != selected_product.name:
        state = None

    if not selected_product:
        st.warning("品種を選択してください。")
        return

    available_stages = list(selected_product.stages) if selected_product else list(YieldService.STAGES)
    default_stage = state.get("stage") if state else available_stages[0]
    if default_stage not in available_stages:
        default_stage = available_stages[0]
    selected_stage = st.segmented_control(
        "工程を選択",
        options=available_stages,
        default=default_stage,
        key="yield_stage_selector",
    )

    if not run_analysis and not state:
        st.info("サイドバーから Run Analysis を押してデータを読込んでください。")
        return

    stage_cache: dict[str, pd.DataFrame] = {} if run_analysis else (state["data"] if state else {})
    needs_load = run_analysis or selected_stage not in stage_cache

    if needs_load:
        df_stage = service.load_dataset(selected_product, selected_stage)
        if df_stage.empty:
            st.warning(f"{selected_product.label} の {selected_stage} データが見つかりません。")
            return
        stage_cache = stage_cache.copy()
        stage_cache[selected_stage] = df_stage
        st.session_state[SESSION_KEY] = {
            "product": selected_product.name,
            "data": stage_cache,
            "stage": selected_stage,
            "backend": current_backend,
        }
        if run_analysis:
            st.success(f"{selected_product.label} の {selected_stage} データを読み込みました。")
        else:
            st.info(f"{selected_product.label} の {selected_stage} データを読み込みました。")
    else:
        df_stage = stage_cache[selected_stage]
        st.info(f"{selected_product.label} のキャッシュ済み {selected_stage} データを使用しています。")

    def render_stage_section(stage_name: str, df_stage: pd.DataFrame) -> None:
        agg_period = st.radio(
            "集計粒度",
            options=["Daily", "Weekly", "Monthly", "Quarterly", "BulkID"],
            horizontal=True,
            key=f"agg_period_{stage_name.lower()}",
        )
        df_summary = service.build_summary(df_stage, agg_period)
        st.plotly_chart(build_yield_combo_chart(df_summary), width="stretch")

        col1, col2 = st.columns(2)
        with col1:
            st.markdown("#### Lot別分布")
            st.plotly_chart(build_distribution_chart(df_stage), width="stretch")
        with col2:
            st.markdown("#### 不良モード構成比")
            fig_failure = build_failure_mode_chart(df_stage)
            if fig_failure.data:
                st.plotly_chart(fig_failure, width="stretch")
            else:
                st.info("FAIL_BIN_* カラムが存在しません。")

    render_stage_section(selected_stage, df_stage)


if __name__ == "__main__":
    main()
