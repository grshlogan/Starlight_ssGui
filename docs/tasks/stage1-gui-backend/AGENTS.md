# Task Folder Rules (`stage1-gui-backend`)

本目录是任务 `stage1-gui-backend` 的记录。协议与 profile 版本由 packet 记录(`agent-dev-loop-v3`,`packet-v12`),此处**不复制**协议内容。上层规则:[`docs/tasks/AGENTS.md`](../AGENTS.md)、根 [`AGENTS.md`](../../../AGENTS.md)。

## 文件与写者

| 文件 | 写者 | 可变性 |
| --- | --- | --- |
| `packet-vN.md` | Coordinator `A002` | 发布后不可变;变更建 `vN+1` |
| `state.md` | Coordinator `A002` | 可变索引;从不作为 verdict 源 |
| `coverage-ledger.md` | Coordinator 绑定;Review 写自己的切片 | 追加/状态更新 |
| `coding/dispatch-N.md` | Coordinator `A002` | 发出后不可变 |
| `coding/receipt-vN.md` | Coding `A003` | 追加版本 |
| `coding/evidence/` | Coding `A003` | 追加 |
| `review/Rxx/dispatch.md` | Coordinator `A002` | 发出后不可变 |
| `review/Rxx/report.md` | Review(每轮新会话 `A003-Rxx`) | 发布后不可变;**末节即 next action** |
| `review/Rxx/evidence/` | Review | 轮内追加 |
| `acceptance.md` | 验收人(项目所有者) | 不可变记录 |

## 规则

1. 轮次零填充(`R01`)且只增;版本为 `vN`。
2. **候选载荷不在本目录**——在 `<BUNDLE_ROOT>`(源码树外,`<PROJECT_ROOT>.bundle/`)。
3. **身份的 ACK/checkpoint 不在本目录**——在各自工作区 `docs/handoff/<identity-id>.md`,永不进候选。
4. 已发布版本与已发布报告永不覆盖。
5. 任务关闭后仍保留在 [文档索引](../../index.md),不删除。

## 当前状态

| 项 | 值 |
| --- | --- |
| packet | `packet.md`(活文档,`packet_rev: 12`)/ `packet-v12.md`(当前 pin;46 条 AC = 40 verifiable + 6 deferred;`review.ocr: scan`) |
| 文档桥 | `baseline/docs-bridge-manifest.txt` |
| 拓扑 | `stream` |
| 模块 | `backend`、`GUI` |
| Master Coding | `A003[PiDeck]Master Coding` |
| Review 家族 | `stage1-gui-backend`(`A003-R01`–`R04` 均关闭=FAIL;下一轮 `A003-R05`) |
| 验收人 | 项目所有者 |
| 任务状态 | `REVIEW_READY` |

## 治理文档如何到达 `<CODING_ROOT>`

PiDeck 的 worktree 相互独立,且 `hosts/pideck.md` 载明 cross-session messaging **unavailable** —— 治理工作区的任何新文件**不会**自动出现在 Coding 工作区。

规则:**packet / dispatch / Review report 一发布,立即桥进 `<CODING_ROOT>`**,不等对方来要。

- 桥记录:`baseline/docs-bridge-manifest.txt`(文件 + SHA-256)。
- 排除:**A003 自己的产物** —— `docs/handoff/A003.md`、`coding/receipt-*.md`、`coding/evidence/**`。桥只做单向覆盖,不得回写对方产物。
- 自检:A003 报「文件不存在」时,先查桥,不要怀疑对方读错路径。

此前的缺口(2026-10-21):`packet-v7/v8`、`coding/dispatch-3.md`、`review/R02/**` 只在治理工作区建立,A003 报到时全部不可见,导致一次 admission 中断。已补桥并登记。

## 冻结前置机械检查(2026-10-21 起,不可跳过)

`freeze` 之前,Coordinator 必须跑这三项,结果留档到 `baseline/a002-receipt-check-<candidate>.txt`:

1. **候选间 Rust 测试名集合比对** —— 从 `backend/src/*.rs` 提取 `#[test] fn <name>`,与上一候选求差集。**消失的测试必须被解释或被补回**。绿灯不能以删测试换取。
2. **receipt 声称的测试名 vs evidence 内容一致性** —— receipt 里每提到一个测试名,该名字必须能在其引用的 evidence 文件中 `grep` 到 `... ok` 行。
3. **receipt 里反引号包裹的标识符必须真实存在** —— 至少两个下划线、非全大写的 token,必须能在候选源码 / evidence / dispatch 任一处找到。防“引用了一个从未存在过的符号”(A002-C1、R04-F5c)。

三项都是纯机械比对,不依赖任何人自述。脚本：`baseline/a002-receipt-check.py`。

**校验器必须用反例自证能红。** 本脚本第 3 项首版有个 bug:`known` 集合把 receipt 自身也包进去了,于是任何 token 都“已知”,幽灵名一个也抓不到 —— 而它当时是 `PASS`。用一条凭空捧造的测试名做反例才发现。

**已撤除**:第四项 `--require-ac-table`(校验 receipt 内 `## AC 覆盖表` 的形状)随 `packet-v10` 删除。原因:覆盖表是 A002 自造物,不在 Skill 里;而且它只是**形式校验**——把 AC-1 行换成一句无意义的描述,闸仍然 PASS(R04-F2)。契约层面改为「AC 原子化 + clause → symbol → check 映射归 Review」。
