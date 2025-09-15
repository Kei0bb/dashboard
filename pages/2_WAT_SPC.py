import pandas as pd
import streamlit as st

from src.modules.sidebar import product_selector
from src.modules.spc_charts import create_individual_chart, create_wafer_map, load_spec_limits

st.set_page_config(page_title="WAT SPC Analysis", layout="wide")

st.title("WAT SPC Analysis")


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
    file_path = f"data/{selected_product}/wat.csv"
    df_product = load_data(file_path)

    if df_product is not None:
        st.header("WAT Data")
        st.dataframe(df_product)

        # パラメータ選択
        # 識別子列を除外してパラメータ列を特定
        param_cols = [
            c
            for c in df_product.columns
            if c not in ["Product", "BulkID", "WaferID", "DieX", "DieY", "Site", "Time"]
        ]
        selected_param = st.selectbox("Select Parameter", param_cols)

        if selected_param:
            # 2カラムレイアウト
            col1, col2 = st.columns(2)

            # 選択されたパラメータのデータを準備 (NaNを除外)
            df_param = df_product[["DieX", "DieY", selected_param]].dropna()

            with col1:
                # ウェーハマップ
                st.header(f"Wafer Map: {selected_param}")
                fig_wafer = create_wafer_map(df_param, selected_param)
                st.plotly_chart(fig_wafer, use_container_width=True)

            with col2:
                # SPCチャート
                st.header(f"Individual Chart: {selected_param}")
                spec_path = f"data/{selected_product}/specs.csv"
                usl, lsl = load_spec_limits(spec_path, selected_param)
                fig_i = create_individual_chart(df_param, selected_param, usl, lsl)
                st.plotly_chart(fig_i, use_container_width=True)

    else:
        st.warning(f"`{file_path}` が見つかりません。")

else:
    st.info("サイドバーから品種を選択してください。")