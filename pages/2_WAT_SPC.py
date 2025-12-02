import streamlit as st

from src.app.charts import (
    build_bulk_trend_chart,
    build_individual_chart,
    build_wafer_map,
)
from src.app.config import load_config
from src.app.data import create_repository
from src.app.services import WATService, YieldService
from src.app.specs import extract_limits, load_specs
from src.app.ui import (
    sidebar_backend_selector,
    sidebar_product_selector,
    sidebar_run_button,
)

st.set_page_config(page_title="WAT / SPC Analysis", layout="wide")


def main() -> None:
    config = load_config()
    config = sidebar_backend_selector(config)
    repo = create_repository(config)
    wat_service = WATService(repo)
    yield_service = YieldService(repo)
    current_backend = config.database.backend

    st.title("WAT / SPC Analysis")
    st.caption(f"DB Backend: {current_backend.upper()}")
    products = yield_service.get_products()
    product = sidebar_product_selector(products)
    run_analysis = sidebar_run_button()

    SESSION_KEY = "wat_page_state"
    state = st.session_state.get(SESSION_KEY)
    if state and state.get("backend") != current_backend:
        state = None
    if state and product and state.get("product") != product.name:
        state = None

    if not run_analysis and not state:
        st.info("Run Analysis を押してデータを読み込みます。")
        return
    if not product:
        st.warning("品種を選択してください。")
        return

    if run_analysis:
        df = wat_service.load_dataset(product.source_name)
        if df.empty:
            st.warning("対象データが空です。")
            return
        specs = load_specs(product.name)
        st.session_state[SESSION_KEY] = {
            "product": product.name,
            "data": df,
            "specs": specs,
            "backend": current_backend,
        }
        state = st.session_state[SESSION_KEY]
        st.success(f"{product.label} のWATデータを読み込みました。")
    elif state:
        df = state["data"]
        specs = state["specs"]
        st.info(f"{product.label} のキャッシュ済みデータを使用しています。")
    else:
        st.warning("データが存在しません。Run Analysis を実行してください。")
        return

    if specs is None:
        st.info("Specsが見つからないため管理限界線は表示されません。")

    params = wat_service.available_parameters(df)
    if not params:
        st.warning("数値パラメータが見つかりません。")
        return

    st.markdown("### Bulk Trend")
    columns = st.columns(3)
    for idx, param in enumerate(params):
        trend = wat_service.aggregate_bulk_trend(df, param)
        if trend.empty:
            continue
        usl, lsl = extract_limits(specs, param)
        with columns[idx % 3]:
            st.plotly_chart(
                build_bulk_trend_chart(trend, param, usl, lsl),
                width="stretch",
            )

    st.markdown("### Drill-down")
    bulk_ids = df["BulkID"].unique()
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        selected_bulk = st.selectbox("Bulk ID", bulk_ids)
    with col_sel2:
        selected_param = st.selectbox("Parameter", params)

    if selected_bulk and selected_param:
        df_detail = df[df["BulkID"] == selected_bulk]
        usl, lsl = extract_limits(specs, selected_param)
        col_a, col_b = st.columns(2)
        with col_a:
            st.plotly_chart(
                build_wafer_map(df_detail, selected_param), width="stretch"
            )
        with col_b:
            st.plotly_chart(
                build_individual_chart(df_detail, selected_param, usl, lsl),
                width="stretch",
            )


if __name__ == "__main__":
    main()
