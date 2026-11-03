WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (close_sma24_distance_atr < -2.0) AS _condition_0 FROM s0),
s2 AS (SELECT *, (close_sma24_distance_atr > 2.0) AS _condition_1 FROM s1),
s3 AS (SELECT *, (close_sma24_distance_atr >= 0.0) AS _condition_2 FROM s2),
s4 AS (SELECT *, (close_sma24_distance_atr <= 0.0) AS _condition_3 FROM s3)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_0, FALSE) AS entry_long, coalesce(_condition_1, FALSE) AS entry_short, coalesce(_condition_2, FALSE) AS exit_long, coalesce(_condition_3, FALSE) AS exit_short FROM s4 ORDER BY instrument, bar_open_time
