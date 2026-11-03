WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (failed_breakout_down_24 = TRUE) AS _condition_0 FROM s0),
s2 AS (SELECT *, (range_position_24 < 0.5) AS _condition_1 FROM s1),
s3 AS (SELECT *, (efficiency_24 < 0.25) AS _condition_2 FROM s2),
s4 AS (SELECT *, (range_position_24 > 0.1) AS _condition_3 FROM s3),
s5 AS (SELECT *, (_condition_0 AND _condition_1 AND _condition_2 AND _condition_3) AS _condition_4 FROM s4),
s6 AS (SELECT *, (failed_breakout_up_24 = TRUE) AS _condition_5 FROM s5),
s7 AS (SELECT *, (range_position_24 > 0.5) AS _condition_6 FROM s6),
s8 AS (SELECT *, (efficiency_24 < 0.25) AS _condition_7 FROM s7),
s9 AS (SELECT *, (range_position_24 < 0.9) AS _condition_8 FROM s8),
s10 AS (SELECT *, (_condition_5 AND _condition_6 AND _condition_7 AND _condition_8) AS _condition_9 FROM s9),
s11 AS (SELECT *, (range_position_24 >= 0.5) AS _condition_10 FROM s10),
s12 AS (SELECT *, (range_position_24 <= 0.5) AS _condition_11 FROM s11)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_4, FALSE) AS entry_long, coalesce(_condition_9, FALSE) AS entry_short, coalesce(_condition_10, FALSE) AS exit_long, coalesce(_condition_11, FALSE) AS exit_short FROM s12 ORDER BY instrument, bar_open_time
