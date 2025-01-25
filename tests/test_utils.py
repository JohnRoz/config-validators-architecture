import os
from collections import defaultdict
from typing import Iterable

from src.exceptions import BaseException

TESTS_DIR = os.path.dirname(__file__)
TEST_RESOURCES_DIR = os.path.join(TESTS_DIR, "test_resources")

VALID_CONFIGS_PATH = os.path.join(TEST_RESOURCES_DIR, "valid_configs")
INVALID_CONFIGS_PATH = os.path.join(TEST_RESOURCES_DIR, "invalid_configs")


def group_error_kwargs(errors: Iterable[BaseException]) -> dict[str, list[str]]:
    error_kwd_to_values: dict[str, list[str]] = defaultdict(list)

    error_kwargs = [err._error_kwargs for err in errors]

    for kwargs in error_kwargs:
        for kwd, value in kwargs.items():
            error_kwd_to_values[kwd].append(value)

    return error_kwd_to_values
