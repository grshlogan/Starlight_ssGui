# Dispatch `stage1-gui-backend/A003/7`

> **rev 2（2026-10-21，ACK 之前）**：`review-ready` 已从 Task state 集合退休，正确 token 是 `REVIEW_READY`；本文两处已改。
>
> **rev 3（2026-10-21，ACK 之前）**：`agent-dev-loop` 升到 **v3.1.0**，packet 从 `v11` 改钉 **`packet-v12`**（`8d0a1f2c…`）。**七项任务、base 候选、机械闸口径仍然一字未变。** 对你有影响的两处：
> 1. 6 条 owner-blocked AC（`AC-4.3`、`AC-7.1`–`7.3`、`AC-11.1`–`11.2`）已在 packet 里写成 `deferral`，本阶段交付边界收窄到 **40 条 verifiable**。**不要**再去想办法产出真实 Topaz 证据——那不是本轮的事。
> 2. `review.ocr` 定为 `scan`，但那是**下一轮 Review 的事**，与 Coding 无关；你不需要安装或调用 OCR。

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/7` |
| Kind | **repair**（消费 `R05` FAIL + OpenCodeReview 实测复核结论） |
| Sent at | 2026-10-21 |
| Receiver | `A003[PiDeck]Master Coding`（同一会话） |
| **Packet** | `docs/tasks/stage1-gui-backend/packet-v12.md`（**pinned，`packet_rev: 12`；v11 及以前全部作废**），`sha256:8d0a1f2cfb32c65e09b867fc3461218dcf465589e0200a375b691257c8576eef` |
| 机械闸 | `baseline/a002-receipt-check.py` `sha256:cf53601c39768e606744c904db7329ad2968e0f4a36ff8d1a1b87af2e2cb52f8`（**三项**，`--require-ac-table` 已在 v10 撤除，见下） |
| Workspace | `<CODING_ROOT>` = `E:/project/Starlight_ssGui.worktree/A003/Master`，分支 `a003/master` |
| Candidate base | `candidate-5` `28d99bd4cbf38f606b56b6ad59d85bda0ddc6ce47affb8c2b2735c78d8f2fce5`（58 files） |
| Resumed | `coding/receipt-v5.md` → **`coding/receipt-v6.md`** |
| ACK 位置 | `docs/handoff/A003.md`（追加 checkpoint） |

## 本轮与前四轮有一个本质区别

**这是 R02 之后第一次要改生产代码。**

| 轮次 | 生产代码 | 结论 |
| --- | --- | --- |
| R03 / R04 / R05 | **零变更**（candidate-2 → candidate-5 的 6 份 production prefix 逐字节相等） | 所有 finding 都是「测试没守住」 |
| **R06（本轮）** | **会变**：`hook/sitecustomize.py` + `backend/src/log_parser.rs` | 前两类是**真实现缺陷**，不是断言缺口 |

所以本轮验收里，「生产 diff = 零」这条不再适用；我改成要你**逐条列出改了哪几行、为什么**。

## 上一轮结论（两路，互相独立）

### 路 A：`A003-R05` 判 **FAIL**

报告：`docs/tasks/stage1-gui-backend/review/R05/report.md`。绑定 `candidate-5` + `packet-v10`，43 个变异（38 红 / 5 绿），46 条 AC 逐条判定。

4 条 P2，**全部是「测试缺少断言」，实现全部正确**：

| ID | AC | 一句话 |
| --- | --- | --- |
| R05-F1 | AC-10.6 | 前缀规则只被 4 个具体键测过；换回枚举仍 15/15 绿 |
| R05-F2 | AC-6.2 | 夹具测试**没有任何 chunk 断言** |
| R05-F3 | AC-6.1 | 夹具测试**没有阶段断言**，`unknown_count <= 1` 的容差恰好能藏掉 1.7.0 的一个丢失阶段 |
| R05-F4 | AC-2.1 | `PYTHONPATH` 只断言 `contains("hook")`，改成字面量 `"hook"` 仍全绿 |

### 路 B：OpenCodeReview v1.13.2 实测（A002 亲自跑，不是采信）

实测记录：`E:/project/Learn/notes/open-code-review/measurement-starlight-ssgui-v1.md`。27 条评论，A002 逐条复核，确认 3 条真缺陷：

| 编号 | 位置 | 缺陷 | 我如何复现 |
| --- | --- | --- | --- |
| C-1 | `hook/sitecustomize.py:196-200` | `exec_module` 吞掉目标模块的导入异常 → `import` 正常返回、**半初始化模块留在 `sys.modules`** | 20 行探针：`import models.slp2`（模块内 `raise RuntimeError`）→ `import SUCCEEDED`，`sys.modules` 命中，模块只有 `RAISED` 一个键 |
| C-2 | `backend/src/log_parser.rs:150-180` | `parse_chunk` 无锚点 → 任何含 `chunk` 的告警行变成 `Progress` | 追加探针测试：`Warn chunk size must be at least 256` → `Progress{chunk_index: Some(256)}`，`cargo test` 2 passed |
| C-2b | `log_parser.rs:215` vs `:186` | 路由用 `contains("total processing time")`，取数用 `find("total processing time:")` → 无冒号的行产出 `Completed{seconds: null}` 且永不落 `Unknown` | 同一批探针：该行 → `Completed { seconds: None }` |

**这两路零交集。** R05 一篇也找不到 C-1/C-2；OCR 一条也看不到 R05 那四条。原因在方法：变异测试只证明「删掉守卫会红」，证明不了「守卫现在的做法对不对」——R05 的 M08 删掉 `exec_module` 的 try/except 后 `G-FAILSAFE` 确实红了，于是 AC-3.1 判 pass，而那个 try/except 本身是错的。

## 契约已改（`packet-v11`，所有者 2026-10-21 批准）

`acceptance` 是敏感字段，三条改动全部记在 packet 的 `change_log`。**AC 总数仍 46 条，id、`verification`、`state`、门定义全不变**——只改措辞与 note：

1. **AC-3.1** 由「目标模块导入抛异常时仍可导入且进程不中断」改为「**目标模块自身导入抛异常时，可观察行为与未注入时一致：同一异常类型向上传播、`sys.modules` 不残留该模块名、不产生部分初始化的模块对象**」。
   并加 note 划界：v6 的「进程可用严格优先于行为等同未注入」**只适用于 hook 自身故障**（AC-3.2/3.4），不适用于目标模块自己失败——那时没有可挽救的模块，吞掉只会把干净的 `ImportError` 变成远处的 `AttributeError`。AC-3.3 的 v6 note 同步加了这条范围界定。
2. **AC-6.3** 加 note：`Completed` 必须带解析出的耗时；**路由与取数必须用同一个匹配式**；解析不出耗时即计入 `Unknown`。
3. **AC-6.4** criterion 不变，加 note：必须用反例覆盖「行不得被误认成已知事件」，并给出 C-2 的实测反例与修复要求。

**这不是放宽，是收紧。** 旧措辞允许两种互斥读法，实现选了弱的那个。

## 本轮要做的七件事

### 1. C-1（P1，必修）— `exec_module` 必须上抛，不得吞

**位置**：`hook/sitecustomize.py:196-200`。

**现状**：

```python
def exec_module(self, module: ModuleType) -> None:
    try:
        self._loader.exec_module(module)
    except Exception as error:
        _record_error("import", error)
        return              # ← 这里
    apply_overrides(module, self._module_name)
```

**要求**：

- 真实 loader 抛异常时，**先记 `_record_error("import", error)`，然后原样上抛**（同一异常实例，不改类型、不包装、不 `SystemExit`）。
- `apply_overrides` 只在真实 loader 成功后才执行（现在是，保持）。
- 审计 error 行照旧写入（AC-3.5 / AC-5.3 不变）。
- CPython 在 `exec_module` 抛出时会自己 `del sys.modules[name]`，所以只要上抛，第三条（`sys.modules` 无残留）自动成立——**不要自己手写 sys.modules 清理**，多一个活动部件（ADR-003 §3）。

**测试要求**（这是本项的重点，不是附带）：

- `hook/tests/test_failsafe.py:46` 的 `test_failsafe_import_failure_is_swallowed_at_injection_boundary` **必须消失或被替换**。它的名字就把缺陷写成了规格。
- 新用例必须**经真实 import 机制**跑，不能只调 `proxy.exec_module(module)`。至少断言三件事：
  1. 抛出的是**同一个异常类型**（用 `assertRaises(RuntimeError)` 或捕获后比 `type`）；
  2. `assertNotIn("models.slp2…", sys.modules)`；
  3. 紧接着 import 一个健康模块仍成功（进程可用）。
- 构造方式建议：`tempfile` 造一个包目录，里面一个模块 `raise RuntimeError(...)`，`sys.path` 插入后 `import`。跑完清理 `sys.path` 与 `sys.modules`。
- **删测试/改名是被允许的，但必须在 receipt 里写明「删了哪个、换成哪个、为什么」**——机械闸第 1 项会抓到测试名集合差异，我不接受无解释的消失。

### 2. C-2（P2，必修）— `parse_chunk` 必须锚定分块语法

**位置**：`backend/src/log_parser.rs:150-180`。

**现状**：无 `/` 时，取 `chunk` 之后的前两个数字 token，于是任何含 `chunk` 又恰好有数字的行都变成分块进度。

**要求**：

- 只在**分块语法成立**时才返回序号；否则 `(None, None)`，让该行落到 `Unknown`（计入 `unknown_count`）。
- 具体锚定方式由你定（要求出现 `chunk` 与 `/` 的组合，或要求 `N/M` 形态，或限定已知前缀），**但必须满足**：
  - `... Warn chunk size must be at least 256` → `Unknown`，`unknown_count` +1；
  - 夹具 `1.7.0` 的 `chunk 1/3`、`chunk 2/3` 与 `1.7.1` 的 `chunk 1/2`、`chunk 2/2` **仍然解析出相同的序号/总数/百分比**（这是第 5 项的护栏，别把两件事做成一件）。
- 补**至少 2 条对抗用例**（非分块行）：一条含 `chunk` + 数字无 `/`，一条含 `chunk` + 数字 + `%`。都断言得到 `Unknown` 且 `unknown_count` 增加。

### 3. C-2b（P2，必修）— 路由与取数用同一匹配式

**位置**：`backend/src/log_parser.rs:215`（路由）与 `:186`（取数）。

**现状**：路由 `contains("total processing time")`，取数 `find("total processing time:")`。两者不是同一个条件 → 无冒号的行得到 `Completed{seconds: null}`，且永远不落 `Unknown`。

**要求**：二选一，**优先选活动部件更少的**：

- (a) 路由也改成带冒号的 marker；或
- (b) 保持路由不变，但 `parse_seconds` 返回 `None` 时**不产出 `Completed`**，改落 `Unknown`。

我倾向 (a)：一个条件写两遍是这次缺陷的根因，把它变回一个条件最省事。但如果你有理由选 (b)（例如"提到了总耗时但没给值"在语义上确实算完成），在 receipt 里说明，我按行为验。

**测试要求**：加一条 `total processing time 3.5s`（无冒号）→ 断言**不是** `Completed`（`Unknown` 或你选定的语义），并断言带冒号的夹具行仍然 `Completed{seconds: Some(3.5)}`。

### 4. R05-F1（P2，必修）— AC-10.6 的前缀规则需要非枚举键用例

**位置**：`backend/src/injection.rs` 的 `#[cfg(test)]`，现测试在 `:245-278`、`:381-416`。

**问题**：`is_reserved_override` 的规则是「`PYTHONPATH` 或 `TOPAZ_SLP_` 前缀」，但测试只用到了 4 个具体键。把它换回枚举 → 15/15 全绿。

**要求**（生产代码零改动）：

- 加一条**非枚举键**用例：`overrides.insert("TOPAZ_SLP_LAUNCH_ID", "spoofed")` → 断言 `Err(InjectionError::ReservedOverride(...))`，且错误里带该键名。
- 再加一条**任意未来键**用例：`TOPAZ_SLP_ANY_FUTURE_FLAG` → 同拒。
- 加一条断言：被拒之后，环境里的 `TOPAZ_SLP_LAUNCH_ID` 仍等于 `request.launch_id`（后端在 `:122-130` 先写它、再让 overrides 覆盖——被覆盖就是 attribution spoof）。

### 5. R05-F2（P2，必修）— 夹具必须断言 chunk

**位置**：`backend/src/log_parser.rs` 的 `parses_checked_in_fixtures`。

**要求**（生产零改动）：断言两个夹具的 `Progress` 事件：

| 夹具 | 期望 |
| --- | --- |
| 1.7.0 | `(chunk_index, chunk_total, percent) = (1,3,33.0)`、`(2,3,66.0)` |
| 1.7.1 | `(1,2,50.0)`、`(2,2,100.0)` |

（准确值以你实跑结果为准；**如果你跑出来的不是这组数，先停下来在 receipt 里写清楚实际值与你凭什么认为它对**，别把断言写成"等于实际值"——那就是 R04-F2 的 tautology 又一遍。）

### 6. R05-F3（P2，必修）— 夹具必须断言阶段，并收紧容差

**位置**：同上。

**要求**（生产零改动）：

- 断言 1.7.0 的阶段集合含 `VaeEncode`、`DitUpscale`、`VaeDecode`；1.7.1 含它实际有的阶段（据实写，别猜）。
- `unknown_count`：1.7.0 收紧为 `== 0`，1.7.1 保持 `== 1`（其末尾确有截断行）。
- 理由：现在的 `<= 1` 容差**恰好**够藏掉 1.7.0 丢掉一个阶段（R05 的 M21 就是这么绿的）。

### 7. R05-F4（P2，必修）— `PYTHONPATH` 精确断言

**位置**：`backend/src/injection.rs:227-241`。

**问题**：唯一断言是 `.contains("hook")`。`hook`、`…/hook`、相对路径、错误工作树都能让它绿。

**要求**（生产零改动）：

- 断言精确值：`PYTHONPATH == format!("{}{}existing", request.hook_dir.display(), path_separator())`；或按分隔符 split 后断言**首段等于 `request.hook_dir`**（后者更稳，windows/posix 分隔符各一例更好）。
- 加一条 `base_environment` 里**没有** `PYTHONPATH` 的用例 → 断言结果就等于 `hook_dir`（不加分隔符、不产生 `;` 前缀）。

## 明确不做的

| 不做 | 原因 |
| --- | --- |
| 改 `path_is_within`（`injection.rs:59-61`） | OCR 也报了这条（`starts_with` 无 canonicalize，符号链接/8.3 短名可绕）。**但它没进 v11 契约**：加固方式会引入 `canonicalize` 与错误处理，属于新增活动部件，需先在 v12 定 AC 再动。**本轮不要顺手改** |
| 动 R04 及更早的 `waived` 项 | R04-F3/F4(b)/F6、R03-F4、R02-F3/F6、R01 F6/F7 全部维持 `waived` |
| 改 `hook/gates/test_host_capability.py` | AC-11 仍 blocked，门红是正确观测 |
| 为 C-1 手写 `sys.modules` 清理 | 上抛后 CPython 自己会清；自己写等于多一个可能错的部件 |
| 把第 2、5 项合并成"一起改，绿了就行" | 一个是生产改动、一个是断言补强，必须能分别证明。合并后我无法判断夹具绿是靠代码还是靠断言 |
| 用旧 evidence | 全部重录 |
| 在 receipt 里写没跑过的命令 | R04-F5 就是这么来的 |
| 动 `review/R0*`、`state.md`、`coverage-ledger.md`、`packet-v*.md` | 治理侧 |

## 机械闸（变了两项）

`baseline/a002-receipt-check.py` 现在**只有三项，且没有 `--require-ac-table`**：

1. 候选间 Rust 测试名集合比对——**消失的测试必须被解释**（本轮你会删掉一条，闸会点名它，你必须在 receipt 里对得上）；
2. receipt 声称的测试名必须在其 evidence 里有 `... ok` 行；
3. receipt 里反引号包裹的标识符（≥2 下划线、非全大写）必须真实存在于源码/evidence/dispatch。

跑法：

```
python docs/tasks/stage1-gui-backend/baseline/a002-receipt-check.py \
  E:/project/Starlight_ssGui.bundle/stage1-gui-backend/candidate-5/payload \
  . docs/tasks/stage1-gui-backend/coding/receipt-v6.md \
  docs/tasks/stage1-gui-backend/coding/evidence/*.txt \
  -- docs/tasks/stage1-gui-backend/coding/dispatch-7.md
```

目标 **exit 0**。注意：**不再要求 AC 覆盖表**——`packet-v10` 已撤除该交付物，`receipt-v5` 里的 `## AC 覆盖表` 是历史产物，**v6 不必写，也不要为它花时间**。

## 交付

1. `coding/receipt-v6.md`（state `REVIEW_READY`），逐条响应七项；**必须含一节「本轮生产代码改动清单」**：改了哪个文件、哪几行、为什么、对应哪条 AC；
2. `coding/evidence/` 全量重录（含 C-1 的新 import 测试输出、C-2/C-2b 的对抗用例输出）；
3. `docs/handoff/A003.md` 追加 checkpoint；
4. **报告前自己跑上面那条机械闸并贴 exit code**（目标 0）。

## 我收到后

1. 机械闸 → 目标 exit 0；
2. **生产 diff 逐行审**（本轮不再期望零差异；我会用 `git diff` 对着 `candidate-5` 看，剥掉 `#[cfg(test)]` 后只允许 `sitecustomize.py` 的 `exec_module` 块 + `log_parser.rs` 的 `parse_chunk`/`parse_seconds`/`parse_line` 三处有实质变化）；
3. **独立复现 C-1 / C-2 / C-2b 已消失**：用我自己那三个探针（不是你的测试）跑一遍——半初始化模块必须不再出现，告警行必须落 `Unknown`，无冒号行必须不产出 `Completed`；
4. 抽查 R05 四条：把流水线改成 R05 的变异形态，确认现在会红；
5. 冻结 `candidate-6` → 派 `A003-R06`（全新会话，`Previous report: review/R05/report.md`，base `candidate-5`）。
