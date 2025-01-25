from typing import Iterable

from ..exceptions import BaseException, BaseValidationError
from ..models.base_config import BaseConfig
from .validators import VALIDATORS


def run_validations(
    available_configs: dict[type[BaseConfig], BaseConfig], should_raise_on_error: bool = False
) -> Iterable[BaseValidationError]:
    errors = _run_validations(available_configs=available_configs)

    if should_raise_on_error and errors:
        raise BaseException.group_errors(errors)

    return errors


def _run_validations(
    available_configs: dict[type[BaseConfig], BaseConfig],
) -> Iterable[BaseValidationError]:
    validation_errors: list[BaseValidationError] = []

    for validation_func, required_configs in VALIDATORS:
        validation_args = [available_configs.get(config_type, None) for config_type in required_configs]

        if None in validation_args:
            # Means we don't have all configs required for this validation function and we can't run it
            continue

        validation_errors.extend(validation_func(*validation_args))

    return validation_errors
