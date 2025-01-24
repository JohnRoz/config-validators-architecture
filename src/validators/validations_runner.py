from ..models.base_config import BaseConfig
from . import VALIDATORS_REGISTRY
from .validation_exceptions import BaseValidationError


def run_validations(available_configs: dict[type[BaseConfig], BaseConfig]):
    validation_errors: list[BaseValidationError] = []

    for validation_func, required_config_types in VALIDATORS_REGISTRY:
        if missing_configs := required_config_types - available_configs.keys():
            # Means we don't have all configs requied for this validation function and we can't run it
            continue

        available_and_required_config_types = required_config_types & available_configs.keys()
        validation_args = [
            config_instance
            for config_type, config_instance in available_configs.items()
            if config_type in available_and_required_config_types
        ]

        validation_errors.extend(validation_func(*validation_args))

    return validation_errors
