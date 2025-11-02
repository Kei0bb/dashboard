import plotly.graph_objects as go
import streamlit as st

from src.modules.sidebar import product_selector
from src.modules.spc_charts import (
    create_individual_chart,
    create_wafer_map,
    load_spec_limits,
)
from src.modules.db_utils import get_db_connection, load_data_from_db

st.set_page_config(page_title="WAT SPC Analysis", layout="wide")
st.title("WAT Analysis Dashboard")

ID_COLUMNS = ["Product", "BulkID", "WaferID", "DieX", "DieY", "Site", "Time"]

# サイドバー
st.sidebar.title("Controls")
selected_product = product_selector()
st.sidebar.markdown("---")
run_button = st.sidebar.button("Run Analysis")

# データ読み込み処理
data = None
if run_button:
    if selected_product:
        conn = get_db_connection()
        if conn:
            data = load_data_from_db(conn, selected_product)
    else:
        st.warning("Please select a product first.")

# メインコンテンツエリア
if data:
    st.write(f"## 選択された品種: {selected_product}")
    if "wat" in data and "specs" in data:
        df_product = data["wat"]
        df_specs = data["specs"]
        param_cols = [c for c in df_product.columns if c not in ID_COLUMNS]

        st.header("Parameter Trends by Bulk ID")
        cols = st.columns(3)

        for i, param in enumerate(param_cols):
            with cols[i % 3]:
                with st.container(border=True):
                    st.markdown(f"### {param}")
                    df_agg = (
                        df_product.groupby("BulkID")
                        .agg(mean_val=(param, "mean"), Time=("Time", "first"))
                        .sort_values("Time")
                        .reset_index()
                    )
                    df_agg["moving_avg"] = df_agg["mean_val"].rolling(window=3, min_periods=1).mean()

                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(x=df_agg["BulkID"], y=df_agg["mean_val"], name="Bulk Mean", mode="markers", marker=dict(size=6)))
                    fig_trend.add_trace(go.Scatter(x=df_agg["BulkID"], y=df_agg["moving_avg"], name="Moving Avg (n=3)", mode="lines", line=dict(color="red", width=2)))

                    usl, lsl = load_spec_limits(df_specs, param)
                    if usl is not None:
                        fig_trend.add_hline(y=usl, line_dash="dash", line_color="orange", annotation_text="USL")
                    if lsl is not None:
                        fig_trend.add_hline(y=lsl, line_dash="dash", line_color="orange", annotation_text="LSL")

                    fig_trend.update_layout(
                        height=350,
                        margin=dict(l=40, r=40, t=40, b=40),
                        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)

        with st.expander("Drill-down Analysis by Bulk ID", expanded=False):
            st.markdown("#### Select a Bulk ID and Parameter for detailed analysis")
            col1, col2 = st.columns(2)
            with col1:
                bulk_id_list = df_product["BulkID"].unique()
                selected_bulk_id = st.selectbox("Bulk ID", bulk_id_list)
            with col2:
                selected_param_detail = st.selectbox("Parameter", param_cols, key="detail_param")

            if selected_bulk_id and selected_param_detail:
                df_detail = df_product[df_product["BulkID"] == selected_bulk_id]
                col_a, col_b = st.columns(2)
                with col_a:
                    st.markdown("##### Wafer Map")
                    fig_wafer = create_wafer_map(df_detail, selected_param_detail)
                    st.plotly_chart(fig_wafer, use_container_width=True)
                with col_b:
                    st.markdown("##### Individual Chart")
                    usl, lsl = load_spec_limits(df_specs, selected_param_detail)
                    fig_i = create_individual_chart(df_detail, selected_param_detail, usl, lsl)
                    st.plotly_chart(fig_i, use_container_width=True)
    else:
        st.error(f"'wat' or 'specs' data not found for product: {selected_product}")

elif not run_button:
    st.info("サイドバーから品種を選択し、「Run Analysis」ボタンを押してください。")
