
from kalshi_client.models.base import KalshiResponse
from kalshi_client.models.response import (
    OperationResponse,
    OrderCancelledResponse,
    OrderCreatedResponse,
)


class TestKalshiResponse:
    def test_default_values(self):
        response = KalshiResponse()

        assert response.success is True
        assert response.message is None
        assert response.status_code is None
        assert response.request_id is None

    def test_custom_values(self):
        response = KalshiResponse(
            success=False,
            message="Error occurred",
            status_code=400,
            request_id="req123"
        )

        assert response.success is False
        assert response.message == "Error occurred"
        assert response.status_code == 400
        assert response.request_id == "req123"


class TestOrderCreatedResponse:
    def test_initialization(self):
        response = OrderCreatedResponse(
            success=True,
            message="Order created",
            status_code=201,
            order_id="order123"
        )

        assert response.success is True
        assert response.message == "Order created"
        assert response.status_code == 201
        assert response.order_id == "order123"

    def test_default_order_id(self):
        response = OrderCreatedResponse()
        assert response.order_id is None


class TestOrderCancelledResponse:
    def test_initialization(self):
        response = OrderCancelledResponse(
            success=True,
            message="Order cancelled",
            status_code=200,
            order_id="order456"
        )

        assert response.success is True
        assert response.message == "Order cancelled"
        assert response.status_code == 200
        assert response.order_id == "order456"

    def test_default_order_id(self):
        response = OrderCancelledResponse()
        assert response.order_id is None


class TestOperationResponse:
    def test_initialization(self):
        response = OperationResponse(
            success=True,
            message="Operation completed",
            status_code=200,
            operation_id="op789",
            affected_count=5
        )

        assert response.success is True
        assert response.message == "Operation completed"
        assert response.status_code == 200
        assert response.operation_id == "op789"
        assert response.affected_count == 5

    def test_default_values(self):
        response = OperationResponse()
        assert response.operation_id is None
        assert response.affected_count is None
