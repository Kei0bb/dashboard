import plotly.express as px
import streamlit as st

from src.modules.database import create_test_db_engine, fetch_data
from src.modules.sidebar import product_selector

st.set_page_config(page_title="Yield Analysis", layout="wide")

st.title("Yield Analysis")

# サイドバーから品種を選択
selected_product = product_selector()

# メインコンテンツエリア
if selected_product:
    st.write(f"## 選択された品種: {selected_product}")

    # データベースエンジンを作成
    engine = create_test_db_engine()

    # データを取得
    sql = "SELECT lot_id, yield FROM yields WHERE product = :product"
    params = {"product": selected_product}
    df = fetch_data(engine, sql, params)

    if not df.empty:
        # データを表示
        st.dataframe(df)

        # Yieldの推移をプロット
        st.header("Yield Trend")
        fig = px.line(df, x="lot_id", y="yield", title=f"{selected_product} Yield Trend")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("データが見つかりません。")
else:
    st.info("サイドバーから品種を選択してください。")