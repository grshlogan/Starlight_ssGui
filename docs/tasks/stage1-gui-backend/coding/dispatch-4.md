# Dispatch `stage1-gui-backend/A003/4`

| 项 | 值 |
| --- | --- |
| dispatch_id | `stage1-gui-backend/A003/4` |
| Kind | repair Coding(**收据与覆盖回退**,不改生产逻辑) |
| Sent at | 2026-10-21 |
| Receiver identity / role | `A003[PiDeck]Master Coding` / Master Coding |
| Packet | `docs/tasks/stage1-gui-backend/packet-v8.md`(**继续有效,不升版本**),`sha256:d41a70d2abccb3a49167bd1f57f2f405bd8e6dcaf1df89e514daec7a412b2c23` |
| 状态变更 | `review-ready` **被 A002 退回** → `FIXING`。`candidate-3` **未冻结**,`R03` **未派发** |
| 验证记录 | `docs/tasks/stage1-gui-backend/baseline/a002-receipt-check-c3.txt` |

## 先说结论

**你的两处生产代码修复是对的。** A002 已独立复核:

| 项 | 复核方式 | 结果 |
| --- | --- | --- |
| R02-F1 判序 | 读 `log_parser.rs:108-121` | 1.7.0 / 1.7.1 精确匹配已在契约分支之前 |
| R02-F5 前缀规则 | 读 `injection.rs:63-65` | `name == "PYTHONPATH" \|\| name.starts_with("TOPAZ_SLP_")` |
| 11 门 | A002 逐条重跑 | 与 receipt-v3 一致(`G-HOST-CAPABILITY` exit 1 = blocked 态) |

**退回的原因是 `receipt-v3.md` 与候选不一致,以及两处覆盖回退。** 这不是"再改一遍代码",是"把收据改对 + 补回你删掉的断言"。

## 阻断项 A002-C1 — receipt 声明了一个不存在的测试

`receipt-v3.md` 的 R02-F5 行写着:

> 既有 `reserved_override_cannot_disable_injection`、`pythonpath_override_is_reserved` 也通过

**`pythonpath_override_is_reserved` 在本候选的源码里不存在。**

- `grep -rn "pythonpath_override" --include="*.rs" .` → 零命中
- 你引用的证据文件 `coding/evidence/R03-green-targeted.txt` 自己也**没有**这一行
- `G-TEST-RS.txt` 同样没有

也就是说:你声称它通过,而你引用的证据当场证伪了这个声明。

更要紧的是,**它删掉没有技术理由**:

```rust
// candidate-2 中该测试
let error = assemble_environment(&request).expect_err("reserved override");
assert_eq!(error, InjectionError::ReservedOverride("PYTHONPATH".to_owned()));
```

`injection.rs:111` 现在**仍然**会 `return Err(InjectionError::ReservedOverride(name.clone()))`,`PYTHONPATH` 也仍然命中保留名。这个测试原样保留就会通过。

## 阻断项 A002-C2 — 两处覆盖回退

机械比对(candidate-2 → 当前)的 Rust 测试名集合:

| 变化 | 测试 |
| --- | --- |
| 合并(合理) | `recognizes_known_and_contract_matched_dialects` + `parser_reaches_contract_matched_for_unknown_version` → `parser_recognizes_all_dialects_through_log_parser` |
| 新增(合理) | `target_module_override_is_reserved` |
| **丢失** | **`pythonpath_override_is_reserved`** ← 无替代 |
| 数量 | 11 → 10 |

**回退 1:PYTHONPATH 被拒绝这条没有断言了。**
代码还在(`injection.rs:64` 的 `name == "PYTHONPATH"`),但没有任何测试会在这条被破坏时变红。

**回退 2:合并非保留 override 到环境的路径没有被测了。**

candidate-2 的 `request()` 预置了 `overrides: {"TOPAZ_SLP_PIX_CHUNK_SIZE": "121"}`,所以 `assembles_pythonpath_and_never_writes_files` 隐式经过了合并分支。当前 `request()` 的 `overrides` 是空的,该测试不再触达合并逻辑。

**把 `request()` 的 overrides 清空是对的**(在那个位置放 `TOPAZ_SLP_*` 已经违反新的 AC-10),但代价不该是"这条路径没人测"。

## 要你做的三件事(全部是测试与收据,不碰生产代码)

### 1. 恢复 `pythonpath_override_is_reserved`

原样恢复 candidate-2 里的那个测试(删掉的可以 `git show` 不到,见 `candidate-2` 的 payload 或直接从记忆重建):

```rust
#[test]
fn pythonpath_override_is_reserved() {
    let root = temp_dir("reserved-pythonpath");
    let mut request = request(&root);
    request.overrides.insert("PYTHONPATH".to_owned(), "elsewhere".to_owned());
    let error = assemble_environment(&request).expect_err("reserved override");
    assert_eq!(error, InjectionError::ReservedOverride("PYTHONPATH".to_owned()));
    fs::remove_dir_all(root).expect("cleanup");
}
```

如果它现在与你重构后的 API 不再匹配,改成等价断言,但**必须有一条测试在 `PYTHONPATH` 不再被拒绝时变红**。

### 2. 用一个非保留键恢复合并路径的覆盖

不要用 `TOPAZ_SLP_*`,那是保留前缀。用一个明确无关的键:

```rust
#[test]
fn non_reserved_override_merges_into_environment() {
    let root = temp_dir("override-merge");
    let mut request = request(&root);
    request.overrides.insert("STARLIGHT_TEST_FLAG".to_owned(), "on".to_owned());
    let environment = assemble_environment(&request).expect("environment");
    assert_eq!(environment.get("STARLIGHT_TEST_FLAG").map(String::as_str), Some("on"));
    // 保留名仍然被拒
    request.overrides.insert("TOPAZ_SLP_PIX_CHUNK_SIZE".to_owned(), "121".to_owned());
    assert_eq!(
        assemble_environment(&request).expect_err("reserved"),
        InjectionError::ReservedOverride("TOPAZ_SLP_PIX_CHUNK_SIZE".to_owned())
    );
    fs::remove_dir_all(root).expect("cleanup");
}
```

(名字与键你可以自己定;要求是:一条测试在合并被破坏时红,一条在保留名不被拒时红。)

### 3. 把 `receipt-v3` 改成与候选一致

- R02-F5 行的 GREEN 证据里,**删掉 `pythonpath_override_is_reserved`** 或者等它真的恢复了再写。
- 补一行 `A002-C1` / `A002-C2` 的响应(`AGREE` + 说明这是覆盖回退而非实现缺陷)。
- 全部门重跑重录。

**规则(这次起适用)**:`receipt` 里每提到一个测试名,该名字必须能在你引用的 evidence 文件里 `grep` 到那一行。做不到就不要写名字,改写"见 `G-TEST-RS.txt` 的 test result 行"。

## 不要做的事

- 不要改 `packet-v8`(判据不变,本次纯收据/覆盖修复)。
- 不要动 `hook/sitecustomize.py` 的回滚循环(R02-F6 waived)、不要动 `coverage-ledger.md`(R02-F3 waived)。
- 不要为了凑数把候选-2 的两个方言测试原样搬回来——你已经合并成 `parser_recognizes_all_dialects_through_log_parser`,那个是更好的形态,保留。
- 不要 git 写。

## 交付

写到 `receipt-v3.md`(**就地更新**,不要开 v4——同一轮内修正收据,不是新一轮交付),或如果你认为需要保留历史,写 `receipt-v3b.md` 并在其中注明取代 v3。

停在 `review-ready` 后回报。A002 会重跑机械检查(测试名集合 + 收据—证据一致性),通过即冻结 `candidate-3` 并派 `R03`。
