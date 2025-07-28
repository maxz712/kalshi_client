from unittest.mock import Mock, patch

import httpx
import pytest

from kalshi_client import KalshiAuthError, KalshiClient, KalshiConfig
from kalshi_client.exceptions import (
    KalshiNotFoundError,
    KalshiRateLimitError,
    KalshiServerError,
    KalshiValidationError,
)
from kalshi_client.models import (
    Event,
    Market,
    ObjectList,
    OrderBook,
    OrderCancelledResponse,
    OrderCreatedResponse,
)


@pytest.fixture
def mock_config():
    return KalshiConfig(
        api_key="test_api_key",
        api_secret="test_api_secret",
        base_url="https://api.kalshi.com",
        timeout=30.0,
    )


@pytest.fixture
def client(mock_config):
    return KalshiClient(config=mock_config)


class TestKalshiClient:
    def test_client_initialization(self, mock_config):
        client = KalshiClient(config=mock_config)
        assert client.config == mock_config
        assert client.base_url == "https://api.kalshi.com"
        assert isinstance(client.client, httpx.Client)

    def test_generate_signature(self, client):
        timestamp = "1234567890"
        method = "GET"
        path = "/events"
        signature = client._generate_signature(timestamp, method, path)
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_get_headers(self, client):
        headers = client._get_headers("GET", "/events")
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"
        assert "KALSHI-API-KEY" in headers
        assert headers["KALSHI-API-KEY"] == "test_api_key"
        assert "KALSHI-API-SIGNATURE" in headers
        assert "KALSHI-API-TIMESTAMP" in headers

    @patch("httpx.Client.request")
    def test_get_events(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [
                {
                    "event_ticker": "ECON-2024",
                    "title": "Economic Indicators",
                    "mutually_exclusive": True,
                    "category": "Economics",
                    "status": "open",
                    "close_time": "2024-12-31T23:59:59Z",
                    "open_time": "2024-01-01T00:00:00Z",
                }
            ]
        }
        mock_request.return_value = mock_response

        events = client.get_events(limit=10)

        assert isinstance(events, ObjectList)
        assert len(events) == 1
        assert events[0].event_ticker == "ECON-2024"
        assert events.cursor is None
        assert events.has_more is False

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["params"]["limit"] == 10

    @patch("httpx.Client.request")
    def test_get_event(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "event": {
                "event_ticker": "ECON-2024",
                "title": "Economic Indicators",
                "mutually_exclusive": True,
                "category": "Economics",
                "status": "open",
                "close_time": "2024-12-31T23:59:59Z",
                "open_time": "2024-01-01T00:00:00Z",
            }
        }
        mock_request.return_value = mock_response

        event = client.get_event("ECON-2024")

        assert isinstance(event, Event)
        assert event.event_ticker == "ECON-2024"

    @patch("httpx.Client.request")
    def test_get_market_order_book(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orderbook": {
                "yes": [
                    {"price": 60, "quantity": 100},
                    {"price": 59, "quantity": 200},
                ],
                "no": [
                    {"price": 41, "quantity": 150},
                    {"price": 42, "quantity": 250},
                ],
            }
        }
        mock_request.return_value = mock_response

        orderbook = client.get_market_order_book("ECON-GDP-24", depth=5)

        assert isinstance(orderbook, OrderBook)
        assert len(orderbook.yes) == 2
        assert orderbook.yes[0].price == 60

    @patch("httpx.Client.request")
    def test_get_balance(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"balance": 100000}
        mock_request.return_value = mock_response

        balance = client.get_balance()

        assert isinstance(balance, int)
        assert balance == 100000

    @patch("httpx.Client.request")
    def test_cancel_order(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        response = client.cancel_order("order123")

        assert isinstance(response, OrderCancelledResponse)
        assert response.success is True
        assert response.order_id == "order123"
        assert "cancelled successfully" in response.message
        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "DELETE"
        assert "orders/order123" in call_args.kwargs["url"]

    @patch("httpx.Client.request")
    def test_auth_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        with pytest.raises(KalshiAuthError, match="Authentication failed"):
            client.get_events()

    @patch("httpx.Client.request")
    def test_api_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_request.return_value = mock_response

        with pytest.raises(KalshiValidationError, match="Validation error: Bad Request"):
            client.get_events()

    @patch("httpx.Client.request")
    def test_get_markets(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "markets": [
                {
                    "ticker": "ECON-GDP-24",
                    "event_ticker": "ECON-2024",
                    "market_type": "binary",
                    "title": "GDP Growth",
                    "subtitle": "Will GDP grow?",
                    "open_time": "2024-01-01T00:00:00Z",
                    "close_time": "2024-12-31T23:59:59Z",
                    "status": "open",
                    "can_close_early": False,
                    "category": "Economics",
                    "risk_limit_cents": 100000,
                    "strike_type": "yesno",
                    "volume": 1000,
                    "volume_24h": 500,
                    "liquidity": 10000,
                    "open_interest": 5000,
                }
            ]
        }
        mock_request.return_value = mock_response

        markets = client.get_markets(limit=10)

        assert isinstance(markets, ObjectList)
        assert len(markets) == 1
        assert markets[0].ticker == "ECON-GDP-24"
        assert markets.cursor is None
        assert markets.has_more is False

    @patch("httpx.Client.request")
    def test_get_market(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "market": {
                "ticker": "ECON-GDP-24",
                "event_ticker": "ECON-2024",
                "market_type": "binary",
                "title": "GDP Growth",
                "subtitle": "Will GDP grow?",
                "open_time": "2024-01-01T00:00:00Z",
                "close_time": "2024-12-31T23:59:59Z",
                "status": "open",
                "can_close_early": False,
                "category": "Economics",
                "risk_limit_cents": 100000,
                "strike_type": "yesno",
                "volume": 1000,
                "volume_24h": 500,
                "liquidity": 10000,
                "open_interest": 5000,
            }
        }
        mock_request.return_value = mock_response

        market = client.get_market("ECON-GDP-24")

        assert isinstance(market, Market)
        assert market.ticker == "ECON-GDP-24"

    @patch("httpx.Client.request")
    def test_get_trades(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "trades": [
                {
                    "trade_id": "trade123",
                    "ticker": "ECON-GDP-24",
                    "taker_side": "yes",
                    "yes_price": 60,
                    "no_price": 40,
                    "count": 10,
                    "created_time": "2024-01-01T00:00:00Z",
                }
            ]
        }
        mock_request.return_value = mock_response

        trades = client.get_trades(ticker="ECON-GDP-24")

        assert isinstance(trades, ObjectList)
        assert len(trades) == 1
        assert trades[0].trade_id == "trade123"
        assert trades.cursor is None
        assert trades.has_more is False

    @patch("httpx.Client.request")
    def test_get_orders(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "orders": [
                {
                    "order_id": "order123",
                    "user_id": "user456",
                    "ticker": "ECON-GDP-24",
                    "status": "open",
                    "action": "buy",
                    "side": "yes",
                    "type": "limit",
                    "yes_price": 60,
                    "count": 10,
                    "yes_filled_count": 0,
                    "no_filled_count": 0,
                    "created_time": "2024-01-01T00:00:00Z",
                }
            ]
        }
        mock_request.return_value = mock_response

        orders = client.get_orders(ticker="ECON-GDP-24")

        assert isinstance(orders, ObjectList)
        assert len(orders) == 1
        assert orders[0].order_id == "order123"
        assert orders.cursor is None
        assert orders.has_more is False

    @patch("httpx.Client.request")
    def test_get_positions(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "event_positions": [
                {
                    "ticker": "ECON-GDP-24",
                    "event_ticker": "ECON-2024",
                    "market_exposure": 1000,
                    "realized_pnl": 100,
                    "total_traded": 5000,
                    "resting_order_count": 2,
                    "fees_paid": 50,
                }
            ]
        }
        mock_request.return_value = mock_response

        positions = client.get_positions(ticker="ECON-GDP-24")

        assert isinstance(positions, ObjectList)
        assert len(positions) == 1
        assert positions[0].ticker == "ECON-GDP-24"
        assert positions.cursor is None
        assert positions.has_more is False

    @patch("httpx.Client.request")
    def test_create_order_limit_buy_yes(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "order": {
                "order_id": "order123",
                "user_id": "user456",
                "ticker": "ECON-GDP-24",
                "status": "open",
                "action": "buy",
                "side": "yes",
                "type": "limit",
                "yes_price": 60,
                "no_price": None,
                "count": 10,
                "yes_filled_count": 0,
                "no_filled_count": 0,
                "created_time": "2024-01-01T00:00:00Z",
                "client_order_id": "client123",
                "order_group_id": None,
                "self_trade_prevention_type": None,
            }
        }
        mock_request.return_value = mock_response

        response = client.create_order(
            ticker="ECON-GDP-24",
            action="buy",
            side="yes",
            type="limit",
            count=10,
            yes_price=60,
            client_order_id="client123"
        )

        assert isinstance(response, OrderCreatedResponse)
        assert response.success is True
        assert "created successfully" in response.message
        assert response.status_code == 201

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        assert call_args.kwargs["method"] == "POST"
        assert "portfolio/orders" in call_args.kwargs["url"]
        assert call_args.kwargs["json"]["ticker"] == "ECON-GDP-24"
        assert call_args.kwargs["json"]["action"] == "buy"
        assert call_args.kwargs["json"]["side"] == "yes"
        assert call_args.kwargs["json"]["yes_price"] == 60

    @patch("httpx.Client.request")
    def test_create_order_market_sell_no(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "order": {
                "order_id": "order456",
                "user_id": "user456",
                "ticker": "ECON-GDP-24",
                "status": "filled",
                "action": "sell",
                "side": "no",
                "type": "market",
                "yes_price": None,
                "no_price": None,
                "count": 5,
                "yes_filled_count": 0,
                "no_filled_count": 5,
                "created_time": "2024-01-01T00:00:00Z",
                "client_order_id": None,
                "order_group_id": None,
                "self_trade_prevention_type": None,
            }
        }
        mock_request.return_value = mock_response

        response = client.create_order(
            ticker="ECON-GDP-24",
            action="sell",
            side="no",
            type="market",
            count=5
        )

        assert isinstance(response, OrderCreatedResponse)
        assert response.success is True
        assert "created successfully" in response.message
        assert response.status_code == 201

    @patch("httpx.Client.request")
    def test_create_order_with_all_optional_params(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {
            "order": {
                "order_id": "order789",
                "user_id": "user456",
                "ticker": "ECON-GDP-24",
                "status": "open",
                "action": "buy",
                "side": "yes",
                "type": "limit",
                "yes_price": 65,
                "no_price": None,
                "count": 20,
                "yes_filled_count": 0,
                "no_filled_count": 0,
                "created_time": "2024-01-01T00:00:00Z",
                "expiration_time": "2024-01-02T00:00:00Z",
                "client_order_id": "client789",
                "order_group_id": "group123",
                "self_trade_prevention_type": "cancel_resting",
            }
        }
        mock_request.return_value = mock_response

        response = client.create_order(
            ticker="ECON-GDP-24",
            action="buy",
            side="yes",
            type="limit",
            count=20,
            yes_price=65,
            buy_max_cost=1300,
            client_order_id="client789",
            expiration_ts=1704153600,
            order_group_id="group123",
            post_only=True,
            self_trade_prevention_type="cancel_resting",
            time_in_force="gtc"
        )

        assert isinstance(response, OrderCreatedResponse)
        assert response.success is True
        assert "created successfully" in response.message
        assert response.status_code == 201

        mock_request.assert_called_once()
        call_args = mock_request.call_args
        json_data = call_args.kwargs["json"]
        assert json_data["buy_max_cost"] == 1300
        assert json_data["expiration_ts"] == 1704153600
        assert json_data["post_only"] is True
        assert json_data["time_in_force"] == "gtc"

    def test_context_manager(self, mock_config):
        with KalshiClient(config=mock_config) as client:
            assert isinstance(client, KalshiClient)
            assert isinstance(client.client, httpx.Client)

    @patch("httpx.Client.request")
    def test_objectlist_functionality(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "events": [
                {
                    "event_ticker": "ECON-2024",
                    "title": "Event 1",
                    "category": "Economics",
                    "status": "open",
                    "mutually_exclusive": True,
                    "close_time": "2024-12-31T23:59:59Z",
                    "open_time": "2024-01-01T00:00:00Z"
                },
                {
                    "event_ticker": "TECH-2024",
                    "title": "Event 2",
                    "category": "Technology",
                    "status": "open",
                    "mutually_exclusive": False,
                    "close_time": "2024-12-31T23:59:59Z",
                    "open_time": "2024-01-01T00:00:00Z"
                }
            ],
            "cursor": "next_page_token"
        }
        mock_request.return_value = mock_response

        events = client.get_events(limit=2)

        # Test ObjectList functionality
        assert len(events) == 2
        assert bool(events) is True
        assert events.cursor == "next_page_token"
        assert events.has_more is True

        # Test iteration
        event_tickers = [event.event_ticker for event in events]
        assert event_tickers == ["ECON-2024", "TECH-2024"]

        # Test indexing
        assert events[0].event_ticker == "ECON-2024"
        assert events[1].event_ticker == "TECH-2024"

        # Test conversion to list
        events_list = events.to_list()
        assert isinstance(events_list, list)
        assert len(events_list) == 2

    @patch("httpx.Client.request")
    def test_validation_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Invalid parameter"
        mock_request.return_value = mock_response

        with pytest.raises(KalshiValidationError, match="Validation error: Invalid parameter"):
            client.get_events()

    @patch("httpx.Client.request")
    def test_not_found_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request.return_value = mock_response

        with pytest.raises(KalshiNotFoundError, match="Resource not found"):
            client.get_event("NONEXISTENT")

    @patch("httpx.Client.request")
    def test_rate_limit_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.text = "Rate limit exceeded"
        mock_request.return_value = mock_response

        with pytest.raises(KalshiRateLimitError, match="Rate limit exceeded"):
            client.get_events()

    @patch("httpx.Client.request")
    def test_server_error(self, mock_request, client):
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal server error"
        mock_request.return_value = mock_response

        with pytest.raises(KalshiServerError, match="Server error: 500 - Internal server error"):
            client.get_events()
