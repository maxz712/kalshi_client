from .api_errors import KalshiAPIError


class KalshiAuthError(KalshiAPIError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)
