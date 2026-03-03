# Quant Agent v1

### Autonomous AI-Driven Trading System

Quant Agent v1 is a modular, AI-powered equity trading system that combines large language model reasoning with deterministic risk guardrails to execute structured swing trades.

Built for controlled experimentation, disciplined risk management, and automation — not blind execution.

> **Note:** This is a portfolio reference implementation. Core trading logic, risk parameters, AI prompts, and broker integration details have been abstracted. See [Architecture](#architecture) for system design.

---

## Architecture

### System Overview

```
                            +---------------------+
                            |    Scheduled Entry   |
                            |   (cron / task svc)  |
                            +---------+-----------+
                                      |
                                      v
+---------------------------------------------------------------------+
|                          AGENT ORCHESTRATOR                          |
|                                                                      |
|  +----------------+     +-----------------+     +-----------------+  |
|  |  Market Data   |---->|   AI Analyst    |---->|  Risk Manager   |  |
|  |  Service       |     |   (LLM Engine)  |     |  (Guardrails)   |  |
|  +----------------+     +-----------------+     +--------+--------+  |
|         |                       |                        |           |
|         |  Yahoo Finance        |  Claude API            |           |
|         |  OHLCV + Technicals   |  Structured JSON       |           |
|         |                       |  Recommendations       |           |
|         |                       |                        v           |
|         |                       |               +--------+--------+  |
|         |                       |               |  Broker Router  |  |
|         |                       |               |  (Abstract I/F) |  |
|         |                       |               +---+--------+---+  |
|         |                       |                   |        |       |
|         |                       |                   v        v       |
|         |                       |            +------+--+ +---+----+  |
|         |                       |            | Alpaca  | |  T212  |  |
|         |                       |            | (paper) | | (live) |  |
|         |                       |            +---------+ +--------+  |
|         |                       |                                    |
|  +------+-------------------------------------------------------+   |
|  |                       Trade Logger (JSON)                     |   |
|  +---------------------------------------------------------------+   |
+---------------------------------------------------------------------+
```

### Execution Flow

Each analysis cycle (configurable interval):

```
1. GATHER       Fetch OHLCV data + compute technicals for watchlist
                Retrieve portfolio positions + account balances
                Load recent trade history for context

2. ANALYZE      Construct structured prompt with all market context
                Send to Claude API with role-specific system prompt
                Receive JSON-structured trade recommendations
                Each recommendation includes confidence score + reasoning

3. VALIDATE     Duplicate order detection (pending order deconfliction)
                Position sizing enforcement
                Exposure ceiling check
                Cash reserve verification
                Daily loss circuit breaker
                Trade frequency rate limiting
                Confidence threshold gating

4. EXECUTE      Route approved trades through broker abstraction layer
                Support for market / limit / stop / stop-limit orders
                Normalize order formats across broker APIs

5. LOG          Persist all decisions (executed, rejected, skipped)
                Track daily P&L and trade counts
                Full audit trail with AI reasoning attached
```

---

## Technical Indicators

The market data pipeline computes the following for each watchlist instrument:

| Indicator           | Method                              | Usage                        |
| ------------------- | ----------------------------------- | ---------------------------- |
| RSI (14)            | Wilder's smoothed RS                | Overbought / oversold signal |
| MACD                | EMA(12) - EMA(26), Signal EMA(9)   | Momentum + crossover signal  |
| Bollinger Bands     | SMA(20) +/- 2 std dev              | Volatility envelope          |
| SMA 20 / 50         | Simple moving averages              | Trend direction              |
| EMA 12 / 26         | Exponential moving averages         | Short-term momentum          |
| Volume Ratio        | Current vol / 20-day avg vol        | Participation intensity      |
| Price Momentum      | 5D and 20D percentage returns       | Directional strength         |

All indicators are computed from Yahoo Finance historical data and formatted into a structured context window for LLM consumption.

---

## Risk Architecture

The AI cannot override risk rules. Every proposed trade passes through a deterministic validation pipeline before execution.

```
Proposal ──> [Daily Limit] ──> [Loss Circuit] ──> [Position Size]
                                                         |
         [Confidence Gate] <── [Sell Validation] <── [Exposure Cap]
                |                                        |
                v                                        v
           REJECTED                              [Cash Reserve]
                                                        |
                                                        v
                                                    APPROVED
```

Risk checks are applied sequentially. A single failure rejects the trade. Quantities may be adjusted downward (never upward) to comply with position sizing rules.

Key guardrails (configurable):
- Per-position size cap
- Total portfolio exposure ceiling
- Daily drawdown circuit breaker
- Trade frequency rate limiter
- Minimum cash reserve enforcement
- AI confidence threshold gating
- Sell quantity validation against held positions
- Pending order deconfliction (no duplicate orders)

---

## Multi-Broker Abstraction

The system supports multiple brokers through a unified interface layer:

```python
# Broker-agnostic interface (simplified)
class BrokerInterface:
    def get_account_cash(self) -> dict: ...
    def get_positions(self) -> list[dict]: ...
    def place_market_order(self, symbol, quantity) -> dict: ...
    def place_limit_order(self, symbol, quantity, price) -> dict: ...
    def place_stop_order(self, symbol, quantity, price) -> dict: ...
    def get_pending_orders(self) -> list[dict]: ...
    def cancel_order(self, order_id) -> dict: ...
```

| Broker      | Mode         | Use Case                    |
| ----------- | ------------ | --------------------------- |
| Alpaca      | Paper / Live | Free paper trading, US equities |
| Trading212  | Demo / Live  | European broker, fractional shares |

Ticker formats are normalized automatically (`AAPL` <-> `AAPL_US_EQ`).

---

## AI Decision Model

The LLM analyst operates as a structured swing trader (1-5 day horizon).

**Inputs provided per cycle:**
- Technical indicators for full watchlist
- Current portfolio positions with unrealized P&L
- Account balances and buying power
- Pending (unfilled) orders
- Recent trade history with outcomes

**Output format (structured JSON):**

```json
{
    "market_assessment": "Overall market thesis",
    "recommendations": [
        {
            "ticker": "AAPL",
            "action": "BUY",
            "order_type": "limit",
            "quantity": 10,
            "limit_price": 185.00,
            "confidence": 0.72,
            "reasoning": "Technical setup rationale...",
            "stop_loss": 178.00,
            "take_profit": 195.00
        }
    ],
    "portfolio_notes": "Current portfolio observations"
}
```

Low-conviction signals default to HOLD. The system prefers cash over marginal setups.

---

## Project Structure

```
quant-agent_v1/
|
|-- run.py                  # Entry point (--once | --status | continuous)
|-- agent.py                # Main orchestrator (data -> AI -> risk -> execute)
|-- config.py               # All parameters + broker selection
|-- market_data.py          # Yahoo Finance data + technical indicators
|-- claude_analyst.py       # LLM integration + structured prompt engineering
|-- risk_manager.py         # Deterministic risk validation pipeline
|-- alpaca_client.py        # Alpaca broker implementation
|-- trading212_client.py    # Trading212 broker implementation
|-- requirements.txt        # Python dependencies
|-- .env.example            # Environment variable template
+-- .gitignore
```

---

## Stack

| Layer         | Technology                          |
| ------------- | ----------------------------------- |
| Language      | Python 3.11+                        |
| AI Engine     | Anthropic Claude API                |
| Market Data   | Yahoo Finance (yfinance)            |
| Broker (US)   | Alpaca Markets SDK (alpaca-py)      |
| Broker (EU)   | Trading212 Public API v0            |
| Scheduling    | Windows Task Scheduler / cron       |
| Data Format   | JSON (trades log, config)           |

---

## Operating Costs

| Component               | Estimated Cost         |
| ------------------------ | ---------------------- |
| Alpaca Paper Trading     | Free                   |
| Claude API per cycle     | ~$0.02 - $0.10        |
| ~13 cycles/day           | ~$0.50 - $1.50 daily  |

Costs scale with watchlist size and analysis interval.

---

## Intended Use

Designed for:
- AI-augmented trading experimentation
- Guardrail-driven autonomous execution research
- Portfolio decision augmentation
- Structured capital allocation prototyping

Not designed for:
- High-frequency trading
- Financial advice
- Guaranteed profitability

---

## Risk Disclosure

Trading equities involves substantial risk of loss. Past performance does not guarantee future results. Paper trading does not replicate live execution conditions. AI models can produce incorrect analysis. Market gaps can bypass stop logic. Deploy only capital you can afford to lose.

---

## License

MIT License — Use at your own risk.

---

## Author

Built by [Iyanuoluwa] as part of autonomous systems research combining large language models with deterministic control architectures.
