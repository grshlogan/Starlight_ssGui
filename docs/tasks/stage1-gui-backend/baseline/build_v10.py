# -*- coding: utf-8 -*-
# 已发布。不要重跑：packet-v10 发布后手工补了 Block 表的 AC 映射与「版本变更(v9→v10)」节，重跑会丢这两处。
"""Build packet-v10 from packet-v9.

v10 = split 11 multi-clause ACs into 45 atomic ACs (one criterion + one verification each),
and delete deliverables.ac_coverage_table (A002 invention, not in the Skill).

Usage: python baseline/build_v10.py   (cwd = docs/tasks/stage1-gui-backend)
"""
import io
import json
import sys

AC = [
    ("AC-1.1", "cargo fmt --check 在 workspace 内零差异", "G-FMT", None),
    ("AC-1.2", "cargo clippy --workspace --all-targets 在 -D warnings 下无告警", "G-CLIPPY", None),
    ("AC-1.3", "cargo test --workspace 全部通过且失败数为 0", "G-TEST-RS", None),
    ("AC-1.4", "cargo build --workspace 成功产出 backend 交付物", "G-BUILD", None),
    ("AC-1.5", "Cargo.lock 只含本 workspace 成员,无 bun 或 pocketjs 相关包",
     "manual-procedure: test $(grep -c '^name = ' Cargo.lock) -eq 1",
     "无单测能看见容器;这是依赖集断言,由 R 轮执行该命令复核"),

    ("AC-2.1", "装配出的子进程环境以 PYTHONPATH 指向 hook 目录作为注入通道", "G-TEST-RS", None),
    ("AC-2.2", "backend 与 hook 产物中不存在以 TOPAZ_INSTALL_DIR 为目标的文件系统变更调用",
     "manual-procedure: 审读 backend/src 与 hook/sitecustomize.py 全部 write/rename/remove/mkdir 调用目标",
     "静态审读项,机械闸不判"),
    ("AC-2.3", "hook_dir 落在 TOPAZ_INSTALL_DIR 内时装配整体拒绝并产生结构化回退", "G-TEST-RS", None),

    ("AC-3.1", "目标模块导入抛异常时目标模块仍可导入且进程不中断", "G-FAILSAFE", None),
    ("AC-3.2", "契约校验抛异常时目标模块仍可导入且进程不中断", "G-FAILSAFE", None),
    ("AC-3.3", "setattr 第 N 步(N>1)抛异常时不留部分生效:全批不生效或全部回滚", "G-FAILSAFE",
     "v6 收口语义:进程可用严格优先于行为等同未注入"),
    ("AC-3.4", "审计写入抛异常时目标模块仍可导入且进程不中断", "G-FAILSAFE", None),
    ("AC-3.5", "失败时审计写入 error 行,并记录已回滚或已生效的属性子集", "G-PY-UNIT", None),
    ("AC-3.6", "失败原因以固定前缀写入 stderr,同一次运行内前缀稳定", "G-FAILSAFE", None),
    ("AC-3.7", "hook 载荷在 Python 3.11 下可编译通过(py_compile 无错误)", "G-PY-COMPILE",
     "sitecustomize 语法错误会让目标进程中 site.execsitecustomize 失败,属真实启动风险,不是构建洁癖"),

    ("AC-4.1", "注入成功时审计 JSONL 出现 event=apply 行", "G-PY-UNIT",
     "hook 侧可独立验证,不依赖真实 Topaz"),
    ("AC-4.2", "apply 行内每个属性的 before/after/source 与实际生效值一致", "G-PY-UNIT",
     "R04-F4(a) 的直接对应项:after 记成旧值必须变红"),
    ("AC-4.3", "真实 Topaz SLP 渲染进程中 apply 行出现且生效参数与请求参数逐项一致",
     "M-TOPAZ-INJECT", None),

    ("AC-5.1", "审计每行含 timestamp_utc / pid / launch_id / event / changes 五个字段", "G-PY-UNIT", None),
    ("AC-5.2", "进程启动即写 header 行", "G-PY-UNIT", None),
    ("AC-5.3", "失败时写入 event=error 行", "G-PY-UNIT", None),

    ("AC-6.1", "夹具日志解析出阶段 VAE Encode / DiT Upscale / VAE Decode", "G-TEST-RS", None),
    ("AC-6.2", "夹具日志解析出分块序号与进度值", "G-TEST-RS", None),
    ("AC-6.3", "夹具日志解析出完成标记", "G-TEST-RS", None),
    ("AC-6.4", "未知行不 panic、不退出,计入 unknown 计数", "G-TEST-RS", None),
    ("AC-6.5", "末行被截断时不 panic、不退出,计入 unknown 计数", "G-TEST-RS", None),

    ("AC-7.1", "真实 SLP 渲染的 tzlog 被本解析器解析出阶段、进度、完成三项且均非空", "M-TOPAZ-LOG", None),
    ("AC-7.2", "原始夹具 SHA-256 记录在案且与文件一致", "M-TOPAZ-LOG", None),
    ("AC-7.3", "夹具来源(Topaz 版本号、获取方式、时间)记录在案", "M-TOPAZ-LOG", None),

    ("AC-8.1", "Topaz 1.7.0 目标模块名 models.slp25.m0vm5nn8kicb 经 LogParser 入口判为 Version170",
     "G-TEST-RS",
     "判别式:已知版本的精确匹配必须优先于命名空间契约匹配。R02-F1 即在此处:契约分支前移后本行必红"),
    ("AC-8.2", "Topaz 1.7.1 目标模块名 models.slp25.rx095brph7m1 经 LogParser 入口判为 Version171",
     "G-TEST-RS", None),
    ("AC-8.3", "未知版本搭配 models.slp25.future 经 LogParser 入口判为 ContractMatched",
     "G-TEST-RS", None),
    ("AC-8.4", "非 models.slp2 命名空间的模块名经 LogParser 入口判为 Unknown", "G-TEST-RS", None),

    ("AC-9.1", "控制命令、状态快照、结构化事件、结构化错误四类消息各有 TS 侧类型校验",
     "G-GUI-TEST", None),
    ("AC-9.2", "四类消息各有拒绝路径测试:缺必需字段、未知 kind、错误类型均被拒绝",
     "G-GUI-TEST", None),
    ("AC-9.3", "非法输入返回结构化错误对象,不抛异常、不静默通过", "G-GUI-TEST", None),
    ("AC-9.4", "GUI 源码不直接读日志文件或进程:child_process / readFile / readdir 零命中",
     "manual-procedure: rg -n 'child_process|readFile|readdir' gui/src 应零命中",
     "测绘型断言,机械闸不判"),

    ("AC-10.1", "注入不可用预检失败时以无注入方式启动目标程序并记录回退原因", "G-TEST-RS", None),
    ("AC-10.2", "hook 缺失预检失败时以无注入方式启动目标程序并记录回退原因", "G-TEST-RS", None),
    ("AC-10.3", "audit_file 不可写预检失败时以无注入方式启动目标程序并记录回退原因", "G-TEST-RS",
     "范围界定:指启动前预检,不指进程启动后运行时写失败(后者归 AC-3.4)"),
    ("AC-10.4", "audit_file 落在禁用位置(TOPAZ_INSTALL_DIR 内)预检失败时以无注入方式启动并记录回退原因",
     "G-TEST-RS", "R04-F1 的直接对应项:删 injection.rs 的禁用位置预检必须变红"),
    ("AC-10.5", "回退记录含判据(哪条预检触发),不是无原因的一行", "G-TEST-RS", None),
    ("AC-10.6", "调用方 overrides 中任何以 TOPAZ_SLP_ 开头的键与 PYTHONPATH 一律被拒绝", "G-TEST-RS",
     "v8 改为前缀规则:逐项枚举曾漏掉 TOPAZ_SLP_TARGET_MODULE_NAME 并产生静默降级"),
    ("AC-10.7", "被拒绝的 override 产生结构化回退,不得静默报 Injected", "G-TEST-RS", None),

    ("AC-11.1", "pocketjs 宿主能力结论为 direct / rust-adapter / windows-render-blocked 之一并落盘",
     "G-HOST-CAPABILITY", "该门 skip 即失败,故在 B01 完成前必然为红;这是刻意设计"),
    ("AC-11.2", "结论附可复现命令与输出,不得以推测代替", "G-HOST-CAPABILITY", None),
]

BLOCKED = {
    "AC-4.3": "项目所有者(需授权一次真实 SLP 短导出)",
    "AC-7.1": "项目所有者(需授权一次真实 SLP 渲染)",
    "AC-7.2": "项目所有者(需授权一次真实 SLP 渲染)",
    "AC-7.3": "项目所有者(需授权一次真实 SLP 渲染)",
    "AC-11.1": "项目所有者(需提供 <SHARED_LEARN_ROOT> 只读映射)",
    "AC-11.2": "项目所有者(需提供 <SHARED_LEARN_ROOT> 只读映射)",
}


def q(s):
    """YAML double-quoted scalar, JSON-compatible."""
    return json.dumps(s, ensure_ascii=False)


def main():
    src = io.open("packet-v9.md", encoding="utf-8").read()

    lines = ["acceptance:"]
    for i, (aid, crit, ver, note) in enumerate(AC):
        if i == 0:
            lines.append("  # v10: 每条 AC = 一条可观察行为 + 一条 verification。粒度依据 templates/packet.md:63-64")
            lines.append("  # (criterion 与 verification 均为单数)。clause -> symbol -> check 的映射由 Review 产出,不入本条。")
        lines.append("  - id: %s" % aid)
        lines.append("    criterion: %s" % q(crit))
        lines.append("    verification: %s" % (q(ver) if ':' in ver else ver))
        if aid in BLOCKED:
            lines.append("    state: blocked")
            lines.append("    blocked_owner: %s" % q(BLOCKED[aid]))
        else:
            lines.append("    state: verifiable")
        if note:
            lines.append("    note: %s" % q(note))
    acc_block = "\n".join(lines)

    head, rest = src.split("\nacceptance:\n", 1)
    tail = "\ntoolchain:" + rest.split("\ntoolchain:", 1)[1]

    before_deliv, after_deliv = tail.split("\ndeliverables:\n", 1)
    tail = before_deliv + "\noutputs:" + after_deliv.split("\noutputs:", 1)[1]

    new = head + "\n" + acc_block + tail

    subs = [
        ("# Task Packet — stage1-gui-backend v9", "# Task Packet — stage1-gui-backend v10"),
        ("packet_version: 9\n", "packet_version: 10\n"),
        ("supersedes: 8\n", "supersedes: 9\n"),
        ('published_at: "2026-10-18"', 'published_at: "2026-10-21"'),
    ]
    for a, b in subs:
        assert src.count(a) == 1 or a.startswith("packet_version") or a.startswith("supersedes"), a
        new = new.replace(a, b, 1)

    anchor = 'published_by: "A002[PiDeck]Main Coordinator (session A002-session-01)"\n'
    assert new.count(anchor) == 1
    new = new.replace(anchor, anchor + (
        "change_log:\n"
        "  - date: \"2026-10-21\"\n"
        "    change: \"acceptance 由 11 条多分句 AC 拆为 46 条原子 AC(AC-1.1..AC-11.2(46 条));删除 deliverables.ac_coverage_table;AC-4 拆出可跑半边(4.1/4.2 归 G-PY-UNIT,只有 4.3 端到端为 blocked)\"\n"
        "    reason: \"templates/packet.md:63-64 规定 criterion 与 verification 均为单数;11 条 AC 细读约 40 余个可观察分句而覆盖表只有 11 行,导致每轮只撞到 2-3 个分句(R03-F2 与 R04-F1 同落 AC-10 即为例证)\"\n"
        "    sensitive_field: acceptance\n"
        "    approved_by: \"项目所有者 (project owner)\"\n"
        "    approved_at: \"2026-10-21\"\n"
    ), 1)

    old_note = "> v6 取代 v5。"
    assert new.count(old_note) == 1
    new = new.replace(old_note,
        "> v10 取代 v9:acceptance 由 11 条多分句 AC 拆为 46 条原子 AC;删除 A002 自创的 AC 覆盖表要求"
        "(acceptance 是敏感字段,改动经所有者 2026-10-21 批准,见 change_log)。\n>\n> v6 取代 v5。", 1)

    io.open("packet-v10.md", "w", encoding="utf-8", newline="\n").write(new)
    print("written bytes:", len(new.encode("utf-8")))
    print("AC rows:", len(AC), "blocked:", len(BLOCKED))
    return 0


if __name__ == "__main__":
    sys.exit(main())
