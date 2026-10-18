# 来源登记与出处 — Starlight_ssGui

## 目的

本目录登记**只读**的学习/参考来源。获得快照不等于获得代码复用许可;快照不证明运行期能力。快照实体存放在只读位置(`<PROJECT_ROOT>/learn/` 或共享 Learn 库),本文件是仓库内登记表。

## 布局与锁定

- 路径约定:`<learn_root>/sources/<host>/<owner>/<repo>/<tag-or-short-sha>/`;有正式标签用标签名,无标签用 7 位短 SHA。归档保留在 `.downloads/` 并登记 SHA-256。
- 每次修订建新快照目录,不覆盖旧目录;不向上游源码树添加项目文件、补丁、构建产物、凭据或会话数据。

## 来源登记表

| 来源 | 锁定基线 | 用途 | 状态 |
| --- | --- | --- | --- |
| LoveRain1997/TopazStarlightUI | `v5.9`(`3bcb73739c7daed731094143afbbf85ca36771da`) | 同机制开源实现:注入/调度/日志解析的行为与失败案例参考 | 已获取并登记(`learn/README.md`;许可证**未声明**) |
| skv89/Topaz-SLP-Launcher | `v1.2.0`(exe SHA-256 `8edc0728…`) | 闭源调参参考:参数校验/cuDNN/监控设计(经解包分析) | 已获取并分析(`learn/analysis/`) |
| naxci1/SLP-Launcher-Lite | `v1.7.4`(exe SHA-256 `8dfca1a5…`) | 闭源调参+监控参考:`.pth` 引导、双方言解析、审计(经解包分析) | 已获取并分析(`learn/analysis/`) |
| pocket-nexus/pocketjs | `v0.14.0`(`cba59337dbd89f69484c6dca50f63a093a8ff2ec`) | GUI 栈能力与 API 依据 | 共享 Learn 库只读快照(`<SHARED_LEARN_ROOT>`,MIT) |
| Topaz Labs 官方文档 / 社区帖 | 按访问日期引用(无快照) | SLP 模型与 Neuroserver 行为规格 | 外部来源,引用见 `research/references/` 报告 |

## 获取与验证记录

- 2026-10-17:TopazStarlightUI `v5.9` 标签归档经进程级代理下载(47,034 B,SHA-256 `f6dcff98…`);`python zipfile` 解压;仓库元数据(license=None)存 `.downloads/TopazStarlightUI-v5.9.repo-meta.json`。
- 2026-10-17:两个闭源工具 exe 经 PyInstaller 解包(`pyinstxtractor` v2.0)+ 字节码转储(自研 `dump_pyc.py`);产物哈希登记于 `learn/analysis/README.md`。
- 安全检查:归档来源为 GitHub 官方标签归档;解压未检出路径穿越/符号链接;逐文件 SHA-256 对照未执行(标签归档无官方逐文件清单)——标 `not verified`。

## 参考简报

外部参考简报与本登记配套,位于 [`references/`](references/AGENTS.md):简报记结论与适用边界,证据附录按来源逐条钉在版本/提交上。

## 延后与排除

- **延后**:闭源工具的完整解包树(仅存应用逻辑关键子集于 `learn/analysis/extracted-key/`);Topaz 官方文档快照(暂以链接引用,若链接失效再补快照)。
- **排除**:与范围无关的 ComfyUI 集成类项目、`morluto/rea` 等工具本身(仅作为方法被提及,不登记快照)。
