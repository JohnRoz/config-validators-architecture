import pytest

from src.cross_config_validations.validators import register_validation
from src.exceptions import InvalidValidationFunctionSignature


def test_register__validation():
    def validation_with_non_config_objs_in_signature(num: int):
        pass

    with pytest.raises(InvalidValidationFunctionSignature) as exc_info:
        register_validation(validation_with_non_config_objs_in_signature)

    assert exc_info.value._error_kwargs["func"] == validation_with_non_config_objs_in_signature.__name__
    assert "num" in {param.name for param in exc_info.value._error_kwargs["invalid_parameters"]}
