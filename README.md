# Quant Testing

**A research-grade quantitative trading strategy research and backtesting platform.**

Quant Testing is designed to answer a more important question than:

> "Did this strategy make money historically?"

Instead:

> **"Does this trading hypothesis demonstrate a statistically defensible and economically meaningful edge after realistic execution assumptions?"**

The project combines historical market data, strategy logic, realistic execution simulation, portfolio accounting, performance analytics, walk-forward validation, transaction-cost sensitivity, and research verdicts into a single research workflow.

The goal is not to build a generic stock-prediction system. The goal is to create a transparent environment for **testing, challenging, and rejecting trading hypotheses**.

---

## Research Philosophy

Quant Testing follows this research pipeline:

```text
Market Data
     ↓
Data Cleaning & Validation
     ↓
Strategy
     ↓
Signal
     ↓
Order
     ↓
Realistic Execution
     ↓
Portfolio
     ↓
Risk & Performance
     ↓
Walk-Forward Validation
     ↓
Robustness Analysis
     ↓
Research Verdict
```

A strategy is not considered reliable simply because it performs well on historical data.

Quant Testing emphasizes:

- Out-of-sample performance
- Realistic execution costs
- Drawdown
- Parameter stability
- Walk-forward validation
- Benchmark comparison
- Trade-count awareness
- Research transparency

---

# Current Status

Quant Testing is currently in the **Backtesting and Research Validation** stage.

### Implemented

- Historical market-data loading
- Data cleaning
- Data validation
- OHLCV → internal market-bar conversion
- Strategy abstraction
- SMA crossover strategy
- Event-driven backtesting engine
- Next-bar execution
- Market-order execution simulation
- Slippage modeling
- Transaction-fee modeling
- Portfolio accounting
- Position sizing
- Equity-curve generation
- Trade tracking
- Performance analytics
- Benchmark comparison
- Walk-forward optimization
- Out-of-sample testing
- Parameter stability analysis
- Execution-cost sensitivity analysis
- Research verdict generation
- Interactive Streamlit dashboard
- Research analysis views
- Statistical analysis
- Automated test suite

The project currently prioritizes **research correctness and transparency over feature count**.

---

# Core Architecture

The system separates the major components of a quantitative research workflow:

```text
Data
  │
  ▼
Validation
  │
  ▼
Strategy
  │
  ▼
Signal
  │
  ▼
Order
  │
  ▼
Execution Simulator
  │
  ▼
Fill
  │
  ▼
Portfolio
  │
  ▼
Analytics
  │
  ▼
Research
  │
  ▼
Verdict
```

This separation makes it possible to improve individual components without turning the entire platform into a single monolithic backtesting script.

---

# Research Verdict

One of the core features of Quant Testing is the **Research Verdict**.

Instead of presenting performance metrics without interpretation, the platform evaluates the available evidence and produces a research-oriented classification.

| Verdict | Meaning |
|---|---|
| `PASS` | Evidence supports continued research or potential deployment consideration |
| `WEAK` | Some evidence exists, but important weaknesses remain |
| `FAIL` | Current evidence does not support the strategy |
| `INSUFFICIENT EVIDENCE` | There is not enough reliable evidence to reach a meaningful conclusion |

The research evaluation can consider:

- Out-of-sample CAGR
- Sharpe ratio
- Maximum drawdown
- Positive OOS windows
- Strong OOS windows
- Aggregate OOS performance
- Trade count
- Parameter stability
- Research failure conditions

The verdict is a **research decision aid**, not a guarantee of future performance.

---

# Walk-Forward Research

Quant Testing supports walk-forward validation to reduce dependence on a single historical optimization period.

The process is:

```text
Historical Data
      │
      ├── Training Window ──→ Parameter Selection
      │
      └── Test Window ──────→ Out-of-Sample Evaluation
                                  │
                                  ▼
                           Research Metrics
                                  │
                                  ▼
                         Next Walk-Forward Window
```

For example:

```text
Window 1
Train: 2020 → 2022
Test:  2022 → 2023

Window 2
Train: 2021 → 2023
Test:  2023 → 2024

Window 3
Train: 2022 → 2024
Test:  2024 → 2025
```

Each window:

1. Evaluates candidate parameters on training data.
2. Selects parameters according to the research objective.
3. Applies the selected parameters to unseen test data.
4. Records out-of-sample performance.
5. Contributes to aggregate research statistics.

This creates a clear distinction between:

```text
In-Sample Performance
        ≠
Out-of-Sample Performance
```

---

# Parameter Stability

A parameter combination that performs well once is not necessarily robust.

Quant Testing records parameter-selection frequency across walk-forward windows.

For the current SMA strategy, the parameter grid can include:

```text
10 / 30
20 / 50
30 / 100
50 / 200
```

Repeated selection of similar parameter regions across independent training windows provides stronger evidence than finding one highly optimized combination on a single historical sample.

---

# Execution Model

Quant Testing separates signal generation from execution:

```text
Signal Generation
        ↓
Order
        ↓
Execution
        ↓
Fill
        ↓
Portfolio Update
```

Signals generated from a bar are executed on a **future bar**, currently at the next bar's open.

This avoids assuming that a strategy can observe a closing price and execute at that same price.

The execution simulator supports:

- Market orders
- Slippage
- Transaction fees

The execution flow is:

```text
Current Bar
    ↓
Strategy Signal
    ↓
Order
    ↓
Next Bar Open
    ↓
Slippage Applied
    ↓
Transaction Fee
    ↓
Fill
    ↓
Portfolio Updated
```

---

# Transaction-Cost Sensitivity

A strategy that only works before transaction costs may not have a meaningful tradable edge.

Quant Testing can evaluate strategy performance under different execution-cost assumptions.

Example scenarios:

```text
Slippage    Fees
----------------
0 bps       0 bps
5 bps       10 bps
10 bps      20 bps
20 bps      40 bps
50 bps      100 bps
```

This helps determine how sensitive a strategy is to increasingly unfavorable execution assumptions.

Cost sensitivity is particularly important for:

- High-turnover strategies
- Small expected edges
- Frequent trading
- Short holding periods

---

# Portfolio & Position Sizing

Quant Testing currently supports multiple position-sizing approaches.

## Fixed Quantity

A fixed number of shares is traded for each signal.

## Target Exposure

The portfolio can target a percentage of current equity.

For example:

```text
Portfolio Equity = ₹100,000
Target Exposure  = 100%
Asset Price      = ₹1,000

Target Position ≈ ₹100,000
```

The sizing layer also considers available cash and a configurable cost buffer.

---

# Performance Analytics

Quant Testing currently calculates:

- Total return
- CAGR
- Annualized volatility
- Sharpe ratio
- Sortino ratio
- Maximum drawdown
- Trade statistics
- Benchmark performance

The research dashboard provides analysis including:

- Equity curves
- Drawdown
- Rolling volatility
- Return distribution
- Market context
- Walk-forward results
- Parameter stability
- Execution-cost sensitivity

---

# Current Strategy

The current baseline strategy is an **SMA Crossover Strategy**.

It compares a fast moving average against a slow moving average.

A long entry is generated when:

```text
Fast SMA > Slow SMA
```

A long exit is generated when:

```text
Fast SMA < Slow SMA
```

The strategy is intentionally simple.

Its purpose is to provide a baseline for validating the research infrastructure before introducing more complex strategies.

---

# Research Dashboard

Quant Testing provides an interactive Streamlit interface.

The application currently has two primary modes:

```text
User
Research
```

The Research interface contains:

```text
Overview
Analysis
Statistics
Models
Experiments
```

The main research dashboard currently focuses on:

- Strategy verdict
- Out-of-sample performance
- Walk-forward windows
- Parameter stability
- Execution-cost sensitivity
- Market context
- Return distribution
- Rolling volatility
- Drawdown

Some sections remain under active development.

---

# Project Structure

```text
.
├── app
│   ├── components
│   │   ├── cards.py
│   │   ├── charts.py
│   │   ├── header.py
│   │   ├── __init__.py
│   │   ├── layout.py
│   │   ├── research_dashboard.py
│   │   ├── sections.py
│   │   ├── status.py
│   │   └── styles.py
│   │
│   ├── main.py
│   │
│   ├── pages
│   │   ├── market_data.py
│   │   ├── research
│   │   │   ├── analysis.py
│   │   │   ├── __init__.py
│   │   │   ├── overview.py
│   │   │   └── statistics.py
│   │   │
│   │   └── user
│   │       ├── __init__.py
│   │       └── overview.py
│   │
│   └── state
│       ├── context.py
│       └── __init__.py
│
├── scripts
│   ├── run_real_backtest.py
│   └── run_train_test.py
│
├── src
│   ├── analytics
│   │   ├── benchmark.py
│   │   ├── __init__.py
│   │   ├── metrics.py
│   │   └── verdict.py
│   │
│   ├── core
│   │   ├── data_adapter.py
│   │   ├── engine.py
│   │   ├── __init__.py
│   │   └── models.py
│   │
│   ├── data
│   │   ├── cleaner.py
│   │   ├── __init__.py
│   │   ├── loader.py
│   │   └── validator.py
│   │
│   ├── execution
│   │   ├── __init__.py
│   │   └── simulator.py
│   │
│   ├── features
│   │   └── engineering.py
│   │
│   ├── portfolio
│   │   ├── __init__.py
│   │   ├── portfolio.py
│   │   └── sizing.py
│   │
│   ├── research
│   │   ├── cost_sensitivity.py
│   │   ├── __init__.py
│   │   └── walk_forward.py
│   │
│   ├── stats
│   │   ├── distributions.py
│   │   └── time_series.py
│   │
│   ├── strategies
│   │   ├── base.py
│   │   ├── __init__.py
│   │   └── sma_crossover.py
│   │
│   └── __init__.py
│
├── tests
│   ├── test_analytics.py
│   ├── test_cost_sensitivity.py
│   ├── test_data.py
│   ├── test_data_adapter.py
│   ├── test_engine.py
│   ├── test_execution.py
│   ├── test_portfolio.py
│   └── test_walk_forward.py
│
├── .gitignore
├── pytest.ini
├── README.md
├── requirements.txt
└── run.py
```

---

# Installation

Clone the repository:

```bash
git clone https://github.com/Sujit-Hiwale/quant-testing.git
cd quant-testing
```

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Running the Dashboard

Launch the application with:

```bash
python run.py
```

The Streamlit dashboard will open in your browser.

---

# Running Backtests

The repository includes research scripts under:

```text
scripts/
```

Run the real backtest workflow:

```bash
python scripts/run_real_backtest.py
```

Run the train/test workflow:

```bash
python scripts/run_train_test.py
```

---

# Running Tests

Run the complete test suite:

```bash
pytest -q
```

The tests cover:

- Analytics
- Data handling
- Data adapters
- Backtest engine
- Execution simulation
- Portfolio accounting
- Cost sensitivity
- Walk-forward research

Before committing changes:

```bash
pytest -q
git diff --check
```

---

# Data

Quant Testing works with historical OHLCV market data.

The expected structure is:

```text
Date
Open
High
Low
Close
Volume
```

Market data passes through validation and cleaning before being converted into Quant Testing's internal `Bar` representation.

The research engine is separated from the data source so that different market-data providers can be integrated without changing the core backtesting logic.

---

# Current Limitations

Quant Testing is an active research project and is **not yet a production trading system**.

Current limitations include:

- Long-only strategy support
- No short selling
- Full-position exits only
- No partial fills
- No order-book simulation
- No market-impact model
- No intrabar execution model
- Limited multi-asset portfolio support
- No live brokerage integration
- No live paper-trading engine yet
- Limited handling of trades crossing walk-forward boundaries
- Small trade samples can make statistical conclusions unreliable
- Current cost-sensitivity analysis is not a replacement for full out-of-sample cost validation
- Historical backtests cannot guarantee future performance

These limitations are documented intentionally.

---

# Design Principles

### Research before complexity

A simple strategy with trustworthy validation is more valuable than a complicated model with questionable evaluation.

### Out-of-sample evidence matters

In-sample performance alone is insufficient.

### Execution matters

Fees and slippage can turn an apparent edge into a loss.

### Rejection is useful

A failed strategy is still useful if the research explains why it failed.

### Transparency over black boxes

Research results should be explainable from the underlying data, parameters, execution assumptions, and evaluation methodology.

### Reproducibility

The same research configuration should produce results that can be independently inspected and reproduced.

---

# Disclaimer

Quant Testing is a research and educational software project.

Backtested and simulated performance does not guarantee future results. Historical market data can contain data-quality problems, survivorship bias, regime-specific behavior, and other limitations. Simulated execution may differ materially from real-world execution.

Nothing in this project constitutes financial advice or a recommendation to buy or sell any security.

---

# Project Goal

Quant Testing aims to evolve into a complete quantitative research environment:

```text
Hypothesis
    ↓
Implement
    ↓
Backtest
    ↓
Challenge
    ↓
Walk Forward
    ↓
Stress Test
    ↓
Measure Uncertainty
    ↓
Research Verdict
    ↓
Paper Trade
    ↓
Deploy Only If Evidence Supports It
```

The goal is not to find strategies that merely **look profitable**.

**The goal is to determine whether the evidence is strong enough to believe that a real edge may exist.**
