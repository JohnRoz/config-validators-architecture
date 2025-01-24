from typing import Callable, Iterable, TypeVar

from src.models.base_config import BaseConfig
from src.validators.validation_exceptions import BaseValidationError

ValidationFunction = Callable[..., Iterable[BaseValidationError]]
_T_VALIDATION_FUNCTION = TypeVar("_T_VALIDATION_FUNCTION", bound=ValidationFunction)


VALIDATORS_REGISTRY: list[tuple[ValidationFunction, set[type[BaseConfig]]]] = []


def register_validator(*config_types):
    def decorator(func: _T_VALIDATION_FUNCTION) -> _T_VALIDATION_FUNCTION:
        VALIDATORS_REGISTRY.append((func, set(config_types)))
        return func

    return decorator
