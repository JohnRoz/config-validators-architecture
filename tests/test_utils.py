import os
from collections import defaultdict
from typing import Iterable

from src.exceptions import BaseException

TESTS_DIR = os.path.dirname(__file__)
TEST_RESOURCES_DIR = os.path.join(TESTS_DIR, "test_resources")

CROSS_CONFIGS_PATH = os.path.join(TEST_RESOURCES_DIR, "cross_configs")
VALID_CROSS_CONFIGS_PATH = os.path.join(CROSS_CONFIGS_PATH, "valid_configs")
INVALID_CROSS_CONFIGS_PATH = os.path.join(CROSS_CONFIGS_PATH, "invalid_configs")

SINGLE_CONFIGS_PATH = os.path.join(TEST_RESOURCES_DIR, "single_configs")
VALID_SINGLE_CONFIGS_PATH = os.path.join(SINGLE_CONFIGS_PATH, "valid_configs")
INVALID_SINGLE_CONFIGS_PATH = os.path.join(SINGLE_CONFIGS_PATH, "invalid_configs")


def group_error_kwargs(errors: Iterable[BaseException]) -> dict[str, list[str]]:
    error_kwd_to_values: dict[str, list[str]] = defaultdict(list)

    error_kwargs = [err._error_kwargs for err in errors]

    for kwargs in error_kwargs:
        for kwd, value in kwargs.items():
            error_kwd_to_values[kwd].append(value)

    return error_kwd_to_values
