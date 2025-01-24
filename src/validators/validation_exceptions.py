from typing import Any

from ..exceptions import BaseException


class BaseValidationError(BaseException):
    error_msg: str
    _error_kwargs: dict[str, Any]

    def __init__(self, err_msg: str, **kwargs):
        super().__init__(err_msg)

        self.error_msg = err_msg
        self._error_kwargs = kwargs

    def __str__(self) -> str:
        _NEW_LINE = "\n"
        return (
            f"ERROR: "
            + self.error_msg
            + _NEW_LINE
            + _NEW_LINE.join(f"{kwarg_name}={str(kwarg_value)}" for kwarg_name, kwarg_value in self._error_kwargs.items())
        )

    def __repr__(self) -> str:
        return str(self)


class InvalidValidationFunctionSignature(BaseValidationError):
    pass
