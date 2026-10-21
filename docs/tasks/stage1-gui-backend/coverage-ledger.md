# Coverage Ledger — stage1-gui-backend

一个 Review family 一份。记录**哪些 criteria / rules / conventions / gates 在哪个候选上被证明过**,供 `delta` 轮界定范围。
本文件**不记录整候选裁决**,也不豁免必须重跑的门。

作用边界:本文件由 Review 轮填写(每轮的 ledger slice 由该轮报告给出),Coordinator 只做格式与绑定校验。
**Coding 不写本文件。**

```markdown
| Row | Kind | Anchors | Check | Evidence digest | Proven in | Result | Invalidated by |
| --- | --- | --- | --- | --- | --- | --- | --- |
```

取值集以 Skill `core/loop.md` 的 **Check result** 为准:`done`(本候选本轮已证)/ `inherited`(四条继承条件全部成立时从早轮结转)/ `N/A`(经批准豁免,须带批准人与理由)/ `not run`(未证,含本轮未跑到与判据已变两种)。**`stale` 已从该集合退休**(2026-10-21 Skill 升级),不再使用。

## 绑定

| 项 | 值 |
| --- | --- |
| Packet | `packet-v12.md` `8d0a1f2cfb32c65e09b867fc3461218dcf465589e0200a375b691257c8576eef` |
| 候选 | **`candidate-7` `df838a0831947789e08952a2f422c5234cc92973f5bcd2c98b62b2ad22547315`(69 files)** — R07 判 PASS;上一候选 `candidate-6` `3ee2f087…`(63) |
| 轮次 | `R07` **PASS**(`candidate-7` + `packet-v12`);`R01`–`R06` 关闭(全部 FAIL) |
| AC 总数 | 46 —— **verifiable 40 + deferred 6** |

**6 条不在本表**:`AC-4.3`、`AC-7.1`–`7.3`、`AC-11.1`–`11.2` 在 `packet-v12` 中带 `deferral`。按 `agent-dev-loop` v3.1.0 `lanes/review.md`「the criteria the pinned packet defers are not rows」,它们**不是 Coverage 行**,故不列入本表;回看条件见 `packet-v12.md` 各条的 `deferral.until`。它们的原地记录保留在下方「Blocked」段。

**为什么其余 40 行全部 `not run`**(两条,先后叠加):

1. `packet-v10` 把 acceptance 从 11 条多分句 AC 改为 46 条原子 AC(所有者 2026-10-21 批准)。在此之前没有任何一轮按 46 条粒度证明过任何一条,不满足继承条件 2(判据变更)。
2. `packet-v11` 又改了 `AC-3.1` 的 criterion 与 `AC-6.3`/`AC-6.4` 的 note(所有者 2026-10-21 批准)。`R05` 按 v10 措辞给的判定**不能继承到 v11**——尤其 `AC-3.1`,`R05` 判 pass 而实测证明旧措辞允许错误读法。所以 40 行全部继续 `not run`,`R06` 起按 v12 重填。

**注意**:`R05` 的 4 条 P2 已判必修并进入 `dispatch-7`;它们改写的是测试,不是 ledger 的 anchor。

## Criteria

| Row | Kind | Anchors | Check | Evidence | Proven in | Status |
| --- | --- | --- | --- | --- | --- | --- |
| AC-1.1 | criterion | `cargo fmt --all --check` 零差异 | G-FMT | — | — | not run |
| AC-1.2 | criterion | `cargo clippy --workspace --all-targets -- -D warnings` 无告警 | G-CLIPPY | — | — | not run |
| AC-1.3 | criterion | `cargo test --workspace` 全通过 | G-TEST-RS | — | — | not run |
| AC-1.4 | criterion | `cargo build --workspace` 成功 | G-BUILD | — | — | not run |
| AC-1.5 | criterion | `Cargo.lock` 只含 workspace 成员 | `manual-procedure`(见 packet) | — | — | not run |
| AC-2.1 | criterion | `PYTHONPATH` 指向 hook 目录 | G-TEST-RS | — | — | not run |
| AC-2.2 | criterion | 产物无 install-dir 目标 fs 变更调用 | `manual-procedure`(审读) | — | — | not run |
| AC-2.3 | criterion | hook_dir 在 install dir 内 → 整批回退 | G-TEST-RS | — | — | not run |
| AC-3.1 | criterion | **目标模块自身导入失败 → 可观察行为与未注入一致**(同一异常上抛 / `sys.modules` 无残留 / 无部分初始化模块) | G-FAILSAFE | — | — | not run |
| AC-3.2 | criterion | 契约校验异常 → 目标仍可导入 | G-FAILSAFE | — | — | not run |
| AC-3.3 | criterion | setattr 第 N 步失败 → 无部分残留 | G-FAILSAFE | — | — | not run |
| AC-3.4 | criterion | 审计写入异常 → 目标仍可导入 | G-FAILSAFE | — | — | not run |
| AC-3.5 | criterion | 失败写 error 行 + 已回滚/已生效子集 | G-PY-UNIT | — | — | not run |
| AC-3.6 | criterion | 固定 stderr 前缀(运行内稳定) | G-FAILSAFE | — | — | not run |
| AC-3.7 | criterion | hook 载荷 `py_compile` 可编译 | G-PY-COMPILE | — | — | not run |
| AC-4.1 | criterion | 审计出现 `event=apply` 行 | G-PY-UNIT | — | — | not run |
| AC-4.2 | criterion | apply 行 before/after/source == 实际生效值 | G-PY-UNIT | — | — | not run |
| AC-5.1 | criterion | 审计五行字段齐全 | G-PY-UNIT | — | — | not run |
| AC-5.2 | criterion | 启动即写 header 行 | G-PY-UNIT | — | — | not run |
| AC-5.3 | criterion | 失败写 `event=error` 行 | G-PY-UNIT | — | — | not run |
| AC-6.1 | criterion | 解析出三个阶段 | G-TEST-RS | — | — | not run |
| AC-6.2 | criterion | 解析出分块序号与进度 | G-TEST-RS | — | — | not run |
| AC-6.3 | criterion | 解析出完成标记;**Completed 必须带耗时,路由与取数同一匹配式** | G-TEST-RS | — | — | not run |
| AC-6.4 | criterion | 未知行计入 unknown 且不 panic;**不得被误认成已知事件** | G-TEST-RS | — | — | not run |
| AC-6.5 | criterion | 截断行计入 unknown 且不 panic | G-TEST-RS | — | — | not run |
| AC-8.1 | criterion | 1.7.0 → `Version170`(经 LogParser) | G-TEST-RS | — | — | not run |
| AC-8.2 | criterion | 1.7.1 → `Version171`(经 LogParser) | G-TEST-RS | — | — | not run |
| AC-8.3 | criterion | 未知版本 → `ContractMatched` | G-TEST-RS | — | — | not run |
| AC-8.4 | criterion | 非 `models.slp2` → `Unknown` | G-TEST-RS | — | — | not run |
| AC-9.1 | criterion | 四类 seam 消息各有 TS 校验 | G-GUI-TEST | — | — | not run |
| AC-9.2 | criterion | 四类各有拒绝路径测试 | G-GUI-TEST | — | — | not run |
| AC-9.3 | criterion | 非法输入返回结构化错误 | G-GUI-TEST | — | — | not run |
| AC-9.4 | criterion | GUI 不直读日志/进程 | `manual-procedure`(rg) | — | — | not run |
| AC-10.1 | criterion | 注入不可用 → 原生回退 + 原因 | G-TEST-RS | — | — | not run |
| AC-10.2 | criterion | hook 缺失 → 原生回退 + 原因 | G-TEST-RS | — | — | not run |
| AC-10.3 | criterion | audit_file 不可写 → 原生回退 + 原因 | G-TEST-RS | — | — | not run |
| AC-10.4 | criterion | audit_file 在禁用位置 → 原生回退 + 原因 | G-TEST-RS | — | — | not run |
| AC-10.5 | criterion | 回退记录含判据 | G-TEST-RS | — | — | not run |
| AC-10.6 | criterion | `TOPAZ_SLP_*` 前缀与 `PYTHONPATH` 被拒 | G-TEST-RS | — | — | not run |
| AC-10.7 | criterion | 被拒 override → 结构化回退,不静默 Injected | G-TEST-RS | — | — | not run |

## Rules / conventions

| Row | Kind | Anchors | Check | Proven in | Status |
| --- | --- | --- | --- | --- | --- |
| RULE-1 | convention | 产品不变量 #1:注入失败必须原生回退 | `AC-2.3` / `AC-10.1`–`AC-10.7` | — | not run |
| RULE-2 | convention | 产品不变量 #2:默认不改 Topaz 安装文件 | `AC-2.2` / `AC-10.4` | — | not run |
| RULE-3 | convention | 产品不变量 #3:不得伪造监控数据 | `AC-6.4` / `AC-6.5`(未知显示为未知) | — | not run |
| RULE-4 | convention | 产品不变量 #4:结论可追溯 | `AC-11.2` / `AC-7.2` / `AC-7.3` | — | not run |
| RULE-5 | convention | ADR-003:variant 不得把 P3 提升为 AC | 本文件与 packet 的人工复核 | — | not run |

## Blocked(由所有者阻塞,非候选缺陷)

| Row | 阻塞原因 | Owner |
| --- | --- | --- |
| AC-4.3 | 需一次真实 SLP 短导出 —— **已 deferral**(until: Stage 2 启动或首次真实导出可用) | 项目所有者 |
| AC-7.1 / AC-7.2 / AC-7.3 | 需一次真实 SLP 渲染 —— **已 deferral**(同上 until) | 项目所有者 |
| AC-11.1 / AC-11.2 | 需 `<SHARED_LEARN_ROOT>` 只读映射 —— **已 deferral**(until: 映射到位且 B01 完成) | 项目所有者 |

## Waived findings(ADR-003 §1,不修、不入 AC)

决策人:项目所有者(ADR-003,2026-10-20)。这些是 finding 而非 criterion,故单列,不进上表。

| Finding | 级别 | 内容 | 为何不修 |
| --- | --- | --- | --- |
| R01-F6 | P3 | `path_is_within` 用大小写敏感的 `Path::starts_with` | 无可达写路径(Python 侧 `commonpath` 二次拦截);修它是弱化纵深防御之外的无收益改动 |
| R01-F7 | P3 | 夹具测试断言偏弱 | 弱在断言不在实现;加强断言属新增部件 |
| R02-F3 | P3 | ledger 的 A-4/A-5 合并成一行 | 记录瑕疵,无产品路径 |
| R02-F6 | P3 | 双故障(写入失败 + 回滚失败)残留 | `setattr` 对已存在属性不失败 → 无产品路径 |
| R04-F3 | P3 | `ERROR_PREFIX` 字面值未钉住 | 「固定前缀」的语义是运行内稳定,不是某个字面值 |
| R04-F4(b) | P3 | 夹具测试未断言阶段/分块 | 与 `AC-6.1`/`AC-6.2` 重复 |
| R04-F6 / A002-C4 | P3 | 4 个文件仅 LF→CRLF | 变异脚本用文本模式恢复所致,内容零变化 |

## 待所有者决定(本轮实测产出,未进契约)

| 编号 | 位置 | 内容 | 为何暂不处理 |
| --- | --- | --- | --- |
| C-3 | `backend/src/injection.rs:59-61` | `path_is_within` 是 `child.starts_with(parent)`,无 `canonicalize`;符号链接或 Windows 8.3 短名可绕过 `TOPAZ_INSTALL_DIR` 硬边界 | 加固要引入 `canonicalize` + 错误处理,属新增活动部件;需先在 `packet-v12` 定 AC 再动。**注意与 R01-F6 不是同一条**:F6 是大小写敏感(已 `waived`),C-3 是未规范化 |
| C-2b 残余 | `backend/src/log_parser.rs` | `Completed{seconds:null}` 的语义边界已在 v11 的 AC-6.3 note 中界定,但「提到了总耗时却没给值」是否等同于完成,仍是产品判断 | 本轮按「不产出 Completed」收紧;若所有者认为该行应算完成,改 note 即可,不影响代码 |

## 变更记录

| 日期 | 变更 | 依据 |
| --- | --- | --- |
| 2026-10-21 | 重建为 46 条原子 AC;清出历史 finding 表(改单列 waived);全部 `not run` | `packet-v10` 拆 AC,所有者批准 |
| 2026-10-21 | 移除 `deliverables.ac_coverage_table` 及其机械校验项 | A002 自造物,不在 Skill;且只是形式校验(R04-F2) |
| 2026-10-21 | 绑定 `packet-v12`;6 条 blocked AC 转入 `deferral`,从本表移出(按 v3.1.0 不是 Coverage 行);40 行维持 `not run` | 所有者 2026-10-21 批准 deferral |
| 2026-10-21 | 词汇按升级后的 Skill 收口:`stale` → `not run`,列名 `Status` → `Result`(Check result 集合只有 `done`/`inherited`/`N/A`/`not run`) | Skill v3.0.0 内容升级,`core/loop.md` 的 Check result 集合 |
| 2026-10-21 | 绑定改为 `packet-v11`;`AC-3.1`/`AC-6.3`/`AC-6.4` 三行按新措辞重述并维持 `not run`;新增「待所有者决定」段(C-3、C-2b 残余) | `packet-v11` 三处措辞收口,所有者批准;46 条仍 `stale` |
| 2026-10-21 | 绑定切到 `candidate-6`(生产首次变更:`log_parser.rs` 3 处 + `sitecustomize.py` 1 行)。**R05 的推行不继承**——判据版本由 Skill v3.0.0 升 v3.1.0,退出码与输出正则两条判据本身已变;40 行全部重证 | `candidate-6` 冻结 + `packet-v12` |
| 2026-10-22 | `R06` 关闭(FAIL):`AC-6.3`、`AC-3.5` 记 `not run`(证据链指向违约/缺口);其余 38 条 verifiable + 4 条 RULE + 8 门 + 14 变异 + OCR 记 `done`;`RULE-4` 记 `N/A`(锚点整组 deferred,所有者批准);`G-HOST-CAPABILITY` 记 `not run`(非 required) | `review/R06/report.md` |
| 2026-10-22 | `waived` 新增 12 项(L-1/L-2/L-3/L-4/OCR#1/#2/#3/#5/#6/#7/#10/#13),均答过「不修则哪条路径会坏」= 无可达路径;`receipt` 编号错记 P3 并进 `receipt-v7` | ADR-003 ①②;`coding/dispatch-8.md` |
| 2026-10-22 | **R07 slice**:40 criteria + 5 rules = 45 行,**14 done / 30 inherited / 1 N/A / 0 `not run`**;9 门全重跑(8 done + `G-HOST-CAPABILITY` not run,AC-11 deferral 正确观测);变异 10 条自跑并还原;OCR 1 次(7 评论,只产 lead) | `review/R07/report.md`;A002 复算:Criteria 40/0 not run、Rules 5/0、Gates 9/1 |
| 2026-10-22 | `AC-1.3` 行记 `inherited` 但注释与 `G-TEST-RS` 门行为 `done`(19→20 本轮重跑)——**P3 标签不一致,`waived`**:判据有证、无产品路径受影响,不返工 | ADR-003 ①;`review/R07/report.md` |
