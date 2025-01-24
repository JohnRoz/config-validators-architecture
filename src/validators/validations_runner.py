import inspect
from typing import Callable, Iterable, TypeVar

from ..exceptions import BaseValidationError, InvalidValidationFunctionSignature
from ..models.base_config import BaseConfig

_ValidationFunction = Callable[..., Iterable[BaseValidationError]]
_T_VALIDATION_FUNCTION = TypeVar("_T_VALIDATION_FUNCTION", bound=_ValidationFunction)


_VALIDATORS: list[tuple[_ValidationFunction, tuple[type[BaseConfig], ...]]] = []


def register_validation(func: _T_VALIDATION_FUNCTION) -> _T_VALIDATION_FUNCTION:
    validation_parameters = inspect.signature(func).parameters

    if any(not issubclass(param.annotation, BaseConfig) for param in validation_parameters.values()):
        raise InvalidValidationFunctionSignature(
            f"Function {func.__qualname__} has parameters in its signature that are not subclasses of {BaseConfig.__qualname__}",
            parameters=validation_parameters,
        )

    _VALIDATORS.append((func, tuple(param.annotation for param in validation_parameters.values())))
    return func


def run_validations(available_configs: dict[type[BaseConfig], BaseConfig]) -> Iterable[BaseValidationError]:
    validation_errors: list[BaseValidationError] = []

    for validation_func, required_configs in _VALIDATORS:
        validation_args = [available_configs.get(config_type, None) for config_type in required_configs]

        if None in validation_args:
            # Means we don't have all configs required for this validation function and we can't run it
            continue

        validation_errors.extend(validation_func(*validation_args))

    return validation_errors
