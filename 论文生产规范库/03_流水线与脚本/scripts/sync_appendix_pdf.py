# -*- coding: utf-8 -*-
"""把磁盘上的最新 solver.py / run_all.py 同步进 论文_定稿版_pdf.md 的附录代码块。
（PDF 由 _pdf.md 直接编译，export_pdf.sh 会先 prep 再覆盖，所以此处只改 _pdf.md，
  单独跑 build_pdf.sh 即可生效，不触发 prep 覆盖。）"""
import io

BASE = r"D:\WorkBuddy_output\数模并行工作流\sim"
MD = BASE + r"\论文_定稿版_pdf.md"

def replace_block(text, fname, start_marker, end_marker):
    code = open(BASE + "\\" + fname, encoding="utf-8").read()
    s = text.find(start_marker)
    e = text.find(end_marker, s + len(start_marker))
    if s == -1 or e == -1:
        raise RuntimeError("找不到 %s 的代码块边界 (s=%d e=%d)" % (fname, s, e))
    new = text[:s + len(start_marker)] + code + text[e:]
    return new, (e - (s + len(start_marker)))

# 主 md(定稿版.md) 与 PDF 用 md(_pdf.md) 都同步，保证 PDF / Word 附录一致
TARGETS = [r"\论文_定稿版.md", r"\论文_定稿版_pdf.md"]
for rel in TARGETS:
    md = BASE + rel
    text = open(md, encoding="utf-8").read()
    text, n1 = replace_block(text, "solver.py",
        "**solver.py**\n\n```python\n", "\n```\n\n**run_all.py**")
    text, n2 = replace_block(text, "run_all.py",
        "**run_all.py**\n\n```python\n", "\n```\n\n### 8.3 AI 工具使用详情")
    open(md, "w", encoding="utf-8").write(text)
    print("✅ %s  solver.py %d 字符 / run_all.py %d 字符 已同步" % (rel, n1, n2))
