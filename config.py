"""
Configuration for the AI Trading Agent.
Supports both Alpaca (paper trading) and Trading212 (live).

NOTE: Risk parameters and thresholds are configured via environment
variables in production. Defaults shown here are illustrative only.
"""
import os
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TradingConfig:
    # -- Broker Selection ---------------------------------------------------
    # "alpaca" or "trading212"
    BROKER: str = os.getenv("BROKER", "alpaca")

    # -- Alpaca API ---------------------------------------------------------
    ALPACA_API_KEY: str = os.getenv("ALPACA_API_KEY", "")
    ALPACA_API_SECRET: str = os.getenv("ALPACA_API_SECRET", "")
    ALPACA_ENV: str = os.getenv("ALPACA_ENV", "paper")  # "paper" or "live"

    # -- Trading212 API -----------------------------------------------------
    T212_API_KEY: str = os.getenv("T212_API_KEY", "")
    T212_API_SECRET: str = os.getenv("T212_API_SECRET", "")
    T212_ENV: str = os.getenv("T212_ENV", "demo")  # "demo" or "live"

    @property
    def T212_BASE_URL(self) -> str:
        if self.T212_ENV == "live":
            return "https://live.trading212.com/api/v0"
        return "https://demo.trading212.com/api/v0"

    # -- Claude API ---------------------------------------------------------
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    CLAUDE_MODEL: str = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-5-20250929")

    # -- Risk Management ----------------------------------------------------
    # Production values loaded from environment; defaults are placeholders.
    MAX_POSITION_SIZE_PCT: float = float(os.getenv("MAX_POSITION_SIZE_PCT", "5"))
    MAX_TOTAL_EXPOSURE_PCT: float = float(os.getenv("MAX_TOTAL_EXPOSURE_PCT", "50"))
    MAX_DAILY_LOSS_PCT: float = float(os.getenv("MAX_DAILY_LOSS_PCT", "3"))
    MAX_TRADES_PER_DAY: int = int(os.getenv("MAX_TRADES_PER_DAY", "10"))
    MIN_CASH_RESERVE_PCT: float = float(os.getenv("MIN_CASH_RESERVE_PCT", "20"))

    # -- Trading Parameters -------------------------------------------------
    WATCHLIST: list = field(default_factory=lambda: [
        "AAPL", "MSFT", "GOOGL", "AMZN",
        "NVDA", "META", "TSLA",
        "SPY", "QQQ",
    ])
    ANALYSIS_INTERVAL_MINUTES: int = int(os.getenv("ANALYSIS_INTERVAL", "30"))
    TRADING_HOURS_START: str = "09:30"  # NYSE open (ET)
    TRADING_HOURS_END: str = "16:00"    # NYSE close (ET)

    # -- Logging ------------------------------------------------------------
    LOG_FILE: str = "trading_agent.log"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    TRADE_LOG_FILE: str = "trades.json"

    def get_broker_symbol(self, symbol: str) -> str:
        """Convert plain symbol to broker-specific format."""
        if self.BROKER == "trading212":
            if "_" not in symbol:
                return f"{symbol}_US_EQ"
        return symbol

    def get_plain_symbol(self, broker_symbol: str) -> str:
        """Convert broker-specific symbol to plain format."""
        if "_" in broker_symbol:
            return broker_symbol.split("_")[0]
        return broker_symbol

    def validate(self) -> list[str]:
        """Validate required config values are present."""
        errors = []
        if self.BROKER == "alpaca":
            if not self.ALPACA_API_KEY:
                errors.append("ALPACA_API_KEY is required")
            if not self.ALPACA_API_SECRET:
                errors.append("ALPACA_API_SECRET is required")
        elif self.BROKER == "trading212":
            if not self.T212_API_KEY:
                errors.append("T212_API_KEY is required")
            if not self.T212_API_SECRET:
                errors.append("T212_API_SECRET is required")
        else:
            errors.append(f"Unknown broker: {self.BROKER}")

        if not self.ANTHROPIC_API_KEY:
            errors.append("ANTHROPIC_API_KEY is required")
        return errors
