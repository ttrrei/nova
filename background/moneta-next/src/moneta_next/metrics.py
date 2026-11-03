from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone


def next_month(value):
    return value.replace(year=value.year+1, month=1) if value.month == 12 else value.replace(month=value.month+1)


def summarize(trades, windows):
    per_instrument = {}
    pooled = Counter()
    for instrument, (start, end) in windows.items():
        subset = [trade for trade in trades if trade["instrument"] == instrument]
        entries = Counter(trade["entry_time"].strftime("%Y-%m") for trade in subset)
        pooled.update(entries)
        annual = defaultdict(float)
        for year in range(start.year, (end-timedelta(microseconds=1)).year+1):
            annual[str(year)] = 0.0
        for trade in subset:
            annual[str(trade["exit_time"].year)] += trade["net_return"]
        month = datetime(start.year, start.month, 1, tzinfo=timezone.utc)
        monthly = []
        while month < end:
            following = next_month(month)
            monthly.append({"month": month.strftime("%Y-%m"), "actual_entries": entries[month.strftime("%Y-%m")],
                            "complete_calendar_month": month >= start and following <= end})
            pooled.setdefault(month.strftime("%Y-%m"), 0)
            month = following
        full = [row for row in monthly if row["complete_calendar_month"]]
        all_months = all(row["actual_entries"] > 0 for row in full) if full else None
        years = (end-start).total_seconds() / (365.25*86400)
        total = sum(trade["net_return"] for trade in subset)
        score = total / years if years > 0 else None
        per_instrument[instrument] = {
            "window_start": start.isoformat(), "window_end": end.isoformat(),
            "trade_count": len(subset), "net_trade_return_sum": total,
            "annualized_trade_return_score": score,
            "mean_net_trade_return": total/len(subset) if subset else None,
            "win_rate": sum(trade["net_return"] > 0 for trade in subset)/len(subset) if subset else None,
            "yearly_net_trade_return_sum": dict(sorted(annual.items())), "monthly_entries": monthly,
            "every_full_month_has_entry": all_months,
            "passes_initial_screen": bool(score is not None and score > 0 and all_months is True),
        }
    return {
        "metric_definition": "annualized_trade_return_score = sum(per-trade net fractional returns) / full calendar years; NOT account CAGR",
        "monthly_rule": "Actual openings; complete UTC calendar months checked per instrument; partial months shown separately",
        "per_instrument": per_instrument,
        "pooled_monthly_actual_entries": dict(sorted(pooled.items())),
        "total_trades": len(trades),
    }
