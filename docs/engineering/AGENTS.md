# 工程约束与验证策略 — Starlight_ssGui

本文件是 `docs/engineering/` 的常驻规则入口,在开发、验证、交付前阅读。根 `AGENTS.md` 优先级更高;工具链或契约变化时更新本文件。

## 项目与架构

- 目标/非目标:[产品章程](../product/AGENTS.md)。
- 技术栈/运行时/支持平台:**Rust**(stable,具体版本 `TBD`)+ **pocketjs v0.14.0**(TS 界面 + QuickJS guest + Rust core;快照在共享 Learn 库 `<SHARED_LEARN_ROOT>/sources/github.com/pocket-nexus/pocketjs/v0.14.0`,只读)+ **Python**(仅作被注入侧 hook 载荷语言,不引入运行期依赖)。运行目标:Windows 10/11 x64(与 Topaz Video 一致)。
- 模块边界/公共契约:[架构基础](../architecture/AGENTS.md)(工程侧不复制模块表)。
- 关键不变量:注入失败回退原生(见产品章程);日志解析不得阻塞 UI 线程;文件监听需容忍日志轮转与写入竞争。

## 主机与平台职责

- 开发与验收在同一 Windows x64 主机进行(主题域仅此一平台);GUI、进程句柄、文件锁、DPI 等行为必须以**原生**证据验收,模拟/兼容层结果不关闭平台门。

## 数据与安全边界

- 凭据使用本地安全配置;别名映射不入库(见 `docs/START_HERE.md` 映射表)。
- 网络、代理、依赖安装、外部服务、付费与 Git 写操作的授权入口:**由所有者按任务逐次授权**(当前未建立常备授权清单)。
- 不记录真实密钥、私网端点、绝对路径;共享文档不写端口号。

## 参考环境(只读)

| 参考 | 用途 | 边界 |
| --- | --- | --- |
| `learn/sources/.../TopazStarlightUI/v5.9` | 同机制开源实现(行为与失败案例) | 只读;许可证未声明,不复制代码 |
| `learn/analysis/` | 两个闭源工具的实现级证据(明文 hook/字节码/转储) | 只读;不重发布 |
| `<SHARED_LEARN_ROOT>` 的 pocketjs v0.14.0 | GUI 栈能力与 API 依据 | 只读;不写入 |
| `<TOPAZ_INSTALL_DIR>` / `<TOPAZ_LOG_DIR>` / `<TOPAZ_MODEL_STORE>` | 目标程序、日志与模型库(实测采样对象) | 只读;写操作(如 cuDNN)需单独授权 |

参考快照只提供行为与规格证据,**不证明**运行期能力;来源登记见 [来源登记](../research/AGENTS.md)。

## 验证策略

### 验证标签

未执行的检查不是结果。每次结果必须记录:精确版本、平台/主机、数据集、命令、真实退出码、未覆盖范围。

### 夹具族

- ①真实渲染日志样本:在目标机上跑一次 SLP 短导出,保存 tzlog 为夹具(覆盖双方言)。
- ②注入 smoke:6 帧小任务验证注入生效与回退。
- ③参数自证:审计 JSONL 与界面设置逐项对照(含"设置无效但被忽略"的耐心路径)。
- ④异常路径:注入失败回退、Topaz 未运行、日志轮转/截断、并发写。

夹具文件随任务包创建,不为占位预建。

### 平台门

- 可移植逻辑(解析器、参数模型)可在任何平台检查;GUI、输入、DPI/IME、文件锁与原子替换、进程生命周期以 Windows 原生证据关闭。
- 每条验收结果绑定精确平台与版本;状态标签沿用根规则,平台限定项标 `platform-limited`。

### 性能测量

暂无硬性指标。候选指标(待 Stage 1 定义样本集后固化):日志增量到界面可见的延迟、注入对启动时间的增量(应≈0,仅启动期)、长日志(≥30MB)解析耗时。

### 门与回退

- 阶段门见 [阶段路线图](../plan/AGENTS.md):Stage 0 冻结契约(参数表/日志模式/别名),Stage 1 只读切片;门失败时禁用候选能力并保留回退(原生运行不受影响)。
- 测试结果不授权写入、schema 迁移、打包或发布。

## 验证入口

权威定义在任务包的 `verify_commands`(当前:`docs/tasks/stage1-gui-backend/packet-v5.md`)。下表是映射摘要,不另立第二套。

| 门 | cwd | 实际命令 | 工具链/前置 | 预期退出码 |
| --- | --- | --- | --- | --- |
| `G-FMT` | `<CODING_ROOT>` | `cargo fmt --all --check` | rustfmt 1.9.0-stable | 0 |
| `G-CLIPPY` | `<CODING_ROOT>` | `cargo clippy --workspace --all-targets -- -D warnings` | clippy 0.1.95 | 0 |
| `G-TEST-RS` | `<CODING_ROOT>` | `cargo test --workspace` | cargo 1.95.0 | 0 |
| `G-BUILD` | `<CODING_ROOT>` | `cargo build --workspace` | cargo 1.95.0 | 0 |
| `G-PY-UNIT` | `<CODING_ROOT>` | `python -m unittest discover -s hook/tests -t . -v` | Python 3.11.9,stdlib only(无 pytest) | 0 |
| `G-FAILSAFE` | `<CODING_ROOT>` | `python -m unittest discover -s hook/tests -t . -v -k failsafe` | 同上 | 0 |
| `G-PY-COMPILE` | `<CODING_ROOT>` | `python -m compileall -q hook` | 同上 | 0 |
| `G-GUI-TEST` | `<CODING_ROOT>/gui` | `node --test` | Node v24.22.0(**无 bun**;禁 enum/namespace,跨文件导入写 `.ts`) | 0 |
| `G-HOST-CAPABILITY` | `<CODING_ROOT>` | `python -m unittest hook.tests.test_host_capability -v` | 需 `coding/evidence/host-capability.md` 为 `status: BOUND` | 0(**缺证据即为 1**) |
| `M-TOPAZ-INJECT` | — | 真实 SLP 短导出,注入前/后对照审计 JSONL | 真实 Topaz + 所有者授权 | 手工 |
| `M-TOPAZ-LOG` | — | 一次真实 SLP 渲染产出 `tzlog` 并解析 | 同上 | 手工 |

**门语义规则**:`required: true` 的门不得在缺失证据时静默 skip——skip 必须表现为非零退出码。`G-HOST-CAPABILITY` 即按此实现。

测试、构建、静态检查、集成与产品验收分开记录;无法运行时写明缺失条件,不声称成功。

## 已知陷阱(来源见括号)

1. SLP 目标模块名随 Topaz 版本变化(1.7.0 `models.slp25.m0vm5nn8kicb` / 1.7.1 `models.slp25.rx095brph7m1` / 1.7.2 未知)→ 必须动态发现+契约校验(逆向报告)。
2. 日志行格式:`YYYY-MM-DD HH-MM-SS.mmm Thread: <tid> <Level> <msg>`;完成标记 `total processing time: ([\d.]+)s`;`Video Export Started` 是队列事件**不是**处理边界(逆向报告)。
3. 取消/关窗时日志可能没有结束行 → 需与进程快照对账(逆向报告,skv89 monitor 注记)。
4. ETA 必须排除 warm-up 首个分块与末尾短片(同上)。
5. hook 必须失败安全:异常只写审计,不影响原生运行(两个参考实现共识)。
