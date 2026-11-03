# 旧输入与新数据契约

| 输入 | 必需字段 | 周期 |
|---|---|---|
| raw / all_data | instrument, time, is_complete, volume, mid_o/h/l/c | 显式 source-minutes，通常 1 |
| OHLCV / Gold | instrument, time, open/high/low/close, volume, n_bars | 明确 5 或 60 等源周期 |
| canonical | instrument, bar_open_time, bar_close_time, open/high/low/close, volume, is_complete | 两个时刻之差须符合源周期 |

旧 time 为 Bar 开始时刻，新 close_time 为开始＋已知周期，表示信号最早可用时刻。时间必须带时区；明确知道 naive 时间为 UTC 才用 --assume-utc。

支持旧 bid_o/h/l/c、ask_o/h/l/c 和新 bid_open/high/low/close、ask_open/high/low/close。列全有或全无；每行允许八项全部为空，部分缺失报错。有实测报价时不叠加合成点差，没有时使用 Mid＋配置点差。

过滤 is_complete=false。旧聚合只有 n_bars=源周期分钟数才算完整。重复键按完整报价优先、文件名、价格和载荷字段排序选择；完全相同载荷属于等价重复。转换记录保留前后行数。

不补 Bar。时间模式 N Bar 指实际 N 根观测；重采样要求完整覆盖 UTC 桶，尾部不完整桶丢弃。不同格式、周期或字段映射分别导入。重采样不能复用原周期特征。

36 个已识别的旧缓存列与 h1_* 投影不自动导入。数据生产版本记录为 unknown，不把审阅代码的 commit 冒充为文件的生成 commit。

仓库中没有真实行情载荷，包内也不提供真实市场数据。
