import plotly.express as px
import streamlit as st

from src.modules.database import fetch_data
from src.modules.sidebar import product_selector

st.set_page_config(page_title="Yield Analysis", layout="wide")

st.title("Yield Analysis")

# サイドバーから品種を選択
selected_product = product_selector()

# メインコンテンツエリア
st.write(f"## 選択された品種: {selected_product}")

# データを取得
df = fetch_data(selected_product)

if not df.empty:
    # データを表示
    st.dataframe(df)

    # Yieldの推移をプロット
    st.header("Yield Trend")
    fig = px.line(df, x="lot_id", y="yield", title=f"{selected_product} Yield Trend")
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("データが見つかりません。")
