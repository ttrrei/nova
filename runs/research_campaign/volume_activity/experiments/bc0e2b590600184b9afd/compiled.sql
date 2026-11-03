WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (breakout_up_24 = TRUE) AS _condition_0 FROM s0),
s2 AS (SELECT *, (relative_volume_24 > 1.5) AS _condition_1 FROM s1),
s3 AS (SELECT *, (_condition_0 AND _condition_1) AS _condition_2 FROM s2),
s4 AS (SELECT *, (breakout_down_24 = TRUE) AS _condition_3 FROM s3),
s5 AS (SELECT *, (relative_volume_24 > 1.5) AS _condition_4 FROM s4),
s6 AS (SELECT *, (_condition_3 AND _condition_4) AS _condition_5 FROM s5),
s7 AS (SELECT *, (range_position_24 < 0.5) AS _condition_6 FROM s6),
s8 AS (SELECT *, (range_position_24 > 0.5) AS _condition_7 FROM s7)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_2, FALSE) AS entry_long, coalesce(_condition_5, FALSE) AS entry_short, coalesce(_condition_6, FALSE) AS exit_long, coalesce(_condition_7, FALSE) AS exit_short FROM s8 ORDER BY instrument, bar_open_time
