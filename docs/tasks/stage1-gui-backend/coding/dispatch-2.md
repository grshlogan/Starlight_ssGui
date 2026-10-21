# Dispatch `stage1-gui-backend/A003/2` — 修复轮

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/2` |
| Kind | coding(repair) |
| Sent at | 2026-10-20 |
| Receiver | `A003[PiDeck]Master Coding`(会话 `A003-session-01`,续用) |
| 前序 | `R01` verdict **`FAIL`**,绑定 `candidate-1` `3644d35020d13a370635398129d33a66c25e3edfc867c7b9798b05c74c7036c6` |
| Packet | `docs/tasks/stage1-gui-backend/packet-v6.md`(现行活版本,含**修订 A**),`sha256:a357226bd6c9dd48f4c59d908c3e32d555658977ce9f476a0dc0d78665e8c2f9` |
| Workspace | `E:/project/Starlight_ssGui.worktree/A003/Master`,分支 `a003/master`,detached baseline `6e85b9e` |
| ACK 期望位置 | `<CODING_ROOT>/docs/handoff/A003.md` —— **追加 `Resumed:` 行**,不要重写 ACK 段 |

## 恢复准入(v3 continuity)

修复会话写入前,先在你既有的 `docs/handoff/A003.md` 追加一行:

```
Resumed: 2026-10-20 / session A003-session-01 / lease epoch 1 / 新 dispatch_id stage1-gui-backend/A003/2 / 磁盘与 checkpoint 一致
```

## 上一版 packet 的关键变化(packet-v6)

本 packet **没有放宽任何门**,而是收口了措辞并调整了 AC-11 门的位置。逐条对应你的 F1–F8:

| 变更 | 影响你什么 |
| --- | --- |
| AC-11 门移到 `hook/gates/`,命令改 `discover -s hook/gates` | **F1 解耦**:`G-PY-UNIT` 不再收集宿主门,应恢复 exit 0 |
| A-4 删除「ETA 排除 warm-up 首块」;新增「Stage 1 非目标」 | 你不需要实现 ETA;不要为它加代码 |
| AC-2 明确要求两条负例((a) hook_dir 在安装目录内;(b) 大小写变体) | F6 |
| AC-3 明确语义优先级:「进程可用」>「等同未注入」;setattr 第 N 步失败须全批预校验或回滚 | F2 |
| AC-9 明确 GUI 只到类型 + 校验层 | 你不用做渲染 |
| AC-10 明确「审计写入失败」= 启动前预检;并禁止 overrides 覆盖 hook 控制变量 | F5 |

## 必修(blocking)

### F1 — 门布局 + 证据重录

**两件事,缺一不可:**

1. 把 `hook/tests/test_host_capability.py` 移到 `hook/gates/test_host_capability.py`(新建 `hook/gates/__init__.py`),packet v6 的门命令已改为 `python -m unittest discover -s hook/gates -t . -v`。移动后确认 `python -m unittest discover -s hook/tests -t . -v` **不再收集**该测试。
2. **全部 evidence 在 `candidate-2` 字节上重录,禁止沿用任何旧输出。** R01 已证伪:`coding/evidence/G-PY-UNIT.txt` 记的测试方法 `test_evidence_is_bound_or_reports_unverified` 在候选里不存在,7 tests + skipped 是冻结前旧版本的运行结果,而候选实际是 8 tests + 2 failures。这是 F1 里比「门变红」更严重的一条——违反项目规则 §7。

`G-HOST-CAPABILITY` 的 evidence 必须记**一次真实红跑**(退出码 1 + 失败原因),不是 `exit_code: not run`。A-7 要求三态:缺失态 exit 1、UNVERIFIED 态 exit 1、BOUND 态 exit 0。前两态你可实测;BOUND 态若无法构造真实证据,写 `not run: 无可信证据` 并说明。

### F2 — AC-3 部分应用非原子

现状:`_requested_changes` 循环内逐条 `_set_attribute`,第 N 步失败时前 N−1 个已生效,审计只有 `error` 行。

要求(packet v6 AC-3 已写死):**全批预校验(all-or-nothing)或回滚已写属性**。做到:
- 对全部请求属性先做 `hasattr`/`getattr` 预检,任何缺失即整批放弃、一个都不写;或
- 失败时按记录的已写子集回滚,并在审计里记 `rolled_back` 子集。

必须新增回归用例:**第 N 次 setattr 失败(N≥2)** 时,断言模块属性与未注入一致。现在的 `test_failsafe_setattr_failure_is_fail_safe` 只覆盖第 1 次就失败,所以没发现。

### F3 — AC-8 契约匹配不可达

现状:`parse_line` 里 `detect_module_dialect(&version, module, false)` 是**字面 false**,`contract_match` 永远算不出来;`Dialect::ContractMatched` 只有单元测试直接调函数时产生。即「测试断言了一条生产永远走不到的行为」。

要求:
- 让解析器自己决定 `contract_match`(例如由 `set_module` 提供的模块名 + 属性契约探测得出,或对未知版本走 `ContractMatched{module}` 并把「为什么算契约匹配」落进事件);
- 补一条**经 `LogParser` 的端到端方言用例**(1.7.9 + `models.slp25.future` → `ContractMatched`),不能只测函数;
- F3b:两个硬编码模块名(`m0vm5nn8kicb`/`rx095brph7m1`)在候选内**没有任何来源证据**,夹具里也没有模块名。请补来源(调研简报引用 + 摘录哈希,或明确标注为「社区资料,未实测」并让断言不依赖它)。

## 本轮按 ADR-003 重新分级(见 packet-v6「v6 修订 A」)

`docs/decisions/ADR-003-finding-consumption-policy.md` 已生效:**P3 默认 `waived`,不修、不入 AC**,除非所有者显式提升。

| Finding | 级别 | 本轮处置 | 说明 |
| --- | --- | --- | --- |
| F1 / F2 / F3 | P1 | **必修** | 见上 |
| **F4** | P2 | **修** | `-k failsafe` 零命中时 `Ran 0 tests … OK` 且 exit 0;与 A-7 同类(静默绿灯),有可达路径 |
| **F5** | P2 | **修** | override 可覆盖 `TOPAZ_SLP_OVERRIDE_ENABLE` / `PYTHONPATH` → 实际未注入却报 `Injected`,违反产品不变量 #1 |
| **F8** | P3 | **修(零成本,与 F4 合并)** | 把 4 个 failsafe 用例移进 `hook/tests/test_failsafe.py`,G-FAILSAFE 命令改为显式模块名 —— **同时消灭空壳文件与 `-k` 过滤,净减少部件** |
| **F6** | P3 | **`waived` — 不修** | Review 明写「无写可达,Python 侧 `commonpath` 已二次拦截,仅纵深防御弱化」。守卫代码保持现状(移除会削弱纵深防御),不补大小写用例。原因与决策人记在 `coverage-ledger.md` |
| **F7** | P3 | **`waived` — 不修** | 解析器行为经独立探针确认正确,弱在测试断言强度。加强断言属「新增部件」,ADR-003 §3 不优先。变异记录保留在 `review/R01/evidence/M2-*.txt` 供未来回归时参照 |

**F6/F7 的 waived 由项目所有者随 ADR-003 一并确认(2026-10-20)。你不必为它们写代码,但需在 `receipt-v2.md` 的 finding 响应表里各记一行 `AGREE`(同意豁免),不得标记为已修。**

### F4 + F8 的具体改法(已选定,不要再选另一条)

1. 把 `hook/tests/test_sitecustomize.py` 里 4 个 `test_failsafe_*` 用例移到 `hook/tests/test_failsafe.py`(该文件现在是空壳,只剩一行 docstring)。
2. `G-FAILSAFE` 命令由 `python -m unittest discover -s hook/tests -t . -v -k failsafe` 改为:
   `python -m unittest hook.tests.test_failsafe -v`
   并在 packet 里同步(我已在 v6 改好门命令,你只需按新命令跑)。
3. 这样 `-k` 过滤消失,「零命中且 exit 0」的漏洞自然不存在;**不要**额外再加计数守卫脚本(那是更多部件)。

> 注:G-FAILSAFE 的命令变更属门定义变更,我已写入 packet-v6;若你发现 packet 里仍是旧命令,以 packet 为准并报告,而不是自行沿用旧命令。

## 不要求你改的(治理侧,已由 A002 处理)

| ID | 处置 |
| --- | --- |
| F9 | `baseline/dirty-apply-manifest.txt` 已重写为 rev 2,明确「描述 materialize 后的 `<CODING_ROOT>`,**不描述 candidate-N**」——候选身份只由 `snapshot.json` 的 `manifest_sha256` 决定 |
| F9b | `docs/STATUS.md` 验证边界已按 R01 实测改写:「9 个门退出码 0」的 `verified` 标签已撤销,现记「2 个 required 门为红」 |
| F11 | packet-v6 的 `review.criteria_versions` 已把根 `AGENTS.md` 更新为磁盘实际 `d743097b…` |
| F10 | 已按你的裁定写进 packet-v6 的 AC-2/3/9/10 与「Stage 1 非目标」小节 |
| 裁定 3(A-4 ETA) | 已按「删除」处理:A-4 的 ETA 分句移除,ETA 列入「Stage 1 非目标」 |

## 交付要求

1. 修完跑全部 9 个自动门(含移动后的 `G-HOST-CAPABILITY`),**每个门在 `candidate-2` 字节上真实运行**,evidence 写真实退出码。
2. 写 `docs/tasks/stage1-gui-backend/coding/receipt-v2.md`,逐条回应 F1–F8:`AGREE` / `DISAGREE` / `NEEDS-EVIDENCE`,附 RED-GREEN 证据。**不得编辑 R01 报告,不得自行关闭 finding。**
3. 停 `review-ready`,等 A002 冻结 `candidate-2`。
4. `Resumed:` 行已追加到 `docs/handoff/A003.md`。

## 硬约束(不变)

无 git 写、不写 `<TOPAZ_INSTALL_DIR>`、注入失败必须原生回退、不伪造监控数据、`learn/` 只读、Python 只用 stdlib、Node 用 `node --test`。

## 写范围(不变)

`Cargo.toml`、`Cargo.lock`、`rust-toolchain.toml`、`.gitignore`、`backend/`、`hook/`、`gui/`、`fixtures/`、`docs/tasks/stage1-gui-backend/coding/`、`docs/handoff/A003.md`。

新增 `hook/gates/` 在本轮范围内(它是 `hook/` 的子目录)。
