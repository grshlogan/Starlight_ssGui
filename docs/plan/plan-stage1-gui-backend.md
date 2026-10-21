# Stage 1 技术验证计划：GUI/backend 最小闭环

状态: `active`；所有者已确认 D002 的方向，Stage 1 实测证据仍待完成。本文保留执行范围、依赖和验收门；未被证据支持的内容仍标记为 `planned` 或 `hypothesis`。

## 目标

在 Windows x64 单一开发与验收环境中，验证 Starlight_ssGui 的两个交付模块能形成可追溯的技术闭环：

1. `backend` 能在不写入 Topaz 安装目录的前提下完成最小注入尝试、审计和失败回退。
2. `backend` 能取得一次真实 SLP 日志，解析阶段、分块和进度信息。
3. `GUI` 能通过一个小而稳定的 seam 展示结构化状态，并向 `backend` 发送最小控制命令。
4. pocketjs 宿主能力结论明确：现有宿主可直接满足进程/文件监听/定时读取，或明确由 Rust backend 补齐。

## 范围

- Windows x64 实机验证。
- Rust backend 骨架与 pocketjs GUI 骨架。
- 注入最小闭环、原生回退和审计证据。
- 一次真实日志采样、版本方言识别和解析原型。
- GUI/backend 的最小命令、状态快照、结构化事件和错误模型。

## 非目标

- 完整参数集、预设矩阵和生产级 GUI。
- cuDNN 管理、自动更新、安装器、云功能、账号操作和转码链。
- 跨系统源码、跨系统工作树或跨系统验收流程。
- 将 `learn/` 中闭源工具的 hook、反编译字节码、转储或下载归档重新发布。

## 当前证据

- `verified`: 技术栈为 Rust + pocketjs v0.14.0，见 [ADR-001](../decisions/ADR-001-rust-pocketjs-stack.md)。
- `verified`: 项目目标平台为 Windows x64，见 [README](../../README.md) 与 [工程约束](../engineering/AGENTS.md)。
- `verified`: 当前架构只有 `GUI` 与 `backend` 两个交付模块，内部日志、注入、配置能力不独立拆模块，见 [架构基础](../architecture/AGENTS.md)。
- `verified`: Stage 1 的阶段门要求真实 Topaz 注入证据、真实日志夹具和 pocketjs 宿主能力结论，见 [阶段路线图](AGENTS.md)。
- `planned`: 所有者确认 Stage 1 优先完成注入闭环，再完成日志监控。
- `planned`: 注入 spike 以 `PYTHONPATH + sitecustomize` 为首选，默认不写 Topaz 安装目录；失败时保留原生启动回退。
- `planned`: 以 Topaz 主日志 `tzlog` 为主源，以 `neuroserver stdout` 作为补充源，并保留版本方言解析。
- `planned`: GUI/backend seam 采用少量命令、状态快照、结构化事件和结构化错误；原始日志、注入细节和文件系统能力留在 backend。
- `planned`: 同时使用本地夹具回归和 Windows x64 + 真实 Topaz 证据；没有真实环境时相关验收保持 `BLOCKED`。

## 已确认方向与未决项

已确认方向已记录于 [ADR-002](../decisions/ADR-002-stage1-boundaries-and-evidence.md)：

- Stage 1 采用注入优先顺序。
- 注入和日志沿用当前技术草案，实测失败时回到备选方案。
- GUI/backend 采用“命令 + 状态快照/结构化事件/结构化错误”的 seam。
- 验收同时需要本地夹具和 Windows x64 + 真实 Topaz 证据。

仍需在任务包中细化：首个 GUI 用户流程、必须支持的 Topaz 版本、参数字段、错误体验和明确排除项；pocketjs 宿主能力路线仍需 spike 结论。

## 执行步骤与依赖

1. `completed`: 所有者确认 Stage 1 优先顺序、技术草案、GUI/backend seam 和双重证据门；首个 GUI 用户流程、Topaz 版本、参数字段和错误体验仍待细化。
2. `completed`: 将已确认的不可逆取舍写入 ADR-002，并建立领域词汇表。
3. `pending`: 完成 pocketjs 宿主能力 spike；若能力不足，在 backend 侧确定 Rust adapter seam。
4. `pending`: 做注入 spike，记录候选、环境、审计对照、失败回退和 Topaz 影响。
5. `pending`: 采集真实日志夹具，确定版本方言并实现可回归的解析原型。
6. `pending`: 冻结 GUI/backend interface 后实现最小 GUI 验证面板和 backend 状态/事件输出。
7. `pending`: 形成 REVIEW_READY candidate，执行独立 Review；修复后重新 Review，再由所有者验收 Stage 1。

## Stage 1 Block 拆分与验收映射

| Block | 负责模块 | 依赖 | 产出 | 验收证据 |
| --- | --- | --- | --- | --- |
| `B01-host-spike` | backend | 无 | pocketjs 进程启动、文件监听、定时读取能力结论 | Windows x64 运行记录；直接可用或 Rust adapter 决策 |
| `B02-injection-closure` | backend | B01 | `PYTHONPATH + sitecustomize` 首选路径、审计对照、原生回退 | 真实 Topaz 注入前后对照；失败时原生运行；不写安装目录 |
| `B03-log-fixture-parser` | backend | B02 | `tzlog` 主源的真实夹具、版本方言识别、阶段/分块/进度解析 | 夹具哈希、原始来源、解析输出和回归结果 |
| `B04-gui-backend-seam` | GUI + backend | B02、B03 | 最小控制命令、状态快照、结构化事件/错误与验证面板 | GUI 只消费结构化结果；命令顺序和错误路径可回归 |
| `B05-review-acceptance` | GUI + backend | B04 | 冻结 candidate、独立 Review 报告、修复记录和验收包 | `PASS/FAIL/UNCERTAIN/BLOCKED` 绑定具体 candidate；所有者关闭 Stage 1 |

当前只登记 Block 范围与依赖，不分配 Master Coding、写范围或 Review 家族；这些内容须在任务包建立时登记。

## 验收命令与证据

代码骨架建立后至少执行：

- `cargo fmt --check`
- `cargo test --workspace`
- `cargo build --workspace`
- Windows x64 实机手工证据：注入审计对照、原生回退、真实日志解析、宿主能力结果。

在代码骨架建立前，不宣称上述命令已通过；当前只有文档和仓库状态证据。

## 风险与停止条件

- 没有真实 Topaz 或真实日志时，相关验收项保持 `BLOCKED`，不以模拟结果替代真实证据。
- 注入失败必须回退原生运行；不得为规避失败而写入 Topaz 安装目录或移除防御性检查。
- GUI/backend 的公开接口、错误码、事件顺序或所有权不清时停止实现，回到决策点 4。
- 发现参考材料许可或发布边界不清时停止复制或提交，保持材料在本地只读。

## 进展

- `completed`: 项目仓库已初始化，初始提交已推送到 `origin/master`。
- `completed`: 架构已收敛为 `GUI` 与 `backend` 两个交付模块。
- `completed`: 建立 Stage 1 最小决策包并完成所有者确认。
- `completed`: 将确认方向记录为 [ADR-002](../decisions/ADR-002-stage1-boundaries-and-evidence.md)，并建立 [领域词汇表](../../CONTEXT.md)。
- `in_progress`: 细化首个 GUI 用户流程、Topaz 版本、参数字段和任务包边界。
- `pending`: 完成 pocketjs 宿主能力 spike 与真实注入/日志证据。

## 决策引用

- [ADR-001 Rust + pocketjs 技术栈](../decisions/ADR-001-rust-pocketjs-stack.md)
- [产品章程](../product/AGENTS.md)
- [架构基础](../architecture/AGENTS.md)
- [工程约束与验证策略](../engineering/AGENTS.md)
- [阶段路线图](AGENTS.md)
