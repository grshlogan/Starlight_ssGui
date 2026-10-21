# A002 Coordinator Bootstrap Brief

状态: `BLOCKED`，等待 PiDeck 手动启动 `A002[PiDeck]Main Coordinator` 独立会话。

## 身份与治理位置

- 身份：`A002[PiDeck]Main Coordinator`
- 主机：PiDeck / Windows governance
- 项目：`Starlight_ssGui`
- 工作区：`<PROJECT_ROOT>`
- 治理配对：`A001[PiDeck]DocArch Planner` + `A002[PiDeck]Main Coordinator`
- Git authority：`integrated-with-windows-governance`；不创建独立 Git Repository Owner
- 当前 baseline：`6e85b9e4aba16cc52f9fcc74dedf0170327382e2`，已推送 `origin/master`

## 启动时必须读取

1. `<PROJECT_ROOT>/AGENTS.md`
2. `<PROJECT_ROOT>/docs/START_HERE.md`
3. `<PROJECT_ROOT>/docs/STATUS.md`
4. `<PROJECT_ROOT>/docs/identity/AGENTS.md`
5. `<PROJECT_ROOT>/docs/identity/A001.md`
6. `<PROJECT_ROOT>/docs/plan/plan-stage1-gui-backend.md`
7. `<PROJECT_ROOT>/docs/decisions/AGENTS.md`
8. `<PROJECT_ROOT>/docs/decisions/ADR-002-stage1-boundaries-and-evidence.md`
9. `agent-dev-loop/SKILL.md`
10. `agent-dev-loop/core/loop.md`
11. `agent-dev-loop/lanes/coordinator.md`
12. `agent-dev-loop/hosts/pideck.md`
13. `agent-dev-loop/platform/placement.md`
14. `agent-dev-loop/templates/packet.md`
15. `agent-dev-loop/templates/handoff.md`

## 首次动作

1. 在 `docs/identity/A002.md` 建立自己的身份上下文；只由 A002 写入。
2. 在 `docs/identity/AGENTS.md` 登记 A002，写明 Coordinator 身份、治理写范围和当前会话。
3. 创建正式任务目录 `docs/tasks/stage1-gui-backend/` 及该目录的 `AGENTS.md`。
4. 创建 `packet-v1.md` 和 `state.md`；packet 必须包含模块、拓扑、身份、workspace、writer、验收标准、验证命令、授权和 review 绑定。
5. 先确认 packet 中的身份、工作区、单写者、验收标准均可解析；任何未解析项记录 `BLOCKED`，不要派发 Coding。
6. 根据 owner 已确认的 D002 编写 Stage 1 packet；Coordinator 只治理和派发，不实现 GUI/backend。
7. 先保持 `topology: stream`，除非提出明确的 tiered 拆分、互不冲突的写范围和验收成本，并取得 owner 对 packet 新版本的批准。
8. 在 packet 授权内派发 Master Coding/Coding；模块认领由 Coding 身份完成，Coordinator 不认领模块。

## 模块方向

- `GUI` 与 `backend` 是两个交付模块。
- 当前 owner 已确认 Stage 1 注入优先、`PYTHONPATH + sitecustomize` 首选、`tzlog` 主源、命令 + 状态快照/结构化事件 seam、夹具 + 真实 Windows/Topaz 双证据。
- 下一执行入口是 `B01-host-spike`；其实际 Block 是否独立派发，以 packet topology 和 owner 授权为准。
- Coding 必须在 committed baseline 或 packet 明确授权的 workspace 中工作，不能继承主工作区当前未提交规划文档。

## 身份边界

- Coordinator 可写：task packet、`state.md`、candidate binding、dispatch、consumption record。
- Coordinator 不可写：GUI/backend implementation、Coding receipt、Review verdict、acceptance record。
- Coding 必须写自己的 ACK、implementation、receipt 和 handoff，并停在 `REVIEW_READY`。
- Review 必须是独立新会话，绑定冻结 candidate manifest；Review PASS 不等于 acceptance。

## 当前阻塞

`pebrel env --pretty` 已验证输出 `runtime.reachable=false`，错误码 `runtime_unavailable`，消息 `no resident Pebrel runtime found`。当前主会话没有可调用的 PiDeck session launch 或 cross-session transport；A002 必须由用户在 PiDeck 手动启动。启动后以本 brief 为入口，创建 packet/state，再将实际 artifact 路径和 packet digest 回写给 A001/所有者。
