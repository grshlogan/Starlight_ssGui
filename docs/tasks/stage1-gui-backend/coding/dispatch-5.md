# Dispatch `stage1-gui-backend/A003/5`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/5` |
| Kind | **repair**（消费 `R03` FAIL） |
| Sent at | 2026-10-21 |
| Deadline | 交付 `receipt-v4.md` 且 state = `review-ready`；超期由 A002 记 `TIMEOUT` |
| Receiver | `A003[PiDeck]Master Coding`（**同一会话,不换身份**） |
| Packet | `docs/tasks/stage1-gui-backend/packet-v8.md`（**pinned,不升版本**）,`sha256:d41a70d2abccb3a49167bd1f57f2f405bd8e6dcaf1df89e514daec7a412b2c23` |
| 协议 | `agent-dev-loop-v3`（Skill v3.0.0,`SKILL.md` `sha256:049857138fcff222d38eb36679775e178b9bf66633fea6d2c5feb0959c0fcfe4`） |
| Workspace | `<CODING_ROOT>` = `E:/project/Starlight_ssGui.worktree/A003/Master`,分支 `a003/master` |
| Candidate base | `candidate-3` `manifest_sha256` = `5f57238a81d5932414f4734a34dc10810c0ec91d9c031a872be097c672ff3098`（37 files） |
| Resumed | `coding/receipt-v3.md` → **`coding/receipt-v4.md`** |
| ACK 位置 | `docs/handoff/A003.md`（追加 checkpoint） |

## 上一轮的结论

`A003-R03` 判 **FAIL**，绑定 `candidate-3` + `packet-v8`，报告在 `docs/tasks/stage1-gui-backend/review/R03/report.md`（末节即它的 next action）。

它跑了 **28 个变异：22 检出 / 6 未检出**。本轮要清掉的就是未检出的那部分。

**关键事实：三条 blocking 都不需要改生产代码。** R03 用独立探针确认三处实现**当前是正确的**，缺的是能证明它正确的断言。

| Finding | 级别 | AC | 变异 | 现在的后果 |
| --- | --- | --- | --- | --- |
| R03-F1 | P1 blocking | AC-9 | 删 `changes`/`timestamp_utc` 校验、未知 `kind` 改 `throw` | 4 条 GUI 测试**仍全绿** |
| R03-F2 | P2 blocking | AC-10 | 删 `injection.rs:93-107` 两段审计预检 | 12 条 Rust 测试**仍全绿** |
| R03-F3 | P2 blocking | AC-3 | `ERROR_PREFIX` 置空 | 7 条 Python 测试**仍全绿** |

## 本轮只做三件事 + 一张表，不许加戏

### 1. R03-F1（P1，AC-9）

`structured_event` 没有拒绝路径用例。AC-9 原文就要求「四类消息各有 TS 侧校验与**拒绝路径**测试」。

要补的（至少）：
- `structured_event` 缺必填字段（`changes` 或 `timestamp_utc`）→ 必须被拒；
- `structured_event` 未知 `kind` → 必须被拒。

补完后，上面那条变异（删校验 / 未知 kind 改 `throw`）**必须让新测试变红**。这条自行验证，把两次运行的输出放进 evidence。

### 2. R03-F2（P2，AC-10）

`injection.rs:93-107` 的两段审计预检（路径可写、父目录存在）没有任何断言，`audit_unavailable` 分支从未被触发过。

要补一条能真正触发它的用例：审计路径指向不可写/不可创建的位置 → 断言**回退行为**与**审计内容**都符合 AC-10。补完把预检删掉必须变红。

### 3. R03-F3（P2，AC-3）

`ERROR_PREFIX` 置空后 7 条 Python 测试全绿 → stderr 固定前缀没有任何断言。

补断言：错误路径的 stderr 必须以该前缀开头。置空 `ERROR_PREFIX` 必须变红。

### 4. 全 AC 覆盖表（**这是交付物的一部分，不是可选说明**）

写进 `receipt-v4.md` 的 `## AC 覆盖表` 节。表头**一字不差**（我的机械闸按它解析）：

```
## AC 覆盖表

| AC | 断言 | 变异 | 变异后 | 证据 |
| --- | --- | --- | --- | --- |
| AC-1 | `some_test_name` | 把 pocketjs 依赖加进 Cargo.toml | RED | `evidence/ac-coverage/AC-1.txt` |
```

规则：

- **11 行**，`AC-1`..`AC-11` 各出现且只出现一次；
- **断言**列用反引号列出**真实存在于源码**的断言名（Rust `#[test] fn`、Python `def test_*`、TS `test('…')`）。闸会逐个核验，写不存在的名字直接 FAIL；
- **变异**列写一个具体改动（单行/单表达式最好），不要写"破坏它"这种抽象描述；
- **变异后**只能是 `RED` / `GREEN` / `blocked`。**只有 `AC-4`、`AC-7`、`AC-11` 可以写 `blocked`**；
- **证据**列指向 `coding/evidence/ac-coverage/` 下文件，里面同时有**基线跑**和**变异后跑**两份输出。

**出现 `GREEN` 就是失败。** 空格必须自己补掉。

如果某条你判断"补它的成本高于它防的风险"，**不要静默 waive**：在 receipt 里单列一节「请求豁免」，填 ADR-003 四问（级别 / 可达路径 / 修法成本 / 契约还是实现），我交所有者定。豁免权限不在你也不在我。

已经知道的映射（可以直接用，但要自己验证）：

- `AC-8` → `parser_recognizes_all_dialects_through_log_parser`
- `AC-10` → `pythonpath_override_is_reserved`、`non_reserved_override_merges_into_environment`
- `AC-11` → `test_evidence_exists`、`test_evidence_is_bound`（变异：让 `test_evidence_is_bound` 跳过 `status:` 检查 → 应红）

## 机械闸升级了

`docs/tasks/stage1-gui-backend/baseline/a002-receipt-check.py` 新增第三项检查，本轮冻结前用 `--require-ac-table` 跑：

```
python docs/tasks/stage1-gui-backend/baseline/a002-receipt-check.py --require-ac-table \
  E:/project/Starlight_ssGui.bundle/stage1-gui-backend/candidate-3/payload \
  <CODING_ROOT> <CODING_ROOT>/docs/tasks/stage1-gui-backend/coding/receipt-v4.md \
  <evidence files...> -- documentation of explained removals...
```

它检查：11 行齐全、无重复、每个断言名真实存在、`变异后` 取值合法、无空单元格、非 blocked AC 不得为 `GREEN`。

**你可以自己先跑一遍**，跑通再报 `review-ready`，省一轮往返。

## 候选范围变化（`candidate-4` 起，**不用你做任何事**）

`docs/handoff/.gitignore` 与 `docs/handoff/AGENTS.md` 回到 allowlist。

原因：R03-F5 是我的错。我在 v8 把治理文档踢出候选时，把这两个也一起踢了 —— 它们不是"治理内容"，是**保留路径机制的执行者**。它们一没，`git check-ignore docs/handoff/A003-R03.md` 从 exit 0 变成 exit 1，我在 dispatch 里却写了 exit 0。

## 不要做的事

| 禁止 | 原因 |
| --- | --- |
| 改生产代码 | R03 已验证实现正确；改它会让 AC-8/AC-10 的既有证据失效 |
| 碰 R03-F4 | P3，`waived`（父包命中前缀多写一条 error 事件，不改变注入决策、不影响回退，审计行描述的是真实发生的不匹配） |
| 碰 R02-F3 / R02-F6 / R01 F6 / F7 | 已 `waived` |
| 升 packet 版本 | packet-v8 已 pinned，本轮不变 |
| 动 `review/R01`、`R02`、`R03` | Review 的归档，只读 |
| 写 acceptance | 那是所有者的 |
| 复用旧 evidence | R01-F1 就是这么来的。**全部重录** |

## 交付

1. `docs/tasks/stage1-gui-backend/coding/receipt-v4.md`，state = **`review-ready`**，含 `## AC 覆盖表`，含 F1/F2/F3 的响应行（`AGREE` + 修复位置 + 变红证据）；
2. `docs/tasks/stage1-gui-backend/coding/evidence/` 全量重录（旧的删掉或覆盖）；
3. `docs/tasks/stage1-gui-backend/coding/evidence/ac-coverage/` 每行一份；
4. `docs/handoff/A003.md` 追加 checkpoint。

报 `review-ready` 之前，请自己跑一次上面的机械闸（带 `--require-ac-table`），贴 exit code。

## 我收到后做什么

机械闸 → 生产代码 diff（剥掉 `#[cfg(test)]` 后应当**零差异**，否则说明你动了不该动的东西）→ 冻结 `candidate-4` → 派 `A003-R04`（全新会话）。
