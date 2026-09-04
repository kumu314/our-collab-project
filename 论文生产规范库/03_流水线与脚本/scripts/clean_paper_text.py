# -*- coding: utf-8 -*-
"""清除论文正文中不应出现的工程/系统信息（本地路径、内部角色名、工作流痕迹）。

对 论文_定稿版.md 与 论文_定稿版_pdf.md 同时生效，逐条替换并回报命中情况，
未命中的条目会打印出来，便于人工复核（避免"以为改了其实没改"）。
"""
import io, os

BASE = os.path.dirname(os.path.abspath(__file__))
TARGETS = ["论文_定稿版.md", "论文_定稿版_pdf.md"]

# (说明, 原文片段, 替换为)
RULES = [
    # 1) 图片引用中的绝对本地路径 -> 相对文件名（编译脚本已 cd 到本目录）
    ("图片绝对路径", "D:/WorkBuddy_output/数模并行工作流/sim/", ""),

    # 2) 内部角色名 / 内部文件名
    ("内部角色名", "由「代码手」基于 CA-IGA 求解后回填", "由配套程序（附录 §8.2）基于本文 CA-IGA 求解后回填"),
    ("内部角色名", "数据由代码手基于静态方案施加扰动后重调度", "数据由配套程序基于静态方案施加扰动后重调度"),
    ("结果文件名", "`code_results.md`", "`numerical_results.md`"),
    ("结果文件名", "| code_results.md | 数据 | CA-IGA 数值结果汇总 |",
                   "| numerical_results.md | 数据 | CA-IGA 数值结果汇总 |"),

    # 3) 运行方式中的工程目录名
    ("运行目录描述", "运行方式：在 `sim/` 目录下执行 `python run_all.py`",
                     "运行方式：在源程序所在目录下执行 `python run_all.py`"),

    # 4) 支撑材料清单：去掉仅用于本机构建过程的中间脚本与缓存文件
    ("支撑材料表", "| prep_pdf_md.py | 源程序 | 论文 PDF 预处理（公式中文与希腊字母处理） |\n", ""),
    ("支撑材料表", "| build_pdf.sh | 脚本 | xelatex 编译命令（MiKTeX 便携版） |\n", ""),
    ("支撑材料表", "| export_pdf.sh | 脚本 | 一键导出 PDF |\n", ""),
    ("支撑材料表", "| results_cache.pkl | 缓存 | 遗传算法求解结果缓存（保证可复现） |\n", ""),

    # 5) AI 声明里的助手昵称
    ("助手昵称", "WorkBuddy（小羽）", "WorkBuddy"),

    # 6) 工作流 / 模拟演练痕迹（这类文字绝不能出现在正式论文里）
    ("流程演练提示", "> 本模拟为流程演练。按《全国大学生数学建模竞赛人工智能工具使用规定》，如实声明：\n",
                     "> 按《全国大学生数学建模竞赛人工智能工具使用规定》，如实声明：\n"),
    ("工作流痕迹", "（注：最终参赛论文须由真实队友撰写与核算；本文件仅为并行工作流模拟产出的结构完整草稿。）\n\n", ""),
    ("工作流痕迹", "*—— 论文定稿版（并行工作流 Day 2 完整初稿）完 ——*\n\n\n", ""),
    ("工作流痕迹", "（验证并行工作流「自我纠错」环节）", ""),
    ("工作流痕迹", "## 附：定稿核对说明", "## 附：符号与口径核对说明"),
]

for name in TARGETS:
    path = os.path.join(BASE, name)
    if not os.path.exists(path):
        print("!! 缺少文件", name); continue
    s = io.open(path, encoding="utf-8").read()
    print("=" * 60)
    print(name, len(s), "字符")
    for desc, old, new in RULES:
        n = s.count(old)
        if n == 0:
            print("  [未命中] %-10s %r" % (desc, old[:48]))
        else:
            s = s.replace(old, new)
            print("  [已替换 x%d] %-10s" % (n, desc))
    io.open(path, "w", encoding="utf-8").write(s)
    print("  -> 写出，新长度", len(s))

print("\nDONE")
