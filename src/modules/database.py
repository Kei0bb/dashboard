from __future__ import annotations

from typing import Any, Dict, Optional

import numpy as np
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine


def get_engine(
    user: str, password: str, host: str, port: int, sid: str, **kwargs
) -> Engine:
    import oracledb

    dsn = oracledb.makedsn(host, port, sid=sid)
    url = f"oracle+oracledb://{user}:{password}@"
    default_kwargs = {"pool_pre_ping": True, "pool_recycle": 1800, "echo": False}
    default_kwargs.update(kwargs)

    engine = create_engine(url, connect_args={"dsn": dsn}, **default_kwargs)
    return engine


def create_test_db_engine(db_path: str = "data/test.db") -> Engine:
    """Creates a new SQLite engine for testing."""
    return create_engine(f"sqlite:///{db_path}")


def init_test_db(engine: Engine):
    """Initializes the test database with sample data."""
    products = ["ProductA", "ProductB", "ProductC"]
    # Create sample yield data
    yield_data = {
        "product": [products[0]] * 4 + [products[1]] * 3 + [products[2]] * 3,
        "lot_id": [f"lot_{i}" for i in range(1, 11)],
        "yield": [95.5, 96.2, 95.8, 94.9, 85.1, 84.5, 85.3, 92.1, 91.8, 92.5],
    }
    yield_df = pd.DataFrame(yield_data)
    yield_df.to_sql("yields", engine, if_exists="replace", index=False)

    # Create sample WAT data with subgroups
    wat_data = []
    for lot in range(1, 11):
        for subgroup in range(1, 6):
            if lot <= 4:
                product = products[0]
                base_value = 1.2
            elif lot <= 7:
                product = products[1]
                base_value = 0.8
            else:
                product = products[2]
                base_value = 1.0

            wat_data.append(
                {
                    "product": product,
                    "lot_id": f"lot_{lot}",
                    "subgroup": subgroup,
                    "param1": base_value
                    + (lot * 0.01)
                    + (subgroup * 0.005)
                    + (np.random.randn() * 0.01),
                    "param2": (base_value * 10)
                    + (lot * 0.1)
                    + (subgroup * 0.05)
                    + (np.random.randn() * 0.1),
                }
            )
    wat_df = pd.DataFrame(wat_data)
    wat_df.to_sql("wat_data", engine, if_exists="replace", index=False)


def fetch_data(
    engine: Engine,
    sql: str,
    params: Optional[Dict[str, Any]] = None,
    chunksize: Optional[int] = None,
) -> pd.DataFrame:
    if chunksize:
        it = pd.read_sql_query(text(sql), engine, params=params, chunksize=chunksize)
        return pd.concat(it, ignore_index=True)
    return pd.read_sql_query(text(sql), engine, params=params)


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "init":
        print("Initializing test database...")
        test_engine = create_test_db_engine()
        init_test_db(test_engine)
        print("Test database initialized.")