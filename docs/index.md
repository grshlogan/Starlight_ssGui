# 文档索引 — Starlight_ssGui

Owner: 项目所有者(暂代)。只登记**已存在**的入口;每项标注状态:`Current`(生效中)/ `Proposed`(已提出未采纳)/ `Planned`(已排期)/ `Historical`(被取代,保留指针)。

| 入口 | 职责 | 状态 |
| --- | --- | --- |
| [START_HERE](START_HERE.md) | 接手顺序与项目路径映射 | Current |
| [STATUS](STATUS.md) | 当前状态、阻塞与任务指针 | Current |
| [product/](product/AGENTS.md) | 产品章程:使命、交付顺序、范围/非目标、词汇、不变量 | Proposed |
| [architecture/](architecture/AGENTS.md) | 架构基础、边界、模块注册表(`Proposed` 项经 ADR 提升) | Proposed |
| [engineering/](engineering/AGENTS.md) | 工程约束与验证策略(工具链、平台门、验证入口) | Current |
| [design/](design/AGENTS.md) | 交互/视觉设计约束与资产索引 | Current(无实例) |
| [plan/](plan/AGENTS.md) | 阶段路线图与阶段门 | Current |
| [decisions/](decisions/AGENTS.md) | 决策索引、开放决策清单与 ADR 规则 | Current |
| [research/](research/AGENTS.md) | 来源登记(锁定基线、许可证、获取与验证证据) | Current |
| [research/references/](research/references/AGENTS.md) | 外部参考简报与证据附录(报告实例) | Current |
| [tasks/](tasks/AGENTS.md) | 任务包位置/命名/版本与绑定规则 | Current |
| [tasks/stage1-gui-backend/](tasks/stage1-gui-backend/AGENTS.md) | Stage 1 任务包:`packet.md`(活,rev 12)/ `packet-v12.md`(40 verifiable + 6 deferred)、state、coverage ledger、`coding/dispatch-2.md`–`dispatch-7.md`、`review/R01`–`R05`(FAIL)、`R06` 待 `receipt-v6` | Current |
| [runbooks/](runbooks/AGENTS.md) | 操作步骤、恢复入口与事故记录规则 | Current(无实例) |
| [release/](release/AGENTS.md) | 发布记录结构与发布纪律 | Current(无版本) |
| [identity/](identity/AGENTS.md) | 身份登记、单写者与身份上下文规则 | Current |
| [handoff/](handoff/AGENTS.md) | 身份 ACK/checkpoint（`snapshot.mjs` 保留路径，永不进候选） | Current |

## 维护规则

- 新建顶级目录时必须同时创建该目录 `AGENTS.md` 并在此登记(职责/状态/维护者)。
- 实例文件(ADR、计划、任务包、简报)沿用其业务命名,遵循最近目录的 `AGENTS.md`。
- 被取代的条目标 `Historical` 并保留替代指针,不删除。
- 每类事实只有一个权威位置:`STATUS` 记"现在",计划记"下一步",ADR 记"为什么",证据记"怎么证明",身份上下文记"如何接手"。
