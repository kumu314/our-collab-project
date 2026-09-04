#!/usr/bin/env bash
# 一键重出 Word 版论文：docx 变体 → pandoc 转 docx → 居中后处理 → 代码附录
# 默认产物：论文_定稿版.docx；如被 Word 占用则写到 _论文_定稿版_新.docx
set -e
cd "$(dirname "$0")"

PY="D:/WorkBuddyData/.workbuddy/binaries/python/envs/default/Scripts/python.exe"
PANDOC="pandoc"

echo "==> 1/6 生成 docx 变体 markdown"
$PY make_docx.py

echo "==> 2/6 决定输出文件名（若 docx 正被 Word 占用，落到新文件名）"
DOCX_OUT="论文_定稿版.docx"
if $PY -c "import sys; open('论文_定稿版.docx','ab').close()" 2>/dev/null; then
  : # 可写
else
  DOCX_OUT="_论文_定稿版_新.docx"
fi
echo "目标 docx: $DOCX_OUT"

echo "==> 3/6 pandoc 转 docx"
# 注意：-t docx 不保留 raw_tex，所以源里不能残留 \begin{center} 之类，
# 居中一律由第 4 步在 docx 上后处理完成（见 make_docx.py 顶部说明）。
$PANDOC "论文_定稿版_docx.md" -o "$DOCX_OUT" \
    -f "markdown" \
    -t "docx" \
    --resource-path ".:data" \
    --syntax-highlighting="tango" \
    -M fontsize=12pt

echo "==> 4/6 居中后处理（图本体 / Image Caption / 表题清单精确匹配）"
$PY fix_docx_alignment.py "$DOCX_OUT"

echo "==> 5/6 关键词后插入分页符（摘要 + 关键词独占一页）"
$PY fix_docx_pagebreak.py "$DOCX_OUT"

echo "==> 6/6 重出代码附录 docx（独立文件）"
$PY make_code_appendix_docx.py

ls -la "$DOCX_OUT" "附录_全部Python代码.docx"
echo "DOCX_DONE"
