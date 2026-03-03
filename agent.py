"""
AI Trading Agent - Main Orchestrator
Supports both Alpaca (paper trading) and Trading212 (live).
Connects: Claude AI analysis -> Risk Management -> Broker execution.

NOTE: Core orchestration logic has been abstracted in this public version.
The execution pipeline, data gathering, and trade routing implementations
are part of the proprietary trading system.
"""
import json
import time
import logging
import sys
from datetime import datetime
from pathlib import Path

from config import TradingConfig
from market_data import MarketDataService
from claude_analyst import ClaudeAnalyst
from risk_manager import RiskManager, TradeProposal

# ===================================================================
# LOGGING SETUP
# ===================================================================

def setup_logging(config: TradingConfig):
    """Configure logging to file and console."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"

    file_handler = logging.FileHandler(config.LOG_FILE, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(log_format))

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter(log_format))

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=log_format,
        handlers=[file_handler, console_handler],
    )

logger = logging.getLogger(__name__)


# ===================================================================
# BROKER FACTORY
# ===================================================================

def create_broker(config: TradingConfig):
    """Create the appropriate broker client based on config."""
    if config.BROKER == "alpaca":
        from alpaca_client import AlpacaClient
        return AlpacaClient(config)
    elif config.BROKER == "trading212":
        from trading212_client import Trading212Client
        return Trading212Client(config)
    else:
        raise ValueError(f"Unknown broker: {config.BROKER}")


# ===================================================================
# TRADE LOGGER
# ===================================================================

class TradeLogger:
    """Persists all trade decisions and executions to JSON."""

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)
        self._ensure_file()

    def _ensure_file(self):
        if not self.filepath.exists():
            self.filepath.write_text(json.dumps([], indent=2))

    def log_trade(self, trade_data: dict):
        """Append a trade record with timestamp."""
        trades = json.loads(self.filepath.read_text())
        trade_data["timestamp"] = datetime.now().isoformat()
        trades.append(trade_data)
        self.filepath.write_text(json.dumps(trades, indent=2))

    def get_recent_trades(self, n: int = 10) -> list[dict]:
        """Get the N most recent trades."""
        trades = json.loads(self.filepath.read_text())
        return trades[-n:]

    def get_performance_summary(self) -> dict:
        """Calculate overall performance stats."""
        trades = json.loads(self.filepath.read_text())
        executed = [t for t in trades if t.get("status") == "EXECUTED"]
        rejected = [t for t in trades if t.get("status") == "REJECTED"]
        return {
            "total_decisions": len(trades),
            "executed": len(executed),
            "rejected": len(rejected),
            "buy_count": sum(1 for t in executed if t.get("action") == "BUY"),
            "sell_count": sum(1 for t in executed if t.get("action") == "SELL"),
        }


# ===================================================================
# MAIN AGENT CLASS
# ===================================================================

class TradingAgent:
    """
    The main AI trading agent.

    Execution Flow:
        1. Fetch market data for watchlist (OHLCV + technicals)
        2. Get current portfolio and account status from broker
        3. Send structured context to Claude for analysis
        4. Run AI recommendations through risk management pipeline
        5. Execute approved trades via broker abstraction layer
        6. Log all decisions (executed, rejected, skipped)
        7. Repeat at configured interval
    """

    def __init__(self, config: TradingConfig):
        self.config = config
        self.broker = create_broker(config)
        self.market_data = MarketDataService()
        self.analyst = ClaudeAnalyst(config)
        self.risk_mgr = RiskManager(config)
        self.trade_log = TradeLogger(config.TRADE_LOG_FILE)
        self._running = False
        self._cycle_count = 0

    # -- DATA GATHERING ---------------------------------------------------

    def _get_account_summary(self) -> tuple[str, float, float]:
        """Fetch and format account info from broker.

        Returns:
            Tuple of (formatted_summary, available_cash, total_portfolio_value)
        """
        # Implementation: queries broker API, normalizes response format
        # across Alpaca and Trading212, returns human-readable summary
        # along with key numeric values for risk calculations.
        raise NotImplementedError(
            "Account summary pipeline is part of the proprietary system."
        )

    def _get_portfolio_summary(self) -> tuple[str, list[dict]]:
        """Fetch and format current positions from broker.

        Returns:
            Tuple of (formatted_summary, raw_positions_list)
        """
        raise NotImplementedError(
            "Portfolio summary pipeline is part of the proprietary system."
        )

    def _get_market_data(self) -> dict[str, str]:
        """Fetch market data and technicals for all watchlist tickers.

        Returns:
            Dict mapping ticker -> formatted analysis string for LLM context
        """
        raise NotImplementedError(
            "Market data aggregation is part of the proprietary system."
        )

    def _get_pending_orders_summary(self) -> tuple[str, set]:
        """Fetch pending orders for duplicate detection.

        Returns:
            Tuple of (formatted_summary, set_of_tickers_with_pending_orders)
        """
        raise NotImplementedError(
            "Pending order tracking is part of the proprietary system."
        )

    # -- TRADE EXECUTION --------------------------------------------------

    def _execute_trade(self, proposal: TradeProposal, adjusted_qty: float = None):
        """Execute a single trade via the broker abstraction layer.

        Handles:
            - Symbol format conversion (plain -> broker-specific)
            - Order type routing (market / limit / stop / stop-limit)
            - Execution logging with full audit trail
            - Error capture and graceful failure recording
        """
        raise NotImplementedError(
            "Trade execution pipeline is part of the proprietary system."
        )

    # -- MAIN ANALYSIS CYCLE ----------------------------------------------

    def run_analysis_cycle(self):
        """Run one complete analysis + trade cycle.

        Pipeline:
            1. Gather market data, account info, portfolio, pending orders
            2. Send structured context to Claude AI for analysis
            3. Filter recommendations against pending orders (deduplication)
            4. Run each proposal through risk management checks
            5. Execute approved trades, log rejections
            6. Update daily counters
        """
        raise NotImplementedError(
            "The full orchestration loop is part of the proprietary system. "
            "See README.md for the architecture and execution flow."
        )

    # -- STATUS REPORTING -------------------------------------------------

    def print_status(self):
        """Print current agent status to console."""
        raise NotImplementedError(
            "Status reporting is part of the proprietary system."
        )

    # -- CONTINUOUS LOOP --------------------------------------------------

    def run(self):
        """Run the agent in a continuous loop with configured interval."""
        logger.info("[START] AI Trading Agent Starting...")
        logger.info(f"  Broker: {self.config.BROKER.upper()}")
        logger.info(f"  AI Model: {self.config.CLAUDE_MODEL}")
        logger.info(f"  Watchlist: {len(self.config.WATCHLIST)} instruments")
        logger.info(f"  Interval: {self.config.ANALYSIS_INTERVAL_MINUTES} min")

        errors = self.config.validate()
        if errors:
            for err in errors:
                logger.error(f"  [X] {err}")
            logger.error("Fix configuration errors before starting.")
            return

        self._running = True
        interval = self.config.ANALYSIS_INTERVAL_MINUTES * 60

        while self._running:
            try:
                self.run_analysis_cycle()
            except KeyboardInterrupt:
                logger.info("[STOP] Agent stopped by user.")
                break
            except Exception as e:
                logger.error(f"Unexpected error in cycle: {e}", exc_info=True)

            if self._running:
                logger.info(
                    f"[WAIT] Next analysis in "
                    f"{self.config.ANALYSIS_INTERVAL_MINUTES} min..."
                )
                try:
                    time.sleep(interval)
                except KeyboardInterrupt:
                    logger.info("[STOP] Agent stopped by user.")
                    self._running = False

    def stop(self):
        """Stop the agent gracefully."""
        self._running = False
        logger.info("Agent stopping...")


# ===================================================================
# ENTRY POINT
# ===================================================================

def main():
    config = TradingConfig()
    setup_logging(config)
    agent = TradingAgent(config)

    if "--status" in sys.argv:
        agent.print_status()
    elif "--once" in sys.argv:
        agent.run_analysis_cycle()
    else:
        agent.run()


if __name__ == "__main__":
    main()
