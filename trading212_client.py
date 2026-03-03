"""
Trading212 API Client
Handles all communication with the Trading212 Public API (v0).

Implements the same unified broker interface as AlpacaClient,
enabling seamless broker switching via config.

NOTE: Full implementation including auth, rate limiting, and
API communication details are proprietary.
"""
import logging
from typing import Optional
from config import TradingConfig

logger = logging.getLogger(__name__)


class Trading212Client:
    """
    Client for Trading212 Public API v0.

    Supports demo and live environments.
    Uses Basic Auth with API key + secret.
    Includes built-in rate limit tracking.
    """

    def __init__(self, config: TradingConfig):
        self.config = config
        self.base_url = config.T212_BASE_URL
        # Sets up Basic Auth headers and rate limit tracker.

    # === ACCOUNT ===========================================================

    def get_account_cash(self) -> dict:
        """Get account cash balance info."""
        raise NotImplementedError

    def get_account_info(self) -> dict:
        """Get account metadata (ID, currency, etc.)."""
        raise NotImplementedError

    # === PORTFOLIO =========================================================

    def get_positions(self) -> list[dict]:
        """Get all open positions."""
        raise NotImplementedError

    def get_position(self, ticker: str) -> Optional[dict]:
        """Get a specific position by ticker."""
        raise NotImplementedError

    # === ORDERS ============================================================

    def place_market_order(self, ticker: str, quantity: float) -> dict:
        """Place a market order. quantity > 0 = BUY, < 0 = SELL."""
        raise NotImplementedError

    def place_limit_order(
        self, ticker: str, quantity: float, limit_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a limit order. time_validity: 'Day' or 'GTC'."""
        raise NotImplementedError

    def place_stop_order(
        self, ticker: str, quantity: float, stop_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a stop order."""
        raise NotImplementedError

    def place_stop_limit_order(
        self, ticker: str, quantity: float,
        stop_price: float, limit_price: float,
        time_validity: str = "Day"
    ) -> dict:
        """Place a stop-limit order."""
        raise NotImplementedError

    def cancel_order(self, order_id: int) -> dict:
        """Cancel a pending order by ID."""
        raise NotImplementedError

    def get_pending_orders(self) -> list[dict]:
        """Get all pending (unfilled) orders."""
        raise NotImplementedError

    # === INSTRUMENTS =======================================================

    def get_instruments(self) -> list[dict]:
        """Get all tradable instruments."""
        raise NotImplementedError

    def get_exchanges(self) -> list[dict]:
        """Get all available exchanges and schedules."""
        raise NotImplementedError

    # === HISTORY ===========================================================

    def get_order_history(self, limit: int = 50) -> dict:
        """Get historical orders."""
        raise NotImplementedError

    def get_dividend_history(self, limit: int = 50) -> dict:
        """Get dividend payment history."""
        raise NotImplementedError

    # === PIES (Automated Portfolios) =======================================

    def get_pies(self) -> list[dict]:
        """Get all investment pies."""
        raise NotImplementedError

    def get_pie(self, pie_id: int) -> dict:
        """Get a specific pie by ID."""
        raise NotImplementedError
