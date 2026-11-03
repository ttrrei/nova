# 提案：AGENTS.md — 冻结核心（待人工审核）

状态：**仅为提案** — 本阶段未修改 `AGENTS.md`。

建议追加到 `AGENTS.md`（英文版见 `AGENTS_frozen_core.md`；英文版为准，两版不一致时以英文版为准）：

---

## 冻结核心

Nova 的核心是**冻结的**。任何对因果性、引擎、执行或成本规则、指标或环境
（依赖）的改动都会使所有历史结果失效，并迫使全部策略重新运行；对现有特征
的更新会使依赖该特征的运行失效。

永远不得编辑、重构、格式化、重命名或改动以下路径的导入：

- `src/nova/`（全部 Python 文件）
- `pyproject.toml`
- `requirements.lock`
- `FEATURE_VERSION` 的取值

完整性由仓库根目录的 `FROZEN_CORE.sha256` 与 `scripts/check_frozen_core.py`
保证（`tests/test_frozen_core.py` 在每次测试中运行该检查）。用 `--write`
重新生成基线是**仅限人工**的操作，且意味着承认所有历史结果已失效。

新增特征遵循“只增不改”原则，不会使历史失效，但受独立协议
（`docs/proposals/FEATURE_ADDITION_PROTOCOL.md`）约束，需人工重新应用
`FEATURE_VERSION` 规则，不属于常规仓库整理。

对现有特征的更新、重命名或删除，或对引擎、执行、成本、指标、依赖的任何
改动，没有明确的人工决定一律不允许。
