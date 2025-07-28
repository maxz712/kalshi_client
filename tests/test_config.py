import pytest

from kalshi_client.configs.kalshi_configs import KalshiConfig


class TestKalshiConfig:
    def test_config_with_env_vars(self, monkeypatch):
        monkeypatch.setenv("KALSHI_API_KEY", "test_key")
        monkeypatch.setenv("KALSHI_API_SECRET", "test_secret")

        config = KalshiConfig()
        assert config.api_key == "test_key"
        assert config.api_secret == "test_secret"
        assert config.base_url == "https://trading-api.kalshi.com/trade-api/v2"
        assert config.demo_mode is False
        assert config.timeout == 30.0

    def test_config_with_demo_mode(self, monkeypatch):
        monkeypatch.setenv("KALSHI_API_KEY", "test_key")
        monkeypatch.setenv("KALSHI_API_SECRET", "test_secret")
        monkeypatch.setenv("KALSHI_DEMO_MODE", "true")

        config = KalshiConfig()
        assert config.demo_mode is True
        assert config.api_url == "https://demo-api.kalshi.com/trade-api/v2"

    def test_config_with_custom_values(self):
        config = KalshiConfig(
            api_key="custom_key",
            api_secret="custom_secret",
            base_url="https://custom.kalshi.com",
            timeout=60.0,
        )
        assert config.api_key == "custom_key"
        assert config.api_secret == "custom_secret"
        assert config.base_url == "https://custom.kalshi.com"
        assert config.timeout == 60.0
        assert config.api_url == "https://custom.kalshi.com"

    def test_config_missing_required_fields(self):
        with pytest.raises(Exception):
            config = KalshiConfig()
