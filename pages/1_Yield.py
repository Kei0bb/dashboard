import streamlit as st

from src.modules.sidebar import product_selector
from src.modules.db_utils import get_db_connection, load_yield_data, load_specs_from_csv
from src.modules.yield_charts import (
    create_failure_mode_chart,
    create_summary_chart,
    create_yield_distribution_chart,
)

st.set_page_config(page_title="Yield Analysis", layout="wide")
st.title("Yield Analysis")

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
            st.info(f"Loading data for product '{selected_product}'...")
            df_sort = load_yield_data(conn, selected_product)
            df_specs = load_specs_from_csv(selected_product)
            data = {"sort": df_sort, "specs": df_specs}
            st.success("Successfully loaded data.")
    else:
        st.warning("Please select a product first.")

# メインコンテンツエリア
if data:
    st.write(f"## 選択された品種: {selected_product}")
    if "sort" in data:
        df_product = data["sort"]
        id_cols = ["Product", "BulkID", "LotID", "WaferID", "Time", "SortNo", "Tester", "TP"]
        pass_col = "0_PASS"
        fail_cols = [c for c in df_product.columns if c not in id_cols and c != pass_col]

        st.header("Yield Summary")
        agg_period = st.radio(
            "Aggregate by",
            ["Daily", "Weekly", "Monthly", "Quarterly", "BulkID"],
            index=4,
            horizontal=True,
        )
        fig_summary = create_summary_chart(df_product, agg_period, id_cols, pass_col, fail_cols)
        st.plotly_chart(fig_summary, use_container_width=True)

        st.header("Detailed Analysis")
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Wafer by Wafer Yield Distribution")
            fig_box = create_yield_distribution_chart(df_product, pass_col)
            st.plotly_chart(fig_box, use_container_width=True)
        with col2:
            st.subheader("Top Failure Modes (Overall)")
            fig_pie = create_failure_mode_chart(df_product, fail_cols)
            if fig_pie:
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("不良モードのデータが見つかりません。")
    else:
        st.error(f"'sort' data not found for product: {selected_product}")

elif not run_button:
    st.info("サイドバーから品種を選択し、「Run Analysis」ボタンを押してください。")
