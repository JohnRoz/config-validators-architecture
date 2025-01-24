import dataclasses
import json
from pathlib import Path
from typing import Callable, Iterable, TypeVar

import pydantic

from src.exceptions import (
    BaseSingleConfigValidationError,
    BaseValidationError,
    ConfigCreationFailedError,
)
from src.models.base_config import BaseConfig

_MODEL_REGISTRY: dict[str, type[BaseConfig]] = {}
_T_CONFIG_TYPE = TypeVar("_T_CONFIG_TYPE", bound=type[BaseConfig])


def register_config_model(*, filename: str) -> Callable[[_T_CONFIG_TYPE], _T_CONFIG_TYPE]:
    def decorator(cls: _T_CONFIG_TYPE) -> _T_CONFIG_TYPE:
        _MODEL_REGISTRY[filename] = cls
        return cls

    return decorator


@dataclasses.dataclass
class ConfigLoadResult:
    configs: dict[type[BaseConfig], BaseConfig]
    single_config_validation_errors: Iterable[BaseSingleConfigValidationError | ConfigCreationFailedError]

    def unpack(
        self,
    ) -> tuple[dict[type[BaseConfig], BaseConfig], Iterable[BaseSingleConfigValidationError | ConfigCreationFailedError]]:
        return (self.configs, self.single_config_validation_errors)


class ConfigLoader:
    configs_dir: Path

    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir: Path = configs_dir

    def _load_configs(self) -> ConfigLoadResult:
        configs: dict[type[BaseConfig], BaseConfig] = {}
        single_config_validation_errors: list[BaseSingleConfigValidationError | ConfigCreationFailedError] = []

        for file in self.configs_dir.glob("*.json"):
            if file.name not in _MODEL_REGISTRY:
                continue

            config_cls = _MODEL_REGISTRY[file.name]
            try:
                config_raw_data = json.loads(file.read_text())
                configs[config_cls] = config_cls(**config_raw_data)
            except pydantic.ValidationError as e:
                print(f"Error loading '{file.name}':")
                single_config_validation_errors.extend(
                    [
                        BaseSingleConfigValidationError(
                            f'Pydantic validation failed: {err.get("msg", "Unknown error")}', location=err.get("loc", [])
                        )
                        for err in e.errors()
                    ]
                )
            except Exception as e:
                single_config_validation_errors.append(ConfigCreationFailedError(err_msg=str(e), error=e))

        return ConfigLoadResult(configs=configs, single_config_validation_errors=single_config_validation_errors)

    def load_configs(self, should_raise_on_error: bool = False) -> ConfigLoadResult:
        config_load_result = self._load_configs()

        if should_raise_on_error and config_load_result.single_config_validation_errors:
            msg = ("\n" + "#" * 80 + "\n").join(str(err) for err in config_load_result.single_config_validation_errors)
            raise BaseValidationError(msg)

        return config_load_result
