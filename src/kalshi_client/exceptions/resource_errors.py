from .api_errors import KalshiAPIError


class KalshiNotFoundError(KalshiAPIError):
    def __init__(self, message: str = "Resource not found"):
        super().__init__(message, status_code=404)
