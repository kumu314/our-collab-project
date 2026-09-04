# -*- coding: utf-8 -*-
"""生成 docx 友好变体（论文_定稿版_docx.md）。

关键教训（不要再犯）：
    pandoc 的 -t docx **不保留 raw_tex**。任何 \\begin{center}...\\end{center}、
    \\qquad 之类的 LaTeX 片段在 docx 输出时会被整段丢弃，导致表题/图题内容消失。
    因此本脚本只做「markdown -> markdown」的安全改写，居中一律交给
    fix_docx_alignment.py 在生成的 docx 上后处理。

本脚本做的事：
1. 表题 \\begin{center}表X-X ...\\end{center} -> 纯文本行，并把完整文本写入
   docx_center_list.txt，供后处理精确居中（避免误伤以「图4-1」开头的正文句）；
2. 图片 ![图X-X 题注](path) **保持原样**，交给 pandoc 生成 Image Caption 段
   （实测 pandoc 3.10 对已含「图X-X」的 alt 不会再叠 "Figure N:" 前缀）；
3. 清掉 docx 不支持的 \\tag{N}。
"""
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "论文_定稿版.md")
DST = os.path.join(HERE, "论文_定稿版_docx.md")
LIST = os.path.join(HERE, "docx_center_list.txt")

with io.open(SRC, encoding="utf-8") as f:
    t = f.read()

center_list = []


def _table_caption(m):
    """\\begin{center}表X-X 标题\\end{center} -> 纯文本行（居中由后处理完成）。"""
    cap = m.group(1).strip()
    center_list.append(cap)
    return cap


# 表题：去掉 LaTeX 环境，只留纯文本
t = re.sub(
    r"\\begin\{center\}(表\d+-\d+[^\n]*?)\\end\{center\}",
    _table_caption,
    t,
    flags=re.DOTALL,
)

# 兜底：任何残留的 \begin{center}...\end{center} 都拆成纯文本
def _any_center(m):
    cap = " ".join(m.group(1).split())
    if cap:
        center_list.append(cap)
        return cap
    return ""


t = re.sub(r"\\begin\{center\}(.*?)\\end\{center\}", _any_center, t, flags=re.DOTALL)

# 图片题注：保持 ![图X-X ...](path) 原样，让 pandoc 生成 Image Caption 段。
# 同时把题注文本也登记进居中清单（后处理按「完全相等」匹配，不会误伤正文）。
for m in re.finditer(r"!\[(图\d+-\d+[^\]]*)\]\(([^)]+)\)", t):
    center_list.append(m.group(1).strip())

# \tag{N} 在 docx(OMML) 不被支持，转成 \qquad\text{(N)}
t = re.sub(r"\\tag\{(\d+)\}", r"\\qquad\\text{(\1)}", t)

with io.open(DST, "w", encoding="utf-8") as f:
    f.write(t)

with io.open(LIST, "w", encoding="utf-8") as f:
    for item in dict.fromkeys(center_list):
        f.write(item + "\n")

print("✅ docx 变体已生成：%s" % os.path.basename(DST))
print("   居中清单 %d 条 -> %s" % (len(center_list), os.path.basename(LIST)))
for item in center_list:
    print("   ·", item)
