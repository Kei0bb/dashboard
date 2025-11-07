"""DBバックエンドごとの実装を切り替えるためのヘルパー。"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

import pandas as pd

from ..config import AppConfig, load_config
from .sqlite_repo import SQLiteRepository
from .oracle_repo import OracleRepository


class DatabaseRepository(Protocol):
    """Yield/WATデータを提供するための共通インターフェース。"""

    def load_yield_overview(self, product_name: str) -> pd.DataFrame: ...

    def load_wat_measurements(self, product_name: str) -> pd.DataFrame: ...


@dataclass
class RepositoryFactory:
    config: AppConfig

    def create(self) -> DatabaseRepository:
        backend = self.config.database.backend
        if backend == "oracle":
            return OracleRepository(self.config)
        if backend == "sqlite":
            return SQLiteRepository(self.config)
        raise ValueError(f"Unsupported DB backend: {backend}")


def create_repository(config: AppConfig | None = None) -> DatabaseRepository:
    cfg = config or load_config()
    return RepositoryFactory(cfg).create()
