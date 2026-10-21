# Task Packet — stage1-gui-backend v4

> v4 取代 v3。v4 修正 `read_first` 指向被取代版本 `packet-v1.md` 的缺陷,并记录所有者授权的 **B01 延后**(见文末「版本变更」)。验收标准、门、write_scope、profile、topology 均未变。v1–v3 保持原样,不覆盖。

```yaml
protocol: agent-dev-loop-v2
project_id: starlight-ssgui
task_id: stage1-gui-backend
packet_version: 4
owner: "项目所有者 (project owner, 决策权威)"
acceptance_owner: "项目所有者"
published_at: "2026-10-18"
supersedes: 3
published_by: "A002[PiDeck]Main Coordinator (session A002-session-01)"

profile: standard
profile_reason: "普通功能验证任务(非安全/权限/持久化边界),但注入与回退涉及第三方进程与失败安全,故在 standard 基线上附加 hook 失败安全、不写安装目录、原生回退三行攻击矩阵;无 N/A 豁免。"
topology: stream

roots:
  project: <PROJECT_ROOT>
  task: <PROJECT_ROOT>/docs/tasks/stage1-gui-backend
  skill: <AGENT_DEV_LOOP_ROOT>
  coding: <CODING_ROOT>
  sandbox: <REVIEW_SANDBOX>

baseline:
  revision: 6e85b9e4aba16cc52f9fcc74dedf0170327382e2
  initial_status: docs/tasks/stage1-gui-backend/baseline/initial-status.txt
  initial_diff: docs/tasks/stage1-gui-backend/baseline/initial-diff.txt
  materialization_manifest: docs/tasks/stage1-gui-backend/baseline/dirty-apply-manifest.txt
  note: "基线提交不含规划文档;规划文档(ADR-002/CONTEXT/A001/A002/两份 plan/任务目录)按 dirty-apply 从治理工作区复制进 <CODING_ROOT>,不产生提交。清单与逐文件 SHA-256 见 materialization_manifest。"

read_first:
  - AGENTS.md
  - docs/START_HERE.md
  - docs/STATUS.md
  - docs/index.md
  - docs/tasks/AGENTS.md
  - docs/tasks/stage1-gui-backend/AGENTS.md
  - docs/tasks/stage1-gui-backend/packet-v4.md
  - docs/tasks/stage1-gui-backend/state.md
  - docs/tasks/stage1-gui-backend/coverage-ledger.md
  - CONTEXT.md
  - docs/decisions/ADR-002-stage1-boundaries-and-evidence.md
  - docs/plan/plan-stage1-gui-backend.md
  - docs/engineering/AGENTS.md
  - docs/architecture/AGENTS.md
  - docs/product/AGENTS.md
  - docs/research/AGENTS.md
  - docs/research/references/2026-10-17-SLP调参与日志监控-技术简报.md
  - docs/identity/A002.md
  - <AGENT_DEV_LOOP_ROOT>/SKILL.md
  - <AGENT_DEV_LOOP_ROOT>/core/loop.md
  - <AGENT_DEV_LOOP_ROOT>/lanes/coding.md
  - <AGENT_DEV_LOOP_ROOT>/templates/receipt.md
  - <AGENT_DEV_LOOP_ROOT>/templates/handoff.md

# 相对 <CODING_ROOT> 的路径。A003 是本任务在 <CODING_ROOT> 的唯一写者。
write_scope:
  - Cargo.toml
  - Cargo.lock
  - rust-toolchain.toml
  - .gitignore
  - backend/
  - hook/
  - gui/
  - fixtures/
  - docs/tasks/stage1-gui-backend/coding/
  - docs/tasks/stage1-gui-backend/handoff/A003.md

protected_paths:
  - AGENTS.md
  - CLAUDE.md
  - README.md
  - CONTEXT.md
  - docs/            # 除 docs/tasks/stage1-gui-backend/coding/ 与 handoff/A003.md 外全部只读
  - learn/           # 参考库,只读;不复制、不改写、不重新发布
  - .git/

authorizations:
  git_write: false
  worktree_create: "仅 A002,一次性:`<CODING_ROOT>` 由 `git worktree add -b a003/master <PROJECT_ROOT>.worktree/A003/Master 6e85b9e` 创建(所有者 2026-10-18 批准;分支名由所有者 2026-10-18 选定);该授权不包含在其中写实现,也不包含移除/移动/改分支"
  worktree_remove: false
  branch_delete: false
  session_create: false
  network: "crates.io + npm registry;npm 安装必须落在 npm config get prefix 指向的共享开发盘前缀,禁止写入系统盘用户目录;不访问其它主机"
  install_scripts: false
  paid_services: false

verify_commands:
  - id: G-FMT
    cwd: <CODING_ROOT>
    command: cargo fmt --all --check
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-FMT.txt
    required: true
  - id: G-CLIPPY
    cwd: <CODING_ROOT>
    command: cargo clippy --workspace --all-targets -- -D warnings
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-CLIPPY.txt
    required: true
  - id: G-TEST-RS
    cwd: <CODING_ROOT>
    command: cargo test --workspace
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-TEST-RS.txt
    required: true
  - id: G-BUILD
    cwd: <CODING_ROOT>
    command: cargo build --workspace
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-BUILD.txt
    required: true
  - id: G-PY-UNIT
    cwd: <CODING_ROOT>
    command: python -m unittest discover -s hook/tests -t . -v
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-PY-UNIT.txt
    required: true
  - id: G-FAILSAFE
    cwd: <CODING_ROOT>
    command: python -m unittest discover -s hook/tests -t . -v -k failsafe
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-FAILSAFE.txt
    required: true
  - id: G-PY-COMPILE
    cwd: <CODING_ROOT>
    command: python -m compileall -q hook
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-PY-COMPILE.txt
    required: true
  - id: G-GUI-TEST
    cwd: <CODING_ROOT>/gui
    command: node --test
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-GUI-TEST.txt
    required: true
  - id: G-HOST-CAPABILITY
    cwd: <CODING_ROOT>
    command: "python -m unittest hook.tests.test_host_capability -v"
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-HOST-CAPABILITY.txt
    required: true
    note: "该门运行的是对已落盘结论的复核断言:读取 coding/evidence/host-capability.md,断言结论 ∈ {direct, rust-adapter, windows-render-blocked}、断言每条结论附有可复现命令与退出码、断言结论与 pocketjs 快照可读性一致。若 <SHARED_LEARN_ROOT> 不可读,该门必须报 UNVERIFIED 而不是通过。"
  - id: M-TOPAZ-INJECT
    cwd: <CODING_ROOT>
    command: "手工:真实 Topaz SLP 短导出,注入前/后各一次,比对审计 JSONL 与生效参数"
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/M-TOPAZ-INJECT.md
    required: false
  - id: M-TOPAZ-LOG
    cwd: <CODING_ROOT>
    command: "手工:一次真实 SLP 渲染产出 tzlog,用本项目解析器解析并留存原始夹具哈希"
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/M-TOPAZ-LOG.md
    required: false

acceptance:
  - id: AC-1
    criterion: "Rust workspace 骨架在 Windows x64 上格式化、lint(-D warnings)、单测、构建全部通过,且无 crate 依赖 bun/pocketjs 宿主"
    verification: G-FMT, G-CLIPPY, G-TEST-RS, G-BUILD
    state: verifiable
  - id: AC-2
    criterion: "注入装配以 PYTHONPATH + sitecustomize 组装子进程环境;有测试证明装配过程不写、不删、不重命名 <TOPAZ_INSTALL_DIR> 内任何文件,产物中不含安装目录写入路径"
    verification: G-TEST-RS, G-PY-UNIT
    state: verifiable
  - id: AC-3
    criterion: "hook 失败安全:目标模块导入、契约校验、setattr、审计写入任一步抛异常时,目标模块仍正常导入且行为与未注入一致;失败原因以固定前缀写入 stderr,不阻断进程"
    verification: G-PY-UNIT, G-FAILSAFE
    state: verifiable
  - id: AC-4
    criterion: "真实 Topaz SLP 渲染中注入生效:审计 JSONL 出现 apply 记录,且生效参数与请求参数逐项一致"
    verification: M-TOPAZ-INJECT
    state: blocked
    blocked_owner: "项目所有者(需授权一次真实 SLP 短导出)"
  - id: AC-5
    criterion: "审计 JSONL 结构可回归:每行含 timestamp_utc / pid / launch_id / event / changes,且启动即写 header 行、失败写 error 行"
    verification: G-PY-UNIT, G-PY-COMPILE
    state: verifiable
  - id: AC-6
    criterion: "日志解析原型在夹具上解析出阶段(VAE Encode/DiT Upscale/VAE Decode)、分块序号与进度、完成标记;对未知行与截断行不 panic、不退出、计入 unknown 计数"
    verification: G-TEST-RS
    state: verifiable
  - id: AC-7
    criterion: "一次真实 SLP 渲染的 tzlog 被本项目解析器正确解析,原始夹具哈希与来源记录在案"
    verification: M-TOPAZ-LOG
    state: blocked
    blocked_owner: "项目所有者(需授权一次真实 SLP 渲染)"
  - id: AC-8
    criterion: "版本方言识别:对 1.7.0 与 1.7.1 的目标模块命名差异和日志版本行差异各自识别成功,未知版本走契约匹配而非硬编码模块名"
    verification: G-TEST-RS, G-PY-UNIT
    state: verifiable
  - id: AC-9
    criterion: "GUI/backend seam 可回归:控制命令、状态快照、结构化事件、结构化错误四类消息各有 TS 侧校验与拒绝路径测试;非法输入产生结构化错误而不是异常崩溃;GUI 不直接读日志文件或进程"
    verification: G-GUI-TEST
    state: verifiable
  - id: AC-10
    criterion: "原生回退可执行:注入不可用、hook 缺失或审计写入失败时,backend 以无注入方式启动目标程序,并记录回退原因与判据"
    verification: G-TEST-RS
    state: verifiable
  - id: AC-11
    criterion: "pocketjs 宿主能力结论落盘并绑定证据:结论为 direct / rust-adapter / windows-render-blocked 之一,附可复现命令与输出;不得以推测代替"
    verification: G-HOST-CAPABILITY
    state: verifiable

toolchain: "rustc 1.95.0 / cargo 1.95.0 (x86_64-pc-windows-msvc); rustfmt 1.9.0-stable; clippy 0.1.95; Python 3.11.9 (仅 stdlib unittest,pytest 不可用); Node v24.22.0 (内置 TS type-stripping 测试运行器,**bun 不可用**); git 2.55.0; Windows 11 x64 10.0.22631; Cargo.lock 必须提交"

attack_matrix:
  - id: A-1
    risk: "hook 抛异常导致目标程序导入失败或渲染中断"
    check: "G-FAILSAFE:注入点导入/契约/setattr/审计四类故障注入后目标模块可导入"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-FAILSAFE.txt"
  - id: A-2
    risk: "实现为通过验证而写入 <TOPAZ_INSTALL_DIR>(.pth / 覆盖模块 / 改 dll)"
    check: "G-TEST-RS 中断言装配产物路径集合不含安装目录;G-PY-UNIT 中断言 hook 仅读取环境变量"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-TEST-RS.txt"
  - id: A-3
    risk: "注入失败后静默降级,用户以为参数已生效"
    check: "G-TEST-RS:回退路径产生结构化原因并可被 GUI 状态快照表达"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-TEST-RS.txt"
  - id: A-4
    risk: "解析器伪造或补齐缺失的进度/ETA 数据"
    check: "G-TEST-RS:缺失字段返回 None/Unknown,夹具中断言不产生虚构值;ETA 排除 warm-up 首块"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-TEST-RS.txt"
  - id: A-5
    risk: "GUI 越过 seam 直接读日志文件或进程,形成第二套事实源"
    check: "G-GUI-TEST:gui/ 目录下无 fs/child_process 导入;状态只来自快照与事件"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-GUI-TEST.txt"
  - id: A-6
    risk: "把夹具结论当成真实 Topaz 证据"
    check: "AC-4/AC-7 保持 blocked;receipt 中 M-* 门必须记 not run 或 BLOCKED,不得以 G-* 结果替代"
    evidence: "docs/tasks/stage1-gui-backend/coding/receipt-v1.md"

identities:
  coordinator: "A002[PiDeck]Main Coordinator / session A002-session-01"
  master_coding: "A003[PiDeck]Master Coding / session A003-session-01 (所有者手动启动)"
  coding: "A003[PiDeck]Master Coding(stream 拓扑下不派发 Sub-Coding)"
  review: "A004[PiDeck]Review / 独立新会话,启动时分配 session 标签"
  acceptance_owner: "项目所有者"

workspace:
  provider: windows-git
  path: <CODING_ROOT>
  writer: "A003[PiDeck]Master Coding"
  baseline_materialization: dirty-apply
  branch: a003/master
  shared_paths: "<SHARED_LEARN_ROOT>(只读参考库);CARGO_HOME/RUSTUP_HOME(共享 cargo 缓存);npm prefix(共享开发盘前缀);本工作区与治理工作区共享同一 .git 目录,故 A003 不得执行任何 git 写操作"

transport:
  kind: manual-file
  host_profile: pideck
  host_name: PiDeck
  host_version: unconfirmed
  connector: none
  connector_verified_operations: none
  dispatch_authority: coordinator

review:
  family: stage1-gui-backend
  container: <REVIEW_SANDBOX>
  first_round: R01
  scope: full
  base: none
  ledger: docs/tasks/stage1-gui-backend/coverage-ledger.md
  previous_report: none
  candidate_kind: bundle
  candidate: docs/tasks/stage1-gui-backend/snapshots/candidate-1
  manifest_sha256: pending-freeze-at-candidate-1
  criteria_versions: "ADR-002 0bdaec7b1e8d406f141e9be4cb0f4e1d8f550bff493f0ec447b58cbbd0b75377;plan-stage1-gui-backend da6093198bc6eda3783172523ff6f0612dde2dc75efcff3684f77823c4072d4d;CONTEXT 66fe89b01f7acb3fa768f7f4e89d60ec0df7b69a0d367a275baa9a954ba6515a;AGENTS.md 77449f751c742874857c6fffde967538a9d10d1893354c93e282ddfd4ae9c7d4"
  review_instruction_version: "agent-dev-loop SKILL.md c7a4bbe2680f2a8056b56bccedf304c4383f20e8a286b631ac46587c969755c3"
  inspection_mode: isolated-sandbox

outputs:
  coding_receipt: docs/tasks/stage1-gui-backend/coding/receipt-v1.md
  report: docs/tasks/stage1-gui-backend/review/R01/report.md
  next_action: docs/tasks/stage1-gui-backend/review/R01/next-action.md
  evidence: docs/tasks/stage1-gui-backend/review/R01/evidence/
  state: docs/tasks/stage1-gui-backend/state.md

placement:
  docarch_planner_id: "A001[PiDeck]DocArch Planner"
  coordinator_id: "A002[PiDeck]Main Coordinator"
  governance_system: windows
  colocated: true
  repository_owner_mode: integrated-with-windows-governance

execution_plan:
  - module_id: backend
    surface: backend
    coding_system: windows
    review_system: windows
    validation_adapter: native
  - module_id: GUI
    surface: gui
    coding_system: windows
    review_system: windows
    validation_adapter: native

lease:
  workspace_id: stage1-gui-backend-coding
  worktree_id: A003-coding
  owner_role: master_coding
  owner_instance: "A003[PiDeck]Master Coding"
  owner_session: A003-session-01
  state: transferring
  epoch: 1
```

## 进度图(stream 下的顺序,不是 tiered 分解)

本任务 `topology: stream`,由 A003 单线程推进;下表的 Block 只表示进度与依赖,**不产生**独立 Sub-Coding、独立 write_scope 或独立验收。

> **执行顺序偏离(v4,所有者 2026-10-19 批准)**:因 `<SHARED_LEARN_ROOT>` 私有映射尚未提供,`B01-host-spike` 暂缓,先行 `B02` → `B03` → `B04` 中不依赖宿主结论的部分。这不是放弃 B01:AC-11 在该映射到位前保持 `UNVERIFIED`,`B01` 完成后必须先出结论再收尾 B04 的 seam。若 B01 结论为 `rust-adapter`,B04 的 seam 根形态可能变化,届时按新结论返工 B04 —— 此风险由所有者接受。

| Block | 模块 | 依赖 | 完成判据 | 关联 AC |
| --- | --- | --- | --- | --- |
| `B01-host-spike` | backend | 无 | 宿主能力结论落盘(AC-11),Rust adapter 决策明确 | AC-11 |
| `B02-injection-closure` | backend | B01 | 注入装配 + 审计 + 失败安全 + 原生回退 | AC-2, AC-3, AC-5, AC-10 |
| `B03-log-fixture-parser` | backend | B02 | 夹具解析 + 版本方言 | AC-6, AC-8 |
| `B04-gui-backend-seam` | GUI + backend | B02, B03 | 四类 seam 消息可回归 | AC-9 |
| `B05-review-acceptance` | GUI + backend | B04 | 冻结 candidate-1 → R01 → 所有者验收 | AC-1 |

真实 Topaz 门(AC-4、AC-7)不阻塞 B01–B04 的 `verifiable` 部分;它们在任何时候都保持 `blocked`,直到所有者提供真实证据。

## 硬约束(与根 `AGENTS.md` 及 ADR-002 一致)

1. 工作区 `<CODING_ROOT>` 位于分支 `a003/master`(从 `6e85b9e` 创建),layout 依 `platform/placement.md:114,121` 的 `<Axxx>/Master` + `-b <Axxx>/master`。**commit / push / merge / rebase / reset / stash / 分支切换一律禁止**;`a003/master` 只用于让工作区有可命名的稳定身份,不用于提交。交付物是工作树中的文件 + `coding/receipt-v1.md`。
2. 不得写 `<TOPAZ_INSTALL_DIR>` 内任何文件;首选机制 `PYTHONPATH + sitecustomize`,被否的 `.pth` 引导器不得复活。
3. 注入失败必须原生回退,且回退原因可被 state/event 表达。
4. 不得在 `gui/` 中出现文件系统、子进程或日志直读;GUI 只消费控制命令/状态快照/结构化事件/结构化错误。
5. 不得伪造监控数据(进度、ETA、阶段);缺失即 Unknown。
6. `learn/` 与 `<SHARED_LEARN_ROOT>` 只读:不复制闭源 hook 代码、不重新发布反编译产物;参考实现只可作行为参考。
7. Node 24 type-stripping 限制:`enum`、`namespace`、参数属性不可用;跨文件导入必须写显式 `.ts` 扩展名。
8. Python 侧只用 stdlib(`unittest`),不得试图安装或依赖 pytest。
9. 未跑的命令在 receipt 中写 `not run`,不得留空、不得暗示通过。
10. A003 不写 Review verdict、不写 acceptance、不写 `state.md`/`packet-v1.md`/`coverage-ledger.md`。

## 停止条件

- GUI/backend 的公开接口、错误码、事件顺序或所有权不清时停止实现,提交最小决策包给所有者(ADR-002 决策点 4)。
- 需要写 `<TOPAZ_INSTALL_DIR>` 才能实现时停止,不用替代方案绕过不变量。
- 需要 git 写、网络越界、安装到系统盘或付费服务时停止,等待新授权。
- 发现参考材料许可或发布边界不清时停止复制,保留本地只读。

## 发布记录

- v1 由 `A002[PiDeck]Main Coordinator` 于 2026-10-18 发布。发布后不可覆盖;变更建 `v2`。
- 本文件的 SHA-256 记录在 `state.md` 与 `dispatch/A003.md`,不写入本文件自身。

## 版本变更（v3 → v4）

| 项 | v3 | v4 | 原因 |
| --- | --- | --- | --- |
| `read_first[6]` | `docs/tasks/stage1-gui-backend/packet-v1.md` | `docs/tasks/stage1-gui-backend/packet-v4.md`(自身) | 该字段自 v1 逐字继承,四次迭代未更新。A003 的 ACK 已证明它实际生效:其「Materials actually read」含 `packet-v1.md`,并注明「按 packet-v3 的 read_first 声明」。v1 的 AC-11 是散文验证、`G-PY-COMPILE` 无 AC 映射,照读会拿到已被推翻的验收定义 |
| 进度图 | B01 → B02 → B03 → B04 | B02 → B03 → B04(不含宿主依赖部分),B01 延后 | 所有者 2026-10-19 选择方案 B:`<SHARED_LEARN_ROOT>` 不可读时不让整条链路停摆;AC-11 在映射到位前保持 `UNVERIFIED` |

`write_scope`、`verify_commands`、`acceptance`、`attack_matrix`、`profile`、`topology`、`identities`、`toolchain`、`workspace`、`authorizations` 与 v3 逐字一致。AC-4/AC-7 仍为 `blocked`,AC-11 在 B01 完成前为 `UNVERIFIED`。

## 版本变更（v2 → v3）

| 项 | v2 | v3 | 原因 |
| --- | --- | --- | --- |
| `authorizations.worktree_create` | `git worktree add --detach …` | `git worktree add -b a003/master …` | `platform/placement.md:121` 给 Master 的配方是 `-b a001/master`;`--detach --no-checkout`(:123)是 **Review 容器**的配方。v2 误用 Review 配方建 Master,导致工作区无分支、侧边栏显示 `detached` |
| `workspace.branch` | 缺字段 | `a003/master` | 原 packet 无法表达工作区分支;缺字段使错误不可被解析器发现 |
| 硬约束 #1 | 「工作区是 detached HEAD」 | 「工作区位于分支 `a003/master`,commit/push/merge 等仍全禁」 | detached 不是目的,只是没命名;真正的不变量是「禁 git 写」 |

`write_scope`、`verify_commands`、`acceptance`、`attack_matrix`、`profile`、`topology`、`identities`、`toolchain` 与 v2 逐字一致。AC-4/AC-7 仍为 `blocked`。

## 版本变更（v1 → v2）

| 项 | v1 | v2 | 原因 |
| --- | --- | --- | --- |
| `G-PY-COMPILE` | `required: true` 但无 AC 引用 | AC-5 的 verification 增加 `G-PY-COMPILE` | 派发前校验:`required` 门必须被至少一条 AC 映射,否则等于未验证的强制门 |
| AC-11 verification | 散文「手工:…,由 R01 复核」 | 新增 `G-HOST-CAPABILITY` 门并引用 | 同一校验发现 AC-11 未映射到任何 gate id,不满足「验收标准全部映射到验证项」 |
| AC-8 verification | `G-TEST-RS` | `G-TEST-RS, G-PY-UNIT` | 方言识别同时横跨 Python hook 侧(模块名表)与 Rust 解析侧(版本行),v1 只映射 Rust 侧 |

其余字段在 v1/v2 间逐字一致;`write_scope`、`authorizations`、`topology`、`profile`、`identities`、`workspace` 未变。
