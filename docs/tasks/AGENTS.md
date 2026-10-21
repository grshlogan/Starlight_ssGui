# 任务包目录规则

本目录存放任务包:`<task-id>/packet-vN.md`。一个任务包承载一次授权,是验收记录的入口;创建后由该任务维护,本文件定义位置、命名与版本规则,随目录常驻。

## 规则

1. 一个任务一个子目录。创建 `<task-id>/` 时,任务工作流必须同时创建该目录的 `AGENTS.md`。包文件名含版本号,**已发布版本永不覆盖**;变更建 vN+1,旧版留作历史。
2. 工作流 Skill(如 `agent-dev-loop`)拥有任务包结构与门;不要在此复制第二套协议。记录任务包实际使用的协议/配置版本或摘要。
3. 主工作流入口与常备授权在根 `AGENTS.md`;新任务包登记到 [文档索引](../index.md),关闭的包保留不删除。
4. 派发前确认任务包引用的 Skill/协议版本在本地可读;Skill 文件存在不代表已进入会话上下文。
5. **绑定模块交付**:每个新任务包记录 `module_id`、`topology`、Master Coding、验收人、Review 家族;`tiered` 任务包记录每个 Block、Sub-Coding、互不冲突的 `write_scope`、依赖与验收标准。Block 的 Review PASS 后才能写 `block-delivery`;Master 集成仍需独立 Review。移交、回执、Review 报告与验收记录的详细结构由主工作流负责。

## 当前状态

| 任务 | 当前版本 | 拓扑 | 模块 | Master Coding | Review 家族 | 验收人 | 状态 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| [`stage1-gui-backend`](stage1-gui-backend/AGENTS.md) | `packet-v12`(`sha256:8d0a1f2c…`,`packet_rev: 12`) | `stream` | `backend`、`GUI` | `A003[PiDeck]Master Coding` | `stage1-gui-backend`(`R01`–`R05` 均 FAIL;`R06` 待 `receipt-v6`) | 项目所有者 | `FIXING` |

Stage 0 由所有者直接授权,不适用任务包。`stage1-gui-backend` 是首个正式任务包。
