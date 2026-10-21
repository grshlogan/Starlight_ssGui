# ADR-003 — Review finding 的消费策略（防过拟合）

- 状态:`accepted`(所有者 2026-10-20 确认)
- 决策人:项目所有者
- 记录人:`A002[PiDeck]Main Coordinator`
- 触发:Stage 1 `R01` 的 8 条 finding 消费过程

## 背景

`R01` 产出 3 条 P1(blocking)与 5 条 P2/P3(non-blocking)。消费时出现一个真实偏差:

Review 对 F6(Windows 路径大小写变体可绕过安装目录守卫)明确判定:

> 当前**无写可达**…Python 侧 `os.path.commonpath` 二次拦截,e2e 亦未观察到写安装目录,故仅**纵深防御弱化**

标级为 `P3 / non-blocking`。但 Coordinator 在 packet-v6 中把该条提升为 AC-2 的必验负例((b) 路径大小写变体同样回退)。**这是一个 P3 被写入验收契约**。

同时,`agent-dev-loop-v3` 已有两种闲置机制:

| 机制 | 位置 | 本任务使用次数 |
| --- | --- | --- |
| Ledger status `waived` | `templates/coverage-ledger.md` | 0 |
| Gate result `N/A`(approved, with reason and approver) | `core/loop.md` 词汇表 | 0 |

## 决策

### 1. P3 默认不修

P3 finding **一律记 `waived`,不进入修复、不进入验收标准**,除非所有者显式提升。

提升必须留下记录:谁提升、为什么、提升后由哪条 AC 承接。未提升的 P3 只在 coverage ledger 留一行 `waived` + 一行理由。

### 2. 消费 finding 前先过成本判据

对每条非 blocking finding,先回答一个固定问题:

> **如果完全不修,产品在什么具体路径上会坏?**

- 答案是「没有可达路径」→ 记 `waived`,附该判断的依据与决策人。
- 答案是「有可达路径,但代价低于风险」→ 记 `waived`,附代价比较。
- 答案是「有可达路径且会坏」→ 提升为 blocking,才允许改 AC。

**禁止**把一个 non-blocking finding 直接写成 AC 文本。AC 是产品需求,不是 finding 的化石记录。

### 3. 修复方向优先选「更少活动部件」

同一 finding 有多种修法时,优先选**删除/移动/合并**而不是**新增守卫/新增抽象/新增门**。

Review 给出的多个候选修法中,若一条能同时消除缺陷且减少部件数,默认选它;Coordinator 在 dispatch 中须标明该偏好,而不是让 Coding 自选。

### 4. 契约模糊回到契约,不到代码

若 finding 源于 spec 措辞不清(而非实现错误),处置是**修 packet / 记决策**,不是让实现去迎合两种解释中的一种。

`R01` 的裁定 3(A-4 要求 ETA 排除 warm-up,但无任何 AC 要求 ETA)是本条的正面样本:Review 拒绝把「未入册的契约」判成缺陷,也拒绝代替所有者豁免,而是上交决策。处置结果是从 A-4 删除该分句 + 新增「Stage 1 非目标」。

## 后果

- 每轮 Review 的 `waived` / `N/A` 计数**不应恒为 0**;恒为 0 是「没有做成本判断」的信号,记入 Coordinator 的消费记录。
- packet 的验收标准数量应随轮次**收敛而非膨胀**;若某轮 packet 净增 AC 条数,须在 change log 说明为何这些是产品需求而非 finding 回声。
- 纵深防御类 finding(无可达写路径,但移除会削弱未来安全性)按 `waived` 处理并保留原文缺陷记录;未来真正出现可达路径时,按新任务处理,不改写历史 verdict。

## 被否的选项

| 选项 | 否决理由 |
| --- | --- |
| 所有 non-blocking 一律修 | 会产生「修了比不修更麻烦」的变更;每增加一个守卫就多一处需要验证的行为 |
| 由 Review 自行判定 waived | 放弃风险是验收人/所有者的权限,Review 越权判定会掩盖风险 |
| 把 P3 从流程中删除(不产出) | 丢失缺陷记录;未来出现可达路径时无从追溯 |

## 引用

- `agent-dev-loop` v3.0.0:`core/loop.md`(词汇表)、`templates/coverage-ledger.md`(status 定义)
- 本任务:`docs/tasks/stage1-gui-backend/review/R01/report.md`(F6 的原始分级与「无写可达」判断)
- 根 `AGENTS.md` §7
