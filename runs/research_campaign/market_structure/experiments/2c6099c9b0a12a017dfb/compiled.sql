WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (breakout_up_24 = TRUE) AS _condition_0 FROM s0),
s2 AS (SELECT *, (range_position_24 > 0.75) AS _condition_1 FROM s1),
s3 AS (SELECT *, CASE WHEN count(_condition_1) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) = 2 THEN bool_and(_condition_1) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 1 PRECEDING AND CURRENT ROW) END AS _condition_2 FROM s2),
s4 AS (SELECT *, lag(_condition_0, 2) OVER (PARTITION BY instrument ORDER BY bar_open_time) AND _condition_2 AS _condition_3 FROM s3),
s5 AS (SELECT *, (close_ema60_distance_atr > 0.0) AS _condition_4 FROM s4),
s6 AS (SELECT *, (relative_volume_24 > 1.0) AS _condition_5 FROM s5),
s7 AS (SELECT *, (_condition_3 AND _condition_4 AND _condition_5) AS _condition_6 FROM s6),
s8 AS (SELECT *, FALSE AS _condition_7 FROM s7),
s9 AS (SELECT *, (range_position_24 < 0.5) AS _condition_8 FROM s8),
s10 AS (SELECT *, (range_position_24 > 0.5) AS _condition_9 FROM s9)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_6, FALSE) AS entry_long, coalesce(_condition_7, FALSE) AS entry_short, coalesce(_condition_8, FALSE) AS exit_long, coalesce(_condition_9, FALSE) AS exit_short FROM s10 ORDER BY instrument, bar_open_time
