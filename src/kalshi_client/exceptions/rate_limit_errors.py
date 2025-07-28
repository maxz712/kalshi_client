from .api_errors import KalshiAPIError


class KalshiRateLimitError(KalshiAPIError):
    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(message, status_code=429)
