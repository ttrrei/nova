WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (close_sma24_distance_atr < -2.0) AS _condition_0 FROM s0),
s2 AS (SELECT *, CASE WHEN count(_condition_0) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) = 6 THEN bool_or(_condition_0) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) END AS _condition_1 FROM s1),
s3 AS (SELECT *, (close_sma24_distance_atr > -1.5) AS _condition_2 FROM s2),
s4 AS (SELECT *, (close_sma24_distance_atr < 0.0) AS _condition_3 FROM s3),
s5 AS (SELECT *, (_condition_1 AND _condition_2 AND _condition_3) AS _condition_4 FROM s4),
s6 AS (SELECT *, (close_sma24_distance_atr > 2.0) AS _condition_5 FROM s5),
s7 AS (SELECT *, CASE WHEN count(_condition_5) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) = 6 THEN bool_or(_condition_5) OVER (PARTITION BY instrument ORDER BY bar_open_time ROWS BETWEEN 5 PRECEDING AND CURRENT ROW) END AS _condition_6 FROM s6),
s8 AS (SELECT *, (close_sma24_distance_atr < 1.5) AS _condition_7 FROM s7),
s9 AS (SELECT *, (close_sma24_distance_atr > 0.0) AS _condition_8 FROM s8),
s10 AS (SELECT *, (_condition_6 AND _condition_7 AND _condition_8) AS _condition_9 FROM s9),
s11 AS (SELECT *, (close_sma24_distance_atr >= 0.0) AS _condition_10 FROM s10),
s12 AS (SELECT *, (close_sma24_distance_atr <= 0.0) AS _condition_11 FROM s11)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_4, FALSE) AS entry_long, coalesce(_condition_9, FALSE) AS entry_short, coalesce(_condition_10, FALSE) AS exit_long, coalesce(_condition_11, FALSE) AS exit_short FROM s12 ORDER BY instrument, bar_open_time
