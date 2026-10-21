#!/usr/bin/env python3
"""A002 冻结前置机械检查(2026-10-21 起,不可跳过)。

用法:
  a002-receipt-check.py <prev_candidate_payload> <coding_root> <receipt> <evidence...> -- <context...>

检查三项:
  1. 候选间 Rust 测试名集合差异。消失的测试必须被"解释"——其名字出现在 receipt 或任一 context
     (dispatch / 裁决记录)里;否则判 unexplained removal。
  2. receipt 提到的每个测试名,必须同时(a)存在于源码,(b)在其引用的 evidence 里有 "... ok" 行。
  3. receipt 里反引号包裹的标识符(至少两个下划线、非全大写)必须存在于候选源码、evidence
     或 context 任一处——防"引用了一个从未存在过的符号"。

能当场抓住的三类历史缺陷:
  - R01-F1:evidence 是冻结前旧版本的运行结果,引用了候选里已不存在的测试方法名。
  - A002-C1:receipt 声称一个源码里根本没有的测试通过。第 2 项抓不住"从未存在过"的名字
    (它只遍历候选里出现过的测试名),所以补第 3 项。
  - R04-F5(c):证据文件引用不存在的断言名(形近但拼错)。

退出码:0 = PASS;1 = FAIL;2 = 用法错误。
"""
import re
import sys
import pathlib

try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
except Exception:
    pass

args = sys.argv[1:]
if '--' in args:
    split = args.index('--')
    args, ctx_paths = args[:split], args[split + 1:]
else:
    ctx_paths = []

if len(args) < 3:
    print(__doc__)
    sys.exit(2)

prev, root, receipt = pathlib.Path(args[0]), pathlib.Path(args[1]), pathlib.Path(args[2])
ev_paths = [pathlib.Path(p) for p in args[3:]]

if not receipt.is_file():
    print("receipt 不存在: %s" % receipt)
    sys.exit(2)

NL = chr(10)


def test_names(r):
    """三个运行面的测试名。前缀区分来源,避免跨语言重名互相抵消。

    2026-10-21 补:此前只收 backend/src/*.rs,于是 Python 与 GUI 测试的消失
    不会被本闸发现 —— dispatch-7 换掉一个 Python 测试名时,闸报了「消失的测试:(无)」。
    """
    out = set()
    for p in r.glob('backend/src/*.rs'):
        out |= {'rs:' + n for n in re.findall(r'#\[test\]\s*\n\s*fn\s+(\w+)', p.read_text(encoding='utf-8'))}
    for p in list(r.glob('hook/tests/*.py')) + list(r.glob('hook/gates/*.py')):
        out |= {'py:' + n for n in re.findall(r'^\s*def\s+(test_\w+)\s*\(', p.read_text(encoding='utf-8'), re.M)}
    for p in r.glob('gui/test/*'):
        out |= {'js:' + n for n in re.findall(r'\btest\(\s*["\']([^"\']+)["\']', p.read_text(encoding='utf-8'))}
    return out


t_prev, t_now = test_names(prev), test_names(root)
ev_text = NL.join(p.read_text(encoding='utf-8') for p in ev_paths if p.exists())
rc = receipt.read_text(encoding='utf-8')
ctx_only = NL.join(
    pathlib.Path(p).read_text(encoding='utf-8') for p in ctx_paths if pathlib.Path(p).exists())
ctx = rc + NL + ctx_only

gone = sorted(t_prev - t_now)
new = sorted(t_now - t_prev)

print("prev tests: %d   now tests: %d" % (len(t_prev), len(t_now)))
print(NL + "## 消失的测试")
print(NL.join("  - " + n for n in gone) if gone else "  (无)")
print(NL + "## 新增的测试")
print(NL.join("  + " + n for n in new) if new else "  (无)")

print(NL + "## 消失测试的解释状态")
unexplained = []
for n in gone:
    bare = n.split(':', 1)[1] if ':' in n else n
    # 只在 receipt 里找解释:ctx 含 dispatch,而 dispatch 可能只是"命令删除它"
    # (2026-10-21 反例:把 receipt 里的改名说明删掉后,dispatch 仍提到旧名,
    #  旧规则判 EXPLAINED —— 循环论证,已收紧)
    ok = bare in rc
    if not ok:
        unexplained.append(n)
    print("  [%s] %s" % ('EXPLAINED' if ok else 'UNEXPLAINED', n))

print(NL + "## receipt 提到的测试名 vs evidence")
false_claims = []
for n in sorted(x for x in (t_prev | t_now) if x in rc):
    exists = n in t_now
    in_ev = bool(re.search(re.escape(n) + r".*\.\.\. ok", ev_text))
    ok = exists and in_ev
    if not ok:
        false_claims.append(n)
    print("  [%s] %s  源码存在=%s  evidence含ok行=%s"
          % ('OK' if ok else 'FALSE CLAIM', n, exists, in_ev))

# --- 检查 3:receipt 里反引号包裹的标识符必须真实存在 ---
src_text = ""
for pat in ('backend/**/*.rs', 'hook/**/*.py', 'gui/**/*.ts'):
    for p in root.glob(pat):
        src_text += p.read_text(encoding='utf-8', errors='replace') + NL
known = src_text + ev_text + ctx_only   # 不含 receipt 自身,否则任何 token 都「已知」
ghosts = []
for tok in sorted(set(re.findall(r'`([^`\n]+)`', rc))):
    if not re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', tok):
        continue          # 路径/空格/点号/带附标的 token 不按标识符判
    if tok.count('_') < 2:
        continue          # 至少两个下划线,回避普通词与 Python 私有名
    if tok.isupper():
        continue          # TOPAZ_SLP_* 之类环境变量另在 evidence 里
    if tok not in known:
        ghosts.append(tok)

print(NL + "## receipt 引用的标识符 vs 候选源码/evidence/context")
if not ghosts:
    print("  (全部可定位)")
else:
    for g in ghosts:
        print("  [GHOST] %s  源码/evidence/context 均无此符号" % g)

passed = not false_claims and not unexplained and not ghosts
print(NL + "RESULT: %s  (false claims=%d, unexplained removals=%d, ghost refs=%d)"
      % ('PASS' if passed else 'FAIL', len(false_claims), len(unexplained), len(ghosts)))
sys.exit(0 if passed else 1)
