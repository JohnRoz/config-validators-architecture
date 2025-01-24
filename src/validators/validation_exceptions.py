from ..exceptions import BaseException


class BaseValidationError(BaseException):
    pass


class InvalidValidationFunctionSignature(BaseValidationError):
    pass


class BaseSingleConfigValidationError(BaseValidationError):
    pass


class BaseCrossConfigValidationError(BaseValidationError):
    pass
