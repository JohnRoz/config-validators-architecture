import json
from pathlib import Path
from typing import Callable, TypeVar

from pydantic import BaseModel

_MODEL_REGISTRY: dict[str, type[BaseModel]] = {}
_CONFIG_TYPE = TypeVar("_CONFIG_TYPE", bound=type[BaseModel])


def register_config_model(*, filename: str) -> Callable[[_CONFIG_TYPE], _CONFIG_TYPE]:
    def decorator(cls: _CONFIG_TYPE) -> _CONFIG_TYPE:
        _MODEL_REGISTRY[filename] = cls
        return cls

    return decorator


class ConfigLoader:
    configs_dir: Path

    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir: Path = configs_dir

    def load_configs(self) -> dict:
        configs = {}

        for file in self.configs_dir.glob("*.json"):
            if file.name not in _MODEL_REGISTRY:
                continue

            config_cls = _MODEL_REGISTRY[file.name]
            config_raw_data = json.loads(file.read_text())
            configs[config_cls] = config_cls(**config_raw_data)

        return configs
