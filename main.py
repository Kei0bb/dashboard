import streamlit as st

from src.modules.sidebar import load_prod

st.set_page_config(page_title="Home - Dashboard", layout="wide")

st.title("Dashboard Home")

st.markdown("### Available Products")

products = load_prod()

if products:
    for product in products:
        st.markdown(f"- {product}")
else:
    st.warning("No product data found in the `data` directory.")
