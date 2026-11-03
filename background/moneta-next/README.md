# Moneta Next v0.2

从旧 Moneta 迁移数据平台与指标资产，建立 YAML → SQL → Trade 研究流程。先读 [START_HERE.md](START_HERE.md)，详情见 [迁移指南](migration/MIGRATION_GUIDE.md)。

来源固定为 [ttrrei/moneta@67896d60](https://github.com/ttrrei/moneta/tree/67896d60bc6ecf73fc6aec42aee469a24cce3564)。包内含 40 个原始参考文件、来源哈希、逐文件复用决定及适配代码。旧仓库没有提交实际行情，需要使用你本地已有的 data 目录。

## 安装

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell 使用 .venv\Scripts\Activate.ps1
python -m pip install -e .
moneta-doctor
python -m unittest discover -s tests -v
```

重新计算完整指标和下载行情需要额外依赖：

```bash
python -m pip install -e '.[legacy,ingestion,test]'
moneta-doctor
python -m unittest discover -s tests -v
```

TA-Lib 无法使用平台 wheel 时，按其官方文档安装底层库。旧 requirements.lock 只作参考，不强制安装旧 LLM SDK 和云平台依赖。

## 接入已有行情

旧项目已有 1h OHLCV：

```bash
moneta-data --legacy-root /path/to/old/moneta --dataset ohlcv_1h --output data/imports/h1.parquet
python -m moneta_next --data data/imports/h1.parquet --strategy examples/trend_hold.yaml
```

复用已计算的 Gold 特征，不需要 TA-Lib 重算：

```bash
moneta-data --legacy-root /path/to/old/moneta --dataset features_1h --reuse-features --output data/imports/gold_h1.parquet
python -m moneta_next --data data/imports/gold_h1.parquet --profile imported --strategy examples/legacy_psar_confirmation.yaml
```

从原始 1m 重新聚合，保留可用的 Bid/Ask：

```bash
moneta-data --legacy-root /path/to/old/moneta --dataset raw --target-minutes 60 --output data/imports/h1_quotes.parquet
python -m moneta_next --data data/imports/h1_quotes.parquet --profile legacy --strategy examples/legacy_supertrend.yaml
```

也可指定独立文件：

```bash
moneta-data --source /path/to/all_data.parquet --source-minutes 1 --target-minutes 60 --output data/imports/h1.parquet
```

输出放入新项目；转换器拒绝覆盖源文件或将输出写入正在扫描的旧目录。重采样不继承旧特征，必须在目标周期重算。详细字段规则见 migration/DATA_CONTRACT.md。

## 特征模式

| --profile | 用途 | 范围 |
|---|---|---|
| starter（默认） | 验证行情与 Trade | 9 个基础/转换特征 |
| imported | 复用已转换 Gold | 原 262 个指标名中允许复用的 226 个，加可推导的 PSAR/ST 翻转事件 |
| legacy | 使用迁移算法重新计算 | 262 个原输出＋24 个翻转事件，与 starter 合并后 293 个注册名 |

具体文件未必包含所有列，缺少策略依赖会明确报错。FEATURE_MAP.csv 给出完整对应。

旧缓存排除 36 个名字：BBANDS/AROON 返回顺序问题影响 35 个，另有文档标记尚未重建的 VWAP。legacy 模式使用修正后的算法。旧 h1_* 投影与实验性 catalogue 特征没有自动进入运行时。

Hybrid Feature Store 使用核心宽表＋Trend/Legacy Domain 宽表，原子导出 Parquet，并复用旧目录代码登记 store_* 视图。数据内容、代码和 profile 共同识别缓存。特征计算与 Trade 执行逐标的进行。

## 下载（可选）

在本机设置 OANDA_API_TOKEN，再执行：

```bash
moneta-download --instrument EUR_USD --since 2025-01-01T00:00:00Z --until 2025-01-03T00:00:00Z --output data/raw/eurusd.csv
```

默认 practice 行情端点，MBA、smooth=false，复用旧分页、去重与原子写入。没有下单功能。本轮未请求真实 API。

## 无真实数据时验证功能

```bash
python examples/generate_demo.py
python -m moneta_next --data data/demo.csv --strategy examples/trend_hold.yaml
python -m moneta_next --data data/demo.csv --strategy examples/mean_reversion.yaml
```

SYNTH_A/B 仅用于 starter。legacy 模式保留原项目 21 个标的的 session 配置；新标的需明确其 session。

## 输出与口径

runs/<run_id>/ 包含 trades.csv、signals.csv、summary.json、manifest.json、compiled.sql、feature_catalog.json。转换另存 .import.json，记录源文件哈希、过滤/去重行数及排除列。

2% 相对每笔实际开仓价，多单向下、空单向上；指标信号下一根开盘执行，价格止损盘中处理。未知同根顺序亏损优先，跳空不强行填回止损价。每标的一笔 Trade，不管理仓位、杠杆或账户回撤。

年化 Trade 收益分数＝单笔净收益率合计÷完整区间日历年数，不是账户 CAGR。按实际开仓统计 UTC 自然月，无交易月保留为 0。原始 volume 作为成交量代理；旧数据作为历史研究材料复用。

## 验证状态

见 verification/STATUS.md 和 test_summary.json。当前环境缺少 DuckDB、TA-Lib、pandas-ta-classic 和 requests，下载依赖失败；相应集成检查明确跳过。已执行的 NumPy、时间对齐、来源一致性、接口契约、YAML、Trade 和统计检查单独列出。不声称 262 列数值或完整链路已经端到端验证。

CI 安装全部可选依赖，并要求全部测试执行；远程工作流尚未运行。
