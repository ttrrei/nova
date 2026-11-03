WITH s0 AS (SELECT * FROM features),
s1 AS (SELECT *, (utc_hour >= 13.0) AS _condition_0 FROM s0),
s2 AS (SELECT *, (utc_hour < 17.0) AS _condition_1 FROM s1),
s3 AS (SELECT *, (ema_alignment_6_24 = 1.0) AS _condition_2 FROM s2),
s4 AS (SELECT *, (rsi_14 > 55.0) AS _condition_3 FROM s3),
s5 AS (SELECT *, (_condition_0 AND _condition_1 AND _condition_2 AND _condition_3) AS _condition_4 FROM s4),
s6 AS (SELECT *, (utc_hour >= 13.0) AS _condition_5 FROM s5),
s7 AS (SELECT *, (utc_hour < 17.0) AS _condition_6 FROM s6),
s8 AS (SELECT *, (ema_alignment_6_24 = -1.0) AS _condition_7 FROM s7),
s9 AS (SELECT *, (rsi_14 < 45.0) AS _condition_8 FROM s8),
s10 AS (SELECT *, (_condition_5 AND _condition_6 AND _condition_7 AND _condition_8) AS _condition_9 FROM s9),
s11 AS (SELECT *, (ema_alignment_6_24 = -1.0) AS _condition_10 FROM s10),
s12 AS (SELECT *, (ema_alignment_6_24 = 1.0) AS _condition_11 FROM s11)
SELECT instrument, bar_open_time, bar_close_time, coalesce(_condition_4, FALSE) AS entry_long, coalesce(_condition_9, FALSE) AS entry_short, coalesce(_condition_10, FALSE) AS exit_long, coalesce(_condition_11, FALSE) AS exit_short FROM s12 ORDER BY instrument, bar_open_time
