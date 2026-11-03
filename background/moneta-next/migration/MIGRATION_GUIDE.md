# 旧 Moneta 到 Next v0.2 的迁移说明

来源固定为 [ttrrei/moneta@67896d60](https://github.com/ttrrei/moneta/tree/67896d60bc6ecf73fc6aec42aee469a24cce3564)。40 个 reference 文件与固定 Git blob SHA 已校验。source_inventory.json 为目录级盘点，不代表对全部 1,650 个文件逐行审计。

## 复用决定

| 旧资产 | v0.2 处理 | 理由 |
|---|---|---|
| supertrend / psar / utils | 原字节迁入 vendor | 保留原算法和参数命名 |
| market_structure / catalogue | 原样迁移原语并独立测试，尚未全部注册 | 保存计算资产，先不自动晋级实验定义 |
| table_catalog | 原样作为 storage.py，用 store_* 视图 | 复用 Parquet 目录，保护当前计算表 |
| extract_oanda | 原样迁入 vendor，加显式路径包装 | 保留分页和去重，移除运行入口对旧 config 的依赖 |
| load_data | UTC、去重、原子 Parquet 约定适配到 data_io | 调整字段与目录耦合，对每个源文件检查 Schema |
| aggregate_ohlcv | 聚合逻辑适配，补 Bid/Ask 和完整桶检查 | 旧聚合仅保留 Mid |
| indicators 计算段 | 拆为 legacy_engine，修复具体问题 | 保留默认指标名、参数组合，移除旧 IO/调度 |
| H1→M5 对齐 | 独立 alignment helper | 保留收盘可用性算法，完整多周期 DSL 后续接入 |
| sanity_check / profile_check | 校验规则适配，源码归档 | 使用新契约和元数据 |
| extract_oci | 原源码参考，按需再接 | 先使用本地数据或 OANDA 入口 |
| 旧 engine / strategy_lib | 原实现参考，不导入运行时 | 旧会计、退出口径和工作流与新 Trade 目标不同 |
| 50 项 catalogue / 200 策略总结 | 选定定义与研究记录归档 | 作为 AI 研究材料，不引入旧 OOS/晋级工作流 |

逐文件目标、状态与后续动作见 REUSE_MATRIX.csv。所有源码保留 Apache 2.0 来源与许可。

## 明确修复

1. **BBANDS**：旧代码用 mid, upper, lower 接收，官方为 upper, middle, lower。修复影响 bb_mid、bb_upper、bb_width、bb_pctb 和 sqz_on。参考[官方契约](https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/overlap_studies.md)。
2. **AROON**：旧代码用 up, down 接收，官方为 down, up。参考[官方契约](https://github.com/TA-Lib/ta-lib-python/blob/master/docs/func_groups/momentum_indicators.md)。
3. **首根 gap**：旧函数使用 np.empty 且未设置第 0 项，改为零初始化。

接口哨兵测试验证了修复后的实际调用接线，不冒充 TA-Lib 数值平价验证。完整数值对照测试另外提供，当前缺依赖未运行。源文件保留于 reference，差异见 patches/legacy_engine.patch。

## 旧缓存的使用边界

旧 docs/README 已说明 session DST 修正后 Gold VWAP 尚未重建，因此导入时排除 vwap。旧 AROON/BBANDS 相关缓存也不继承。共排除 36 个输出名，原 262 个中剩余 226 个允许导入。重新计算模式使用已修复算法。

旧 5m Gold 的 35 个 h1_* 投影不自动导入。alignment helper 使用 context_close <= signal_close，并有独立测试；完整多周期策略执行尚未连接。

旧 session 表中的 UK100 使用 Europe/Berlin。研究伦敦时段之前需要核对业务意图；本版保留原市场定义，没有把它当作已核实的伦敦开盘规则。

旧研究如果依赖本次修复列，需要重新检查相关结论。研究知识文件记录的是旧报告陈述，未在本轮重跑。既有数据仍可作为研究/AI 材料，不增加旧 OOS 工作流。

## 重新计算与注册

原指标计算输出 262 项；H1 的 270 列还包括 8 个行情与键字段，M5 的 305 列再包括 35 个 H1 投影。保留窗口 6/12/24/60/120、原 MACD 配对、两组 PSAR 参数和两个 ST multiplier。

在方向列上补充 24 个单 Bar 翻转事件。与 starter 的共享 SMA6/SMA24 合并后，目录共 293 个注册名。共享 SMA 仍由 starter SQL 计算，不覆盖为旧缓存值；未经平价测试，不声称逐位相同。

legacy 模式前 360 根迁移指标置为未知；原始 Bar 和统计区间保留。imported 使用 Gold 已有的 warm-up 边界，不再删除 360 根。不同输入历史、时间区间和初始递归状态下，不直接比较数值或年化分数。

## 数据与规模

见 DATA_CONTRACT.md。新转换器逐文件检查契约，统一 UTC，过滤不完整数据，确定性去重。重采样保留全覆盖 UTC 桶，不补缺 Bar。只有完整源报价才能形成输出 Bid/Ask；缺报价的桶保留 Mid，交给明确点差配置。

特征和 Trade 按标的处理。特征缓存含数据、代码、profile 身份，结果导出 Parquet，并登记元数据和查询视图。当前不承诺未经真实数据测量的加速倍数。

## 下一步验收

1. 在旧项目已有虚拟环境或新环境安装依赖，执行全部检查。
2. 迁移一个标的的 H1 数据，核对时间、报价和 Trade。
3. 在同一历史、warm-up 条件下，对照 imported 和 legacy 的未受修复影响列。
4. 扩大资产池，查看逐月实际开仓、统一年化 Trade 分数，测量性能瓶颈。
5. 注册结构事件、扩展参数化特征与有限候选生成。

缺依赖跳过项见 verification/test_summary.json。没有真实行情或完整依赖时，不声称已完成市场数据数值复核。
