# Dispatch `stage1-gui-backend/A003/6`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/6` |
| Kind | **repair**（消费 `R04` FAIL） |
| Sent at | 2026-10-21 |
| Receiver | `A003[PiDeck]Master Coding`（同一会话） |
| **Packet** | `docs/tasks/stage1-gui-backend/packet-v9.md`（**pinned，v8 已作废**），`sha256:e13ce1a8525de0d1a203bc210c4cf3f95fcb3b17f44b27e1dda3f3928231b825` |
| 机械闸 | `baseline/a002-receipt-check.py` `sha256:6cfe3fae3803979944cb6e0364058e2fceabaf8f4b573f4af83244e93780acd2`（已升级） |
| Workspace | `<CODING_ROOT>` = `E:/project/Starlight_ssGui.worktree/A003/Master`，分支 `a003/master` |
| Candidate base | `candidate-4` `2cecbd4ac14c5304464efbfd1deeb3022ef4ad70403a24f3ef070f2ead54f7e4`（55 files） |
| Resumed | `coding/receipt-v4.md` → **`coding/receipt-v5.md`** |
| ACK 位置 | `docs/handoff/A003.md`（追加 checkpoint） |

## 上一轮结论

`A003-R04` 判 **FAIL**，绑定 `candidate-4` + `packet-v8`。报告：`docs/tasks/stage1-gui-backend/review/R04/report.md`。

R04 跑了 **21 个交付行变异 + 13 次追加运行 → 25 红 / 9 绿**，并逐行审了那张 AC 覆盖表。

A002 已独立复现其中三条关键结论（不是采信报告）：

| 复现 | 做法 | 结果 |
| --- | --- | --- |
| R04-F1 | 沙箱里删 `injection.rs:97-102`（audit_file 落在 install_dir 的预检） | `cargo test` **14/14 全绿** → 确认无断言 |
| R04-F2 | 把 `path_is_within` 压成一行（纯 fmt 违规） | `cargo test` **14/14 绿**、`cargo fmt --check` **exit 1** → 确认 AC-1 只由门守护 |
| R04-F4(a) | 把审计 `after` 记成 `old_value`（实际写入仍是新值） | `G-PY-UNIT` **7/7 全绿** → 确认无断言 |

## 本轮分级（A002 决定，含一条上调）

| Finding | R04 级别 | **本轮处置** | 依据 |
| --- | --- | --- | --- |
| **R04-F1** | P2 blocking | **必修** | AC-10 明文含「或落在禁用位置」。退化后 backend 报 `Injected`、hook 拒写审计 → 审计静默缺失而 GUI 认为注入成功。可达 |
| **R04-F2** | P2 blocking | **必修** | AC-1 的真守卫是 4 个门，表里却引用了一条无关单测 + 改期望的变异（tautology）。**其中一半是我的形状错误**，见下 |
| **R04-F4(a)** | P3 | **上调为 P2 blocking，必修** | R04 用「AC 明文分句 + 零断言」判 F1 为 blocking；AC-4 的「生效参数与请求参数逐项一致」是同一形状，且它守的是**产品不变量 #3（监控数据不得伪造）**唯一没被守住的表面。判据一致，不分两套 |
| R04-F3 | P3 | **`waived`** | AC-3 的「固定前缀」= 运行内稳定、非字面值。现已断言「非空 + stderr 以它开头」，置空会红。字面值不是契约 |
| R04-F4(b) | P3 | **`waived`** | AC-7 的夹具半边（阶段/分块）与 AC-6 的 `parses_phases_progress_and_completion` 重复；AC-6 已守。加重复断言不新增风险，按 ADR-003 §3 选更少部件 |
| R04-F5 | P3 | **随修（不设为独立 AC）** | 3 处记录改正，与 receipt 重写同一批；其中 (c) 机械闸现已能自动抓 |
| R04-F6 | P3 | **`waived`** | 已记为 A002-C4（变异脚本非字节级恢复）。不为此花一轮 |

## 我的错，已在本轮修掉形状（R04-F2 的一半）

`dispatch-5` 要求「11 行，每条 AC 一条断言」。**这个要求本身是错的**：AC-1 的 `verification` 本来就是 `G-FMT, G-CLIPPY, G-TEST-RS, G-BUILD`，没有任何单测能看见它变坏。你被迫填一条无关测试，机械闸又只校验形式，于是 AC-1 行通过了。

**packet-v9 已修**：断言列现在允许写**门 id**，并明文禁止"为填满断言列而引用无关测试"。AC-1 行就写 4 个门 id。

## 本轮要做的四件事

### 1. R04-F1（P2）— AC-10 的「audit_file 落在禁用位置」

`backend/src/injection.rs:97-102` 有预检，但**测试模块里没有任何用例构造该输入**。

在 `injection::tests` 追加一条（A003 自定名，建议 `audit_file_inside_install_directory_uses_native_fallback_with_reason`）：

- `audit_file = <install_dir>/audit.jsonl`（`install_dir` 与 `hook_dir` 都合法）；
- 断言 `LaunchMode::NativeFallback`；
- 断言 `code == "install_directory_forbidden"`；
- 断言 `environment == base_environment`（未被污染）。

**变红证据**：删掉 `injection.rs:97-102` 那段 → 新测试必须红（现在是 14/14 全绿）。把两次运行都放进 evidence。

### 2. R04-F2（P2）— AC-1 行改写

`receipt-v5.md` 的 `## AC 覆盖表` 里，AC-1 行改成：

| AC | 断言 | 变异 | 变异后 | 证据 |
| --- | --- | --- | --- | --- |
| AC-1 | `G-FMT`, `G-CLIPPY`, `G-TEST-RS`, `G-BUILD` | 把 `path_is_within` 压成一行（纯格式化违规，不改行为） | RED | `evidence/ac-coverage/AC-1.txt` |

并在该行或表下注明一行：**「本 AC 无单测能看见，守卫是门」**。

把原来那条 `seam_kinds_are_explicit_and_small` 移到它真正服务的行（AC-9 的 seam 契约），或在 AC-9 行补上。

证据里必须同时有：基线 `cargo test` 14/14 绿 + `cargo fmt --check` exit 0；变异后 `cargo test` 仍 14/14 绿 + `cargo fmt --check` exit 1。**这个"测试看不见、门看得见"的对比就是本条的证据。**

### 3. R04-F4(a)（P2）— AC-4 的「生效参数与请求参数逐项一致」

`hook/sitecustomize.py:137-140` 写 `{"before": old_value, "after": new_value, "source": environment_name}`。当前没有断言钉住 `after` 真的等于**实际写入值**。

在 `hook/tests/` 里补断言（用已有的 apply 用例即可）：

- `changes[name]["after"] == 被 setattr 写入的新值`；
- `changes[name]["before"] == 原值`；
- `changes[name]["source"]` 是对应的环境变量名。

**变红证据**：把 `"after": new_value` 改成 `"after": old_value` → 必须红（现在是 7/7 全绿）。

> 不用构造真实 Topaz。这条只验 hook 自身记录的准确性，AC-4 的「真实渲染」半边仍 `BLOCKED`。

### 4. R04-F5（P3）— 三处记录改正

| # | 问题 | 改法 |
| --- | --- | --- |
| a | `receipt-v4.md:22-27` 称 F3 baseline 用 `python -m unittest hook.tests.test_failsafe -v`（5 tests），而 `ac-coverage/AC-3.txt:6,28` 记的是 `discover -s hook/tests`（7 tests） | 统一为**实际跑过的那条**命令 |
| b | `receipt-v4.md:46` 称「全部 11 个门重录」，但 `M-TOPAZ-*` 是 `not run` | 改成「9 个自动门重录；2 个 M 门 not run / BLOCKED」 |
| c | `ac-coverage/AC-9.txt:2` 写 `rejects_structured_events_missing_required_fields`，源码里**没有这个名字**（真实是 `rejects structured events missing required fields`，带空格） | 改成真实名字 |

(c) 现在会被机械闸抓（见下），(a)(b) 不会——闸管不到，靠你。

## 机械闸已升级（`sha256:6cfe3fae…`）

三项变化：

1. **断言列允许门 id**：`G-FMT`/`G-CLIPPY`/`G-TEST-RS`/`G-BUILD`/`G-PY-UNIT`/`G-FAILSAFE`/`G-PY-COMPILE`/`G-GUI-TEST`/`G-HOST-CAPABILITY`/`M-TOPAZ-*`。
2. **新增 `evidence/ac-coverage/*.txt` 自洽检查**：每个文件的 `assertion:` 行引用的名字必须真实存在。这份检查现已抓到 `AC-9.txt` 的那个假名字（R04-F5c）——**这是 R04 抓到的、我上一轮漏掉的**。
3. **明确作用边界，写进脚本 docstring**：

> 第三项是**形式校验**，只回答"行齐不齐、名字存不存在、取值合不合法"。它**不判断**变异是否真的改动了生产行为，也**不判断**所引断言是否与该 AC 相关。把 AC-1 行换成一句无意义的描述，本闸仍会 PASS。**机械闸全绿不得当作"AC 表可信"的证据。**

R04 指出这一点是对的。我没有加一个假的"语义守卫"去假装能判——**判不了就写明判不了**，把语义判断留给 Review 轮独立复现。

当前对你的要求：

```
python docs/tasks/stage1-gui-backend/baseline/a002-receipt-check.py --require-ac-table \
  E:/project/Starlight_ssGui.bundle/stage1-gui-backend/candidate-4/payload \
  . docs/tasks/stage1-gui-backend/coding/receipt-v5.md \
  docs/tasks/stage1-gui-backend/coding/evidence/*.txt \
  -- docs/tasks/stage1-gui-backend/coding/dispatch-5.md \
     docs/tasks/stage1-gui-backend/coding/dispatch-6.md
```

现在是 **exit 1，唯一红因是 `AC-9.txt` 引用了不存在的断言名**。改完那三处应当 exit 0。

## 不要做的事

| 禁止 | 原因 |
| --- | --- |
| 改生产语义 | 本轮全部是补测试与改记录。生产代码在 R04 眼里是**正确**的（三个探针都证明了） |
| 碰 R04-F3 / F4(b) / F6 | 已 `waived`，理由见上表 |
| 碰 R03-F4、R02-F3/F6、R01 F6/F7 | 历史 `waived` |
| 复用 `receipt-v4.md` 的 AC 表并只改一处 | 11 行全部按 v9 规则复核；门守护的行要写门 id |
| 用旧 evidence | 全部重录 |
| 在 receipt 里写没跑过的命令 | R04-F5(a)(b) 就是这么来的 |
| 动 `review/R0*`、`state.md`、`coverage-ledger.md`、`packet-v*.md` | 治理侧 |

## 交付

1. `coding/receipt-v5.md`（state `review-ready`），含按 v9 规则写的 `## AC 覆盖表`，含 R04-F1/F2/F4a/F5 的响应行；
2. `coding/evidence/` 全量重录 + `ac-coverage/` 11 份更新；
3. `docs/handoff/A003.md` 追加 checkpoint；
4. **报告前自己跑上面那条机械闸并贴 exit code**（目标 0）。

## 我收到后

机械闸 → 生产代码 diff（剥 `#[cfg(test)]` 后应当**零差异**，本轮允许 `hook/sitecustomize.py` 除外——只有测试文件可动）→ 抽查复现你的三条变红 → 冻结 `candidate-5` → 派 `A003-R05`（全新会话）。
