# learn/analysis —— 闭源工具分析产物(只读研究材料)

来源:两个**闭源免费**工具(仅发布二进制),经 PyInstaller 解包 + 字节码转储获得。
用途:为 Starlight_ssGui 的「调参注入 + 日志监控」提供实现级参考。
获取/分析日期:2026-10-17。分析方法与全部结论见 `docs/research/references/` 的两份报告。

> ⚠ 合规边界:仅供本项目内部学习参考;**不整体搬运其代码、不重新发布其反编译产物**;对外引用时注明来源与版本。

## 原始二进制(被分析对象,不存放于本目录)

| 工具 | 版本 | 原始 exe SHA-256 |
| --- | --- | --- |
| skv89/Topaz-SLP-Launcher(portable, onefile) | v1.2.0 | `8edc0728ee2ee3e621211945b859a30cec35ff7d0c50d35ec32d98642dcea5a7` |
| naxci1/SLP-Launcher-Lite(onedir) | v1.7.4 | `8dfca1a5c3f714e63c0002253f2d673dc1ca413adeda8cacd1786037686167a6` |

## 目录内容

### `closed-tools/` —— 作者随包发布的**明文** hook(未加密 Python,取自各自数据目录)

| 文件 | 来源路径(工具数据目录内) | SHA-256 |
| --- | --- | --- |
| `skv89-Topaz-SLP-Launcher-v1.2.0/sitecustomize.py` | `Topaz-SLP-Launcher-Data\slp_high_vram_override\` | `b6a0aa977152965188428b12dd97dff431c34cb64c0eef322e7a4d18205f3e8c` |
| `naxci1-SLP-Launcher-Lite-v1.7.4/sitecustomize-slp_override.py` | `SLP_Lite_Data\slp_override\` | `ed1da36b66006dcde157af83935ed2da7a1df887084ad6bc8eb53b060db6eba5` |
| `naxci1-SLP-Launcher-Lite-v1.7.4/sitecustomize-slp_high_vram_override.py` | `SLP_Lite_Data\slp_high_vram_override\` | `c323a73712f4717297b20110a7ef8ac928852e7a6f27341b705d6847524ec668` |

### `extracted-key/` —— 应用逻辑字节码(绑定特定 Python 版本,供转储/检索)

| 内容 | 版本绑定 | 说明 |
| --- | --- | --- |
| `skv89-slp_launcher-pycs/` | Python 3.11 | 主程序 `slp_launcher` 包(约 120 模块:monitor / autotune* / cudnn_control / fusion_* / settings_* 等) |
| `skv89-slp_high_vram_override-pycs/` | Python 3.11 | 注入 hook(编译版)+ `slp_accel/`(Fusion 加速模块) |
| `naxci1-slp_lite.pyc` (337,678 B) | Python 3.13 | **单文件应用**(195 函数:parse_log / version_profile / build_env / install_hook_into_neuroserver …) |

`naxci1-slp_lite.pyc` SHA-256:`7e0a27e969ec5dae1464171f7ff7b3e1a6add1a360003fa5c87e3e8bd185fd86`

### `pyc-dumps/` —— 字符串 / 函数名 / 全局名转储

16 个模块的 `*.strings.txt` / `*.funcs.txt` / `*.names.txt`,可直接全局检索(如日志正则、环境变量名、URL)。

### `tools/` —— 复现工具

| 文件 | 说明 |
| --- | --- |
| `pyinstxtractor.py` | PyInstaller 解包器 v2.0(第三方) |
| `dump_pyc.py` | 自研 pyc 转储器(须用与 pyc 匹配的 Python 版本运行) |
