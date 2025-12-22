from datetime import datetime
from dataclasses import dataclass
from sortedcontainers import SortedDict
from enum import Enum
import uuid
from collections import deque

class Side(Enum):
    BUY = "BUY"
    SELL = "SELL"

class OrderType(Enum):
    LIMIT = "LIMIT"
    MARKET = "MARKET"

@dataclass
class Order:
    id: str
    side: Side
    quantity: float
    price: float
    timestamp: datetime
    order_type: OrderType

class PriceLevel:
    def __init__(self):
        self.orders = deque()
        self.total_quantity = 0

    def add(self, order: Order):
        self.orders.append(order)
        self.total_quantity += order.quantity

    def remove(self, order: Order):
        self.orders.remove(order)
        self.total_quantity -= order.quantity

    def is_empty(self) -> bool:
        return len(self.orders) == 0

class OrderBook:
    def __init__(self):
        self.bids = SortedDict()
        self.asks = SortedDict()
        self.order_map = {}

    def submit_order(
            self,
            side: Side,
            quantity: float,
            order_type: OrderType,
            price: float) -> (str, list):
        order = Order(
            id=str(uuid.uuid4()),
            side=side,
            quantity=quantity,
            order_type=order_type,
            price=price,
            timestamp=datetime.utcnow()
        )

        trades = []

        if order_type == OrderType.MARKET:
            trades = self._match(order)
            print(f"Best Bid: {self._best_bid()}, Best Ask: {self._best_ask()}, Spread: {self._spread()}")
            print(f"Trades: {trades}")
            return order.id, trades

        if order_type == OrderType.LIMIT:
            trades = self._match(order)
            if order.quantity > 0:
                self._add_limit_order(order)

        print(f"Best Bid: {self._best_bid()}, Best Ask: {self._best_ask()}, Spread: {self._spread()}")
        print(f"Trades: {trades}")
        return order.id, trades

    def cancel_order(self, order_id: str) -> bool:
        if order_id not in self.order_map:
            return False

        order = self.order_map[order_id]
        book = self.bids if order.side == Side.BUY else self.asks
        level = book.get(order.price)

        if not level:
            return False

        level.remove(order)

        if level.is_empty():
            del book[order.price]

        del self.order_map[order_id]
        return True

    def _match(self, incoming: Order) -> list:
        trades = []

        book = self.asks if incoming.side == Side.BUY else self.bids

        while incoming.quantity > 0 and book:
            # Get best price
            best_price, level = (
                book.peekitem(0) if incoming.side == Side.BUY else book.peekitem(-1)
            )

            # Price condition for limit orders
            if incoming.order_type == OrderType.LIMIT:
                if incoming.side == Side.BUY and best_price > incoming.price:
                    break
                if incoming.side == Side.SELL and best_price < incoming.price:
                    break

            # Match at price level
            while level.orders and incoming.quantity > 0:
                resting = level.orders[0]
                traded_quantity = min(incoming.quantity, resting.quantity)

                incoming.quantity -= traded_quantity
                resting.quantity -= traded_quantity
                level.total_quantity -= traded_quantity

                trades.append(
                    {
                        "buy_id": incoming.id if incoming.side == Side.BUY else resting.id,
                        "sell_id": resting.id if incoming.side == Side.BUY else incoming.id,
                        "price": best_price,
                        "quantity": traded_quantity,
                        "timestamp": datetime.utcnow()
                    }
                )

                if resting.quantity == 0:
                    level.orders.popleft()
                    del self.order_map[resting.id]

            # Remove empty price level
            if level.is_empty():
                del book[best_price]

        return trades

    def _add_limit_order(self, order: Order):
        book = self.bids if order.side == Side.BUY else self.asks

        if order.price not in book:
            book[order.price] = PriceLevel()

        book[order.price].add(order)
        self.order_map[order.id] = order

    def _best_bid(self):
        return self.bids.peekitem(-1)[0] if self.bids else None

    def _best_ask(self):
        return self.asks.peekitem(0)[0] if self.asks else None

    def _spread(self):
        if not self.bids or not self.asks:
            return None

        return self._best_ask() - self._best_bid()

if __name__ == "__main__":
    print("--- Order Book Simulation ---")
    print("--------Test Case 1----------")
    # Test case 1: Simple Match
    ob1= OrderBook()
    ob1.submit_order(side=Side.BUY, quantity=100, order_type=OrderType.LIMIT, price=100.00)
    ob1.submit_order(side=Side.BUY, quantity=100, order_type=OrderType.LIMIT, price=100.00)
    ob1.submit_order(side=Side.BUY, quantity=200, order_type=OrderType.LIMIT, price=110.00)
    ob1.submit_order(side=Side.SELL, quantity=200, order_type=OrderType.LIMIT, price=110.00)
    print("-----------------------------")

    print("--------Test Case 2----------")
    # Test case 2: Partial Fill
    ob2 = OrderBook()
    ob2.submit_order(side=Side.SELL, quantity=150, order_type=OrderType.LIMIT, price=101.00)
    ob2.submit_order(side=Side.BUY, quantity=100, order_type=OrderType.LIMIT, price=101.00)
    print("----------------------------")

    print("--------Test Case 3----------")
    # Test case 3: 2 Partial Fills
    ob3 = OrderBook()
    ob3.submit_order(side=Side.SELL, quantity=150, order_type=OrderType.LIMIT, price=101.00)
    ob3.submit_order(side=Side.BUY, quantity=100, order_type=OrderType.LIMIT, price=101.00)
    ob3.submit_order(side=Side.BUY, quantity=60, order_type=OrderType.LIMIT, price=101.00)
    print("----------------------------")

    print("--------Test Case 4----------")
    # Test case 4: Market Order Matching
    ob4 = OrderBook()
    ob4.submit_order(side=Side.SELL, quantity=200, order_type=OrderType.LIMIT, price=102.00)
    ob4.submit_order(side=Side.BUY, quantity=250, order_type=OrderType.MARKET, price=0.00)
    print("----------------------------")

    print("--------Test Case 5----------")
    # Test case 5: Market Order do not rest and no trade occur
    ob5 = OrderBook()
    ob5.submit_order(side=Side.BUY, quantity=250, order_type=OrderType.MARKET, price=102.00)
    ob5.submit_order(side=Side.SELL, quantity=200, order_type=OrderType.LIMIT, price=102.00)
    print("----------------------------------")

    print("--------Test Case 6---------")
    # Test case 6: Limit Order rest and trade occur
    ob6 = OrderBook()
    ob6.submit_order(side=Side.BUY, quantity=250, order_type=OrderType.LIMIT, price=102.00)
    # ob5.cancel_order(order_id5)
    ob6.submit_order(side=Side.SELL, quantity=200, order_type=OrderType.LIMIT, price=102.00)
    print("----------------------------")

    print("--------Test Case 7---------")
    # Test case 6: Submit Limit Order, cancel it, no trade occur
    ob7 = OrderBook()
    order_id7, _ = ob7.submit_order(side=Side.BUY, quantity=250, order_type=OrderType.LIMIT, price=102.00)
    ob7.cancel_order(order_id7)
    ob7.submit_order(side=Side.SELL, quantity=200, order_type=OrderType.LIMIT, price=102.00)
    print("----------------------------")
