# 身份上下文:目录规则与示例

本文件是 `docs/identity/` 的常驻规则入口,在进入该目录工作时生效。身份登记表、身份文档的创建/维护规则与示例骨架都在这里。本文件本身不是身份、任务包或授权记录;根 `AGENTS.md` 优先级更高。

## 身份登记表

| 稳定 ID | 显示名 | 主机/角色 | 独占写范围 | 工作流/配置 | 上下文 |
| --- | --- | --- | --- | --- | --- |
| `A001[PiDeck]DocArch Planner` | DocArch Planner | PiDeck / 文档架构与项目规划 | `docs/identity/A001.md`、规划/决策文档；不得写 GUI/backend 实现 | agent-dev-loop + Windows integrated governance | [A001.md](A001.md) |
| `A002[PiDeck]Main Coordinator` | Main Coordinator | PiDeck / 任务治理协调 | `docs/identity/A002.md`、`docs/tasks/stage1-gui-backend/{packet-vN,state,coverage-ledger}.md`、`dispatch/`、`snapshots/`、`handoff/A002.md`；不得写 GUI/backend 实现、Coding receipt、Review verdict、acceptance record | `agent-dev-loop-v2`(PiDeck `manual` 启动 + file bridge)+ Windows integrated governance | [A002.md](A002.md) |
| 待指派 | 形如 `Axxx[Host]Role` | TBD | TBD(具体路径) | 待选择 | 创建后填写 |

## 当前指派(2026-10-18)

| 身份 | 角色 | 会话 | 绑定任务/模块 | 状态 |
| --- | --- | --- | --- | --- |
| `A002[PiDeck]Main Coordinator` | Coordinator | `A002-session-01`(PiDeck,Windows 11 x64) | `stage1-gui-backend` / 治理侧,不认领模块 | 已启动,packet v1 已发布 |
| `A003[PiDeck]Master Coding` | Master Coding | `A003-session-01`(已启动) | `stage1-gui-backend` / `backend` + `GUI`(`stream` 拓扑) | `REVIEW_READY`:receipt-v1 已交 |
| `A003-R01` | Review（首轮） | 未启动,待 candidate-1 冻结后手动开启 | `stage1-gui-backend` / Review 家族 `stage1-gui-backend` | `PLANNED`:待 `R01` 派发 |

2026-10-20 治理侧更新:`stage1-gui-backend` packet **v5** 已发布(`sha256:a62fd381…`,取代 v4),协议迁移到 `agent-dev-loop-v3`(Skill v3.0.0);A003 已将 ACK 与 checkpoint 迁到 `docs/handoff/A003.md`(保留路径,永不进候选);任务状态 `REVIEW_READY`。Review 身份按 v3 改为**按轮命名** `A003-R01`(不再使用 `A004`)。

A002 与 A003 是**不同身份、不同会话、不同写范围**;Review 按轮命名为 `A003-Rxx`,必须是**独立新会话**。三者不得合并,不得在同一会话内跨越治理与实现/评审边界。

- Coordinator/Coding/Review 角色由任务包指派并在此登记;架构/产品所有者与验收人由项目指派,可以是所有者本人。
- Master Coding 拥有一个模块或任务流;Sub-Coding 继承一个 Master 并拥有一个 Block。其稳定 ID、模块/Block 范围、工作区与独占写范围必须与架构注册表和任务包一致。
- Master 可在任务包授权内派发 Sub-Coding,但不能替代独立 Review 与验收人;每个 Block 交付与 Master 模块候选都需要独立 Review。
- 主工作流、安装入口与常备授权记录在根 `AGENTS.md`;未列入者需任务包或一次性授权。
- 显示名、主机与稳定 ID 只描述身份,**不产生权限**。

## 规则(适用于每个身份文档)

1. **一身份一文档**:用稳定 ID(如 `A001.md`)命名,显示名写在正文;不按会话/平台创建记录。
2. **单写者**:只有该身份本人写自己的文档,其他身份只读;发现错误或过时内容,通过任务包报告给该身份或 Coordinator,不要代为修改。
3. **接手与体积**:新会话接手前确认前写者已停止;常态约 1,000 行,硬上限 1,500;接近上限先归档/清理再追加。
4. **持续清理**:每次更新移除过时结论、噪音与死引用;源/配置/STATUS 冲突时,以可复核证据为准更新。
5. **模块与移交绑定**:Master 上下文记录模块、当前任务/拓扑、Block 分配、Review 家族、验收映射与下一事件;Sub-Coding 上下文记录继承的 Master ID、其唯一 Block、实际验证与交付路径。移交只转移明确写权,不转移模块所有权或授权。
6. **事实标签**:沿用根 `AGENTS.md` 的定义(`verified` / `planned` / `hypothesis` / `deprecated`);结论不得超出证据范围。

## 示例骨架

创建 `<identity-id>.md` 时使用以下结构;不适用的小节删除,不保留空壳。

```markdown
# <显示名,如 A001[Host]Role> 身份上下文

| 字段 | 值 |
| --- | --- |
| 稳定 ID / 父身份 / 唯一写者 | 本身份;其余只读 |
| Agent 与主机 / 会话引用 | Agent 家族与真实主机分开记录 |
| 工作区 / 最近更新 | cwd 别名或 worktree / YYYY-MM-DD |

## 授权与范围
核心职责、已授权操作(精确路径、命令与授权来源)、保护边界、工作流。显示名/会话 ID/稳定 ID 不产生权限。
常备授权与一次性授权分开;Git 写、凭据、主机变更、破坏性清理需单独授权。

## 模块与任务
模块、任务、拓扑、Master/Sub 关系、Block、Review 家族、写范围、验收人。任务包为权威;此处只记接手所需映射。

## 当前事实
绑定任务与阶段;最近验证(精确命令、cwd 别名、真实退出码);未执行项标 `not run`;产物与证据位置。

## 关键路径与契约
只列实际使用的项;共享项目事实留在 STATUS/ADR,不在此重复。

| 类型 | 路径 | 访问 | 契约/身份 |
| --- | --- | --- | --- |

## 决策与移交(新者在前)
目标与结论(`COMPLETED / BLOCKED / UNCERTAIN / NOT RUN`)、决策与依据、变更路径、验证与证据(精确 SHA)、下一身份、下一动作。保留最近三次移交,其余归档并留索引。

## 阻塞与下一步
下一动作(动作、负责人、所需授权);最小阻塞(问题、证据、已排除备选、所需决策)。准备不等于派发;检查通过不等于验收。

## 相关入口
- 本目录规则(AGENTS.md)、根 AGENTS.md
- STATUS / index / 证据位置
```

## 自检

体积达标;过时内容已清理;不与权威文档冲突、不制造第二事实源;最新移交在最前;未做项与边界如实记录;登记表与上下文中的身份/主机/写范围一致。
