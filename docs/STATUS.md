# 当前状态 — Starlight_ssGui

Owner: 项目所有者。基线时间:2026-10-20(Stage 1 进行中)。模板中未填项不是项目事实。

## 基线

已有 **Rust workspace + Python hook + TS seam 骨架**(Stage 1 任务包 `stage1-gui-backend` 授权实现),基线提交 `6e85b9e`;实现位于 `<PROJECT_ROOT>.worktree/A003/Master`(分支 `a003/master`,未提交,交付物为工作树 + receipt)。

## 当前实现

| 能力/范围 | 事实标签 | 版本/证据 | 限制 |
| --- | --- | --- | --- |
| 文档体系(AGENTS 树 + 入口) | `verified` | 本目录各文件 | 已对齐 `agent-dev-loop` v3.0.0;见 `docs/tasks/`、`docs/handoff/` |
| 参考快照:TopazStarlightUI v5.9 | `verified` | `learn/README.md`(归档 SHA-256 已登记) | 许可证未声明,仅行为参考 |
| 逆向分析产物(两个闭源工具) | `verified` | `learn/analysis/README.md`(哈希已登记) | 只读研究材料,不重发布 |
| backend 骨架(Rust) | `verified` | `backend/src/{injection,log_parser,protocol,lib}.rs`;`cargo fmt/clippy/test/build` 均退出码 0(11 tests passed) | 仅本地夹具,未经真实 Topaz |
| hook 载荷(Python) | `verified` | `hook/sitecustomize.py`;`discover -s hook/tests` 退出码 0(7 tests)+ `hook.tests.test_failsafe` 退出码 0(5 tests) | 审计写入真实路径未经真实渲染验证 |
| GUI seam(TS) | `verified` | `gui/src/protocol.ts`;`node --test` 退出码 0(4 tests) | 仅类型与校验层,无渲染宿主 |
| 真实注入 / 真实日志解析 | `planned` | 机制结论见 `docs/research/references/` | AC-4/AC-7 为 `BLOCKED`,需所有者提供真实 Topaz 证据 |
| pocketjs 宿主能力结论 | `planned` | `hook/gates/test_host_capability.py`(门当前为红) | AC-11 `BLOCKED`,缺 `<SHARED_LEARN_ROOT>` 映射 |

## 当前工作

| 任务 / 模块 / Master / 拓扑 | 状态 | 当前 Block / Review 家族 | 任务包/交付 | 下一事件/负责人 |
| --- | --- | --- | --- | --- |
| Stage 0 初始化(文档体系+参考快照) | 已完成 | 不适用 | 所有者直接授权 | 已移交 Stage 1 |
| Stage 1 技术验证 | **`ACCEPTANCE_PENDING`**(R07 PASS) | `B02`/`B03`/`B04` 已实现,`B01` 延后;Review 家族 `stage1-gui-backend` | [packet `v12`](tasks/stage1-gui-backend/packet-v12.md)、[packet.md(活)](tasks/stage1-gui-backend/packet.md)、[state](tasks/stage1-gui-backend/state.md)、[coverage ledger](tasks/stage1-gui-backend/coverage-ledger.md) | `R07` 判 **`PASS`**(2026-10-22):绑定 **`candidate-7`**(`df838a08…`,69 files)+ `packet-v12`;Coverage `complete`(40 criteria + 5 rules,`not run` = 0);R06 两条 P2 均关闭(`Completed{seconds:None}` 结构性不可达、`AC-3.5` import 半边有新断言 + `MB2` 变红)。**`PASS` 不等于验收**:acceptance record 由所有者写;6 条 owner-blocked AC 仍处 `deferral`(`AC-4.3`、`AC-7.1`–`7.3`、`AC-11.1`–`11.2`,等真实 Topaz 证据与 `<SHARED_LEARN_ROOT>` 映射)。判据版本漂移已记账(`SKILL.md`/`adapters/ocr.md` 升 v3.1.1),判定面 `lanes/review.md`+`templates/report.md` 未变 |

## 阻塞与待决

- **AC-4 / AC-7(真实 Topaz 证据)**:保持 `BLOCKED`,负责人 = 项目所有者。没有真实 SLP 短导出与真实 `tzlog` 前,Stage 1 不得整体验收。
- **AC-11(pocketjs 宿主能力)**:保持 `BLOCKED`,`<SHARED_LEARN_ROOT>` 只读映射未提供给 A003。`G-HOST-CAPABILITY` 已改为 skip 即失败,门当前为红——这是刻意设计。
- 未决技术问题登记在 [决策登记](decisions/AGENTS.md)(如 pocketjs 宿主能力路线、发布与许可策略)。

## 验证边界

已配置三类可执行门(Rust / Python / Node),权威定义在任务包 `verify_commands`(当前 `packet-v12`,11 个门;46 条 AC = 40 verifiable + 6 deferred,无孤立 required 门)。

**`candidate-2` 门实测(2026-10-20,A002 独立重跑;`manifest_sha256 20089141…`,53 files)**——注意:R02 已证实这些绿门漏掉了 AC-8 的已知版本半边(见下):

| 门 | 退出码 | 说明 |
| --- | --- | --- |
| `G-FMT` / `G-CLIPPY` / `G-BUILD` | 0 | — |
| `G-TEST-RS` | 0 | 11 Rust 测试通过 |
| `G-PY-UNIT` | 0 | 7 tests(AC-11 门已移出 `hook/tests`,与 `G-PY-UNIT` 解耦) |
| `G-FAILSAFE` | 0 | 5 tests,显式模块名(`-k` 零命中路径已删除) |
| `G-PY-COMPILE` | 0 | — |
| `G-GUI-TEST` | 0 | 4 tests |
| `G-HOST-CAPABILITY` | **1** | **blocked 态的正确观测**;`packet-v7`/`v8` 声明 `blocked_by: AC-11` + `expected_exit_while_blocked: 1`,该门记 `blocked`,**不是 fail** |

- `M-TOPAZ-INJECT` / `M-TOPAZ-LOG` 为 `not run / BLOCKED`(需所有者授权真实 Topaz)。
- 13 个 `coding/evidence/*` 已在 `candidate-2` 字节上全量重录(R01 的 F1 已修:旧输出不得沿用)。
- 本地 `fixtures/tzlog/*.tzlog` 是**自造样本**,证明解析器内部一致性,不证明真实 Topaz 方言兼容;R01 已裁定夹具本身不算缺陷。
- 两条 P3(`path_is_within` 大小写、夹具断言强度)由所有者随 [ADR-003](decisions/ADR-003-finding-consumption-policy.md) 记 `waived`,`candidate-2` 中对应字节未变。
- **R02 结论**:`FAIL`。上面的门表**全部为绿**(除 blocked 的 `G-HOST-CAPABILITY`)仍不足以证明 AC-8 —— `parse_line` 把 `module_contract_matches`(对全部 `models.slp2*` 为真)传给 `detect_module_dialect`,而契约分支排在精确分支之前 → 1.7.0/1.7.1 经 `LogParser` 均返回 `ContractMatched`。A002 已在独立沙箱自写探针复现,并确认候选原样 `cargo test --workspace` = exit 0 / 11 passed。**门绿 ≠ 条款成立**,这是本轮的主要教训。
- 自 `packet-v8` 起,候选只含交付物;治理文档不再进候选。

## 恢复入口

- 接手入口:[START_HERE](START_HERE.md) → 本文件 → [index](index.md)。
- 当前任务:[`stage1-gui-backend` state](tasks/stage1-gui-backend/state.md)。
- 来源材料:`<PROJECT_ROOT>/learn/`(只读快照与分析产物)。
