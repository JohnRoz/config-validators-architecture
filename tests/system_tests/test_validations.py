from pathlib import Path
from typing import Iterable

from src.config_loader import ConfigLoader
from src.validators import validations_runner
from src.validators.validation_exceptions import BaseValidationError
from tests.test_utils import INVALID_CONFIGS_PATH, VALID_CONFIGS_PATH


def _run_validations(configs_path: str) -> Iterable[BaseValidationError]:
    loader = ConfigLoader(Path(configs_path))
    available_configs = loader.load_configs()

    return validations_runner.run_validations(available_configs)


def test_validations__invalid_configs():
    errors = _run_validations(INVALID_CONFIGS_PATH)
    assert errors


def test_validations__valid_configs():
    errors = _run_validations(VALID_CONFIGS_PATH)
    assert not errors
