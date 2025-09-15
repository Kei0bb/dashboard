import streamlit as st

from src.modules.database import fetch_data, fetch_specs
from src.modules.sidebar import product_selector
from src.modules.spc_charts import create_individual_chart

st.set_page_config(page_title="WAT SPC Analysis", layout="wide")

st.title("WAT SPC Analysis")

# サイドバーから品種を選択
selected_product = product_selector()

# メインコンテンツエリア
st.write(f"## 選択された品種: {selected_product}")

# データを取得
df = fetch_data(selected_product)

if not df.empty:
    # データを表示
    st.dataframe(df)

    # SPCチャートを表示するパラメータのリスト
    spc_parameters = ["param1", "param2"]

    # 2カラムでチャートを配置
    cols = st.columns(2)

    for i, param in enumerate(spc_parameters):
        usl, lsl = fetch_specs(selected_product, param)
        with cols[i % 2]:  # 0, 1, 0, 1...と繰り返す
            st.header(f"Individual Chart for {param}")
            # Individual Chartを作成
            fig_i = create_individual_chart(df, param, usl, lsl)
            st.plotly_chart(fig_i, use_container_width=True)

else:
    st.warning("データが見つかりません。")
