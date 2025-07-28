from pydantic import Field
from pydantic_settings import BaseSettings


class KalshiConfig(BaseSettings):
    api_key: str = Field(..., description="Kalshi API key")
    api_secret: str = Field(..., description="Kalshi API secret")
    base_url: str = Field(
        default="https://trading-api.kalshi.com/trade-api/v2",
        description="Kalshi API base URL"
    )
    demo_mode: bool = Field(
        default=False,
        description="Use demo API endpoint"
    )
    timeout: float = Field(
        default=30.0,
        description="Request timeout in seconds"
    )

    model_config = {
        "env_prefix": "KALSHI_",
        "env_file": ".env",
        "env_file_encoding": "utf-8",
    }

    @property
    def api_url(self) -> str:
        if self.demo_mode:
            return "https://demo-api.kalshi.com/trade-api/v2"
        return self.base_url
