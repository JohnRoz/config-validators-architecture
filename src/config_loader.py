import json
from pathlib import Path
from typing import Callable, Iterable, Self, TypeVar

import pydantic

from src.exceptions import (
    BaseException,
    BaseSingleConfigValidationError,
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


class ConfigLoader:
    configs_dir: Path
    configs: dict[type[BaseConfig], BaseConfig]
    _errors: list[BaseSingleConfigValidationError | ConfigCreationFailedError]

    def __init__(self, configs_dir: Path) -> None:
        self.configs_dir: Path = configs_dir
        self.configs: dict[type[BaseConfig], BaseConfig] = {}
        self._errors: list[BaseSingleConfigValidationError | ConfigCreationFailedError] = []

    @classmethod
    def load(cls, configs_dir: str | Path, should_raise_on_error: bool = False) -> Self:
        if isinstance(configs_dir, str):
            configs_dir = Path(configs_dir)

        if not configs_dir.exists():
            err_msg = "Directory specified as configs_dir argument does not exist"
            raise BaseExceptionGroup(err_msg, [ConfigCreationFailedError(err_msg, configs_dir=configs_dir)])

        return cls(configs_dir).load_configs(should_raise_on_error=should_raise_on_error)

    @property
    def all_errors(self) -> Iterable[BaseSingleConfigValidationError | ConfigCreationFailedError]:
        return self._errors

    @property
    def single_config_validation_errors(self) -> Iterable[BaseSingleConfigValidationError]:
        return [err for err in self._errors if isinstance(err, BaseSingleConfigValidationError)]

    @property
    def config_creation_errors(self) -> Iterable[ConfigCreationFailedError]:
        return [err for err in self._errors if isinstance(err, ConfigCreationFailedError)]

    def load_configs(self, should_raise_on_error: bool = False) -> Self:
        self._load_configs()

        if should_raise_on_error and self._errors:
            raise BaseExceptionGroup("Configurations load process resulted with the following errors:", self._errors)

        return self

    def _load_configs(self) -> Self:
        for file in self.configs_dir.glob("*.json"):
            if file.name not in _MODEL_REGISTRY:
                continue

            config_cls = _MODEL_REGISTRY[file.name]
            try:
                config_raw_data = json.loads(file.read_text())
                self.configs[config_cls] = config_cls(**config_raw_data)
            except pydantic.ValidationError as e:
                print(f"Error loading '{file.name}':")
                self._errors.extend(
                    [
                        BaseSingleConfigValidationError(
                            err.get("msg", "Unknown error"), config_file=file.name, location=err.get("loc", [])
                        )
                        for err in e.errors()
                    ]
                )
            except Exception as e:
                self._errors.append(ConfigCreationFailedError(err_msg=str(e), error=e))

        return self
