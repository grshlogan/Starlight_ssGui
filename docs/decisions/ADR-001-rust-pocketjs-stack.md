# ADR-001:技术栈采用 Rust + pocketjs v0.14.0

- Decision status: **Accepted**(2026-10-17,所有者确认)
- Owner / 决策依据:项目所有者 / 个人技术栈偏好 + 单进程小体积目标;GUI 栈快照已存在于共享 Learn 库
- 范围:桌面 GUI 应用层(含 UI 与平台能力封装)

## Context

需要一个 Windows 桌面工具承载「SLP 参数注入 + 日志监控」。候选栈:

- 参考项目 TopazStarlightUI 使用 Python + tkinter(所有者明确不喜欢用 Python 写 GUI);
- 所有者既定偏好:Rust + pocketjs(共享 Learn 库已有 v0.14.0 只读快照);
- pocketjs 为 TS 界面 + QuickJS guest + Rust core 的单进程原生渲染运行时(无 WebView/DOM)。

## Options

| 方案 | 收益 | 成本/风险 | 证据 |
| --- | --- | --- | --- |
| Rust + pocketjs v0.14.0 | 既定栈;单进程小体积;TS 组件写法 | 版本较新(2026-10 快照),进程管理/文件监听等宿主能力需 spike | 共享 Learn 快照;`docs/research/references/` |
| Rust + egui/tauri | 生态成熟 | 非所有者偏好;tauri 引入 WebView 依赖 | 未评估 |
| Python + tkinter | 参考项目同款,零额外学习 | 所有者明确排除 | learn 快照 |

## Decision

采用 **Rust + pocketjs v0.14.0**:UI 以 TS 组件实现,Rust 侧承担进程/文件/日志等平台能力;Python 仅作为被注入侧的 hook 载荷语言,不作为本项目运行栈。

## Consequences

- Stage 1 必须先做宿主能力 spike(进程启动、文件监听、定时读取);若能力缺失,评估"编写 Rust 扩展"路径,并回看本决策。
- 项目需同时维护 TS 与 Rust 两侧代码风格与构建;文档以中文为主,代码/命令保持原文。
- 与参考快照的许可证边界:只读使用,不改写快照树。

## Verification Gate and Adoption

- Gate:Stage 1 spike 能证明——以参数化方式启动外部进程;监视日志目录新增/滚动文件并在秒级读取增量;UI 线程不被日志解析阻塞。以上任一失败即回到本决策重新比较。
- 所有者决策点:spike 结论 + 失败清单。
- 采纳记录:所有者于 2026-10-17 确认本栈(需求对话),依据为个人栈偏好与快照可用性;**运行期能力仍未验证**,待 Stage 1 结论。

## Links

- [架构基础](../architecture/AGENTS.md) · [工程约束](../engineering/AGENTS.md) · [阶段路线图](../plan/AGENTS.md)
- 参考:共享 Learn 库 pocketjs v0.14.0 快照(登记于 [来源登记](../research/AGENTS.md))
