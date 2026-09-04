# -*- coding: utf-8 -*-
"""把正文的项目符号列表（PDF/Word 中渲染成黑点 •）改成编号列表 1. 2. 3.

例外：假设条目本身已带 H1..H8 编号，再套一层"1. **H1**"会重复，
因此这一组改为「每条独立成段、去掉符号」，同样看不到黑点。
仅处理代码块之外的行。
"""
import io, os, re

BASE = os.path.dirname(os.path.abspath(__file__))
TARGETS = ["论文_定稿版.md", "论文_定稿版_pdf.md"]
H_ITEM = re.compile(r'^- \*\*H\d+\*\*')


def convert(text):
    lines = text.split("\n")
    out = []
    infence = False
    buf = []          # 当前收集到的一组 "- " 行

    def flush():
        if not buf:
            return
        if all(H_ITEM.match(l) for l in buf):
            # 假设条目：独立成段，段间空一行
            for l in buf:
                out.append(l[2:])
                out.append("")
        else:
            for k, l in enumerate(buf, 1):
                out.append("%d. %s" % (k, l[2:]))
        del buf[:]

    for l in lines:
        if l.startswith("```"):
            flush()
            infence = not infence
            out.append(l)
            continue
        if infence:
            out.append(l)
            continue
        if l.startswith("- "):
            buf.append(l)
            continue
        flush()
        out.append(l)
    flush()
    return "\n".join(out)


for name in TARGETS:
    p = os.path.join(BASE, name)
    s = io.open(p, encoding="utf-8").read()
    new = convert(s)
    n_before = len(re.findall(r'(?m)^- ', s))
    n_after = len(re.findall(r'(?m)^- ', new))
    n_num = len(re.findall(r'(?m)^\d+\. ', new))
    io.open(p, "w", encoding="utf-8").write(new)
    print("%s：原 %d 个 '- ' -> 现 %d 个 '- '，编号项 %d 个" % (name, n_before, n_after, n_num))

print("DONE")
