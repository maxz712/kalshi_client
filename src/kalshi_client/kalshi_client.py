import base64
import hashlib
import time

import httpx

from .configs.kalshi_configs import KalshiConfig
from .exceptions import (
    KalshiAPIError,
    KalshiAuthError,
    KalshiNotFoundError,
    KalshiRateLimitError,
    KalshiServerError,
    KalshiValidationError,
)
from .models import (
    Event,
    Market,
    ObjectList,
    Order,
    OrderBook,
    OrderCancelledResponse,
    OrderCreatedResponse,
    Position,
    Trade,
)

# HTTP Status Code Constants
HTTP_BAD_REQUEST = 400
HTTP_UNAUTHORIZED = 401
HTTP_NOT_FOUND = 404
HTTP_TOO_MANY_REQUESTS = 429
HTTP_INTERNAL_SERVER_ERROR = 500


class KalshiClient:
    def __init__(self, config: KalshiConfig | None = None):
        self.config = config or KalshiConfig()
        self.base_url = self.config.api_url
        self.client = httpx.Client(timeout=self.config.timeout)

    def _generate_signature(self, timestamp: str, method: str, path: str, body: str = "") -> str:
        msg_string = f"{timestamp}{method}{path}{body}"
        signature = base64.b64encode(
            hashlib.sha256(
                msg_string.encode("utf-8")
            ).digest()
        ).decode("utf-8")
        return signature

    def _get_headers(self, method: str, path: str, body: dict | None = None) -> dict[str, str]:
        timestamp = str(int(time.time() * 1000))
        body_str = "" if body is None else str(body)

        headers = {
            "Content-Type": "application/json",
            "KALSHI-API-KEY": self.config.api_key,
            "KALSHI-API-SIGNATURE": self._generate_signature(timestamp, method, path, body_str),
            "KALSHI-API-TIMESTAMP": timestamp,
        }
        return headers

    def _request(
        self,
        method: str,
        endpoint: str,
        params: dict | None = None,
        json: dict | None = None
    ) -> httpx.Response:
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(method.upper(), endpoint, json)

        response = self.client.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
        )

        if response.status_code == HTTP_BAD_REQUEST:
            raise KalshiValidationError(f"Validation error: {response.text}")
        elif response.status_code == HTTP_UNAUTHORIZED:
            raise KalshiAuthError("Authentication failed")
        elif response.status_code == HTTP_NOT_FOUND:
            raise KalshiNotFoundError("Resource not found")
        elif response.status_code == HTTP_TOO_MANY_REQUESTS:
            raise KalshiRateLimitError("Rate limit exceeded")
        elif response.status_code >= HTTP_INTERNAL_SERVER_ERROR:
            raise KalshiServerError(f"Server error: {response.status_code} - {response.text}")
        elif response.status_code >= HTTP_BAD_REQUEST:
            raise KalshiAPIError(
                f"API error: {response.text}",
                status_code=response.status_code,
                response_text=response.text
            )

        return response

    # Market Data Endpoints
    def get_events(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        status: str | None = None,
        series_ticker: str | None = None,
        with_nested_markets: bool | None = None,
    ) -> ObjectList[Event]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if status is not None:
            params["status"] = status
        if series_ticker is not None:
            params["series_ticker"] = series_ticker
        if with_nested_markets is not None:
            params["with_nested_markets"] = with_nested_markets

        response = self._request("GET", "/events", params=params)
        data = response.json()
        events = [Event(**event) for event in data.get("events", [])]
        return ObjectList(
            items=events,
            cursor=data.get("cursor"),
            has_more=len(events) == limit if limit else False
        )

    def get_event(self, event_ticker: str) -> Event:
        response = self._request("GET", f"/events/{event_ticker}")
        data = response.json()
        return Event(**data["event"])

    def get_markets(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        event_ticker: str | None = None,
        series_ticker: str | None = None,
        max_close_ts: int | None = None,
        min_close_ts: int | None = None,
        status: str | None = None,
        tickers: list[str] | None = None,
    ) -> ObjectList[Market]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if event_ticker is not None:
            params["event_ticker"] = event_ticker
        if series_ticker is not None:
            params["series_ticker"] = series_ticker
        if max_close_ts is not None:
            params["max_close_ts"] = max_close_ts
        if min_close_ts is not None:
            params["min_close_ts"] = min_close_ts
        if status is not None:
            params["status"] = status
        if tickers is not None:
            params["tickers"] = ",".join(tickers)

        response = self._request("GET", "/markets", params=params)
        data = response.json()
        markets = [Market(**market) for market in data.get("markets", [])]
        return ObjectList(
            items=markets,
            cursor=data.get("cursor"),
            has_more=len(markets) == limit if limit else False
        )

    def get_market(self, ticker: str) -> Market:
        response = self._request("GET", f"/markets/{ticker}")
        data = response.json()
        return Market(**data["market"])

    def get_market_order_book(self, ticker: str, depth: int | None = None) -> OrderBook:
        params = {}
        if depth is not None:
            params["depth"] = depth

        response = self._request("GET", f"/markets/{ticker}/orderbook", params=params)
        data = response.json()
        return OrderBook(**data["orderbook"])

    # Trading Data Endpoints
    def get_trades(
        self,
        ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ObjectList[Trade]:
        params = {}
        if ticker is not None:
            params["ticker"] = ticker
        if min_ts is not None:
            params["min_ts"] = min_ts
        if max_ts is not None:
            params["max_ts"] = max_ts
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor

        response = self._request("GET", "/markets/trades", params=params)
        data = response.json()
        trades = [Trade(**trade) for trade in data.get("trades", [])]
        return ObjectList(
            items=trades,
            cursor=data.get("cursor"),
            has_more=len(trades) == limit if limit else False
        )

    # Account Endpoints
    def get_balance(self) -> int:
        response = self._request("GET", "/portfolio/balance")
        data = response.json()
        return data["balance"]

    def get_orders(
        self,
        ticker: str | None = None,
        event_ticker: str | None = None,
        min_ts: int | None = None,
        max_ts: int | None = None,
        status: str | None = None,
        limit: int | None = None,
        cursor: str | None = None,
    ) -> ObjectList[Order]:
        params = {}
        if ticker is not None:
            params["ticker"] = ticker
        if event_ticker is not None:
            params["event_ticker"] = event_ticker
        if min_ts is not None:
            params["min_ts"] = min_ts
        if max_ts is not None:
            params["max_ts"] = max_ts
        if status is not None:
            params["status"] = status
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor

        response = self._request("GET", "/portfolio/orders", params=params)
        data = response.json()
        orders = [Order(**order) for order in data.get("orders", [])]
        return ObjectList(
            items=orders,
            cursor=data.get("cursor"),
            has_more=len(orders) == limit if limit else False
        )

    def create_order(
        self,
        ticker: str,
        action: str,
        side: str,
        type: str,
        count: int,
        yes_price: int | None = None,
        no_price: int | None = None,
        buy_max_cost: int | None = None,
        client_order_id: str | None = None,
        expiration_ts: int | None = None,
        order_group_id: str | None = None,
        post_only: bool | None = None,
        self_trade_prevention_type: str | None = None,
        sell_position_capped: bool | None = None,
        sell_position_floor: int | None = None,
        time_in_force: str | None = None,
    ) -> OrderCreatedResponse:
        """Create a new order.

        Args:
            ticker: The market ticker symbol
            action: Order action ("buy" or "sell")
            side: Order side ("yes" or "no")
            type: Order type ("market" or "limit")
            count: Number of contracts
            yes_price: Price for yes side in cents (required for limit orders on yes side)
            no_price: Price for no side in cents (required for limit orders on no side)
            buy_max_cost: Maximum cost for buy orders in cents
            client_order_id: Client-specified order ID
            expiration_ts: Order expiration timestamp
            order_group_id: Group ID for related orders
            post_only: Whether order should only add liquidity
            self_trade_prevention_type: Type of self-trade prevention
            sell_position_capped: Whether sell is capped by position
            sell_position_floor: Floor for sell position
            time_in_force: Time in force ("gtc", "ioc", "fok")

        Returns:
            The created Order object
        """
        data = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "type": type,
            "count": count,
        }

        # Add optional parameters
        if yes_price is not None:
            data["yes_price"] = yes_price
        if no_price is not None:
            data["no_price"] = no_price
        if buy_max_cost is not None:
            data["buy_max_cost"] = buy_max_cost
        if client_order_id is not None:
            data["client_order_id"] = client_order_id
        if expiration_ts is not None:
            data["expiration_ts"] = expiration_ts
        if order_group_id is not None:
            data["order_group_id"] = order_group_id
        if post_only is not None:
            data["post_only"] = post_only
        if self_trade_prevention_type is not None:
            data["self_trade_prevention_type"] = self_trade_prevention_type
        if sell_position_capped is not None:
            data["sell_position_capped"] = sell_position_capped
        if sell_position_floor is not None:
            data["sell_position_floor"] = sell_position_floor
        if time_in_force is not None:
            data["time_in_force"] = time_in_force

        response = self._request("POST", "/portfolio/orders", json=data)
        order_data = response.json()
        order = Order(**order_data["order"])
        return OrderCreatedResponse(
            success=True,
            message="Order created successfully",
            status_code=response.status_code,
            order_id=order.order_id if hasattr(order, 'order_id') else None
        )

    def cancel_order(self, order_id: str) -> OrderCancelledResponse:
        response = self._request("DELETE", f"/portfolio/orders/{order_id}")
        return OrderCancelledResponse(
            success=True,
            message=f"Order {order_id} cancelled successfully",
            status_code=response.status_code,
            order_id=order_id
        )

    def get_positions(
        self,
        limit: int | None = None,
        cursor: str | None = None,
        settlement_status: str | None = None,
        ticker: str | None = None,
        event_ticker: str | None = None,
    ) -> ObjectList[Position]:
        params = {}
        if limit is not None:
            params["limit"] = limit
        if cursor is not None:
            params["cursor"] = cursor
        if settlement_status is not None:
            params["settlement_status"] = settlement_status
        if ticker is not None:
            params["ticker"] = ticker
        if event_ticker is not None:
            params["event_ticker"] = event_ticker

        response = self._request("GET", "/portfolio/positions", params=params)
        data = response.json()
        positions = [Position(**position) for position in data.get("event_positions", [])]
        return ObjectList(
            items=positions,
            cursor=data.get("cursor"),
            has_more=len(positions) == limit if limit else False
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()
