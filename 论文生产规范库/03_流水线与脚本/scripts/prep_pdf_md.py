# -*- coding: utf-8 -*-
# 预处理：把 .md 转成 PDF 友好的变体（只生成 _pdf.md，不动定稿版）
# 1) 公式（$$...$$ / $...$）内的连续中文 → \text{...}（走 SimSun，避免数学字体缺汉字）
# 2) 正文（非公式、非代码块）中的希腊字母 → $...$（走数学字体，避免正文字体缺希腊字母）
import re

SRC = r"D:/WorkBuddy_output/数模并行工作流/sim/论文_定稿版.md"
OUT = r"D:/WorkBuddy_output/数模并行工作流/sim/论文_定稿版_pdf.md"

t = open(SRC, encoding="utf-8").read()

code_blocks, math_blocks = [], []

def stash_code(m):
    code_blocks.append(m.group(0))
    return "\x01C%d\x01" % (len(code_blocks) - 1)

def fix_cjk_in_math(seg):
    # 连续 CJK 统一包 \text{}；已含 \text{ 的不再重复
    return re.sub(r"([\u3400-\u9fff\uf900-\ufaff]+)", r"\\text{\1}", seg)

def stash_math(m):
    # m.group(0) 含定界符；内部 CJK 处理
    full = m.group(0)
    inner = m.group(1)
    if full.startswith("$$") and full.endswith("$$") and len(full) >= 4:
        restored = "$$" + fix_cjk_in_math(inner) + "$$"
    else:
        restored = "$" + fix_cjk_in_math(inner) + "$"
    math_blocks.append(restored)
    return "\x01M%d\x01" % (len(math_blocks) - 1)

# 1) 代码块先抽走（围栏 ```...```）
t = re.sub(r"```.*?```", stash_code, t, flags=re.S)
# 2) 显示公式 $$...$$（\$ 转义美元不当作定界符）
t = re.sub(r"(?<!\\)\$\$(.*?)\$\$", stash_math, t, flags=re.S)
# 3) 行内公式 $...$（\$ 转义美元不当作定界符；避免与 $$ 冲突）
t = re.sub(r"(?<!\\)(?<!\$)\$(?!\$)(.*?)\$", stash_math, t, flags=re.S)

# 4) 正文中希腊字母包 $...$
greek = "αβγδεζηθικλμνξοπρστυφχψωΑΒΓΔΕΖΗΘΙΚΛΜΝΞΟΠΡΣΤΥΦΧΨΩ"
t = re.sub("[" + greek + "]+", lambda m: "$" + m.group(0) + "$", t)

# 5) 还原
t = re.sub(r"\x01M(\d+)\x01", lambda m: math_blocks[int(m.group(1))], t)
t = re.sub(r"\x01C(\d+)\x01", lambda m: code_blocks[int(m.group(1))], t)

open(OUT, "w", encoding="utf-8").write(t)
print("OK ->", OUT, " math_segs=%d code_blocks=%d" % (len(math_blocks), len(code_blocks)))
