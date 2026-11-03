from dataclasses import asdict, dataclass


@dataclass
class Trade:
    instrument: str
    direction: int
    signal_time: object
    entry_time: object
    exit_time: object
    exit_time_precision: str
    entry_price: float
    exit_price: float
    exit_reason: str
    bars_held: int
    gross_return: float
    cost_return: float
    net_return: float


def quote(bar, direction, point, execution):
    """direction +1 selects bid for liquidation; -1 selects ask."""
    name = ("bid_" if direction == 1 else "ask_") + point
    if bar.get(name) is not None:
        return bar[name]
    return bar[point] * (1 - direction * execution["spread_bps"] / 20000)


def simulate(rows, signals, spec):
    """One instrument, one trade at a time; no quantity/account state."""
    if len(rows) != len(signals):
        raise ValueError("Bars and signals must align")
    if not rows:
        return []
    if len({bar["instrument"] for bar in rows}) != 1:
        raise ValueError("simulate accepts one instrument at a time")
    for bar, signal in zip(rows, signals):
        if (bar["instrument"], bar["bar_open_time"]) != (signal["instrument"], signal["bar_open_time"]):
            raise ValueError("Bars and signals must align")
    execution, exit_spec = spec["execution"], spec["exit"]
    slip = execution["slippage_bps_per_side"] / 10000
    position = None
    pending_entry = None
    pending_exit = None
    result = []

    def finish(bar, raw_price, reason, timestamp, precision):
        nonlocal position
        price = raw_price * (1-position["direction"]*slip)
        gross = position["direction"] * (price-position["price"]) / position["price"]
        days = (timestamp-position["time"]).total_seconds() / 86400
        costs = execution["commission_bps_round_trip"] / 10000 + execution["financing_bps_per_day"] / 10000 * days
        result.append(asdict(Trade(bar["instrument"], position["direction"], position["signal_time"],
                                  position["time"], timestamp, precision, position["price"], price, reason,
                                  position["bars"], gross, costs, gross-costs)))
        position = None

    for bar, signal in zip(rows, signals):
        exited = False
        if pending_entry is not None and position is None:
            side, signal_time = pending_entry
            price = quote(bar, -side, "open", execution) * (1+side*slip)
            position = {"direction": side, "price": price, "time": bar["bar_open_time"],
                        "signal_time": signal_time, "bars": 0}
        pending_entry = None
        if position is not None:
            side, entry = position["direction"], position["price"]
            opening = quote(bar, side, "open", execution)
            low, high = quote(bar, side, "low", execution), quote(bar, side, "high", execution)
            stop = entry * (1-side*exit_spec["stop_loss_pct"])
            target = entry * (1+side*exit_spec["take_profit_pct"]) if "take_profit_pct" in exit_spec else None
            stop_at_open = opening <= stop if side == 1 else opening >= stop
            target_at_open = target is not None and (opening >= target if side == 1 else opening <= target)
            stop_inside = low <= stop if side == 1 else high >= stop
            target_inside = target is not None and (high >= target if side == 1 else low <= target)
            if stop_at_open:
                finish(bar, opening, "stop_gap", bar["bar_open_time"], "bar_open")
            elif target_at_open:
                finish(bar, target, "take_profit", bar["bar_open_time"], "bar_open")
            elif pending_exit:
                finish(bar, opening, pending_exit, bar["bar_open_time"], "bar_open")
            else:
                position["bars"] += 1
                if stop_inside:
                    finish(bar, stop, "stop_loss", bar["bar_close_time"], "bar_interval")
                elif target_inside:
                    finish(bar, target, "take_profit", bar["bar_close_time"], "bar_interval")
            if position is None:
                exited = True
        pending_exit = None
        if position is not None:
            direction = "long" if position["direction"] == 1 else "short"
            if signal[f"exit_{direction}"]:
                pending_exit = "indicator_exit"
            elif position["bars"] >= exit_spec.get("max_holding_bars", float("inf")):
                pending_exit = "time_exit"
        elif not exited:
            long, short = signal["entry_long"], signal["entry_short"]
            if bool(long) != bool(short):
                pending_entry = (1 if long else -1, bar["bar_close_time"])
    if position is not None:
        finish(rows[-1], quote(rows[-1], position["direction"], "close", execution), "end_of_data", rows[-1]["bar_close_time"], "bar_close")
    return result
