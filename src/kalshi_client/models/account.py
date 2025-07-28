from datetime import datetime

from .base import KalshiBaseModel


class Balance(KalshiBaseModel):
    balance: int


class BalanceResponse(KalshiBaseModel):
    balance: int


class Order(KalshiBaseModel):
    order_id: str
    user_id: str
    ticker: str
    status: str
    action: str
    side: str
    type: str
    yes_price: int | None = None
    no_price: int | None = None
    count: int
    yes_filled_count: int
    no_filled_count: int
    created_time: datetime
    expiration_time: datetime | None = None
    updated_time: datetime | None = None
    time_in_force: str | None = None
    close_cancel_count: int | None = None


class OrderResponse(KalshiBaseModel):
    order: Order


class OrdersResponse(KalshiBaseModel):
    orders: list[Order]
    cursor: str | None = None


class Position(KalshiBaseModel):
    ticker: str
    event_ticker: str
    market_exposure: int
    realized_pnl: int
    total_traded: int
    resting_order_count: int
    fees_paid: int


class PositionsResponse(KalshiBaseModel):
    event_positions: list[Position]
    cursor: str | None = None
