import streamlit as st

from src.app.charts import build_wafer_map
from src.app.config import load_config
from src.app.data import create_repository
from src.app.services import WATService, YieldService
from src.app.ui import (
    sidebar_backend_selector,
    sidebar_product_selector,
    sidebar_run_button,
)

st.set_page_config(page_title="Wafer Map Viewer", layout="wide")


def main() -> None:
    config = load_config()
    config = sidebar_backend_selector(config)
    repo = create_repository(config)
    wat_service = WATService(repo)
    yield_service = YieldService(repo)
    current_backend = config.database.backend

    st.title("Wafer Map Viewer")
    st.caption(f"DB Backend: {current_backend.upper()}")

    products = yield_service.get_products()
    product = sidebar_product_selector(products)
    run_analysis = sidebar_run_button("Load Wafers")

    SESSION_KEY = "wafer_map_page_state"
    state = st.session_state.get(SESSION_KEY)
    if state and state.get("backend") != current_backend:
        state = None
    if state and product and state.get("product") != product.name:
        state = None

    if not product:
        st.warning("品種を選択してください。")
        return

    if not run_analysis and not state:
        st.info("サイドバーから Load Wafers を押してデータを読み込んでください。")
        return

    if run_analysis:
        df = wat_service.load_dataset(product.source_name)
        if df.empty:
            st.warning(f"{product.label} の測定データが見つかりません。")
            return
        st.session_state[SESSION_KEY] = {
            "product": product.name,
            "data": df,
            "backend": current_backend,
        }
        state = st.session_state[SESSION_KEY]
        st.success(f"{product.label} のウエハデータを読み込みました。")
    elif state:
        df = state["data"]
        st.info(f"{product.label} のキャッシュ済みデータを使用しています。")
    else:
        st.warning("データが存在しません。Load Wafers を実行してください。")
        return

    wafers = wat_service.list_wafers(df)
    parameters = wat_service.available_parameters(df)

    if not wafers:
        st.warning("WaferID カラムが見つかりません。")
        return
    if not parameters:
        st.warning("数値パラメータが見つかりません。")
        return

    st.markdown("### 表示設定")
    sel_col1, sel_col2, sel_col3 = st.columns(3)
    with sel_col1:
        selected_wafer = st.selectbox("Wafer ID", wafers)
    with sel_col2:
        selected_param = st.selectbox("Parameter", parameters)
    with sel_col3:
        selected_colorscale = st.selectbox(
            "Colorscale", ["Viridis", "Plasma", "Turbo", "Cividis", "RdBu"]
        )

    wafer_df = wat_service.filter_by_wafer(df, selected_wafer)
    zmin, zmax = wat_service.parameter_range(wafer_df, selected_param)

    auto_scale = st.checkbox("ウエハ内の値でカラースケールを自動調整", value=True)
    manual_min, manual_max = zmin, zmax
    if not auto_scale:
        range_col1, range_col2 = st.columns(2)
        with range_col1:
            manual_min = st.number_input(
                "Color Min", value=zmin if zmin is not None else 0.0, format="%.4f"
            )
        with range_col2:
            manual_max = st.number_input(
                "Color Max", value=zmax if zmax is not None else 0.0, format="%.4f"
            )

    fig = build_wafer_map(
        wafer_df,
        selected_param,
        colorscale=selected_colorscale,
        zmin=None if auto_scale else manual_min,
        zmax=None if auto_scale else manual_max,
        title=f"{product.label} / {selected_wafer} ({selected_param})",
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### Data Preview")
    preview_cols = ["DieX", "DieY", selected_param]
    st.dataframe(wafer_df[preview_cols].sort_values(["DieY", "DieX"]))


if __name__ == "__main__":
    main()
