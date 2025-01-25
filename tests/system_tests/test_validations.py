from typing import Iterable

from src.config_loader import ConfigLoader
from src.cross_config_validations import cross_config_validations_runner
from src.exceptions import BaseValidationError
from tests.test_utils import (
    INVALID_CROSS_CONFIGS_PATH,
    INVALID_SINGLE_CONFIGS_PATH,
    VALID_CROSS_CONFIGS_PATH,
    group_error_kwargs,
)


def _get_cross_config_validation_errors(configs_path: str) -> Iterable[BaseValidationError]:
    loader = ConfigLoader.load(configs_path)

    return cross_config_validations_runner.run_validations(loader.configs)


def test_validations__cross_config__invalid():
    cross_config_validation_errors = _get_cross_config_validation_errors(INVALID_CROSS_CONFIGS_PATH)
    assert cross_config_validation_errors
    assert "Referenced subfeature is undefined" in str(cross_config_validation_errors)

    # Find specifig error I know should occur
    assert "sub_3" in group_error_kwargs(cross_config_validation_errors)["undefined_subfeature"]


def test_validations__cross_config__valid():
    cross_config_validation_ = _get_cross_config_validation_errors(VALID_CROSS_CONFIGS_PATH)
    assert not cross_config_validation_


def test_validations__single_config__invalid():
    loader = ConfigLoader.load(INVALID_SINGLE_CONFIGS_PATH)
    assert loader.single_config_validation_errors
    assert "subfeature_names cannot be empty" in str(loader.single_config_validation_errors)

    invalid_configs = group_error_kwargs(loader.single_config_validation_errors)["config_file"]

    assert "FeatureConfig.json" in invalid_configs
