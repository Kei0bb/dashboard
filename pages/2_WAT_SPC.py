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
from src.app.ui import sidebar_product_selector, sidebar_run_button

st.set_page_config(page_title="WAT / SPC Analysis", layout="wide")


def main() -> None:
    config = load_config()
    repo = create_repository(config)
    wat_service = WATService(repo)
    yield_service = YieldService(repo)

    st.title("WAT / SPC Analysis")
    products = yield_service.get_products()
    product = sidebar_product_selector(products)
    run_analysis = sidebar_run_button()

    SESSION_KEY = "wat_page_state"
    state = st.session_state.get(SESSION_KEY)
    if state and product and state.get("product") != product:
        state = None

    if not run_analysis and not state:
        st.info("Run Analysis を押してデータを読み込みます。")
        return
    if not product:
        st.warning("品種を選択してください。")
        return

    if run_analysis:
        df = wat_service.load_dataset(product)
        if df.empty:
            st.warning("対象データが空です。")
            return
        specs = load_specs(product)
        st.session_state[SESSION_KEY] = {"product": product, "data": df, "specs": specs}
        state = st.session_state[SESSION_KEY]
        st.success(f"{product} のWATデータを読み込みました。")
    elif state:
        df = state["data"]
        specs = state["specs"]
        st.info(f"{product} のキャッシュ済みデータを使用しています。")
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
                use_container_width=True,
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
                build_wafer_map(df_detail, selected_param), use_container_width=True
            )
        with col_b:
            st.plotly_chart(
                build_individual_chart(df_detail, selected_param, usl, lsl),
                use_container_width=True,
            )


if __name__ == "__main__":
    main()
