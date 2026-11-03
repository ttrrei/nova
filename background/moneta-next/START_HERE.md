# Moneta Next v0.2：先做什么

保留本轮选择：DuckDB＋Parquet；核心宽表＋Domain 宽表；YAML 策略和 SQL 时间条件；开仓价 2% 不利变动作为退出；只找 Trade，不建设仓位、保证金、账户回撤或旧 OOS 治理。

## 本版资产

目录盘点 1,650 个文件，选择性读取并保留 40 个核心文件。固定来源 67896d60。7 个模块按原字节复用，默认指标计算模块经过适配。262 个原指标输出加 24 个翻转事件，与 starter 合并后有 293 个注册名。

适配器支持旧 raw CSV、all_data、5m/1h OHLCV 和 Gold Parquet。修复 BBANDS、AROON 返回顺序及首根 gap 标志；旧受影响缓存列排除。

## 先选一个入口

| 已有的本地资产 | 先做什么 |
|---|---|
| ohlcv_1h.parquet | 按 README 导入，用 starter 跑通 Trade |
| ohlcv_1h_features.parquet | --reuse-features 导入，用 --profile imported 复用 PSAR/EMA/ST |
| raw_csv / all_data.parquet | 聚合到目标周期，用 --profile legacy 重算指标 |

先使用一份可解释的行情文件，核对十几笔实际开仓、2% 止损、反向退出与成本，再扩大资产池。source-minutes 是源周期，YAML timeframe_minutes 必须与输出周期一致。新增 legacy 示例为 H1。

## 本地验收

1. 安装依赖，运行 moneta-doctor 与全部测试，补跑当前缺依赖的检查。
2. 核对 .import.json：源文件、日期、行数、过滤/去重和排除列。
3. 核对首批 Trade 与完整月份统计；第二次运行确认缓存复用。
4. 统一数据覆盖区间，再按年化 Trade 分数比较候选。

旧 Gold 已去 warm-up，imported 不再次丢 360 根。重新计算 legacy 保留原始 Bar，但将前 360 根的迁移指标置为未知。summary.json 报告真实统计窗口。

## 后续顺序

完成真实数据验收，再把已迁移的结构事件原语注册为特征，扩展参数化注册与受限 YAML 候选生成。旧 50 项研究供 AI 了解旧尝试，不自动成为有效 Alpha 标签。H1→M5 对齐 helper 已独立测试，完整多周期策略运行仍待接入。

逐文件决定见 migration/REUSE_MATRIX.csv；逐特征对应见 FEATURE_MAP.csv；源码差异、来源与复用理由见迁移指南。整个目录可以作为新仓库初始内容，当前未新建远程仓库。
