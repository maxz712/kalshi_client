from kalshi_client import KalshiClient, KalshiConfig


def main():
    # Option 1: Load config from environment variables
    # Set KALSHI_API_KEY and KALSHI_API_SECRET in your environment or .env file
    config = KalshiConfig()

    # Option 2: Manually provide config
    # config = KalshiConfig(
    #     api_key="your_api_key",
    #     api_secret="your_api_secret",
    #     demo_mode=True  # Use demo API
    # )

    # Create client
    with KalshiClient(config=config) as client:
        # Get events
        print("Fetching events...")
        events = client.get_events(limit=5)
        for event in events:
            print(f"Event: {event.event_ticker} - {event.title}")

        # Get specific event
        if events:
            event_ticker = events[0].event_ticker
            print(f"\nFetching event details for {event_ticker}...")
            event = client.get_event(event_ticker)
            print(f"Event: {event.title}")
            print(f"Category: {event.category}")
            print(f"Status: {event.status}")

        # Get markets
        print("\nFetching markets...")
        markets = client.get_markets(limit=5)
        for market in markets:
            print(f"Market: {market.ticker} - {market.title}")

        # Get market order book
        if markets:
            ticker = markets[0].ticker
            print(f"\nFetching order book for {ticker}...")
            orderbook = client.get_market_order_book(ticker, depth=3)
            print("Yes side:")
            for level in orderbook.yes:
                print(f"  Price: {level.price}, Quantity: {level.quantity}")
            print("No side:")
            for level in orderbook.no:
                print(f"  Price: {level.price}, Quantity: {level.quantity}")

        # Get recent trades
        print("\nFetching recent trades...")
        trades = client.get_trades(limit=5)
        for trade in trades:
            print(f"Trade: {trade.ticker} - Yes: {trade.yes_price}, No: {trade.no_price}")

        # Get account balance
        print("\nFetching account balance...")
        balance = client.get_balance()
        print(f"Balance: ${balance / 100:.2f}")

        # Get positions
        print("\nFetching positions...")
        positions = client.get_positions()
        for position in positions:
            print(f"Position: {position.ticker}")
            print(f"  Exposure: ${position.market_exposure / 100:.2f}")
            print(f"  P&L: ${position.realized_pnl / 100:.2f}")

        # Get orders
        print("\nFetching orders...")
        orders = client.get_orders(status="open")
        for order in orders:
            print(f"Order: {order.order_id} - {order.ticker}")
            print(f"  Side: {order.side}, Price: {order.yes_price or order.no_price}")


if __name__ == "__main__":
    main()
