import importlib
import inspect
import pkgutil
from typing import Callable, Iterable, TypeVar

from ...exceptions import (
    BaseException,
    BaseValidationError,
    InvalidValidationFunctionSignature,
)
from ...models.base_config import BaseConfig

_ValidationFunction = Callable[..., Iterable[BaseValidationError]]
_T_VALIDATION_FUNCTION = TypeVar("_T_VALIDATION_FUNCTION", bound=_ValidationFunction)


VALIDATORS: list[tuple[_ValidationFunction, tuple[type[BaseConfig], ...]]] = []


def register_validation(func: _T_VALIDATION_FUNCTION) -> _T_VALIDATION_FUNCTION:
    validation_parameters = inspect.signature(func).parameters

    if any(not issubclass(param.annotation, BaseConfig) for param in validation_parameters.values()):
        raise InvalidValidationFunctionSignature(
            f"Function {func.__qualname__} has parameters in its signature that are not subclasses of {BaseConfig.__qualname__}",
            func=func.__name__,
            invalid_parameters=[
                param for param in validation_parameters.values() if not issubclass(param.annotation, BaseConfig)
            ],
        )

    VALIDATORS.append((func, tuple(param.annotation for param in validation_parameters.values())))
    return func


# Automatically import all validator modules so that their "register_validation" decorators execute
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    if module_name.lower().endswith("validator"):
        importlib.import_module(f"{__name__}.{module_name}")
