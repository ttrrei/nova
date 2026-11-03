WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, FALSE AS _condition_0 FROM s0),
s2 AS (SELECT *, (ema_alignment_6_24 = -1.0) AS _condition_1 FROM s1),
s3 AS (SELECT *, (close_ema60_distance_atr < 0.0) AS _condition_2 FROM s2),
s4 AS (SELECT *, (rsi_14 > 52.0) AS _condition_3 FROM s3),
s5 AS (SELECT *, CASE WHEN count(_condition_3) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) = 12 THEN bool_or(_condition_3) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 11 PRECEDING AND CURRENT ROW) END AS _condition_4 FROM s4),
s6 AS (SELECT *, (rsi_14 < 50.0) AS _condition_5 FROM s5),
s7 AS (SELECT *, CASE WHEN count(_condition_5) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 0 PRECEDING AND CURRENT ROW) = 1 THEN bool_and(_condition_5) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 0 PRECEDING AND CURRENT ROW) END AS _condition_6 FROM s6),
s8 AS (SELECT *, (supertrend_direction = -1.0) AS _condition_7 FROM s7),
s9 AS (SELECT *, (_condition_1 AND _condition_2 AND _condition_4 AND _condition_6 AND _condition_7) AS _condition_8 FROM s8),
s10 AS (SELECT *, (supertrend_direction = -1.0) AS _condition_9 FROM s9),
s11 AS (SELECT *, (supertrend_direction = 1.0) AS _condition_10 FROM s10)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_0, FALSE) AS entry_long, coalesce(_condition_8, FALSE) AS entry_short, coalesce(_condition_9, FALSE) AS exit_long, coalesce(_condition_10, FALSE) AS exit_short FROM s11 ORDER BY instrument, bar_open_time
