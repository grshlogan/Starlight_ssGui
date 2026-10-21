# Dispatch `stage1-gui-backend/A003/3`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/3` |
| Kind | repair Coding |
| Sent at | 2026-10-20 |
| Receiver identity / role | `A003[PiDeck]Master Coding` / Master Coding |
| Packet | `docs/tasks/stage1-gui-backend/packet-v8.md`(**pinned for R03**),`sha256:d41a70d2abccb3a49167bd1f57f2f405bd8e6dcaf1df89e514daec7a412b2c23` |
| 前序 | `R02` verdict **`FAIL`**,绑定 `candidate-2` `200891411f94f96d8c8cf042877fa753a50b3c1860e229c74a99baa98aed95f1`(53 files)+ `packet-v7` `11cdd72a…` |
| 前序报告 | `docs/tasks/stage1-gui-backend/review/R02/report.md` |
| 协议 | `agent-dev-loop-v3`(Skill v3.0.0 `SKILL.md` `04985713…`) |
| Workspace / branch | `<CODING_ROOT>` / `a003/master` |
| Write scope | 不变(`Cargo.toml`、`Cargo.lock`、`rust-toolchain.toml`、`.gitignore`、`backend/`、`hook/`、`gui/`、`fixtures/`、`coding/`、`docs/handoff/A003.md`) |
| ACK 期望 | 在你既有的 `docs/handoff/A003.md` **追加** `Resumed:` 行,不要重写 ACK 段 |

## 先做三件事

1. 追加 Resumed 行(同 dispatch-2 的格式):

   ```
   Resumed: 2026-10-21 / session A003-session-01 / lease epoch 1 / 新 dispatch_id stage1-gui-backend/A003/3 / 磁盘与 checkpoint 一致
   ```

2. 校验并读 packet-v8:

   ```
   sha256sum docs/tasks/stage1-gui-backend/packet-v8.md
   # 必须 d41a70d2abccb3a49167bd1f57f2f405bd8e6dcaf1df89e514daec7a412b2c23
   ```

   重点读「版本变更(v7 → v8)」——里面有这次为什么收紧 AC-8。

3. 读 `review/R02/report.md` 的 Findings 表。只有一条 blocking。

## 必修(1 条 P1)

### R02-F1 — AC-8 的已知版本半边在你的修复后不可达

**这我也有责任,先说清楚。** dispatch-2 里我只写了「补一条经 `LogParser` 的端到端用例(1.7.9 + `models.slp25.future` → `ContractMatched`)」——只点了未知版本那半边。你照做了,结果是:

```rust
// backend/src/log_parser.rs:108-119  现状
pub fn detect_module_dialect(version: &str, module_name: &str, contract_match: bool) -> Dialect {
    if contract_match && module_name.starts_with("models.slp2") {   // ← 先判这个
        return Dialect::ContractMatched;
    }
    if version == "1.7.0" && module_name == "models.slp25.m0vm5nn8kicb" { ... }
    if version == "1.7.1" && module_name == "models.slp25.rx095brph7m1" { ... }
    Dialect::Unknown(version.to_owned())
}
```

`module_contract_matches` 对 `models.slp25.m0vm5nn8kicb` 返回 `true`(`starts_with("models.slp2")`),而契约分支排在精确分支**前面** → 这两个已知模块在生产路径全部返回 `ContractMatched`,`Version170`/`Version171` 两个分支变成死代码。

我用独立探针复核过(自己写的,不是 R02 的脚本):

```
1.7.0  models.slp25.m0vm5nn8kicb    got=ContractMatched  want=Version170  MISMATCH
1.7.1  models.slp25.rx095brph7m1    got=ContractMatched  want=Version171  MISMATCH
1.7.9  models.slp25.future          got=ContractMatched  want=ContractMatched  OK
```

而 `cargo test --workspace` 在这个状态下 **11 passed, exit 0**。所以 `G-TEST-RS` 当时发现不了——它只覆盖了未知那半边。

**改法(R02 建议,我采纳):调整判断顺序,不新增部件。**

已知版本的精确匹配必须**优先于**命名空间契约匹配。不要新增 `enum` 分支、不要加 `Dialect::Unknown` 之外的新变体。

**必须补的测试(packet-v8 的 AC-8 `note` 已写死,缺一不可):**

| 入口 | 输入 | 期望 |
| --- | --- | --- |
| `LogParser`(经 `set_module` + `feed_line`,**不是直调 helper**) | 1.7.0 + `models.slp25.m0vm5nn8kicb` | `Version170` |
| 同上 | 1.7.1 + `models.slp25.rx095brph7m1` | `Version171` |
| 同上 | 1.7.9 + `models.slp25.future` | `ContractMatched` |
| 同上 | 1.7.9 + `models.other.module` | `Unknown("1.7.9")` |

关键点:**必须经 `LogParser`**。R01 的 F3 就是「测试断言了生产走不到的行为」,直调 helper 传字面 `false` 的老测试正是那个错误的残留形态。

改完请附一条**「改前跑一次会红」的证据**:把新的已知版本断言先加到旧实现上跑一次,记录 exit code 与失败输出,再改实现。这是 RED-GREEN,不是可选装饰。

## 修(1 条 P3 被所有者提升为契约变更)

### R02-F5 → AC-10 改前缀规则

```rust
// backend/src/injection.rs:64  现状
fn is_reserved_override(name: &str) -> bool {
    name == "PYTHONPATH" || name.starts_with("TOPAZ_SLP_OVERRIDE_")
}
```

`TOPAZ_SLP_TARGET_MODULE_NAME` 不在枚举内。R02 实测:传它进 `overrides` → 计划报 `Injected`,而 hook 的 `_matches_target` 返回 `False`、`apply_overrides` 返回 `False`、模块属性保持 33,审计只有 header。**「计划说注入了、实际没注入」——产品不变量 #1 的同一失效模式。**

所有者选定**前缀规则**,不是继续枚举:

```rust
fn is_reserved_override(name: &str) -> bool {
    name == "PYTHONPATH" || name.starts_with("TOPAZ_SLP_")
}
```

一行改动,删掉 `_OVERRIDE_` 的枚举性。原有两条测试(`reserved_override_cannot_disable_injection`、`pythonpath_override_is_reserved`)必须仍然通过;新增一条断言 `TOPAZ_SLP_TARGET_MODULE_NAME` 也被拒绝、且产生 `reserved_override` 回退。

## 不要改(2 条 P3 已记 `waived`)

| Finding | 对象 | 你的处置 |
| --- | --- | --- |
| R02-F3 | `coverage-ledger.md` 的 A-4/A-5 合并行 | **不关你的事**,是 A002 的账本,且已由所有者记 `waived`。不要碰 `coverage-ledger.md` |
| R02-F6 | `hook/sitecustomize.py:144-166` 的回滚循环(双故障残留) | **不要改**。真实目标为 `ModuleType`,对其已存在属性 `setattr` 不会失败,无具体可达路径。不要加 `applied`/`not_rolled_back` 字段——那是新增部件 |

R02-F1 是本轮唯一 blocking。**如果 R03 发现你顺手改了 F3/F6 的对象,那会是一条新的越权 finding。**

## 治理范围变化(不需要你做任何事,但要知道)

所有者决定:**候选从 v8 起只含交付物**,治理文档(`AGENTS.md`、`CONTEXT.md`、`README.md`、`docs/**`)一律不进候选。

原因:这个漂移类连续三轮产生 finding(R01 F9 → R02 F2)。根因不是纪律,是「把会变的东西冻进不变的东西」。

对你的影响:
- `docs/` 仍在你的 `protected_paths` 里,**仍然不许写**。
- `<CODING_ROOT>` 里的治理文档副本我不再往候选里放,所以它们和治理工作区是否一致不再产生 finding。
- 你不需要同步任何治理文档;需要读判据就读治理工作区。

## 交付

- 写 `docs/tasks/stage1-gui-backend/coding/receipt-v3.md`,逐条回应 R02-F1(必修)、R02-F5(改前缀规则),并对 R02-F3/R02-F6 各记一行 `AGREE`(同意豁免),**不得标记为已修**。
- 全部 11 个门在修复后的字节上**重跑并重录**;不得沿用任何旧 evidence。
- 不停在第一个绿门就交,`G-HOST-CAPABILITY` 仍为 exit 1(blocked 态的正确观测),按 packet-v8 的两态声明记录。
- 不编辑 `review/R02/**`,不改 `state.md` / `coverage-ledger.md` / `packet-v*.md`,不自行关闭任何 finding。
- 停在 `review-ready`,等 A002 冻结 `candidate-3`。

## 硬约束(不变)

无 git 写(commit/push/merge/rebase/reset/stash/切分支全禁)、不写 `<TOPAZ_INSTALL_DIR>`、注入失败必须原生回退、不伪造监控数据、`learn/` 只读、Python 只用 stdlib、Node 用 `node --test`(不支持 `enum`/`namespace`)、`<SHARED_LEARN_ROOT>` 若仍不可读则 AC-11 报 `UNVERIFIED`,不得编造。
