import streamlit as st

from src.app.config import load_config
from src.app.data import create_repository
from src.app.services import YieldService

st.set_page_config(page_title="Dashboard Home", layout="wide")


def main() -> None:
    config = load_config()
    repo = create_repository(config)
    yield_service = YieldService(repo)

    st.title("半導体製造ダッシュボード")
    st.caption("モックデータ/Oracleのどちらでも動く再構築版")

    st.markdown("### 利用可能な品種")
    products = yield_service.get_products()
    if not products:
        st.warning("config/products.yaml も data/ 以下も製品が登録されていません。")
    else:
        for product in products:
            st.markdown(
                f"- `{product.name}` (label: {product.label}, data: `{product.data_subdir}`)"
            )

    st.markdown("---")
    st.subheader("環境情報")
    st.json(
        {
            "environment": config.environment,
            "database_backend": config.database.backend,
            "sqlite_path": config.database.sqlite_path,
        }
    )


if __name__ == "__main__":
    main()
