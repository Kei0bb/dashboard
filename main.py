import streamlit as st
import pandas as pd

st.set_page_config(page_title="Home - Dashboard", layout="wide")

st.title("Dashboard Home")

st.markdown("### Product List")

try:
    df = pd.read_csv("data/products.csv")
    
    # Check if the 'product_name' column exists
    if 'product_name' in df.columns:
        for product in df['product_name']:
            st.markdown(f"- {product}")
    # Check for 'product' column as a fallback
    elif 'product' in df.columns:
        for product in df['product']:
            st.markdown(f"- {product}")
    else:
        st.warning("Could not find a product column in `data/products.csv`.")
        st.dataframe(df)

except FileNotFoundError:
    st.error("`data/products.csv` not found.")