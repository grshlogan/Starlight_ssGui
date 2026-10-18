# Starlight_ssGui · learn —— 项目特化参考资料库

本目录保存**仅本项目使用**的上游源码快照与逆向分析产物。
通用共享快照(如 pocketjs)位于共享 Learn 库 `<SHARED_LEARN_ROOT>`,不在此重复存放。

快照保持上游内容原样(不写入自定义文件);分析产物为只读研究证据。

## 一、上游源码快照

| 源码 | 快照 | 提交 | 提交日期 (UTC) | 归档大小 | 解压体积 / 文件数 | 许可证 |
| --- | --- | --- | --- | --- | --- | --- |
| LoveRain1997/TopazStarlightUI | `v5.9`(标签归档) | `3bcb73739c7daed731094143afbbf85ca36771da` | 2026-10-14T15:50:20Z | 47,034 B | 151K / 6 | **未声明**(仓库无 LICENSE 文件) |

- 拉取日期:2026-10-17(本地时间);归档经进程级代理下载,仓库元数据见 `.downloads/TopazStarlightUI-v5.9.repo-meta.json`。
- 来源 URL:`https://github.com/LoveRain1997/TopazStarlightUI/archive/refs/tags/v5.9.zip`
- 本地路径:`sources/github.com/LoveRain1997/TopazStarlightUI/v5.9`
- 归档 SHA-256:

```text
f6dcff98e0fde8233f61dd17c440644ab6d64621fd45c76f68a524af5fdc43c2  .downloads/TopazStarlightUI-v5.9.zip
```

- 选择理由:本主题域**唯一开源**的同机制实现(进程内 `sitecustomize` 注入 + neuroserver 调度 + 日志解析),与项目机制同源,可作行为与失败案例参考。
- 边界:许可证缺失(默认保留所有权利),**仅作行为参考,不复制其代码**;运行环境为 Python + tkinter,与本项目 Rust 栈不同。

## 二、闭源工具分析产物

见 [`analysis/README.md`](analysis/README.md):两个闭源免费工具的随包明文 hook、关键字节码与转储证据。
分析报告位于项目文档:`docs/research/references/`。

## 命名与获取约定(与共享 Learn 库一致)

- 正式发布(有标签):快照目录使用标签名,归档地址 `https://github.com/<owner>/<repo>/archive/refs/tags/<tag>.zip`。
- 非正式快照:目录使用提交短 SHA(7 位)。
- 需要新版本时新增快照目录,不覆盖已有目录;归档保留在 `.downloads/`。
- 不往上游源码树内添加自定义文件。
