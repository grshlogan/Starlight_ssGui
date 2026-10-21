# Coding Dispatch `stage1-gui-backend/A003/8`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/8` |
| Kind | **coding**（`repair`） |
| Sent at | 2026-10-22 |
| Receiver | `A003[PiDeck]Master Coding` |
| Base | `candidate-6`（`3ee2f08719e111cbd60f7b7fb026144512ce6707ceed56747bbbe6c63f30dead`，63 files） |
| Pinned packet | `packet-v12.md`（`sha256:8d0a1f2cfb32c65e09b867fc3461218dcf465589e0200a375b691257c8576eef`） |
| Previous round | `review/R06/report.md`（**FAIL**，2×P2 blocking） |
| Write scope | `backend/src/log_parser.rs`（生产段）、`hook/tests/test_failsafe.py`；新证据；`receipt-v7.md`。**不得动** `hook/sitecustomize.py`、`injection.rs`、`protocol.*`、`gui/`、`packet`、`ledger`、既往轮报告 |
| Target state | `REVIEW_READY` 后停手 |

## 上一轮结论：`R06` FAIL，两条 blocking

R06 判 `FAIL` 的两条我在独立副本里各复现了一次（下面是**我实测的输出**，不是转述报告）。两条都成立，都判**必修**。

### 必修 1 — `R06-F1`：`Completed{seconds:None}` 是伪造出来的"完成"（P2, blocking）

`AC-6.3` note 明文：`Completed` 必须携带**解析出的**耗时；路由与取数必须用**同一匹配式**；解析不出即 `Unknown`。

我在 `candidate-6` 的干净副本里加了一个探针测试，实测：

```
Total processing time: unknown        -> Completed { seconds: None }     ← 应为 Unknown
Total processing time:                -> Completed { seconds: None }     ← 应为 Unknown
Total processing time: 3,5s           -> Completed { seconds: None }     ← 应为 Unknown
Total processing time: 3.5s           -> Completed { seconds: Some(3.5) } ← 不变
summary(["... 3.5s", "... unknown"])  -> completed_seconds = None         ← 3.5 被垃圾行覆盖丢失
```

原因是两条独立的路：`log_parser.rs:219-223` 用 `lower.contains(marker)` **路由**，`parse_seconds`（`:185-193`）**另取一次值**，于是「有冒号但值不是数」落进 `Completed{seconds:None}`；再加 `:88` 的 `self.summary.completed_seconds = *seconds` 无条件覆盖写，一个垃圾行就能把已经拿到的 3.5 抹成 None。

**这条是我上一轮 spec 的锅**：`dispatch-7` 只要求收紧「无冒号」半边（C-2b），没要求「路由与取数合一」，于是我改了 note、你按 note 改了无冒号路径，冒号+垃圾值这条子支路原封不动留着。`packet-v12` 的措辞我没再改——它已经写对了，缺的是实现。

**修法（照这个形状，不要再加分支）**：把两条路并成一条——先解析，解析不成就判 `Unknown`：

```rust
// parse_line：放在 phase/progress 检测之前
if let Some(seconds) = parse_seconds(clean) {
    return LogEvent::Completed { seconds: Some(seconds) };
}
if lower.contains(TOTAL_PROCESSING_TIME_MARKER) {
    return LogEvent::Unknown { line: clean.to_owned() };
}
```

聚合处不许用 `None` 覆盖已有值：

```rust
LogEvent::Completed { seconds } => {
    if let Some(seconds) = seconds {
        self.summary.completed_seconds = Some(*seconds);
    }
}
```

枚举里的 `Option<f64>` **保持不动**（改类型会波及 `protocol.rs` 与序列化，收益不值）；要保证的是 `parse_line` 永不产出 `Completed{seconds:None}`。

**必须新增的两条测试**（放 `log_parser.rs` 的 `#[cfg(test)]`）：

1. `completed_requires_a_parsed_duration`：`unknown` / 空值 / `3,5s` 三种 → `LogEvent::Unknown`；`3.5s` → `Completed{seconds:Some(3.5)}`。
2. `completion_without_a_parsed_duration_does_not_clear_summary`：先 `3.5s` 再垃圾行 → `summary.completed_seconds == Some(3.5)`。

**验收信号**：上面四条探针行改完之后，三条变 `Unknown`、`3.5s` 不变、summary 保住 `Some(3.5)`；且 `cargo fmt --all --check` / `cargo clippy --workspace --all-targets -- -D warnings` / `cargo test --workspace` 全 exit 0。

### 必修 2 — `R06-F2`：`AC-3.5` 的 import 失败半边没有任何门守着（P2, blocking）

我按报告给的变异形态自己动手删了一次：把 `hook/sitecustomize.py:199` 的 `_record_error("import", error)` 删掉、`raise` 留着，然后跑三个 Python 门：

```
G-FAILSAFE   OK        （5 tests）
G-PY-UNIT    OK        （7 tests）
G-PY-COMPILE exit 0
```

**全绿。** 也就是说，审计里「目标模块导入失败过」这条记录哪天被删掉、被重构掉、被搬进死代码，现在的门一个都看不见。生产行为此刻是对的（探针能观测到 error 行），但它是**没被守住的对**，和 R05-F1–F4 同一类。

**修法（不加新测试文件，就地补断言）**：在 `hook/tests/test_failsafe.py` 的 `test_failsafe_import_failure_matches_native_import_behavior` 里补三件事：

1. 用 `contextlib.redirect_stderr(stderr)` 包住那次失败的 import；
2. 断言 stderr 首行以 `self.sitecustomize.ERROR_PREFIX + " "` 开头；
3. 断言审计里存在一条 `event == "error"`、`stage == "import"`、`error_type == "RuntimeError"`、且 `error` 含 `target import failure` 的行（行形状见 `_record_error`：`stage`/`error_type`/`error` 与 `event` 同层，`_write_audit_line` 用 `_event()` 合并）。

顺带确认：`self.assertNotIn("models.slp2.broken", sys.modules)` 与 `healthy.VALUE == 42` 两条**保留**——它们守的是 `AC-3.1`，别在改这个测试时把 `AC-3.1` 的绑定弄丢。

**验收信号**：把必修 2 的断言加上之后，重放 `MB2`（删 `_record_error("import", error)`、保留 `raise`）→ `G-FAILSAFE` **必须 RED**。这是本轮唯一能证明「补的是真守卫」的证据，必须自己的证据里有一条 RED 记录 + 还原后 GREEN。

## P3：顺手改，不单独验

`receipt-v6` 的映射表把 `AC-9` 写成 `9.1–9.9`，实际只有 `AC-9.1`–`AC-9.4`。`receipt-v7` 里请引用真实编号（闸不校验编号存在性，所以它没被拦住）。

## `waived`：本轮不修，不要碰

按 `ADR-003` 逐条给了「不修则哪条路径会坏」的答案，全部**无可达路径**：

| 项 | 为什么不修 |
| --- | --- |
| `L-1` `VAE Decode chunk 33% done` 的百分比被丢弃 | 没有任何 AC 约束这个方言；`AC-6.2` 只要求分块对锚定 |
| `L-2` `chunk 5/` → `Unknown` | v11 note 明文要求整对锚定，当前行为**合规** |
| `L-3` `KeyboardInterrupt`/`SystemExit` 不写 error 行 | 原生 Topaz 同样穿透；AC 未把 `BaseException` 纳入「失败」 |
| `L-4` stderr 写失败顶掉原始异常 | 需要 stderr 本身坏掉才可达（环境失效），`lanes/review` 不算 FAIL |
| `OCR#1` loader 缺 `__getattr__` 委托 | traceback/linecache 走 `__file__`，当前部署无影响 |
| `OCR#2` `_launch_id()` 每次新 uuid | 只有不注入 `TOPAZ_SLP_LAUNCH_ID` 的回退路径才触发 |
| `OCR#3` `_coerce` 对非标量默认值静默返回字符串 | 无 AC |
| `OCR#5` `NativeFallback` 的 `base_environment` | 无 AC；spawn 路径无测试 |
| `OCR#6` 裸相对 audit 路径必被拒 | 方向是**拒绝**而非误用（fail-safe） |
| `OCR#7` 预检与 spawn 之间的 TOCTOU 窗口 | 需要并发删除；方向是 fail-safe |
| `OCR#10` 首个 `chunk` 前缀词误占锚点 | 契约未要求多候选取良构对 |
| `OCR#13` percent 无值域校验（`-5%`/`125%`） | `RULE-3` 只要求忠实呈现 |
| `C-2b 残余` / `C-3` | 需 packet 先定 note/AC；归所有者决策，**不在本轮** |

这些若日后要动，先由所有者改 note/AC，再进 dispatch——不要"顺手一起修"。

## 明确不做

| 禁止 | 原因 |
| --- | --- |
| 改 `hook/sitecustomize.py` 的任何生产行 | C-1 已修好；本轮只补它的**测试断言** |
| 改 `injection.rs`、`protocol.rs`/`protocol.ts`、`gui/`、`fixtures/` | 本轮零需求 |
| 把 `Completed { seconds: Option<f64> }` 改成 `f64` | 波及序列化，收益不值；先只保证不产出 `None` |
| 为 `waived` 项"顺手"加守卫 | 增加活动部件，违反 ADR-003 ③ |
| 改 `packet`、`coverage-ledger`、`state`、既往轮报告 | 治理侧只读 |

## 交付

1. 新候选（冻结由我做，你只交 `REVIEW_READY`）+ `coding/receipt-v7.md`：逐条 `AGREE` 回应 `R06-F1`/`R06-F2`，写清改了哪几行、加了哪几条测试、`MB2` 的 RED→GREEN 记录。
2. `coding/evidence/`：9 个门的命令与退出码（含新增测试的 `... ok` 行）、`MB2` 变异 RED 与还原后 GREEN 的原始输出、四条 `total processing time` 探针行改前/改后对照。
3. 生产 diff 必须只剩 `log_parser.rs` 这一段：`injection.rs`、`sitecustomize.py`、`protocol.rs`/`protocol.ts`、`lib.rs`、`gui/**` 应与 `candidate-6` **逐字节相同**（我会自己比对，不要只写结论）。
4. `docs/handoff/A003.md` 追加 checkpoint，停在 `REVIEW_READY`。
