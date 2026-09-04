#!/usr/bin/env bash
# 用 MiKTeX(xelatex) 把 论文_定稿版.md 出成 PDF（中文 + 公式原生渲染）
set -e

# 清理 PATH 中“文件型”错误条目（如 D:\Mysoftware\python.exe）
# MiKTeX 启动会扫描 PATH 并把每个条目当目录 stat，文件型条目会直接让它崩溃
CLEAN_PATH=""
IFS=':' read -ra PARTS <<< "$PATH"
for p in "${PARTS[@]}"; do
  b=$(basename "$p" 2>/dev/null)
  case "$b" in
    python.exe|python3.exe) continue ;;
  esac
  if [ -z "$CLEAN_PATH" ]; then CLEAN_PATH="$p"; else CLEAN_PATH="$CLEAN_PATH:$p"; fi
done
export PATH="$CLEAN_PATH"

OUT="D:/WorkBuddy_output/数模并行工作流/sim"
BIN="D:/MiKTeX/texmfs/install/miktex/bin/x64"
XELATEX="$BIN/xelatex.exe"
cd "$OUT" || { echo "无法进入 $OUT"; exit 1; }
[ -f "$XELATEX" ] || { echo "xelatex 未找到，MiKTeX 安装可能未完成"; exit 1; }

# 1) caption / listings 等宏包本地已安装，跳过联网拉包（沙箱里 mpm 联网会卡死）
#    仅本地刷新文件名数据库（不联网）
"$BIN/initexmf.exe" --update-fndb || true

# 2) pandoc 走 xelatex；CJKmainfont=SimSun 触发模板里 xeCJK 自动启用
pandoc "论文_定稿版_pdf.md" -o "论文_定稿版.pdf" \
  --pdf-engine="$XELATEX" \
  -H "latex_header.tex" \
  --syntax-highlighting=idiomatic \
  -V CJKmainfont="SimSun" \
  -V monofont="Microsoft YaHei" \
  -V papersize=a4 \
  -V fontsize=12pt

echo "PDF_DONE"
ls -la "论文_定稿版.pdf"
