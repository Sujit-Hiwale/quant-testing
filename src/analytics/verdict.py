from dataclasses import dataclass, field


@dataclass
class ResearchVerdict:
    status: str
    reasons: list[str] = field(default_factory=list)
    positives: list[str] = field(default_factory=list)
    recommendation: str = ""


def generate_verdict(
    strategy_metrics: dict,
    benchmark_metrics: dict,
) -> ResearchVerdict:

    reasons = []
    positives = []

    strategy_cagr = strategy_metrics["cagr"]
    benchmark_cagr = benchmark_metrics["cagr"]
    sharpe = strategy_metrics["sharpe_ratio"]
    max_drawdown = strategy_metrics["max_drawdown"]
    trade_count = strategy_metrics.get("trade_count", 0)

    excess_cagr = strategy_cagr - benchmark_cagr

    if excess_cagr < 0:
        reasons.append("UNDERPERFORMS_BENCHMARK")

    if sharpe < 0.5:
        reasons.append("LOW_SHARPE")

    if trade_count < 30:
        reasons.append("INSUFFICIENT_TRADES")

    if max_drawdown < -0.30:
        reasons.append("HIGH_DRAWDOWN")
    elif max_drawdown > -0.15:
        positives.append("CONTROLLED_DRAWDOWN")

    if strategy_metrics["annualized_volatility"] < 0.10:
        positives.append("LOW_VOLATILITY")

    if not reasons:
        status = "PASS"
        recommendation = "Strategy may warrant further robustness testing."
    elif len(reasons) <= 2:
        status = "WEAK"
        recommendation = "Do not deploy. Continue research and robustness testing."
    else:
        status = "FAIL"
        recommendation = "Do not deploy. Strategy does not currently demonstrate sufficient edge."

    return ResearchVerdict(
        status=status,
        reasons=reasons,
        positives=positives,
        recommendation=recommendation,
    )
