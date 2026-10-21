# Coding Dispatch `stage1-gui-backend/A003/9`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/9` |
| Kind | **coding**（`repair`，**极小**：1 条断言 + 1 条 receipt 说明，**不改生产代码**） |
| Sent at | 2026-10-22 |
| Base | 当前工作区（相对 `candidate-6`：`backend/src/log_parser.rs` + `hook/tests/test_failsafe.py`） |
| Pinned packet | `packet-v12.md`（`8d0a1f2c…`） |
| Target state | `REVIEW_READY` 后停手 |

## 先说结论：两条必修都真的修好了

我自己复验过，不是看你的 receipt：

```
Total processing time: unknown   -> Unknown {..}          ✓
Total processing time:           -> Unknown {..}          ✓
Total processing time: 3,5s      -> Unknown {..}          ✓
Total processing time: 3.5s      -> Completed {seconds: Some(3.5)}  ✓
summary(["3.5s","unknown"])      -> Some(3.5), unknown_count=1      ✓
```

`MB2`（删 `sitecustomize.py` 里 exec_module 的 `_record_error("import", error)`、保留 `raise`）现在**变红**（`FAILED (errors=1)`）。9 个门：8 绿（Rust **20** / Python 7 / GUI 6），`G-HOST-CAPABILITY` exit 1 = `AC-11` 缺证据的正确观测。生产 diff 只落在 `log_parser.rs`，`injection.rs`/`sitecustomize.py`/`protocol.*`/`lib.rs`/`gui/**` 与 `candidate-6` 逐字节相同。

## 还差两件小事（机械闸抓到的）

```
## 消失的测试
  - rs:completion_requires_a_parseable_duration
## 新增的测试
  + rs:completion_requires_a_parsed_duration
  + rs:completion_without_a_parsed_duration_does_not_clear_summary
## 消失测试的解释状态
  [UNEXPLAINED] rs:completion_requires_a_parseable_duration
RESULT: FAIL (exit 1)
```

改名本身没问题，问题在两处：

### 1. 改名时**顺手删掉了一条断言**，要补回来

旧测试 `completion_requires_a_parseable_duration` 里有这条：

```rust
assert!(matches!(
    parse_line("2026-10-19 10-00-03.000 Info total processing time 3.5s", None),
    LogEvent::Unknown { .. }
));
```

（**无冒号**的 `total processing time 3.5s` → `Unknown`。）

新测试 `completion_requires_a_parsed_duration` 里它没了。我实测当前行为仍是 `Unknown`（合并路由后靠 fall-through），**行为对，但没东西守着它**——这正是 `R06-F2` 那一类。`R06` 报告里 `AC-6.3` 那一行就是用这个测试绑定「无冒号半边」的，删掉之后下一轮没有依据可指。

**做法**：在 `completion_requires_a_parsed_duration` 里把它加回原样（跟三条垃圾值断言并列即可，别改代码）。

### 2. `receipt-v8` 要写清这次改名

**做法**：交 `receipt-v8.md` = `receipt-v7` 全文 + 一节 `## 相对 receipt-v7 的变更`，两句话：

- `completion_requires_a_parseable_duration` → 改名为 `completion_requires_a_parsed_duration`（原因：断言从「一条正例 + 一条无冒号反例」扩成「三条垃圾值反例 + 一条正例 + 无冒号反例」）；
- 无冒号断言在上一版被误删，本版已补回（行为一直是对的，缺的只是绑定）。

机械闸的规则是「消失的测试名必须在 **receipt** 里被解释」——它会去 receipt 正文里找旧名字，所以这两句话里必须出现 `completion_requires_a_parseable_duration` 这个字符串本身。留在 `dispatch` 里不算（我上一轮刚把这条判定从 `ctx` 收紧到 `receipt`，否则我自己写的 dispatch 提一句就能让闸放行，是循环论证）。

## 不要做的

| 禁止 | 原因 |
| --- | --- |
| 改 `backend/src/log_parser.rs` 的**生产段** | F1 已验收通过，一动就要重验收 |
| 改 `hook/sitecustomize.py`、`injection.rs`、`protocol.*`、`gui/**` | 本轮零需求 |
| 为了让闸放行而改 `baseline/a002-receipt-check.py` 或 dispatch | 闸是判据，不是障碍 |
| 重跑 OCR / 新增探针脚本进候选 | 不需要 |

## 交付

1. `hook/tests/test_failsafe.py` **不动**；`backend/src/log_parser.rs` **只允许动 `#[cfg(test)]` 段**（补回那条断言）。
2. `receipt-v8.md`（含上面两句话）。
3. `coding/evidence/G-TEST-RS.txt` 重录（Rust 仍是 20 个测试，只是断言变多）。
4. 停在 `REVIEW_READY`；冻结与派 Review 由我做。
