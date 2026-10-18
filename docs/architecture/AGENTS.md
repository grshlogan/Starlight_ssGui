# 架构基础 — Starlight_ssGui

## 决策状态

技术栈由 [ADR-001](../decisions/ADR-001-rust-pocketjs-stack.md) 采纳(所有者确认);其余章节 `Proposed`,采纳前经 ADR 提升。支撑证据:`docs/research/references/` 两份报告 + `learn/analysis/` 产物。

## 归属边界

本项目采用两个交付模块；日志、注入、配置等能力作为 backend 内部子域，不单独拆成任务模块。

```text
GUI      : pocketjs(TS)界面与交互状态;不直接持有进程/文件系统能力(经 backend 暴露)
backend  : Rust core;环境组装、注入装配、Topaz 启动、单实例锁、生命周期与退出回退、日志 tail/解析/进度/ETA/历史、参数模型/预设/持久化
```

开发、Review、验证与 Git 权威均在 **Windows x64** 单一系统完成；本项目不采用跨系统源码、工作树或治理流程。

不得跨界的对象:原始日志文本(经 backend 结构化后才给 GUI)、hook 载荷完整性凭据(backend 独占)、Topaz 安装目录写句柄(默认不存在)、凭据与别名映射。

## 备选比较(采纳前需逐项验证)

| 选项 | 优点 | 主要风险 | 比较门槛 |
| --- | --- | --- | --- |
| 注入:PYTHONPATH + sitecustomize | 简单;开源参考实现多(learn 快照同款) | 依赖 Topaz 向子进程继承环境变量 | Stage 1 实机实测 |
| 注入:.pth 引导器 + SHA256(naxci1 式) | 更抗环境差异;可校验载荷 | 需向 Topaz 目录写文件(违背默认不改安装) | 仅当 PYTHONPATH 方案实测失败时评估 |
| 日志源:Topaz 主日志(tzlog) | 内含命令行/阶段/统计,信息最全 | 格式随版本变(需双方言) | Stage 1 采样并锁定 |
| 日志源:neuroserver stdout | 结构化 JSON,直读 | GUI 模式拿不到管道;CLI 模式才可用 | 同上,作为补充源 |
| GUI:pocketjs v0.14.0(已选) | 单进程原生渲染;所有者既定栈 | 较新,宿主能力(进程/文件监听)待 spike | Stage 1 spike |

## 模块注册表与归属

| 模块 ID | 边界/职责 | Master Coding | 当前任务/Block | Review 家族 | 验收人 | 状态 |
| --- | --- | --- | --- | --- | --- | --- |
| `GUI` | pocketjs 界面与交互状态；通过 backend 获取结构化参数、进度和日志 | 未指派 | 无 | 待定 | 所有者 | `planned` |
| `backend` | Rust core：环境组装、Topaz 生命周期、hook 注入、审计、日志监控、参数模型、预设与持久化 | 未指派 | 无 | 待定 | 所有者 | `planned` |

- 每个激活模块只有一个 Master Coding;身份、模块范围与写范围须同时登记于 [身份登记](../identity/AGENTS.md) 与任务包。
- Master 负责实现、Block 拆分、集成与移交;**不能**替代独立 Review 与验收人。
- 后续模块工作、跨模块集成或契约变更必须回指任务包与 Review 家族;不把每轮报告/测试结果复制进本表。

## 证据门

采纳任何架构项前,记录:备选方案、后果、许可证、集成成本、崩溃隔离、取消/背压、错误处理与可测性;验证策略见 [工程约束与验证策略](../engineering/AGENTS.md)。
