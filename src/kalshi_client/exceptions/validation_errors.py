from .api_errors import KalshiAPIError


class KalshiValidationError(KalshiAPIError):
    def __init__(self, message: str, field: str | None = None):
        super().__init__(message, status_code=400)
        self.field = field
