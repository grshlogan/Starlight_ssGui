# Agent 入口 — Starlight_ssGui

> 新会话第一步读这里,其次 `STATUS.md`,再查 `index.md`。
> 只有经过验证的项目事实才会写入本文件;未完成项显式标 `TBD` / `未启动`。

## 阅读顺序

1. 项目根 `AGENTS.md`(边界/授权规则)与本文件;接手已有身份时先读该身份的 `docs/identity/<identity-id>.md` 与其 `docs/handoff/<identity-id>.md`。
2. [当前状态](STATUS.md) → [文档索引](index.md)。
3. 当前任务包/活动计划,以及 STATUS 指向的契约、源码、测试。
4. 开发/验证前读 [工程约束与验证策略](engineering/AGENTS.md);角色协作前读 [身份登记与目录规则](identity/AGENTS.md)。

## 项目映射(初始化时填写)

| 概念 | 实际路径/标识 |
| --- | --- |
| 项目 ID / 目标 / 非目标 | `Starlight_ssGui` — Topaz Video 星光(SLP 2.5/2.6)模型「参数调优注入 + 渲染日志监控」桌面工具;非目标见 [产品章程](product/AGENTS.md) |
| 产品需求与验收 | [产品章程](product/AGENTS.md)(初始章程);细粒度验收在任务包内定义 |
| 当前架构/公共契约 | [架构基础](architecture/AGENTS.md)(`Proposed`,无已实现契约) |
| 模块边界与 Master Coding | 模块注册表在 [架构基础](architecture/AGENTS.md);身份范围与已指派身份在 [身份登记](identity/AGENTS.md) |
| 主工作流/拓扑/Review | `agent-dev-loop` **v3.0.0**(协议 `agent-dev-loop-v3`,根别名 `<AGENT_DEV_LOOP_ROOT>`);当前任务包为 `stream` 拓扑 |
| 活动计划/任务包 | [阶段 1 任务包](tasks/stage1-gui-backend/AGENTS.md)(`packet-v8`);阶段路线图见 [plan](plan/AGENTS.md) |
| 验证入口 | 已配置 Rust/Python/Node 三类门,见 [工程约束](engineering/AGENTS.md) 与任务包 `verify_commands` |
| 身份 ACK/checkpoint | `docs/handoff/<identity-id>.md`(保留路径,永不进候选);规则见 [handoff 规则](handoff/AGENTS.md) |
| STATUS/index 维护者 | 项目所有者(暂代);后续随任务包指派 |
| 本机别名映射 | 所有者私有位置(不入库);文档统一使用别名:<br>`<PROJECT_ROOT>`、`<SHARED_LEARN_ROOT>`、`<TOPAZ_INSTALL_DIR>`、`<TOPAZ_LOG_DIR>`、`<TOPAZ_MODEL_STORE>` |

## 范围门与语言

- **范围门**:搭文档、做调研、准备参考材料**不等于**授权实现;实现必须由任务包(或一次性授权)授权。当前阶段为 **Stage 1 技术验证**(已由 `stage1-gui-backend` 任务包授权实现)。
- **语言**:项目文档使用**中文(简体)**;代码、命令、路径、协议字段保持原文。

## 首次接手

确认 cwd、身份、写范围与既有改动(见 `git status`,若已初始化版本控制)。按 STATUS 继续当前工作,**不要**从历史聊天推断状态。若本文件引用的入口缺失,如实报告并只补齐被授权的最小初始化,不补造整个空目录树。
