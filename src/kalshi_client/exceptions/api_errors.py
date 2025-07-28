class KalshiAPIError(Exception):
    def __init__(self, message: str, status_code: int | None = None, response_text: str | None = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_text = response_text

    def __str__(self) -> str:
        if self.status_code:
            return f"KalshiAPIError({self.status_code}): {self.message}"
        return f"KalshiAPIError: {self.message}"
