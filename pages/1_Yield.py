import pandas as pd
import plotly.express as px
import streamlit as st

from src.modules.sidebar import product_selector

st.set_page_config(page_title="Yield Analysis", layout="wide")

st.title("Yield Analysis")


# データ読み込み関数
@st.cache_data
def load_data(file_path):
    try:
        df = pd.read_csv(file_path)
        df.columns = df.columns.str.strip()
        return df
    except FileNotFoundError:
        return None


# サイドバーから品種を選択
selected_product = product_selector()

# メインコンテンツエリア
if selected_product:
    st.write(f"## 選択された品種: {selected_product}")

    # データを読み込み
    file_path = f"data/{selected_product}/sort.csv"
    df_product = load_data(file_path)

    if df_product is not None:
        st.header("Sort Data")
        st.dataframe(df_product)

        # 2カラムレイアウト
        col1, col2 = st.columns(2)

        with col1:
            # 歩留まりの箱ひげ図
            st.header("Wafer by Wafer Yield Distribution")
            fig_box = px.box(
                df_product,
                x="LotID",
                y="0_PASS",
                color="LotID",
                points="all",
                title="Yield Distribution by Lot",
            )
            st.plotly_chart(fig_box, use_container_width=True)

        with col2:
            # 不良モードの円グラフ
            st.header("Top Failure Modes")
            # '0_PASS' と識別子列を除外して不良モード列を特定
            fail_cols = [
                c
                for c in df_product.columns
                if c.startswith(("1_", "2_", "3_", "4_", "5_", "6_", "7_", "8_", "9_"))
            ]
            if fail_cols:
                # 各不良モードの合計を計算
                fail_sum = df_product[fail_cols].sum().sort_values(ascending=False)
                fig_pie = px.pie(
                    fail_sum,
                    values=fail_sum.values,
                    names=fail_sum.index,
                    title="Failure Mode Contribution",
                )
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.warning("不良モードのデータが見つかりません。")

    else:
        st.warning(f"`{file_path}` が見つかりません。")

else:
    st.info("サイドバーから品種を選択してください。")