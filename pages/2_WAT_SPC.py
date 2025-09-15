import streamlit as st

from src.modules.database import create_test_db_engine, fetch_data
from src.modules.sidebar import product_selector
from src.modules.spc_charts import create_individual_chart, load_spec_limits

st.set_page_config(page_title="WAT SPC Analysis", layout="wide")

st.title("WAT SPC Analysis")

# サイドバーから品種を選択
selected_product = product_selector()

# メインコンテンツエリア
if selected_product:
    st.write(f"## 選択された品種: {selected_product}")

    # データベースエンジンを作成
    engine = create_test_db_engine()

    # データを取得
    sql = "SELECT * FROM wat_data WHERE product = :product"
    params = {"product": selected_product}
    df = fetch_data(engine, sql, params)

    if not df.empty:
        # データを表示
        st.dataframe(df)

        # SPCチャートを表示するパラメータのリスト
        spc_parameters = ["param1", "param2"]

        # 2カラムでチャートを配置
        cols = st.columns(2)

        for i, param in enumerate(spc_parameters):
            usl, lsl = load_spec_limits("data/specs.csv", selected_product, param)
            with cols[i % 2]:
                st.header(f"Individual Chart for {param}")
                # Individual Chartを作成
                fig_i = create_individual_chart(df, param, usl, lsl)
                st.plotly_chart(fig_i, use_container_width=True)

    else:
        st.warning("データが見つかりません。")
else:
    st.info("サイドバーから品種を選択してください。")