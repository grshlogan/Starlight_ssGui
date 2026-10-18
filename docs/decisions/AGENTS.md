# 决策索引与开放决策登记

## 决策索引

| ID | 主题 | 状态 | 记录 |
| --- | --- | --- | --- |
| D001 | 技术栈:Rust + pocketjs v0.14.0 | Accepted(2026-10-17) | [ADR-001-rust-pocketjs-stack.md](ADR-001-rust-pocketjs-stack.md) |

## 开放决策(唯一未决清单)

- **注入机制**:PYTHONPATH + sitecustomize vs `.pth` 引导器 + SHA256(依赖:Stage 1 实测;倾向 PYTHONPATH 以守住"不改 Topaz 安装文件"不变量)。
- **日志源与方言策略**:主日志(tzlog)为主、neuroserver stdout 为辅;双方言(1.7.0 / 1.7.1+)的实现方式(依赖:Stage 1 日志夹具)。
- **pocketjs 宿主能力路线**:直接使用现有宿主 API vs 编写 Rust 扩展(依赖:Stage 1 spike 结论)。
- **发布与许可策略**:项目自身许可证选择;`learn/` 中许可证未声明快照对再发布/分发的影响(依赖:所有者决策,Stage 2 前)。

## 规则

建议不等于已采纳契约。采纳需 ADR(`ADR-<id>-<slug>.md`),含备选、后果、证据、验证门与明确的采纳人;采纳事实只记录在 ADR 的采纳段,本登记表只更新状态、不复制事实。
