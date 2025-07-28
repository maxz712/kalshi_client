from datetime import datetime

from kalshi_client.models import (
    Balance,
    Event,
    EventResponse,
    EventsResponse,
    Market,
    Order,
    OrderBook,
    OrderBookLevel,
    Position,
    Trade,
    TradesResponse,
)


class TestEventModels:
    def test_event_creation(self):
        event = Event(
            event_ticker="ECON-2024",
            title="Economic Indicators",
            mutually_exclusive=True,
            category="Economics",
            status="open",
            close_time=datetime.now(),
            open_time=datetime.now(),
        )
        assert event.event_ticker == "ECON-2024"
        assert event.title == "Economic Indicators"
        assert event.mutually_exclusive is True

    def test_event_response(self):
        event = Event(
            event_ticker="ECON-2024",
            title="Economic Indicators",
            mutually_exclusive=True,
            category="Economics",
            status="open",
            close_time=datetime.now(),
            open_time=datetime.now(),
        )
        response = EventResponse(event=event)
        assert response.event == event

    def test_events_response_with_cursor(self):
        events = [
            Event(
                event_ticker=f"ECON-{i}",
                title=f"Event {i}",
                mutually_exclusive=True,
                category="Economics",
                status="open",
                close_time=datetime.now(),
                open_time=datetime.now(),
            )
            for i in range(3)
        ]
        response = EventsResponse(events=events, cursor="next_page_token")
        assert len(response.events) == 3
        assert response.cursor == "next_page_token"


class TestMarketModels:
    def test_market_creation(self):
        market = Market(
            ticker="ECON-GDP-24",
            event_ticker="ECON-2024",
            market_type="binary",
            title="GDP Growth > 2%",
            subtitle="Will GDP growth exceed 2% in Q4 2024?",
            open_time=datetime.now(),
            close_time=datetime.now(),
            status="open",
            can_close_early=False,
            category="Economics",
            risk_limit_cents=25000,
            strike_type="binary",
            volume=1000,
            volume_24h=5000,
            liquidity=10000,
            open_interest=2000,
        )
        assert market.ticker == "ECON-GDP-24"
        assert market.volume == 1000

    def test_order_book(self):
        yes_levels = [
            OrderBookLevel(price=60, quantity=100),
            OrderBookLevel(price=59, quantity=200),
        ]
        no_levels = [
            OrderBookLevel(price=41, quantity=150),
            OrderBookLevel(price=42, quantity=250),
        ]
        order_book = OrderBook(yes=yes_levels, no=no_levels)
        assert len(order_book.yes) == 2
        assert len(order_book.no) == 2
        assert order_book.yes[0].price == 60


class TestTradeModels:
    def test_trade_creation(self):
        trade = Trade(
            trade_id="trade123",
            ticker="ECON-GDP-24",
            taker_side="yes",
            yes_price=60,
            no_price=40,
            count=10,
            created_time=datetime.now(),
        )
        assert trade.trade_id == "trade123"
        assert trade.yes_price == 60
        assert trade.no_price == 40

    def test_trades_response(self):
        trades = [
            Trade(
                trade_id=f"trade{i}",
                ticker="ECON-GDP-24",
                taker_side="yes",
                yes_price=60 + i,
                no_price=40 - i,
                count=10,
                created_time=datetime.now(),
            )
            for i in range(3)
        ]
        response = TradesResponse(trades=trades)
        assert len(response.trades) == 3


class TestAccountModels:
    def test_balance(self):
        balance = Balance(balance=100000)
        assert balance.balance == 100000

    def test_order_creation(self):
        order = Order(
            order_id="order123",
            user_id="user456",
            ticker="ECON-GDP-24",
            status="open",
            action="buy",
            side="yes",
            type="limit",
            yes_price=60,
            count=10,
            yes_filled_count=0,
            no_filled_count=0,
            created_time=datetime.now(),
        )
        assert order.order_id == "order123"
        assert order.yes_price == 60

    def test_position(self):
        position = Position(
            ticker="ECON-GDP-24",
            event_ticker="ECON-2024",
            market_exposure=1000,
            realized_pnl=-50,
            total_traded=5000,
            resting_order_count=2,
            fees_paid=25,
        )
        assert position.market_exposure == 1000
        assert position.realized_pnl == -50
