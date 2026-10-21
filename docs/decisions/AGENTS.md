# 决策索引与开放决策登记

## 决策索引

| ID | 主题 | 状态 | 记录 |
| --- | --- | --- | --- |
| D001 | 技术栈:Rust + pocketjs v0.14.0 | Accepted(2026-10-17) | [ADR-001-rust-pocketjs-stack.md](ADR-001-rust-pocketjs-stack.md) |
| D002 | Stage 1 闭环顺序、模块 seam 与证据门 | Accepted(当前会话确认;实测待完成) | [ADR-002-stage1-boundaries-and-evidence.md](ADR-002-stage1-boundaries-and-evidence.md) |
| D003 | Review finding 的消费策略(P3 默认不修、成本判据、少部件优先) | Accepted(2026-10-20) | [ADR-003-finding-consumption-policy.md](ADR-003-finding-consumption-policy.md) |

## 开放决策(唯一未决清单)

- **pocketjs 宿主能力路线**:直接使用现有宿主 API vs 编写 Rust 扩展(依赖:Stage 1 spike 结论)。
- **发布与许可策略**:项目自身许可证选择;`learn/` 中许可证未声明快照对再发布/分发的影响(依赖:所有者决策,Stage 2 前)。

D002 已确认注入优先顺序、注入和日志的首选方向、GUI/backend seam 与 Stage 1 证据门；这些方向仍须通过阶段实测，实测失败时按 ADR 记录回到备选方案。

## 规则

建议不等于已采纳契约。采纳需 ADR(`ADR-<id>-<slug>.md`),含备选、后果、证据、验证门与明确的采纳人;采纳事实只记录在 ADR 的采纳段,本登记表只更新状态、不复制事实。
