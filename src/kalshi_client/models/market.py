from datetime import datetime
from decimal import Decimal

from .base import KalshiBaseModel


class Event(KalshiBaseModel):
    event_ticker: str
    series_ticker: str | None = None
    sub_title: str | None = None
    title: str
    mutually_exclusive: bool
    category: str
    status: str
    close_time: datetime
    open_time: datetime


class EventResponse(KalshiBaseModel):
    event: Event


class EventsResponse(KalshiBaseModel):
    events: list[Event]
    cursor: str | None = None


class Market(KalshiBaseModel):
    ticker: str
    event_ticker: str
    market_type: str
    title: str
    subtitle: str
    yes_sub_title: str | None = None
    no_sub_title: str | None = None
    open_time: datetime
    close_time: datetime
    expected_expiration_time: datetime | None = None
    expiration_time: datetime | None = None
    settlement_time: datetime | None = None
    status: str
    response_price_cents: int | None = None
    can_close_early: bool
    expiration_value: str | None = None
    category: str
    risk_limit_cents: int
    strike_type: str
    floor_strike: Decimal | None = None
    cap_strike: Decimal | None = None
    last_price: int | None = None
    volume: int
    volume_24h: int
    liquidity: int
    open_interest: int
    result: str | None = None
    previous_yes_price: int | None = None
    previous_price: int | None = None
    yes_bid: int | None = None
    yes_ask: int | None = None
    no_bid: int | None = None
    no_ask: int | None = None


class MarketResponse(KalshiBaseModel):
    market: Market


class MarketsResponse(KalshiBaseModel):
    markets: list[Market]
    cursor: str | None = None


class OrderBookLevel(KalshiBaseModel):
    price: int
    quantity: int


class OrderBook(KalshiBaseModel):
    yes: list[OrderBookLevel]
    no: list[OrderBookLevel]


class OrderBookResponse(KalshiBaseModel):
    orderbook: OrderBook
