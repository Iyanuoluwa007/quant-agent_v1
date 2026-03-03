"""
Claude AI Market Analyst
Uses Claude API to analyze markets and generate structured trading decisions.

NOTE: The system prompt, prompt engineering strategy, and response parsing
logic are proprietary. This file shows the integration architecture.
"""
import json
import logging
from typing import Optional
from anthropic import Anthropic
from config import TradingConfig
from risk_manager import TradeProposal

logger = logging.getLogger(__name__)

# ===================================================================
# SYSTEM PROMPT
# ===================================================================
# The analyst system prompt defines the AI's trading personality,
# rules, risk awareness, and required JSON output schema.
#
# Key design decisions:
#   - Low temperature (0.3) for consistent, reproducible analysis
#   - Structured JSON output with confidence scoring
#   - Explicit rules preventing overtrading and position chasing
#   - Required stop-loss and take-profit levels for all entries
#   - Cash-preference bias for uncertain conditions
#
# The full prompt is part of the proprietary system.
# ===================================================================

ANALYST_SYSTEM_PROMPT = """[REDACTED - Proprietary trading system prompt]

The system prompt configures Claude as a structured swing trader with:
- Technical analysis integration (RSI, MACD, Bollinger, SMA/EMA)
- Confidence-scored JSON output format
- Position sizing awareness
- Risk-first decision framework

See README.md for the output schema specification.
"""


class ClaudeAnalyst:
    """Uses Claude API to analyze markets and generate trade signals."""

    def __init__(self, config: TradingConfig):
        self.config = config
        self.client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.model = config.CLAUDE_MODEL

    def analyze_market(
        self,
        market_data: dict[str, str],
        portfolio_summary: str,
        account_info: str,
        recent_trades: str = "",
        news_context: str = "",
    ) -> list[TradeProposal]:
        """
        Send market data to Claude for analysis.

        Constructs a structured prompt containing:
            - Current portfolio status and account balances
            - Recent trade history for context continuity
            - Technical indicator data for each watchlist instrument
            - Optional market news context

        The LLM returns structured JSON with:
            - Overall market assessment
            - Trade recommendations with confidence scores
            - Portfolio-level observations

        Recommendations are parsed into TradeProposal objects for
        downstream risk validation.

        Returns:
            List of TradeProposal objects (empty if HOLD recommended)
        """
        # Implementation: builds multi-section prompt, calls Claude API,
        # parses structured JSON response, converts to TradeProposal objects.
        #
        # Prompt construction and response parsing are proprietary.
        raise NotImplementedError(
            "Market analysis pipeline is part of the proprietary system."
        )

    def get_market_sentiment(self, news_headlines: list[str]) -> str:
        """Quick sentiment analysis on news headlines.

        Returns: BULLISH / BEARISH / NEUTRAL with brief explanation.
        """
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=200,
                messages=[{
                    "role": "user",
                    "content": (
                        "Rate the overall market sentiment of these headlines "
                        "as BULLISH, BEARISH, or NEUTRAL with a one-line explanation.\n\n"
                        + "\n".join(f"- {h}" for h in news_headlines[:15])
                    ),
                }],
                temperature=0.1,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Sentiment analysis failed: {e}")
            return "NEUTRAL - Unable to assess sentiment"

    def explain_portfolio(
        self, portfolio_data: str, market_data: dict[str, str]
    ) -> str:
        """Generate a human-readable portfolio analysis summary."""
        try:
            prompt = (
                "Provide a brief, clear analysis of this portfolio. "
                "Highlight any risks, opportunities, and suggestions.\n\n"
                f"Portfolio:\n{portfolio_data}\n\n"
                "Market Data:\n"
                + "\n".join(f"{k}:\n{v}" for k, v in market_data.items())
            )
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.5,
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Portfolio explanation failed: {e}")
            return "Unable to generate portfolio analysis."
