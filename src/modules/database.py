import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

def get_db_connection():
    db_url = st.secrets["database"]["db_url"]
    engine = create_engine(db_url)
    return engine

def fetch_data(product_name: str):
    engine = get_db_connection()
    # この例では、product_nameをテーブル名としてデータを取得します
    # 実際には、WHERE句で品種を指定することになるでしょう
    try:
        df = pd.read_sql(f"SELECT * FROM {product_name}", engine)
    except Exception as e:
        st.error(f"データベースからのデータ取得中にエラーが発生しました: {e}")
        df = pd.DataFrame() # エラーの場合は空のDataFrameを返す
    return df

def fetch_specs(product_name: str, parameter: str):
    try:
        df_specs = pd.read_csv("data/specs.csv")
        spec = df_specs[(df_specs['product_name'] == product_name) & (df_specs['parameter'] == parameter)]
        if not spec.empty:
            usl = spec['USL'].iloc[0]
            lsl = spec['LSL'].iloc[0]
            return usl, lsl
        else:
            return None, None
    except Exception as e:
        st.error(f"仕様データの読み込み中にエラーが発生しました: {e}")
        return None, None
