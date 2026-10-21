# stage1-gui-backend state

本文件是任务的**索引**,只记"现在"。它不产生裁决,也不是验收记录;
裁决在 `review/Rxx/report.md`,派发在 `coding/dispatch-N.md` 与 `review/Rxx/dispatch.md`。
每类事实只有一个权威位置:state 记现在,packet 记契约,ADR 记为什么,报告记怎么证明。

| Field | Value |
| --- | --- |
| Task / `packet_rev` / latest pinned packet | `stage1-gui-backend` / `12` / `docs/tasks/stage1-gui-backend/packet-v12.md` |
| Pinned packet digest | `sha256:8d0a1f2cfb32c65e09b867fc3461218dcf465589e0200a375b691257c8576eef` |
| Task state | **`ACCEPTANCE_PENDING`**(R07 PASS,待所有者写 acceptance) |
| Active writer | **无**(A003 与 A003-R07 均已释放;acceptance record 归所有者) |
| Workspace / lease | `E:/project/Starlight_ssGui.worktree/A003/Master`,branch `a003/master`,epoch `1` |
| Candidate (kind; manifest) | **`candidate-7`**(bundle)(`df838a0831947789e08952a2f422c5234cc92973f5bcd2c98b62b2ad22547315`),69 files |
| Current round / family / report | `R07` **PASS** / `stage1-gui-backend` / `review/R07/report.md`(31.5 KB,45 判据行 + 9 门 + 变异 + OCR) |
| Verdict | `R01`–`R05` 全部 **FAIL**(已关闭);`R07` 判 **PASS**,绑定 `candidate-7`(`df838a08…`,69 files)+ `packet-v12`;Coverage `complete`(40 criteria + 5 rules,**0 `not run`**);R06 两条 P2 均关闭。**`PASS` ≠ 验收**:acceptance 由所有者写 |
| Finding ledger | 各轮报告 + `coverage-ledger.md`(waived 单列);finding 不再抄进本文件 |
| Checkpoints | `docs/handoff/A002.md`(Coordinator)/ `docs/handoff/A003.md`(Coding)/ `docs/handoff/A003-Rxx.md`(Review 各轮) |
| Next event / owner | 所有者写 acceptance record(含 6 条 deferral 的处置与 `until`);之后才可宣布 Stage 1 验收 / **项目所有者** |
| Blocker | 无未决阻塞:**6 条已 `deferral`**(所有者 2026-10-21 批准),交付边界 = 40 条 verifiable;`until` 见 packet |

## R07 裁决消费(2026-10-22):**PASS**

我是从证据复算的,不是从报告的结论抄的:

| 复验项 | 我的结果 |
| --- | --- |
| `verify candidate-7` | ok,**69 files**,`df838a08…` 命中 |
| Review 容器 `check` | missing 0 / modified 0 / stray 0 |
| Criteria 行 | **40 行,`not run` = 0** |
| Rules 行 | 5 行,`not run` = 0(含 `RULE-4` = `N/A`) |
| Gates 行 | 9 行,`not run` = 1(`G-HOST-CAPABILITY`,AC-11 deferral 的正确观测) |
| 判据摘要 | `lanes/review.md` `2d6655f7…` ✓、`templates/report.md` `dc3f0778…` ✓ |

### 三件必须如实记账的事

1. **判据版本漂移(判据侧,非候选缺陷)**:`SKILL.md` 磁盘 `62401e6f…`(metadata `3.1.1`,mtime 02:15)= v3.1.1,`adapters/ocr.md` `505be3e0…`;`packet-v12` 钉的是 v3.1.0 的 `3f805506…` / `cb6e05c3…`。宿主机无 v3.1.0 快照、Skill 无 changelog。**PASS 在 v3.1.0 与 v3.1.1 下都成立**:`PASS`/`Coverage complete` 的定义在 `core/loop.md` 与 `lanes/review.md`,两文件本轮都未变(sha 命中);`SKILL.md` 的 Hard rules 1–8 逐条核对该轮均满足。报告记载"所有者 2026-10-22 指示按 v3.1.1 执行"——该指示发生在 Owner↔R07 会话,我未亲见,按报告记载入账。
2. **Review 写盘位置错了**:`review/R07/{report.md,evidence/**}` 被写进 `<CODING_ROOT>`(`…/A003/Master/docs/tasks/…`)而不是治理仓库;Review 容器里根本没有治理树(候选自 `packet-v8` 起不含治理文档),所以相对路径落到了 Coding 工作区。我已逐字节复制进 `docs/tasks/stage1-gui-backend/review/R07/`(`report.md` `586fa0e9…`,33 文件,`diff -r` 无差异)。**候选未受影响**(冻结在写盘之前,且该路径不在候选清单内)。教训写进 handoff:Review 的 dispatch 必须给出**绝对**落盘路径。
3. **`AC-1.3` 标签不一致(P3,`waived`)**:该行记 `inherited`,但注释与证据显示 `G-TEST-RS` 本轮重跑(19→20);对应 gate 行是 `done`。属行标注口径问题,判据本身有证、无产品路径受影响,故 `waived` 不返工,记入 ledger。

## `candidate-7` 构建(2026-10-22)

`dispatch-9` 交回 `receipt-v8`。机械闸 **PASS exit 0**(`completion_requires_a_parseable_duration` → `..._a_parsed_duration` 已解释)。
`candidate-7` = **69 files**(c6 的 63 + `receipt-v7`/`receipt-v8` + `MB2-red`/`MB2-green`/`R07-total-processing-before`/`-after`)。
生产字节只变 `log_parser.rs`;`injection.rs`/`sitecustomize.py`/`protocol*`/`lib.rs`/`gui/**`/`fixtures/**` 与 c6 逐字节相同。
沙箱 9 门:8 绿(Rust **20** / Python 7 / GUI 6)+ `G-HOST-CAPABILITY` exit 1;候选字节上 `MB2` → RED、还原 → OK。

**冻结时差点出事**:第一次 `freeze` 用了错的 prefix 过滤,清单只覆盖 c6 的 63 个路径,`receipt-v7/v8` 与 4 个新 evidence **静默漏掉**,而且 `freeze` 不报错(它只冻结你给的清单)。已丢弃未发布的 bundle、按全库清单重建再冻。**教训**:冻结后必须跑 `check <bundle> <workspace>` 看 stray,不能只看 `file_count`。

## `dispatch-8` 消费结果(2026-10-22):两条都修好了,卡在一条断言

**我自己复验(不看 receipt)**:`unknown` / 空值 / `3,5s` → `Unknown`,`3.5s` → `Some(3.5)`,`summary(["3.5s","unknown"])` → `Some(3.5)` + `unknown_count=1`;
`MB2`(删 exec_module 的 `_record_error("import", error)` 保留 `raise`)→ **RED**(`FAILED (errors=1)`);
9 门 8 绿(Rust **20** / Python 7 / GUI 6)+ `G-HOST-CAPABILITY` exit 1;
生产 diff 只落 `log_parser.rs`,`injection.rs`/`sitecustomize.py`/`protocol*`/`lib.rs`/`gui/**` 与 c6 逐字节相同。

**机械闸仍 exit 1**,红因一条:`completion_requires_a_parseable_duration` 改名为 `..._a_parsed_duration` 且**顺手删掉了「无冒号 → Unknown」那条断言**,receipt-v7 未解释。
行为实测仍正确(合并路由后走 fall-through),但绑定没了——`R06` 报告 `AC-6.3` 那一行正是用它绑的无冒号半边。已发 `dispatch-9`:**补回断言 + `receipt-v8` 写明改名**,不改生产代码。

## 最近一次消费(`R06`,2026-10-22)

`R06` 判 **FAIL**,绑定 `candidate-6` + `packet-v12`,Coverage `partial`(38/40 done,2 `not run`),69 行覆盖、14 变异、OCR 18 条评论(249,560 tokens)。
**两条 blocking 我都独立复现过**(未采信报告):

| finding | 我的复现 |
| --- | --- |
| `R06-F1` | 干净副本加探针:`: unknown` / `: ` / `: 3,5s` 三例 → `Completed{seconds:None}`;`3.5s` 后跟垃圾行 → `summary.completed_seconds` 从 `Some(3.5)` 被覆盖成 `None` |
| `R06-F2` | 删 `sitecustomize.py:199` 的 `_record_error("import", error)` 保留 `raise` → `G-FAILSAFE` OK(5)、`G-PY-UNIT` OK(7)、`G-PY-COMPILE` exit 0 **全绿** |

**F1 是我的 spec 的锅**:`dispatch-7` 只要求收紧「无冒号」半边(C-2b),没要求「路由与取数合一」,于是「冒号+垃圾值」这条子支路原样留着;`packet-v12` 的 note 已经写对了,缺的是实现。本轮不再改契约。
`waived` 12 项(L-1/L-2/L-3/L-4/OCR#1/#2/#3/#5/#6/#7/#10/#13),全部按 ADR-003 答过「不修则哪条路径会坏」= 无可达路径。`receipt` 编号错(`AC-9.1–9.9`)归 P3,`receipt-v7` 顺手改。

## 上一轮候选构建(`candidate-6`,2026-10-21)

`dispatch-7` 交回 `receipt-v6`(12,154 B),`state=review-ready`。我在冻结前做了四件事:
生产 diff 逐文件比对(不信自述)、在**候选副本**里重放 R05 的四种变异形态、在独立沙箱跑 9 个门、跑机械闸。

**生产改动(相对 `candidate-5`)**:`log_parser.rs` 三处(分块左右须同时解析成功 / 无冒号耗时路由用同一匹配式 / 分块残行连同 `progress_percent` 一并抑制)、`sitecustomize.py` 一行(`return` → `raise`,即 C-1 的修复)。其余生产文件 `SAME`。
**测试**:Rust **19**(+4)、Python 7(GUI 6/6);`G-HOST-CAPABILITY` exit 1 = `AC-11` 缺证据的正确观测(该 6 条已 `deferral`,不阻塞 `PASS`)。
**机械闸**(`baseline/a002-receipt-check.py`)本轮自身有 bug:只扫 `backend/src/*.rs`,漏掉了 Python 测试改名 `…is_swallowed_at_injection_boundary` → `…matches_native_import_behavior`。已补 `py:`/`js:` 前缀;并把「消失必须被解释」的查找面从 `ctx`(含 dispatch)收到 `receipt`——否则我写的 dispatch 里只要提一句"删掉它",闸就判 EXPLAINED,是循环论证。反例自证:抹掉 receipt 里的改名说明 → `unexplained removals=1`,exit 1。

## 最近一次消费(`R05`,2026-10-21)

`R05` 判 **FAIL**,绑定 `candidate-5` + `packet-v10`。**4 条 P2 全部判必修**(无一 `waived`)——它们都是「实现正确、测试没守住」,修法各 1–3 条断言、生产零改动。
同一时间窗内 A002 另跑了一次 OpenCodeReview v1.13.2 实测(记录:`E:/project/Learn/notes/open-code-review/measurement-starlight-ssgui-v1.md`),逐条复核后转出 **3 条 R05 方法上看不见的真缺陷**,已并入 `packet-v11` 的三处措辞收口并进 `dispatch-7`。

finding 原文只在 `review/R05/report.md`;此处不抄。分级与合并口径见 `coding/dispatch-7.md` 的「上一轮结论」两节。

## 待所有者决定（2026-10-21 Skill 升级引发，三项；均不阻塞 A003 的 `dispatch-7`）

| # | 问题 | 选项 | 我的倾向 |
| --- | --- | --- | --- |
| ~~D-1~~ | **已定**：`review.ocr: scan`（`packet-v12`） | `scan` 需把 `authorizations.network` 扩到 OCR 的 provider 并把 `paid_services` 改 `true`（两个敏感字段） | **倾向 `scan` 仅用于 R06**：C-1/C-2 改的是守卫，正是 OCR 唯一擅长、变异测试看不见的那一类。若批，`packet-v12` 写 `scan` 并在 dispatch 里钉 provider 与成本上限 |
| ~~D-2~~ | **已定**：6 条写入 `deferral`（`packet-v12`） | A 供证据 / B 批 `N/A` / C 移出 `acceptance` 进 `deferred_items` / D 接受永不 `PASS` | 升级后的 `PASS` 要求 Coverage `complete`（无 `not run` 行），而这 6 条只能是 `not run` → **本任务当前不可能 PASS**。倾向 **C**（语义最诚实），但它是敏感字段改动，必须所有者批准 |
| ~~D-3~~ | **已定**：Skill 已发 **v3.1.0**（`SKILL.md` `3f805506…`），`packet-v12` 已改钉 v3.1.0 + 四个判据文件摘要 | — | — |

三项已全部落地为 **`packet-v12`**（`8d0a1f2c…`）：`packet_rev: 12`、6 条 `deferral`、`review.ocr: scan`、`review_instruction_version` 钉 v3.1.0 + 四文件摘要。AC 文本、门定义、`write_scope` 均未动，A003 手里的七项不受影响。**`packet.md`（活文档，`packet_rev: 12`）已建**，此后只在派 Review 时切 pin。

## 状态机位置

`PLANNED → CODING → REVIEW_READY → REVIEWING → (FAIL → FIXING → REVIEW_READY) / (PASS → ACCEPTANCE_PENDING) → ACCEPTED`

当前:`R07` 第 7 次 `REVIEWING` 判 **`PASS`**,任务进入 `ACCEPTANCE_PENDING`。六次 `FAIL` 后经 `dispatch-2`…`dispatch-9` 回到 `REVIEW_READY`。

## 派发与消费记录

| # | id | 接收方 | 类型 | 状态 |
| --- | --- | --- | --- | --- |
| 1 | `stage1-gui-backend/D001` | A003 | coding | ACK 已消费 |
| 2 | `stage1-gui-backend/A003/2` | A003 | coding(repair) | 已消费 → `receipt-v2` |
| 3 | `stage1-gui-backend/A003/3` | A003 | coding(repair) | 已消费 → `receipt-v3` 退回 → `/4` |
| 4 | `stage1-gui-backend/A003/4` | A003 | coding(repair) | 已消费 |
| 5 | `stage1-gui-backend/A003/5` | A003 | coding(repair) | 已消费 → `receipt-v4` |
| 6 | `stage1-gui-backend/A003/6` | A003 | coding(repair) | 已消费 → `receipt-v5` |
| 6b | `stage1-gui-backend/A003/7` | A003 | coding(repair) | 已消费 → `receipt-v6` |
| 6c | `stage1-gui-backend/A003/8` | A003 | coding(repair) | 已消费 → `receipt-v7`(两修均验收,剩 1 条断言缺失) |
| 6d | `stage1-gui-backend/A003/9` | A003 | coding(repair) | 已消费 → `receipt-v8` |
| 7 | `stage1-gui-backend/A003-R01/1` | A003-R01 | review | `FAIL` 已关闭 |
| 8 | `stage1-gui-backend/A003-R02/1` | A003-R02 | review | `FAIL` 已关闭 |
| 9 | `stage1-gui-backend/A003-R03/1` | A003-R03 | review | `FAIL` 已关闭 |
| 10 | `stage1-gui-backend/A003-R04/1` | A003-R04 | review | `FAIL` 已关闭 |
| 11 | `stage1-gui-backend/A003-R05/1` | A003-R05 | review | `FAIL` 已关闭 |
| 12 | `stage1-gui-backend/A003-R06/1` | A003-R06 | review | `FAIL` 已关闭(69 行覆盖) |
| 13 | `stage1-gui-backend/A003-R07/1` | A003-R07 | review | **PASS** 已关闭 |

## 候选历史

| 候选 | manifest_sha256 | files | 评审轮 | 裁决 | 生产代码是否变更 |
| --- | --- | --- | --- | --- | --- |
| `candidate-1` | `3644d35020d13a370635398129d33a66c25e3edfc867c7b9798b05c74c7036c6` | 49 | R01 | FAIL | 初版 |
| `candidate-2` | `200891411f94f96d8c8cf042877fa753a50b3c1860e229c74a99baa98aed95f1` | 53 | R02 | FAIL | 有(F2/F3/F5 修复) |
| `candidate-3` | `5f57238a81d5932414f4734a34dc10810c0ec91d9c031a872be097c672ff3098` | 37 | R03 | FAIL | 有(R02-F1/F5 修复) |
| `candidate-4` | `2cecbd4ac14c5304464efbfd1deeb3022ef4ad70403a24f3ef070f2ead54f7e4` | 55 | R04 | FAIL | **无**(仅测试) |
| `candidate-5` | `28d99bd4cbf38f606b56b6ad59d85bda0ddc6ce47affb8c2b2735c78d8f2fce5` | 58 | R05 | FAIL | **无**(仅测试与证据) |
| `candidate-6` | `3ee2f08719e111cbd60f7b7fb026144512ce6707ceed56747bbbe6c63f30dead` | 63 | R06 | FAIL | **有**(`log_parser.rs` 3 处 + `sitecustomize.py` 1 行) |
| `candidate-7` | `df838a0831947789e08952a2f422c5234cc92973f5bcd2c98b62b2ad22547315` | 69 | R07 | **PASS** | **有**(`log_parser.rs` 合并路由 + 聚合守卫) |

bundle 根:`E:/project/Starlight_ssGui.bundle/stage1-gui-backend/<candidate-N>`;Review 容器:`E:/project/Starlight_ssGui.worktree/A003/Review`。

## 验收状态总览(packet-v10,46 条)

| 类别 | 条数 | 当前 |
| --- | --- | --- |
| verifiable | 40 | 全部 `not run`,待 `R06` 按 `packet-v12` 判 |
| blocked(所有者阻塞) | 6 | `AC-4.3`、`AC-7.1`、`AC-7.2`、`AC-7.3`、`AC-11.1`、`AC-11.2` |

`blocked` 不是"未做",是"缺外部证据";没有真实 Topaz 证据前不得转写为 pass。

## 阻塞

| 阻塞项 | 影响 | 负责人 | 解除条件 |
| --- | --- | --- | --- |
| 真实 Topaz SLP 短导出 | `AC-4.3` | 项目所有者 | 授权一次短导出 |
| 真实 Topaz SLP 渲染 tzlog | `AC-7.1`–`AC-7.3` | 项目所有者 | 授权一次渲染 |
| `<SHARED_LEARN_ROOT>` 只读映射 | `AC-11.1`–`AC-11.2`(B01 host-spike) | 项目所有者 | 提供只读映射 |

## 工作区物化记录(dirty-apply)

`E:/project/Starlight_ssGui.worktree/A003/Master` 从 `6e85b9e4…` 以 `--detach` 建出、再 `git switch -c a003/master`,
未提交的规划文档按 `baseline/dirty-apply-manifest.txt`(**rev 2**)逐文件 SHA-256 校验后复制进去。
该清单描述**物化之后的 `<CODING_ROOT>`**,不描述任何候选的字节;候选身份只由 `snapshot.json` 的 `manifest_sha256` 决定。

## 变更历史

| 日期 | packet | 变更 |
| --- | --- | --- |
| 2026-10-18 | v1 | 建包;stream;profile standard;11 条 AC;11 门 |
| 2026-10-18 | v2 | AC ↔ 门双向映射补齐(`G-PY-COMPILE`、`G-HOST-CAPABILITY`) |
| 2026-10-18 | v3 | Master 工作区改为分支 `a003/master`(不再是 detached) |
| 2026-10-19 | v4 | `read_first` 自指修正;记录 B01 延后(所有者批准) |
| 2026-10-20 | v5 | 迁移 `agent-dev-loop-v3`;handoff 到 `docs/handoff/`;Review 按轮命名 |
| 2026-10-20 | v6 | 解耦 AC-11 门;删无 AC 依据的 ETA 分句;四条 AC 措辞收口 |
| 2026-10-21 | v7 | `G-HOST-CAPABILITY` 两态判定(blocked 态红不算 fail);删 `read_first` 自指 |
| 2026-10-21 | v8 | AC-8 增两半边判据;AC-10 改前缀规则;`criteria_versions` 去内嵌摘要 |
| 2026-10-21 | v9 | 引入 AC 覆盖表(A002 自造,后被 v10 撤除) |
| 2026-10-21 | **v10** | **acceptance 拆为 46 条原子 AC;删除 AC 覆盖表;AC-4 拆出可跑半边** |
