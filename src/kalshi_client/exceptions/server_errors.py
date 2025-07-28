from .api_errors import KalshiAPIError


class KalshiServerError(KalshiAPIError):
    def __init__(self, message: str = "Internal server error"):
        super().__init__(message, status_code=500)
