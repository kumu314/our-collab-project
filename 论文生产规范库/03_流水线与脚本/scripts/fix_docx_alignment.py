# -*- coding: utf-8 -*-
"""Word 论文后处理：图片、图题注、表题注统一居中。

设计要点
--------
pandoc -t docx 会把 ![题注](path) 渲染成两段：
    [Captioned Figure]  -> 含 <w:drawing> 的段落（图本体）
    [Image Caption]     -> 题注文字段落
两者默认都不带 w:jc，Word 里表现为左对齐。

表题在 markdown 里是独立文本行，pandoc 输出成普通段落，也不居中。
配合 make_docx.py 生成的 docx_center_list.txt，按「文本完全相等」精确命中，
避免误伤「图4-1 中实线为……」这类以图号开头的正文句。
"""
import io
import os
import sys

from docx import Document
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

CAPTION_STYLES = {"Image Caption", "Captioned Figure"}


def _center(p):
    pPr = p._element.get_or_add_pPr()
    jc = pPr.find(qn("w:jc"))
    if jc is None:
        jc = OxmlElement("w:jc")
        pPr.append(jc)
    jc.set(qn("w:val"), "center")


def main(docx_path):
    here = os.path.dirname(os.path.abspath(__file__))
    list_path = os.path.join(here, "docx_center_list.txt")
    exact = set()
    if os.path.exists(list_path):
        with io.open(list_path, encoding="utf-8") as f:
            exact = {line.strip() for line in f if line.strip()}

    d = Document(docx_path)

    n_img = n_cap = n_list = n_prefix = 0
    for p in d.paragraphs:
        txt = p.text.strip()
        style = p.style.name if p.style is not None else ""

        # 1) 图本体：含 <w:drawing> 的段落
        if p._element.findall(".//" + qn("w:drawing")):
            _center(p)
            n_img += 1
            continue

        # 2) pandoc 生成的题注样式
        if style in CAPTION_STYLES:
            # 万一 pandoc 版本叠了英文前缀，去掉
            if txt.startswith("Figure "):
                for r in p.runs:
                    if "Figure " in r.text:
                        r.text = r.text.replace("Figure ", "", 1)
                        n_prefix += 1
                        break
                txt = p.text.strip()
            _center(p)
            n_cap += 1
            continue

        # 3) 清单精确匹配（表题 + 保底图题）
        if txt in exact:
            _center(p)
            n_list += 1

    d.save(docx_path)
    print("图片段居中 =", n_img)
    print("题注样式段居中 =", n_cap)
    print("清单精确匹配居中 =", n_list)
    if n_prefix:
        print("移除 Figure 前缀 =", n_prefix)
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "论文_定稿版_new.docx"
    )
    sys.exit(main(target))
