import json
from pathlib import Path
from typing import Callable, TypeVar

from src.models.base_config import BaseConfig

_MODEL_REGISTRY: dict[str, type[BaseConfig]] = {}
_T_CONFIG_TYPE = TypeVar("_T_CONFIG_TYPE", bound=type[BaseConfig])


def register_config_model(*, filename: str) -> Callable[[_T_CONFIG_TYPE], _T_CONFIG_TYPE]:
    def decorator(cls: _T_CONFIG_TYPE) -> _T_CONFIG_TYPE:
        _MODEL_REGISTRY[filename] = cls
        return cls

    return decorator


class ConfigLoader:
    configs_dir: Path

    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir: Path = configs_dir

    def load_configs(self) -> dict[type[BaseConfig], BaseConfig]:
        configs = {}

        for file in self.configs_dir.glob("*.json"):
            if file.name not in _MODEL_REGISTRY:
                continue

            config_cls = _MODEL_REGISTRY[file.name]
            config_raw_data = json.loads(file.read_text())
            configs[config_cls] = config_cls(**config_raw_data)

        return configs
