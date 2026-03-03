"""
Alpaca Trading Client
Paper trading + live trading via Alpaca's official alpaca-py SDK.

Implements the unified broker interface for the trading agent.
All responses are normalized to a common dict format shared
across broker implementations.

NOTE: Full implementation details are proprietary.
This file shows the interface and data normalization architecture.
"""
import logging
from typing import Optional
from config import TradingConfig

logger = logging.getLogger(__name__)


class AlpacaClient:
    """
    Alpaca Trading Client.
    Works with both paper and live accounts.

    Paper: https://paper-api.alpaca.markets
    Live:  https://api.alpaca.markets
    """

    def __init__(self, config: TradingConfig):
        self.config = config
        is_paper = config.ALPACA_ENV == "paper"
        # Initializes TradingClient and StockHistoricalDataClient
        # from alpaca-py SDK with appropriate environment routing.
        logger.info(
            f"Alpaca client initialized ({'PAPER' if is_paper else 'LIVE'} mode)"
        )

    # === ACCOUNT ===========================================================

    def get_account_cash(self) -> dict:
        """Get account cash balance info.

        Returns normalized format:
            {
                "free": float,        # Available cash
                "total": float,       # Total portfolio value
                "invested": float,    # Value in positions
                "result": float,      # Day P&L
                "buying_power": float  # Margin-adjusted buying power
            }
        """
        raise NotImplementedError

    def get_account_info(self) -> dict:
        """Get account metadata (ID, currency, status, PDT info)."""
        raise NotImplementedError

    # === PORTFOLIO =========================================================

    def get_positions(self) -> list[dict]:
        """Get all open positions in normalized format.

        Each position dict:
            {
                "ticker": str,
                "quantity": float,
                "averagePrice": float,
                "currentPrice": float,
                "marketValue": float,
                "result": float,       # Unrealized P&L ($)
                "resultPct": float,    # Unrealized P&L (%)
                "side": str
            }
        """
        raise NotImplementedError

    def get_position(self, symbol: str) -> Optional[dict]:
        """Get a specific position by symbol."""
        raise NotImplementedError

    # === ORDERS ============================================================

    def place_market_order(self, symbol: str, quantity: float) -> dict:
        """Place a market order. quantity > 0 = BUY, < 0 = SELL."""
        raise NotImplementedError

    def place_limit_order(
        self, symbol: str, quantity: float, limit_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a limit order with Day or GTC validity."""
        raise NotImplementedError

    def place_stop_order(
        self, symbol: str, quantity: float, stop_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a stop order."""
        raise NotImplementedError

    def place_stop_limit_order(
        self, symbol: str, quantity: float,
        stop_price: float, limit_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a stop-limit order."""
        raise NotImplementedError

    def cancel_order(self, order_id: str) -> dict:
        """Cancel a pending order by ID."""
        raise NotImplementedError

    def get_pending_orders(self) -> list[dict]:
        """Get all open/pending orders in normalized format."""
        raise NotImplementedError

    # === MARKET DATA =======================================================

    def get_latest_quote(self, symbol: str) -> Optional[dict]:
        """Get the latest bid/ask quote for a symbol."""
        raise NotImplementedError

    # === HISTORY ===========================================================

    def get_order_history(self, limit: int = 50) -> dict:
        """Get completed order history."""
        raise NotImplementedError
