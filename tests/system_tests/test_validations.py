from typing import Iterable

from src.config_loader import ConfigLoader
from src.exceptions import BaseValidationError
from src.validators import validations_runner
from tests.test_utils import (
    INVALID_CROSS_CONFIGS_PATH,
    INVALID_SINGLE_CONFIGS_PATH,
    VALID_CROSS_CONFIGS_PATH,
    VALID_SINGLE_CONFIGS_PATH,
    group_error_kwargs,
)


def _get_cross_config_validation_errors(configs_path: str) -> Iterable[BaseValidationError]:
    loader = ConfigLoader.load(configs_path)

    return validations_runner.run_validations(loader.configs)


def test_validations__cross_config__invalid_configs():
    cross_config_validation_errors = _get_cross_config_validation_errors(INVALID_CROSS_CONFIGS_PATH)
    assert cross_config_validation_errors
    assert "Referenced subfeature is undefined" in str(cross_config_validation_errors)

    # Find specifig error I know should occur
    assert "sub_3" in group_error_kwargs(cross_config_validation_errors)["undefined_subfeature"]


def test_validations__cross_config__valid_configs():
    cross_config_validation_ = _get_cross_config_validation_errors(VALID_CROSS_CONFIGS_PATH)
    assert not cross_config_validation_
