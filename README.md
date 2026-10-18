# Starlight_ssGui

Topaz Video 星光(SLP 2.5 / 2.6)模型的**参数调优注入 + 渲染日志监控**桌面工具。
技术栈:Rust + pocketjs(TS 界面 + QuickJS + Rust core)。仅面向 Windows x64。

## 当前状态

**Stage 0:初始化** —— 仅存在文档体系与参考快照,无应用源码与工具链。
见 [docs/STATUS.md](docs/STATUS.md)。

## 目录

| 路径 | 内容 |
| --- | --- |
| `AGENTS.md` | AI 工程规则入口(边界、授权、验证纪律) |
| `docs/` | 文档体系:入口 `docs/START_HERE.md`、索引与各领域规则 |
| `learn/` | 项目特化参考资料(只读):开源快照 + 闭源工具分析产物 |

## 快速入口

- 接手阅读顺序:[docs/START_HERE.md](docs/START_HERE.md)
- 产品范围:[docs/product/AGENTS.md](docs/product/AGENTS.md)
- 工程与验证:[docs/engineering/AGENTS.md](docs/engineering/AGENTS.md)

## 参考与合规

`learn/` 为只读研究材料:开源快照保持上游原样;闭源工具(二进制)的分析产物仅供学习,
不整体搬运代码、不重新发布反编译产物。详见 [learn/README.md](learn/README.md)。

## 语言

项目文档使用中文(简体);代码、命令、路径保持原文。
