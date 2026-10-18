# 当前状态 — Starlight_ssGui

Owner: 项目所有者。基线时间:2026-10-17(Stage 0 初始化)。模板中未填项不是项目事实。

## 基线

仅存在**文档体系与参考快照**:无应用源码、无工具链、无构建产物。目标形态为 Rust + pocketjs 桌面工具,范围限定「SLP 参数调优注入 + 渲染日志监控」两件事。

## 当前实现

| 能力/范围 | 事实标签 | 版本/证据 | 限制 |
| --- | --- | --- | --- |
| 文档体系(AGENTS 树 + 入口) | `verified` | 本目录各文件;2026-10-17 创建 | 多为 `Proposed`/`未启动`,见各文件状态 |
| 参考快照:TopazStarlightUI v5.9 | `verified` | `learn/README.md`(归档 SHA-256 已登记) | 许可证未声明,仅行为参考 |
| 逆向分析产物(两个闭源工具) | `verified` | `learn/analysis/README.md`(哈希已登记) | 只读研究材料,不重发布 |
| 应用代码/工具链 | `planned` | 无 | 需任务包授权(Stage 1+) |
| 调参注入 / 日志监控实现 | `planned` | 机制结论见 `docs/research/references/` | 未验证于本项目环境 |

## 当前工作

| 任务 / 模块 / Master / 拓扑 | 状态 | 当前 Block / Review 家族 | 任务包/交付 | 下一事件/负责人 |
| --- | --- | --- | --- | --- |
| Stage 0 初始化(文档体系+参考快照) | 进行中 | 无(初始化不适用) | 无任务包(所有者直接授权) | 完成校验并移交所有者 |
| Stage 1 技术验证(骨架) | PLANNED | 未开始 | 待建任务包 | 所有者 |

## 阻塞与待决

- **实现授权**:Stage 0 范围门禁止产品代码;进入 Stage 1 需任务包或一次性授权。
- 未决技术问题登记在 [决策登记](decisions/AGENTS.md)(如注入机制选择、日志源选择、pocketjs 宿主能力)。

## 验证边界

尚无任何可执行验证入口(无工具链)。已登记证据为:归档 SHA-256、分析产物哈希、两个闭源工具 exe 哈希(见 `learn/README.md` 与 `learn/analysis/README.md`)。未运行项一律标注,不以文档结论冒充验证结果。

## 恢复入口

- 接手入口:[START_HERE](START_HERE.md) → 本文件 → [index](index.md)。
- 来源材料:`<PROJECT_ROOT>/learn/`(只读快照与分析产物)。
