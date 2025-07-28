from datetime import datetime

from .base import KalshiBaseModel


class Trade(KalshiBaseModel):
    trade_id: str
    ticker: str
    taker_side: str
    yes_price: int
    no_price: int
    count: int
    created_time: datetime


class TradesResponse(KalshiBaseModel):
    trades: list[Trade]
    cursor: str | None = None
