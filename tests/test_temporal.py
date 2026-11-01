from datetime import timedelta

import duckdb

from nova.compiler import compile_strategy
from test_core import START, spec


def evaluate(condition, states, events=None):
    with duckdb.connect() as con:
        con.execute(
            "CREATE TABLE features(instrument VARCHAR,bar_open_time TIMESTAMPTZ,bar_close_time TIMESTAMPTZ,sma_alignment_6_24 INTEGER,sma_cross_up_6_24 BOOLEAN)"
        )
        for i, state in enumerate(states):
            con.execute(
                "INSERT INTO features VALUES(?,?,?,?,?)",
                [
                    "TEST",
                    START + timedelta(hours=i),
                    START + timedelta(hours=i + 1),
                    state,
                    (events or [False] * len(states))[i],
                ],
            )
        value = spec()
        value["entry"] = {"long": condition}
        return [r[3] for r in con.execute(compile_strategy(value)).fetchall()]


C = {"feature": "sma_alignment_6_24", "op": "eq", "value": 1}
E = {"feature": "sma_cross_up_6_24", "op": "eq", "value": True}


def test_after_event_confirms_third_following_close_and_failure_cancels():
    c = {"after_event": {"bars": 3, "event": E, "condition": C}}
    assert evaluate(c, [1, 1, 1, 1, 1], [True, False, False, False, False]) == [
        False,
        False,
        False,
        True,
        False,
    ]
    assert (
        evaluate(c, [1, 1, -1, 1, 1], [True, False, False, False, False]) == [False] * 5
    )


def test_nested_temporal_held_for_and_within_and_unknown_negation():
    assert evaluate({"held_for": {"bars": 3, "condition": C}}, [1, 1, 1, -1, 1]) == [
        False,
        False,
        True,
        False,
        False,
    ]
    assert evaluate(
        {"within": {"bars": 3, "condition": E}},
        [1] * 5,
        [True, False, False, False, False],
    ) == [False, False, True, False, False]
    assert evaluate({"not": C}, [None, None, 1, -1]) == [False, False, False, True]
    nested = {
        "held_for": {"bars": 2, "condition": {"held_for": {"bars": 2, "condition": C}}}
    }
    assert evaluate(nested, [1, 1, 1, 1]) == [False, False, True, True]
