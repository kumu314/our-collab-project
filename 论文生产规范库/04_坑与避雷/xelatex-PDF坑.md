# xelatex / PDF 导出的 4 个致命坑

> 链路：`论文_定稿版.md` → `prep_pdf_md.py` → `论文_定稿版_pdf.md` → pandoc + xelatex → PDF
> 用户级 skill 副本：`~/.workbuddy/skills/math-paper-md2pdf/SKILL.md`

---

## 环境准备：MiKTeX 安装（不要用 winget）

**winget 会把 basic installer 拉成交互模式**，不真正静默，进程空转 20+ 分钟零写入。

正确做法 —— 手动下载 + 静默装到非系统盘：
```bash
curl -L -o D:/MiKTeX/installer.exe \
  https://miktex.org/download/ctan/systems/win32/miktex/setup/windows-x64/basic-miktex-25.12-x64.exe

"D:/MiKTeX/installer.exe" --unattended --portable=D:/MiKTeX --auto-install=yes --paper-size=a4
```

- 该安装器**只认 `--unattended`**；`--silent` / `--no-launch` 会报 `unrecognized option`
- 装完 xelatex 在 portable 布局：**`D:/MiKTeX/texmfs/install/miktex/bin/x64/xelatex.exe`**
  （注意不在 `miktex/bin` 顶层）

---

## 坑 1（致命）：PATH 里的"文件型"条目让 MiKTeX 崩溃

**报错**：`MiKTeX cannot retrieve attributes for the directory 'D:\Mysoftware\python.exe\'`

**根因**：PATH 里有 `D:\Mysoftware\python.exe` 这种**把文件当目录**加进 PATH 的错误条目，
MiKTeX 启动时扫描 PATH 会 stat 它当目录 → 直接崩。

**修法**：出 PDF 前在 shell 里清理 PATH：
```bash
CLEAN=""; IFS=':' read -ra P <<< "$PATH"
for p in "${P[@]}"; do
  b=$(basename "$p")
  case "$b" in python.exe|python3.exe) continue;; esac
  CLEAN="${CLEAN:+$CLEAN:}$p"
done
export PATH="$CLEAN"
```
（`build_pdf.sh` 已内置这段）

---

## 坑 2（字形）：中文 / 希腊字母被丢字

pandoc 默认模板用 latinmodern 字体族，三类字符会 `Missing character`：

| 位置 | 问题 | 修法 |
|------|------|------|
| 公式内中文（元/辆/度/单/位） | 数学字体无汉字 | 连续中文 → 包 `\text{...}`（走 SimSun） |
| 正文裸希腊字母（α/β） | 西文正文字体无希腊 | 包 `$...$`（走数学字体） |
| 代码块希腊字母（ω/ε） | lmmono 无希腊 | pandoc 加 `-V monofont="Microsoft YaHei"` |

> **不要用纯希腊等宽字体**做 monofont —— 会丢代码块里的中文。
> 用 Microsoft YaHei：中 + 希 + 拉丁全覆盖。

pandoc 完整字体参数：
```
-V CJKmainfont="SimSun" -V monofont="Microsoft YaHei" -V papersize=a4 -V fontsize=12pt
```

**验收**：构建日志里 `Missing character` 必须是 **0**。

---

## 坑 3（致命）：`$$` 定界符被塌缩 → `\tag` 报错

**报错**：`! Missing $ inserted`

**根因**：预处理脚本搬运公式时，把 `$$...$$` 的定界符只取首尾单字符还原成 `$...$`，
`\tag{N}` 落到**行内数学**（非法）。

**修法**：还原数学段时**按原定界符长度保留** `$$`（显示）或 `$`（行内）。
`prep_pdf_md.py` 的 `stash_math` 已正确处理。

> **另注**：Word 路径**根本不支持 `\tag{}`**（OMML 不认），
> 转 docx 前必须先 `\tag{N}` → `\qquad\text{(N)}`（`make_docx.py` 已处理）。

---

## 坑 4（致命）：Git Bash 下 `-output-directory` 路径被重映射

**现象**：`-output-directory=/d/...`（POSIX 写法）被 xelatex 重映射成 `D:/d/WorkBuddy_output/...`，
PDF 落到错误路径；即便用 cwd 写法也会写去 `D:/d/...`。

**可靠修法**：用 **Python 子进程**调用 xelatex，
`os.chdir` 到**真实 Windows 路径（反斜杠 `D:\...`）**，
**不传 `-output-directory`**，xelatex 即正确写入当前目录。

---

## build_pdf.sh 关键内容

```bash
XELATEX="D:/MiKTeX/texmfs/install/miktex/bin/x64/xelatex.exe"

# 清 PATH（坑 1）
CLEAN=""; ...; export PATH="$CLEAN"

# 镜像拉包（国内快；沙箱里可省略，联网会卡死 12 分钟）
"$XELATEX/bin/mpm.exe" --set-repository="https://mirrors.hust.edu.cn/..." || true
"$XELATEX/bin/initexmf.exe" --update-fndb || true

# 编译
pandoc "论文_定稿版_pdf.md" -o "论文_定稿版.pdf" \
  --pdf-engine="$XELATEX" -V CJKmainfont="SimSun" -V monofont="Microsoft YaHei" \
  --syntax-highlighting=idiomatic -H latex_header.tex
```

> ⚠️ `--listings` 已废弃，会报
> `Deprecated: --listings. Use --syntax-highlighting=idiomatic instead.`
> 同理 `--highlight-style` → `--syntax-highlighting`。

---

## 验收清单

- [ ] MiKTeX 用 `--unattended --portable=非系统盘`，不用 winget
- [ ] 出 PDF 前清掉 PATH 里的 python.exe 文件型条目
- [ ] 预处理 md 后再出（公式内中文→`\text{}`，正文希腊→`$...$`，monofont=YaHei）
- [ ] `$$` 定界符在预处理中没被塌缩
- [ ] 日志 **0 个 Missing character**、出现 `PDF_DONE`、PDF 含 `%%EOF` 且能打开
- [ ] 页数实测（不是估）
