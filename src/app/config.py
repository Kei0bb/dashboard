"""環境変数や外部設定を1か所で管理するモジュール。"""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class DatabaseConfig:
    backend: str
    sqlite_path: str | None
    oracle_username: str | None
    oracle_password: str | None
    oracle_dsn: str | None


@dataclass(frozen=True)
class AppConfig:
    environment: str
    database: DatabaseConfig
    cache_ttl_seconds: int


@lru_cache(maxsize=1)
def load_config() -> AppConfig:
    backend = os.getenv("DB_BACKEND", "sqlite").lower()
    return AppConfig(
        environment=os.getenv("APP_ENV", "development"),
        database=DatabaseConfig(
            backend=backend,
            sqlite_path=os.getenv("DB_SQLITE_PATH", "data/test.db"),
            oracle_username=os.getenv("DB_USERNAME"),
            oracle_password=os.getenv("DB_PASSWORD"),
            oracle_dsn=os.getenv("DB_DSN"),
        ),
        cache_ttl_seconds=int(os.getenv("CACHE_TTL_SECONDS", "600")),
    )
