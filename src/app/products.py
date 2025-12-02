"""製品メタデータをYAMLから読み込むヘルパー。"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Iterable, Sequence

import yaml

DEFAULT_CONFIG_PATH = Path("config/products.yaml")
DEFAULT_DATA_DIR = Path("data")
DEFAULT_SPEC_DIR = Path("config/specs")
DEFAULT_STAGES: tuple[str, ...] = ("CP", "FT")


@dataclass(frozen=True)
class ProductDefinition:
    """UI表示やデータ取得に利用する製品設定。"""

    name: str
    label: str
    data_subdir: str
    source_name: str
    stages: tuple[str, ...] = DEFAULT_STAGES
    spec_file: str | None = None
    specs: tuple[dict[str, object], ...] = tuple()

    def supports_stage(self, stage: str) -> bool:
        return stage.upper() in {s.upper() for s in self.stages}

    def data_path(self, base_dir: str | Path = DEFAULT_DATA_DIR) -> Path:
        return Path(base_dir) / self.data_subdir


def _normalize_stage_list(raw: Iterable[str] | None) -> tuple[str, ...]:
    if not raw:
        return DEFAULT_STAGES
    return tuple(str(stage).upper() for stage in raw if stage)


@lru_cache(maxsize=1)
def _load_configured_products(config_path: str) -> tuple[ProductDefinition, ...]:
    path = Path(config_path)
    if not path.exists():
        return tuple()
    with path.open(encoding="utf-8") as fp:
        data = yaml.safe_load(fp) or {}
    products: list[ProductDefinition] = []
    for item in data.get("products", []):
        name = str(item.get("name", "")).strip()
        if not name:
            continue
        label = str(item.get("label") or name)
        data_subdir = str(item.get("data_subdir") or name)
        source_name = str(item.get("source_name") or name)
        stages = _normalize_stage_list(item.get("stages"))
        spec_file = item.get("spec_file")
        specs = tuple(item.get("specs") or ())
        products.append(
            ProductDefinition(
                name=name,
                label=label,
                data_subdir=data_subdir,
                source_name=source_name,
                stages=stages,
                spec_file=str(spec_file) if spec_file else None,
                specs=specs,
            )
        )
    return tuple(products)


def _discover_from_data_dir(data_dir: Path) -> list[ProductDefinition]:
    if not data_dir.exists():
        return []
    products: list[ProductDefinition] = []
    for child in sorted(p for p in data_dir.iterdir() if p.is_dir()):
        products.append(
            ProductDefinition(
                name=child.name,
                label=child.name,
                data_subdir=child.name,
                source_name=child.name,
            )
        )
    return products


def list_products(
    data_dir: str | Path = DEFAULT_DATA_DIR, config_path: str | Path | None = None
) -> list[ProductDefinition]:
    """設定ファイル優先で製品一覧を返す。"""
    cfg_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    configured = list(_load_configured_products(cfg_path.as_posix()))
    if configured:
        return configured
    return _discover_from_data_dir(Path(data_dir))


def find_product_definition(
    product_name: str | ProductDefinition,
    data_dir: str | Path = DEFAULT_DATA_DIR,
    config_path: str | Path | None = None,
) -> ProductDefinition | None:
    """name/source/data_subdir のいずれかに合致する製品設定を取得。"""
    if isinstance(product_name, ProductDefinition):
        return product_name
    needle = product_name.lower()
    for product in list_products(data_dir=data_dir, config_path=config_path):
        candidates = {
            product.name.lower(),
            product.source_name.lower(),
            product.data_subdir.lower(),
        }
        if needle in candidates:
            return product
    return None


__all__ = ["ProductDefinition", "list_products", "find_product_definition", "DEFAULT_SPEC_DIR"]
