# Task Packet — stage1-gui-backend v9

> v6 取代 v5。v6 依 R01 FAIL 报告收口契约:解耦 AC-11 门、删除无 AC 依据的 ETA 分句、消除四条 AC 措辞歧义、并把 A-4 的 ETA 半句移出。v1–v5 保持原样,不覆盖。

```yaml
protocol: agent-dev-loop-v3
project_id: starlight-ssgui
task_id: stage1-gui-backend
packet_version: 9
owner: "项目所有者 (project owner, 决策权威)"
acceptance_owner: "项目所有者"
published_at: "2026-10-18"
supersedes: 8
published_by: "A002[PiDeck]Main Coordinator (session A002-session-01)"

profile: standard
profile_reason: "普通功能验证任务(非安全/权限/持久化边界),但注入与回退涉及第三方进程与失败安全,故在 standard 基线上附加 hook 失败安全、不写安装目录、原生回退三行攻击矩阵;无 N/A 豁免。"
topology: stream

roots:
  project: <PROJECT_ROOT>
  task: <PROJECT_ROOT>/docs/tasks/stage1-gui-backend
  bundles: <BUNDLE_ROOT>          # 必须在源码树外;<BUNDLE_ROOT> = <PROJECT_ROOT> 的兄弟目录 Starlight_ssGui.bundle
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
  - docs/handoff/A003.md

protected_paths:
  - docs/handoff/          # v3 保留路径:只有本人写自己的 <id>.md;AGENTS.md 与 .gitignore 可进候选,其余永不进候选
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
    command: python -m unittest hook.tests.test_failsafe -v
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
    command: "python -m unittest discover -s hook/gates -t . -v"
    expected_exit: 0
    evidence: docs/tasks/stage1-gui-backend/coding/evidence/G-HOST-CAPABILITY.txt
    required: true
    blocked_by: AC-11
    expected_exit_while_blocked: 1
    note: "独立入口(v6):门位于 hook/gates/,不在 hook/tests/ 内,故 G-PY-UNIT 的 discover 不会收集它。语义:读取 coding/evidence/host-capability.md,断言 status: BOUND、结论 ∈ {direct, rust-adapter, windows-render-blocked}、且有 command/exit_code/snapshot_sha256。证据缺失或 UNVERIFIED 时该门必须 fail 且退出码 1 —— required 门不得静默 skip。B01 未完成时本门必然为红,这是刻意设计。(v7)因此本门的判定分两态:AC-11 处于 blocked 时,正确观测是 exit 1,该门记 blocked,不得记 fail 也不得记 pass;AC-11 解除 blocked 后,按 expected_exit: 0 判定。评测方不得把 blocked 态的红色观测当作候选缺陷。"
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
    criterion: "注入装配以 PYTHONPATH + sitecustomize 组装子进程环境;装配过程不写、不删、不重命名 <TOPAZ_INSTALL_DIR> 内任何文件,产物中不含安装目录写入路径。证明方式(=v6 收口):G-TEST-RS 中至少有一条负例——hook_dir 落在 TOPAZ_INSTALL_DIR 内时整批回退;并由 R 轮独立复核装配序列中不存在 fs 变更调用"
    verification: G-TEST-RS, G-PY-UNIT
    state: verifiable
  - id: AC-3
    criterion: "hook 失败安全:目标模块导入、契约校验、setattr、审计写入任一步抛异常时,目标模块仍可导入、进程不中断。语义优先级(=v6 收口):「进程可用」严格优先于「行为等同未注入」;当失败发生在 setattr 第 N 步(N>1)时,必须做到全批预校验(all-or-nothing)或回滚已写属性,不得留下部分生效;审计须记录 error 行,若存在已回滚/已应用子集须一并记录。失败原因以固定前缀写入 stderr"
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
    note: "(=v8 收紧)本条的验证必须覆盖两个半边,缺一不可:(a) 已知半边——经 LogParser 入口(而非直调 helper)分别喂 1.7.0/models.slp25.m0vm5nn8kicb 与 1.7.1/models.slp25.rx095brph7m1,必须分别得到 Version170 与 Version171;(b) 未知半边——1.7.9/models.slp25.future 得到 ContractMatched,非 models.slp2 命名空间得到 Unknown。背景:R02 证实只测 (b) 时,G-TEST-RS 在 1.7.0/1.7.1 全部退化为 ContractMatched 的情况下仍然全绿——该门当时无法发现本条的已知半边被破坏。判别式:已知版本的精确匹配必须优先于命名空间契约匹配。"
  - id: AC-9
    criterion: "GUI/backend seam 可回归:控制命令、状态快照、结构化事件、结构化错误四类消息各有 TS 侧校验与拒绝路径测试;非法输入产生结构化错误而不是异常崩溃;GUI 不直接读日志文件或进程。范围界定(=v6 收口):Stage 1 的 GUI 交付物只到类型 + 校验层,不含渲染运行时;pocketjs 渲染宿主由 AC-11 结论决定,不在本条验收内"
    verification: G-GUI-TEST
    state: verifiable
  - id: AC-10
    criterion: "原生回退可执行:注入不可用 / hook 缺失 / 审计目标不可用三类预检失败时,backend 以无注入方式启动目标程序,并记录回退原因与判据。范围界定(=v6 收口):「审计写入失败」指启动前预检不可用(audit_file 不可写或落在禁用位置),不指进程已启动后的运行时写失败;后者由 hook 侧失败安全覆盖(AC-3)。另(=v8 改为前缀规则):调用方传入的 overrides 不得覆盖 hook 控制变量——任何以 `TOPAZ_SLP_` 开头的键与 `PYTHONPATH` 一律保留(v6–v7 的逐项枚举已删除:R02 证实 `TOPAZ_SLP_TARGET_MODULE_NAME` 能绕过枚举并产生「计划报 Injected、实际未注入」的静默降级)。若被拒绝须产生结构化回退而不是静默报 Injected"
    verification: G-TEST-RS
    state: verifiable
  - id: AC-11
    criterion: "pocketjs 宿主能力结论落盘并绑定证据:结论为 direct / rust-adapter / windows-render-blocked 之一,附可复现命令与输出;不得以推测代替"
    verification: G-HOST-CAPABILITY
    state: blocked
    blocked_owner: "项目所有者(需提供 <SHARED_LEARN_ROOT> 只读映射)"
    note: "G-HOST-CAPABILITY 是 required 门且现在 skip 即失败(退出码 1),因此在 B01 完成前该门必然为红。这是刻意设计:required 门不得在缺失证据时静默通过。"

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
    check: "G-TEST-RS:缺失字段返回 None/Unknown,夹具中断言不产生虚构值"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-TEST-RS.txt"
    note: "v6 移除「ETA 排除 warm-up 首块」分句:AC-1..AC-11 无一条要求计算 ETA,Stage 1 不产 ETA(见非目标)。该能力归 MVP。"
  - id: A-5
    risk: "GUI 越过 seam 直接读日志文件或进程,形成第二套事实源"
    check: "G-GUI-TEST:gui/ 目录下无 fs/child_process 导入;状态只来自快照与事件"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-GUI-TEST.txt"
  - id: A-6
    risk: "把夹具结论当成真实 Topaz 证据"
    check: "AC-4/AC-7 保持 blocked;receipt 中 M-* 门必须记 not run 或 BLOCKED,不得以 G-* 结果替代"
    evidence: "docs/tasks/stage1-gui-backend/coding/receipt-v1.md"
  - id: A-7
    risk: "required 门在缺证据时静默 skip 并以退出码 0 冒充通过"
    check: "G-HOST-CAPABILITY 的 skip 路径已改为 self.fail;用缺失/UNVERIFIED/BOUND 三态各跑一次,断言退出码 1/1/0"
    evidence: "docs/tasks/stage1-gui-backend/coding/evidence/G-HOST-CAPABILITY.txt"

identities:
  coordinator: "A002[PiDeck]Main Coordinator / session A002-session-01"
  master_coding: "A003[PiDeck]Master Coding / session A003-session-01 (所有者手动启动)"
  coding: "A003[PiDeck]Master Coding(stream 拓扑下不派发 Sub-Coding)"
  review: "A003-R01(首轮独立新会话;每轮新会话按 <master>-Rxx 命名,handoff 为 docs/handoff/A003-R01.md)"
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
  candidate_kind: bundle
  criteria_versions: "由 dispatch 以外部值提供(文件名 + SHA-256);本 packet 不内嵌判据文件摘要。背景:R01 F11 与 R02-F4 两次复发——内嵌摘要会随治理文档变更而过期,按它校验会把当前基线误判为漂移。ADR-002 / ADR-003 / plan / CONTEXT / 根 AGENTS.md 的权威值以当轮 dispatch 为准"
  review_instruction_version: "agent-dev-loop v3.0.0 SKILL.md 049857138fcff222d38eb36679775e178b9bf66633fea6d2c5feb0959c0fcfe4"
  inspection_mode: isolated-sandbox

# v3: 轮次/候选/base/ledger/previous_report 属于 dispatch 记录,不入 packet。
# v3: 报告末节即 next action,不另立 next-action.md。

deliverables:
  ac_coverage_table:
    location: "coding/receipt-vN.md 内的 `## AC 覆盖表` 节(v9 起为契约的一部分,不是 dispatch 的临时要求)"
    columns: ["AC", "断言", "变异", "变异后", "证据"]
    rules:
      - "11 行,AC-1..AC-11 各一次,不得重复或缺失"
      - "断言列用反引号列出**真实存在**的断言名(Rust `#[test] fn` / Python `def test_` / TS `test('…')`)或**门 id**(`G-FMT`/`G-CLIPPY`/`G-TEST-RS`/`G-BUILD`/`G-PY-UNIT`/`G-FAILSAFE`/`G-PY-COMPILE`/`G-GUI-TEST`/`G-HOST-CAPABILITY`)"
      - "只由门守护的 AC(目前是 AC-1)必须写门 id,并在该行注明「无单测能看见」;禁止为了填满断言列而引用与该 AC 无关的测试"
      - "变异列必须**改变生产行为或构建属性**(改一行生产代码、删一个分支、改一个常量、破坏格式/依赖),**不得修改测试自身的期望常量**——改期望必然变红,不构成证据"
      - "变异后只能是 RED / GREEN / blocked;只有 state: blocked 的 AC 可写 blocked"
      - "证据列指向 `coding/evidence/ac-coverage/` 下文件,内含基线跑与变异后跑两份输出"
    enforcement:
      mechanical: "baseline/a002-receipt-check.py --require-ac-table"
      mechanical_scope: "**仅形式校验**:行数/唯一性/断言名或门 id 是否存在/取值合法性/非 blocked AC 不得为 GREEN。**不判断变异是否真的改动了生产行为**,也不判断所引断言是否与该 AC 相关。"
      semantic: "由 Review 轮独立复现变异判定;机械闸全绿不得被当作「表可信」的证据(R04-F2 即在此处误判形状)"

outputs:
  coding_receipt: docs/tasks/stage1-gui-backend/coding/receipt-v1.md
  report: docs/tasks/stage1-gui-backend/review/R01/report.md
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

## Stage 1 非目标(v6 明确)

以下能力**不在**本任务包验收范围,不得据其判定通过或不通过:

| 非目标 | 理由 | 归属 |
| --- | --- | --- |
| ETA 计算(含 warm-up 首块排除、稳定均值) | AC-1..AC-11 无一条要求;Stage 1 只验证"能解析出阶段/分块/进度/完成",不验证"能估时" | MVP 的日志监控完整性 |
| GUI 渲染运行时 / pocketjs 窗口 | `hosts/desktop` 在 Windows 上 `compile_error!`,且本机无 bun;GUI 交付物只到类型 + 校验层 | B01 结论决定后另立 |
| 真实 Topaz 注入生效(AC-4) | 需所有者授权真实 SLP 短导出 | Stage 1 门,当前 `BLOCKED` |
| 真实 tzlog 解析(AC-7) | 需所有者授权真实 SLP 渲染 | Stage 1 门,当前 `BLOCKED` |
| pocketjs 宿主能力结论(AC-11) | 需所有者提供 `<SHARED_LEARN_ROOT>` 只读映射 | Stage 1 门,当前 `BLOCKED` |
| cuDNN 管理、预设矩阵、安装器、自动更新、云功能 | 明确排除 | Stage 2/3 或永久非目标 |

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

## 版本变更（v8 → v9）

| # | 变更 | 依据 |
| --- | --- | --- |
| 1 | 新增 `deliverables.ac_coverage_table`,把覆盖表的列定义、取值域、变异合法性、机械闸的作用边界写进 packet 本体 | R04-F2:表规格此前只在 `coding/dispatch-5.md` 里,不是契约,导致 AC-1 行用一条无关断言 + 改期望的变异充当证据,而机械闸仍判 PASS |
| 2 | 断言列允许引用**门 id**;明确「只由门守护的 AC 必须写门 id,禁止引用无关测试」 | AC-1 的 `verification` 本来就是 `G-FMT, G-CLIPPY, G-TEST-RS, G-BUILD`,没有任何单测能看见它变坏(R04 实测:纯 fmt 违规 → 14/14 绿、`G-FMT` 红) |
| 3 | 显式声明机械闸的 `mechanical_scope` 为形式校验,并写明「机械闸全绿不得当作表可信的证据」 | R04 观察:把 AC-1 行改成无意义描述,闸仍报 PASS |

AC 文本、门定义、write_scope、authorizations、attack_matrix、identities 均未改动。v8→v9 不改变被测行为,`candidate-4` 的地址不变。

## 版本变更（v7 → v8）

来源:R02 verdict `FAIL`,唯一 blocking 为 **R02-F1**(AC-8 已知版本半边不可达),其余为 P3。本版包含**一处真契约变更**(AC-10 改前缀规则,所有者选定)**一处验证收紧**(AC-8)与**两处 erratum**。

| # | 项 | v7 | v8 | 依据 | 所有者决策 |
| --- | --- | --- | --- | --- | --- |
| 1 | AC-8 的验证要求 | 只写 `G-TEST-RS, G-PY-UNIT`,未注明必须覆盖已知/未知两个半边 | 新增 `note`:必须经 `LogParser` 入口分别验 1.7.0→`Version170`、1.7.1→`Version171`、1.7.9/`models.slp25.future`→`ContractMatched`、非 `models.slp2` 命名空间→`Unknown`;并写明判别式「已知版本精确匹配优先于命名空间契约匹配」 | **R02-F1**:v7 的 F3 修复把「契约匹配不可达」换成了「已知版本不可达」;`G-TEST-RS` 在两者皆退化为 `ContractMatched` 时仍全绿——只测未知半边,门无法发现已知半边被破坏。**这是 A002 的 spec 缺陷**(dispatch-2 只要求了未知版本端到端用例) | 无需决策(缺陷修正) |
| 2 | AC-10 的保留名规则 | 逐项枚举「`TOPAZ_SLP_OVERRIDE_*`、`PYTHONPATH`」 | **前缀规则**:任何 `TOPAZ_SLP_` 开头的键与 `PYTHONPATH` 一律保留;删除逐项枚举 | **R02-F5**:`TOPAZ_SLP_TARGET_MODULE_NAME` 不在枚举内,却能触发「计划报 `Injected`、实际未注入」的静默降级。枚举必然漏下一个变量 | **所有者选定 C(前缀规则)** |
| 3 | `review.criteria_versions` | 内嵌 ADR-002/plan/CONTEXT/根 `AGENTS.md` 四份摘要 | **删除内嵌摘要**;改为「由 dispatch 以外部值提供」 | **R02-F4**:根 `AGENTS.md` 记为 `d743097b…` 而磁盘/候选为 `26a55dfb…`。R01 F11 → v7 已复发一次,这是第二次;按 v7 对 `read_first` 的同一处置——**删除而非再改一次** | 所有者选定(仅 F4) |
| 4 | 标题行 | `# Task Packet — stage1-gui-backend v6`(自 v6 逐字继承,v7 未改) | `v8` | **R02-F4** 同一 finding 的第二半 | 同上 |

**未变**:`profile`、`topology`、`write_scope`、`protected_paths`、`authorizations`、`roots`、`identities`、`toolchain`、其余 10 条 AC 的 `criterion`、全部 11 个门的命令与 `expected_exit`(含 `G-HOST-CAPABILITY` 的 `blocked_by`/`expected_exit_while_blocked`)。

**合并项与豁免项(按 ADR-003)**:

| Finding | 级别 | 处置 |
| --- | --- | --- |
| R02-F1 | P1 | **必修**(AC-8 两个半边都可验) |
| R02-F5 | P3 | **修**(所有者提升为契约变更,AC-10 改前缀规则) |
| R02-F2 | P3 | **对象消失**——候选范围收窄后治理文档不再进候选,过时摘要不再被冻结(见下).不记 waived,记 `superseded-by-scope-change` |
| R02-F4 | P3 | **修**(删除,非新增) |
| R02-F3 | P3 | **`waived`**——账本 A-4/A-5 合并行;无产品路径,本文档非机器消费。保留原文 |
| R02-F6 | P3 | **`waived`**——双故障回滚残留;真实目标为 `ModuleType`,对其已存在属性 `setattr` 不会失败,无具体可达路径。保留现有实现 |

**candidate 范围规则(=v8 起成立,所有者选定 A)**

候选只含**交付物**:

```
Cargo.toml  Cargo.lock  rust-toolchain.toml  .gitignore
backend/**  hook/**  gui/**  fixtures/**
 docs/tasks/stage1-gui-backend/coding/receipt-v*.md
 docs/tasks/stage1-gui-backend/coding/evidence/**
```

**治理文档一律不进候选**:`AGENTS.md`、`CONTEXT.md`、`README.md`、`docs/**`(含 `docs/decisions/`、`docs/plan/`、`docs/identity/`、`docs/STATUS.md`、`docs/index.md`、`docs/tasks/**`)。

理由:该漂移类已连续三轮产生 finding(R01 **F9** → R02 **F2** 的两半)。根因不是纪律不够,而是「把会变的东西冻进不变的东西」这一结构。按 ADR-003 §3 选**删除**而非再维护同步。

代价与补偿:Review 不能再从候选内交叉核对治理文档 → 改由 Coordinator 在冻结时对 `<CODING_ROOT>` 做 `git status --untracked-files=all` 比对并记入 `state.md`,证明 Coding 未越出 `write_scope`;判据文件本来就以 dispatch 的外部摘要为准,不依赖候选内的副本。

## 版本变更（v6 → v7）

来源:两份材料同时指向同一类缺陷——本 packet 的**自引用与门元数据不能稳定存活到下一版**。

- A003 在 `coding/receipt-v2.md` 的「全量门重录」注记中主动上报:`G-HOST-CAPABILITY` 的 `expected_exit` 仍写 `0`,而门语义与 AC-11 的 `blocked` 状态要求退出码 1。A003 按 AC 语义执行真实 exit 1 并显式声明未伪造通过——这是正确处置,包缺陷归 A002。
- R01 的 F11(`read_first[6]` 指向过期 `packet-v1.md`)在 v4 被改成指向 `packet-v4.md`,到 v6 又已过期。**同一缺陷第二次复发。**

| # | 项 | v6 | v7 | 依据 | 分类 |
| --- | --- | --- | --- | --- | --- |
| 1 | `G-HOST-CAPABILITY` 门元数据 | `expected_exit: 0` + `required: true`,但 note 写明证据缺失时必须 exit 1;与 AC-11 `state: blocked` 自相矛盾 | 新增 `blocked_by: AC-11` 与 `expected_exit_while_blocked: 1`;明确两态判定:blocked 态观测红 → 记 `blocked`,不记 `fail`、不记 `pass` | 若照字段字面判,A003 的**正确实现**会被 R02 判成 required 门失败 → 假 FAIL。按 ADR-003 §4,spec 自相矛盾时回到 packet 修正,不让实现迎合其中一种解释 | 契约修复(非候选缺陷) |
| 2 | `read_first[6]` | `docs/tasks/stage1-gui-backend/packet-v4.md`(自身旧版) | **删除该条** | 自引用条目每次发版必过期,无法稳定;调用方(dispatch)已绑定 packet 路径与摘要,该条冗余。按 ADR-003 §3 选择**删除**而非再改一次 | 契约修复(非候选缺陷) |

**未变**:`write_scope`、`protected_paths`、`authorizations`、`profile`、`topology`、`workspace`、`identities`、`toolchain`、`roots`、全部 11 条 AC 的 `criterion` 文本、其余 10 个门的命令与 `expected_exit`。

**对候选的影响:无。** v6 → v7 不改变任何被测行为。`candidate-2` 在 v6 与 v7 下的被测字节完全相同;两项变更只影响"如何判定观测结果"与"读什么"。因此 `receipt-v2.md` 绑定 v6 摘要(`a357226b…`)是**有效历史记录**,无需重签;R02 的判据版本为 v7。

**对 ledger 的影响**:AC-11 一行在 v7 下仍为 `blocked`,其 `blocked_owner` 不变;`G-HOST-CAPABILITY` 的观测值(exit 1)登记为 `blocked` 证据,不计入 fail 计数。

## 版本变更（v5 → v6）

来源:R01 FAIL 报告(`review/R01/report.md`,绑定 `candidate-1` `3644d350…`)。本版**只收口契约措辞与门定义**,不放宽任何验收门。

| # | 项 | v5 | v6 | 依据 | 所有者决策 |
| --- | --- | --- | --- | --- | --- |
| 1 | AC-11 门位置 | `hook.tests.test_host_capability`(在 `hook/tests/` 内,被 G-PY-UNIT 的 discover 一并收集) | `hook/gates/` 独立入口,`discover -s hook/gates` | F1:必红的 AC-11 门把 `expected_exit: 0` 的 G-PY-UNIT 染红 | 选项 A(移动门) |
| 2 | A-4 的 ETA 分句 | 含「ETA 排除 warm-up 首块」 | 删除;新增「Stage 1 非目标」小节明确 ETA 归 MVP | 裁定 3:无 AC 依据、无实现,既不能通过也不能证伪 | 选项 B(删除) |
| 3 | AC-2 | 「有测试证明装配过程不写…」 | 明确两条负例((a) hook_dir 在安装目录内;(b) 大小写变体)+ R 轮独立复核 | F10(c):「有测试证明」实际由代码审查满足;F6:大小写变体可绕过守卫 | 修 |
| 4 | AC-3 | 「行为与未注入一致」(与同句「仍正常导入」互斥) | 明确优先级:「进程可用」>「等同未注入」;setattr 第 N 步失败须全批预校验或回滚,不得部分生效 | F2:第 N 步失败残留已写属性;F10(a):措辞互斥 | 修 |
| 5 | AC-9 | 未界定交付深度 | 明确 Stage 1 GUI 只到类型 + 校验层,渲染宿主不在本条 | F10(d):「GUI 不直读日志」在无运行时时近乎空跑 | 修 |
| 6 | AC-10 | 「审计写入失败」语义模糊 | 明确指启动前预检不可用,非运行时写失败;并禁止 overrides 覆盖 hook 控制变量 | F5:override 可关闭注入却报 `Injected`;F10(b) | 修 |
| 7 | `review.criteria_versions` 根 `AGENTS.md` | `77449f75…`(= `git show 6e85b9e:AGENTS.md`) | 更新为磁盘实际 `d743097b4325…` | F11:下一身份若按该摘要校验会误判基线漂移 | 治理修复 |
| 8 | AC-2 负例条数 | — | 仅保留 (a);删除「大小写变体」要求 | **自纠正**:见「v6 修订 A」;ADR-003 生效后撤回越权提升 | 所有者确认 ADR-003 |
| 9 | `G-FAILSAFE` 命令 | `discover -s hook/tests -t . -v -k failsafe`(零命中仍 exit 0) | `python -m unittest hook.tests.test_failsafe -v`(显式模块) | F4:消除 `-k` 零命中静默绿灯;F8:消灭空壳文件。**净减少部件** | 所有者确认 ADR-003 §3 |

### v6 修订 A(2026-10-20,消费策略生效后自纠正)

依 [ADR-003](../../decisions/ADR-003-finding-consumption-policy.md),撤回 v6 初稿中的一处**越权提升**:

| 项 | v6 初稿 | v6 修订 A | 原因 |
| --- | --- | --- | --- |
| AC-2 的负例 (b) | 要求「路径大小写变体同样回退」 | **删除** | 该条来自 R01 的 **F6,级别 P3、Review 明写「无写可达,仅纵深防御弱化」**。把 P3 写进验收标准违反 ADR-003 §2「禁止把 non-blocking finding 直接写成 AC」。F6 改记 `waived`,不入验收。 |

**由此产生的分类调整**(供 dispatch-2 使用):

| Finding | 原级 | 处置 | 依据 |
| --- | --- | --- | --- |
| F1 / F2 / F3 | P1 | **必修** | 有具体可达路径且违反硬不变量 |
| F4 | P2 | **修** | `-k` 零命中即静默绿灯,与 A-7 同类风险;可达 |
| F5 | P2 | **修** | override 可关闭注入却报 `Injected`,违反产品不变量 #1(注入失败必须回退) |
| F6 | P3 | **`waived`** | 无写可达(Python 侧 `commonpath` 二次拦截已实测);移除守卫会削弱纵深防御,故保留代码现状、只留记录 |
| F7 | P3 | **`waived`** | 解析器行为经独立探针确认正确;弱在测试断言而非实现。加强断言属「新增部件」,按 ADR-003 §3 不优先 |
| F8 | P3 | **修(零成本)** | 与 F4 同一处改动:把 4 个 failsafe 用例移进 `test_failsafe.py` 并改用显式模块名,同时消灭空壳文件与 `-k` 过滤,**净减少部件** |

**未变**:`write_scope`、`protected_paths`、`authorizations`、`profile`、`topology`、`workspace`、`identities`、`toolchain`、`roots`、AC-1/AC-4..AC-8/AC-11 的 criteria 文本、其余 10 个门的命令。

**受影响的行**:AC-2/AC-3/AC-9/AC-10 的 criteria 文本变更 → `coverage-ledger.md` 对应行须由 R02 重新证明,不得继承 R01 结论。A-4 的行因 check 变更同样失效。

## 版本变更（v4 → v5）

| 项 | v4 | v5 | 原因 |
| --- | --- | --- | --- |
| `protocol` | `agent-dev-loop-v2` | `agent-dev-loop-v3` | Skill 已升级到 v3.0.0;v2 的 lane 结构、handoff 路径、门语义均已变更 |
| `roots.bundles` | 缺字段 | `<BUNDLE_ROOT>`(源码树外) | v3 要求 bundle 在源码树外;v4 没写,freeze 目标无权威位置 |
| `review` 块 | 含 `first_round`/`scope`/`base`/`ledger`/`previous_report`/`candidate`/`manifest_sha256` | 只留 `family`/`container`/`candidate_kind`/`criteria_versions`/`review_instruction_version`/`inspection_mode` | v3 明确规定这些**逐轮值属于 dispatch 记录,不入 packet** |
| `outputs.next_action` | 独立 `review/R01/next-action.md` | 删除 | v3 规定报告末节即 next action,不另立文件 |
| handoff 路径 | `docs/tasks/.../handoff/A003.md` | `docs/handoff/A003.md` | v3 hard rule 8:`docs/handoff/<id>.md` 永不跟踪、永不进候选;旧路径在候选范围内 |
| `protected_paths` | 缺 `docs/handoff/` | 增加 | v3 保留路径需要显式登记 |
| `review.review_instruction_version` | Skill v2 摘要 `c7a4bbe2…` | v3.0.0 摘要 `04985713…` | 评审指令版本变更 |
| Review 身份 | `A004[PiDeck]Review` | `A003-R01`(按轮命名) | v3:Review 每轮一个全新会话,命名为 `<master>-Rxx` |

`write_scope`、`verify_commands`、`acceptance`、`attack_matrix`、`profile`、`topology`、`workspace`、`authorizations`、`toolchain` 未变。

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
