"""
Risk Management Module
Enforces deterministic safety guardrails before any trade is executed.
The AI cannot override these rules.

NOTE: Specific validation logic and threshold interactions are proprietary.
This file shows the data models and interface architecture.
"""
import logging
from datetime import datetime, date
from dataclasses import dataclass, field
from typing import Optional
from config import TradingConfig

logger = logging.getLogger(__name__)


@dataclass
class TradeProposal:
    """A proposed trade from the AI analyst."""
    ticker: str
    action: str          # "BUY" or "SELL"
    quantity: float
    order_type: str      # "market", "limit", "stop", "stop_limit"
    limit_price: Optional[float] = None
    stop_price: Optional[float] = None
    reasoning: str = ""
    confidence: float = 0.0  # 0-1 scale


@dataclass
class RiskCheckResult:
    """Result of a risk assessment."""
    approved: bool
    original_proposal: TradeProposal
    adjusted_quantity: Optional[float] = None
    rejection_reasons: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class RiskManager:
    """
    Enforces risk management rules on all proposed trades.

    Validation pipeline (applied sequentially):
        1. Daily trade frequency limit
        2. Daily loss circuit breaker
        3. Per-position size cap (with automatic quantity adjustment)
        4. Cash reserve enforcement
        5. Total portfolio exposure ceiling
        6. Sell quantity validation against held positions
        7. AI confidence threshold gating

    A single check failure rejects the entire trade.
    Quantities may be adjusted downward to comply with position limits.
    """

    def __init__(self, config: TradingConfig):
        self.config = config
        self._trades_today: list[dict] = []
        self._daily_pnl: float = 0.0
        self._current_date: date = date.today()

    def _reset_daily_counters(self):
        """Reset counters at the start of a new trading day."""
        today = date.today()
        if today != self._current_date:
            self._current_date = today
            self._trades_today = []
            self._daily_pnl = 0.0
            logger.info("Daily counters reset for new trading day.")

    def check_trade(
        self,
        proposal: TradeProposal,
        account_cash: float,
        total_portfolio_value: float,
        current_positions: list[dict],
    ) -> RiskCheckResult:
        """
        Run all risk checks on a proposed trade.

        Args:
            proposal: The AI-generated trade recommendation
            account_cash: Available cash in the account
            total_portfolio_value: Total portfolio value (cash + positions)
            current_positions: List of current position dicts

        Returns:
            RiskCheckResult with approval status, adjusted quantities,
            rejection reasons, and warnings.

        The validation pipeline checks (in order):
            - Daily trade count vs. configured limit
            - Daily P&L vs. maximum drawdown threshold
            - Estimated position cost vs. per-position size cap
            - Available cash vs. minimum reserve requirement
            - Current exposure vs. total allocation ceiling
            - Sell quantity vs. actual held quantity
            - AI confidence vs. minimum threshold

        Implementation details are proprietary.
        """
        raise NotImplementedError(
            "Risk validation pipeline is part of the proprietary system."
        )

    def record_trade(self, trade_info: dict):
        """Record a completed trade for daily tracking."""
        self._trades_today.append(trade_info)
        pnl = trade_info.get("realized_pnl", 0)
        self._daily_pnl += pnl
        logger.info(
            f"Trade recorded. Daily trades: {len(self._trades_today)}, "
            f"Daily P&L: ${self._daily_pnl:.2f}"
        )

    def get_daily_stats(self) -> dict:
        """Get current daily trading statistics."""
        self._reset_daily_counters()
        return {
            "trades_today": len(self._trades_today),
            "max_trades": self.config.MAX_TRADES_PER_DAY,
            "daily_pnl": self._daily_pnl,
            "max_daily_loss_pct": self.config.MAX_DAILY_LOSS_PCT,
        }
