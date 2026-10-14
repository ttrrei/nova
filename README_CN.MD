# Nova — 量化策略寻优引擎

> 极轻量、高复用、低算力成本的 Alpha 策略探索与寻优引擎。
> 仅关注策略寻优与 Alpha 算法验证；实盘订单执行、流式计算与运维解耦为独立的后续工程。

---

## 项目简介

**Nova** 是一个面向外汇、贵金属、原油及股指等主流交易标的的量化策略自动发现系统。系统以 **多时间框架状态转换** 为核心交易范式，通过 AI 驱动的策略生成管线与向量化回测引擎，实现策略从构想、编译、去重到评估的全自动闭环。

### 核心特性

- **AI 驱动的策略生成**：Gemini + Gemma 多模型协作，实现"构想 → 编译 → 审计"三级流水线
- **YAML 自描述策略**：策略以 YAML 自包含格式表达，AI 可读可写，自动回写评估结果
- **四级递进去重引擎**：语法规范化 → SHA-256 指纹 → AI 自省重试 → 信号相关性去重，杜绝冗余算力浪费
- **向量化回测 (DuckDB)**：基于 R-Multiple 归一化收益，悲观碰撞判定，单持仓状态机
- **严格防过拟合**：时间均匀性硬门槛、胜率波动率约束、权益厚度积分评估
- **Medallion 数据架构**：Bronze → Silver → Gold 三层分区，DuckDB 零拷贝查询

---

## 交易范式

```
1h K线 ─── 趋势方向判定 ───┐
                            ├──► 状态转换入场信号
5m K线 ─── 入场点捕捉 ─────┘
```

- **趋势判断**：1 小时周期确定方向偏好
- **入场执行**：5 分钟周期捕捉状态转换 (State Transition) 入场时机
- **未来函数消除**：5min 信号计算时，1h 特征严格锁定为上一根已完全收盘的 K 线

---

## 数据架构

采用 **Medallion Architecture** 结合 DuckDB 本地向量化查询：

| 层级 | 说明 | 存储格式 |
|------|------|----------|
| **Bronze** | 从 OCI Object Storage 拉取的 1min OHLCV 原始数据（按年/月/标的分区） | Parquet (OCI Object Storage) |
| **Silver** | 清洗对齐 + 重采样 (1min → 5min / 1h)，Session 隔离 | Parquet (本地) |
| **Gold** | 宽表特征库 (趋势 / 波动率 / 动量)，参数稀疏化 `[12,24,48,72]` | Parquet (本地) |

- **标的覆盖**：21 个主流标的（外汇直盘/交叉盘、贵金属、原油、股指）
- **数据深度**：1 年历史 1 分钟粒度
- **零拷贝查询**：基于 DuckDB `VIEW` 实现基表与宽表的无缝拼接

---

## AI 策略生成管线

### 三级模型分工

```
┌──────────────────────────────────────────────────────────────┐
│  Gemini 3.5 Flash Lite — 策略类/模板架构师                    │
│  职责：生成新 YAML 模版 · 审计 Strategy Zoo · 审查 Backlog    │
└──────────────────────┬───────────────────────────────────────┘
                       │ 下发模版
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Gemma 4 26B — 类内策略微调员 (两阶段 Call)                    │
│  Call 1 (Idea)：参数地图 → Alpha 构想 (≤250 Tokens)           │
│  Call 2 (Compiler)：Idea + Schema → 可执行 YAML / 溢出归档    │
└──────────────────────────────────────────────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│  Gemma 4 31B — 自定义特征编写员                                │
│  职责：Python / DuckDB SQL 新指标 · AST 审查 · Tail Check 沙盒│
└──────────────────────────────────────────────────────────────┘
```

### 两阶段生成流程

1. **Idea 阶段**：输入压缩的参数空间地图（Top-2 标杆 + 死区禁区 + 近 3 次轨迹），输出纯文本 Alpha 构想
2. **Compiler 阶段**：将构想映射至 YAML Schema；不可表达的逻辑剥离至 `ideas_backlog/unsupported_ideas.json`

---

## 四级递进去重引擎

在消耗向量化回测算力之前，层层拦截重复策略：

```
Gemma 生成 YAML
       │
       ▼
 Level 1 ── 语法规范化 & 参数离散化 (AST 重排 + 网格对齐)
       │
       ▼
 Level 2 ── SHA-256 指纹 Hash 库 (秒级比对，命中即拦截)
       │                                    │
       │ (未命中)                        (命中) → Level 3
       ▼                                    │
  向量化回测                        AI 自省重试 Loop
       │                          (连续 3 次重复 → 触发 Gemini 重新生成模版)
       ▼
 Level 4 ── 信号相关性去重 (买卖向量相关系数 > 90% → 淘汰低绩效者)
       │
       ▼
  入库 Strategy Zoo
```

---

## 回测引擎设计

### 核心机制

| 机制 | 说明 |
|------|------|
| **R-Multiple 归一化** | 剥离仓位管理，按初始止损距离标准化为 1R，评估纯 Alpha |
| **悲观碰撞判定** | 单根 5min K 线 TP/SL 同时触及时，强制判定为优先触及止损 |
| **单持仓状态机** | 同一标的持仓未平仓前，忽略后续入场信号，禁止叠加开仓 |
| **零防抖设计** | 不设时间冷却，将震荡磨损作为检验策略 Alpha 覆盖能力的硬指标 |
| **标的属性表** | 21 个标的专属 Pip 大小、动态/百分比点差，禁止硬编码 |

### 评估指标体系

**基础绩效**
- 夏普比率 (Sharpe Ratio)
- 卡玛比率 (Calmar Ratio)
- 盈亏比 (Profit Factor)
- 最大回撤 (Max Drawdown)

**防过拟合硬约束**
- 时间均匀性：每周/每月交易笔数稳定分布
- 胜率稳定性：周/月度胜率标准差 $\sigma_{win\_rate} < 0.15$

**高阶评估**
- 持仓姿态比：正/负收益持仓时间比 $\frac{T_{profit}}{T_{loss}}$
- 权益厚度 (Area Ratio)：

$$
\text{Area Ratio} = \frac{\int PnL_{+}(t) \, dt}{\int |PnL_{-}(t)| \, dt}
$$

- 目标到达率 (First-to-Hit)：率先触及指定收益/亏损比例的分布概率

---

## Schema 演进管道

```
unsupported_ideas.json  ──►  Gemini 定期审查  ──►  yaml_parser.py 重构方案
        ▲                                                    │
        │                                                    ▼
  Gemma Call 2 剥离                                  DuckDB SQL 引擎扩展
  无法表达的逻辑                                     系统表达力版本迭代
```

未被当前 YAML Schema 支持的策略逻辑自动沉淀至 Backlog，由 Gemini 定期审查高频/高潜力条目，驱动系统的表达能力演进。

---

## 项目结构

```
nova/
├── data_pipeline/
│   ├── sync_oci.py              # 从 OCI Object Storage 增量拉取 Parquet 数据
│   ├── build_silver.py          # 1min → 5min / 1h 聚合与 Session 隔离
│   └── build_gold_features.py   # 稀疏参数宽表生成 (12, 24, 48, 72)
├── ai_engine/
│   ├── prompts/                 # 提示词模版库 (Idea & Compiler 模版)
│   ├── gemma_yaml_gen.py        # Gemma 26B 两阶段调用与 Hash 拦截重试
│   ├── gemma_feature_writer.py  # Gemma 31B 特征编写与 Tail Check 沙盒
│   └── gemini_auditor.py        # Gemini 3.5 模版生成、Backlog 审查与全局审计
├── backtest_engine/
│   ├── symbol_specs.py          # 21 个标的点差与 Pip 属性表
│   ├── yaml_parser.py           # YAML → DuckDB 状态转换 SQL
│   ├── deduplicator.py          # SHA-256 指纹 Hash 与信号相关性去重
│   ├── vectorized_tester.py     # R-Multiple 向量化回测引擎
│   └── metrics_evaluator.py     # 评估指标计算器
├── ideas_backlog/
│   └── unsupported_ideas.json   # Gemma 剥离的溢出想法归档
├── strategies_zoo/              # 通过硬性指标审核的 YAML 策略归档
├── DESIGN.md                    # 系统设计文档
├── README.md
└── main.py                      # 寻优主流程调度入口
```

---

## 技术栈

| 类别 | 技术选型 |
|------|----------|
| 语言 | Python 3.12+ |
| 数据引擎 | DuckDB + Apache Parquet |
| 对象存储 | OCI Object Storage |
| 数据源 | OCI Object Storage（上游：OANDA API） |
| AI 模型 | Gemini 3.5 Flash Lite · Gemma 4 26B · Gemma 4 31B |
| 策略描述 | YAML (自包含 spec + evaluation_results) |

---

## 快速开始

> 🚧 项目处于初始化阶段，以下步骤将随开发进度逐步完善。

```bash
# 克隆仓库
git clone https://github.com/<your-org>/nova.git
cd nova

# 安装依赖
pip install -r requirements.txt

# 运行主流程
python main.py
```

---

## 项目路线图

- [x] 系统设计文档定稿
- [ ] 数据管线 (Bronze → Silver → Gold)
- [ ] YAML 策略 Schema 定义
- [ ] 向量化回测引擎
- [ ] 去重引擎
- [ ] 评估指标计算器
- [ ] AI 策略生成管线接入
- [ ] Schema 演进管道
- [ ] Strategy Zoo 管理

---

## 设计哲学

1. **能跑即用**：拒绝过度工程化，轻量 Python 代码库，托管于 GitHub
2. **纯 Alpha 优先**：剥离仓位管理与执行层，专注评估策略本身的信号质量
3. **AI 即工具链**：AI 模型是策略工厂的工人，不是黑箱决策者
4. **防过拟合为第一原则**：时间均匀性、胜率稳定性、信号相关性去重，层层过滤伪策略
5. **可演进的表达力**：未支持的想法不丢弃，沉淀 → 审查 → 升维，系统自我进化

---

## 许可证

[MIT License](LICENSE)

---

*文档版本：v1.0 | 维护者：Strategy Discovery Team*