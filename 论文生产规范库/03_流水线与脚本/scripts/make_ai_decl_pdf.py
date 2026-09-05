#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
生成《AI 工具使用详情》PDF（reportlab + 内置 STSong-Light 中文字体）。

- 单页 A4，可打印签字。
- 人工填 / 手写字段渲染为干净填空线，不写任何禁用词（占位/流程演练/示例/草稿）。
- 运行：python make_ai_decl_pdf.py
  可选参数：python make_ai_decl_pdf.py 输出路径.pdf
  默认在当前目录生成 AI工具使用详情.pdf

字体走 reportlab 内置 CID 字体 STSong-Light，无需外部字体文件。
"""

import os
import sys

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
from reportlab.pdfgen import canvas

FONT = "STSong-Light"


def build_pdf(out_path):
    pdfmetrics.registerFont(UnicodeCIDFont(FONT))

    c = canvas.Canvas(out_path, pagesize=A4)
    w, h = A4

    # 边距
    left = 20 * mm
    right = 20 * mm
    top = 18 * mm
    usable_w = w - left - right

    # 标题
    c.setFont(FONT, 18)
    c.setFillColorRGB(0, 0, 0)
    title = "《AI 工具使用详情》"
    c.drawCentredString(w / 2.0, h - top, title)

    # 副标题说明（合规声明来源，非禁用词）
    c.setFont(FONT, 9)
    sub = "依据《全国大学生数学建模竞赛人工智能工具使用规定》如实填报"
    c.drawCentredString(w / 2.0, h - top - 8 * mm, sub)

    # 表头横线
    y = h - top - 16 * mm

    def field_line(label, value):
        nonlocal y
        c.setFont(FONT, 11)
        c.setFillColorRGB(0, 0, 0)
        # 标签
        c.drawString(left, y, label)
        # 值（填空线或文字）
        c.setFont(FONT, 11)
        c.drawString(left + 40 * mm, y, value)
        # 行底线
        c.setStrokeColorRGB(0.4, 0.4, 0.4)
        c.setLineWidth(0.5)
        c.line(left, y - 3 * mm, left + usable_w, y - 3 * mm)
        y -= 13 * mm

    # 人工填 / 手写字段：干净填空线
    field_line("参赛队号：", "________________________")
    field_line("队员姓名：", "________________________   （全体队员）")
    field_line("队员签名：", "________________________   （手写）")
    field_line("指导教师签名：", "________________________   （手写）")

    # 事实字段（预填模板值）
    field_line("工具名称：", "WorkBuddy")
    field_line("版本：", "2026.09")
    field_line("开发机构：", "Tencent")
    field_line("使用环节：", "建模思路、程序实现、文字组织")

    # 独立性声明（多行文本块）
    y -= 2 * mm
    c.setFont(FONT, 11)
    c.drawString(left, y, "独立性声明：")
    y -= 7 * mm
    decl = "全部数值结果由本队程序独立运行产生，已人工复核。"
    c.setFont(FONT, 10.5)
    # 简单按字符宽度折行
    line_chars = 42
    lines = [decl[i:i + line_chars] for i in range(0, len(decl), line_chars)]
    for ln in lines:
        c.drawString(left + 6 * mm, y, ln)
        y -= 6.5 * mm

    # 页脚提示（可打印签字）
    c.setFont(FONT, 8.5)
    c.setFillColorRGB(0.3, 0.3, 0.3)
    c.drawString(left, 14 * mm, "本表随支撑材料一并提交，签名处须本人手写。")

    c.showPage()
    c.save()


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "AI工具使用详情.pdf"
    out = os.path.abspath(out)
    build_pdf(out)
    print("已生成:", out)


if __name__ == "__main__":
    main()
