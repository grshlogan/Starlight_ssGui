# Checkpoint 目录规则 — docs/handoff/

本目录存放**每个身份自己的 ACK 与 checkpoint**,路径固定为
`docs/handoff/<identity-id>.md`(`A002`、`A003`、`A003-R01` …)。

## 性质

- 由该身份**本人**写入,且只写自己的文件。
- **永不跟踪、永不提交、永不进入候选。** `docs/handoff/` 是 `snapshot.mjs` 的保留路径:
  `freeze` 会拒绝其中的路径(除 `AGENTS.md` 与 `.gitignore`),`verify` 会拒绝携带它们的
  manifest,`sync`/`check` 既不删除也不把其中的未跟踪文件计入 `stray_count`。
- 内容分两节:**ACK**(准入时写一次,恢复时追加 `Resumed:` 行)与 **Checkpoint**
  (随进展覆盖)。
- Checkpoint 是指针,不是事实源。与磁盘冲突时**以磁盘为准**。

## 与任务目录的分工

| 位置 | 内容 |
| --- | --- |
| `docs/tasks/<task-id>/` | 任务治理产物:packet、state、dispatch、receipt、report、acceptance |
| `docs/handoff/<identity-id>.md` | 该身份的准入与恢复锚点;不进候选 |

历史说明:`stage1-gui-backend` 早期把 A003 的 handoff 放在
`docs/tasks/stage1-gui-backend/handoff/A003.md`,该路径在候选范围内,违反
`agent-dev-loop` v3.0.0 hard rule 8;已于 2026-10-20 迁移到本目录。

## 准入自检

进入工作区后先跑:

```bash
git check-ignore -q docs/handoff/<identity-id>.md && echo ignored || echo NOT-IGNORED
```

未命中 ignore 规则时按 `ADMITTED-WITH-LIMITS` 准入,并请 Coordinator 把该规则作为
packet 变更补进基线;**不得**为此改写自己写范围之外的文件。
