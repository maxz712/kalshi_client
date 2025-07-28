from .base import KalshiResponse


class OrderCreatedResponse(KalshiResponse):
    order_id: str | None = None


class OrderCancelledResponse(KalshiResponse):
    order_id: str | None = None


class OperationResponse(KalshiResponse):
    operation_id: str | None = None
    affected_count: int | None = None
