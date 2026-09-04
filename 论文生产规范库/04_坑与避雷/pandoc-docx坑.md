# pandoc md → docx 的 6 个隐性坑

> **适用场景**：同时出 PDF（LaTeX）和 Word（pandoc）双版本。
> **典型症状**：「PDF 看着对，Word 错」或「PDF 着色对，Word 全黑/没边框/题注没了」。
> 用户级 skill 副本：`~/.workbuddy/skills/pandoc-docx-pitfalls/SKILL.md`

---

## 坑 1：raw_tex 在 `-t docx` 路径**会被整体丢弃** ⭐ 最容易翻车

**现象**：md 里写 `\begin{center}表X-X ...\end{center}` 想居中，PDF（LaTeX）正常，
Word 里**整段消失**（表题注没了、图题注没渲染）。

**根因**：pandoc `-t docx` 不解析 raw_tex；`\begin / \end / \qquad / \text` 在 docx 输出时直接被丢弃。

**修法**：
- 表题：改成纯文本行 `表X-X ...`，居中靠 docx 后处理（坑 5）
- 图题注：**保持 `![图X-X 标题](path)` 原样**，让 pandoc 生成 `Image Caption` 样式段
  （实测 pandoc 3.10 对已含"图X-X"的 alt 不再叠 `Figure N:` 前缀）
- **不要**给 `-t docx` 加 `-f markdown+raw_tex` 试图让它"懂" LaTeX —— 照样丢弃

**自检**：python-docx 读回，搜"图X-X"/"表X-X"开头的段，命中数应等于论文图/表数。

> **真实事故**：2026-09-03 我为了修"Word 题注没居中"，把 `![cap](path)` 拆成
> `![](path)` + `\begin{center}cap\end{center}`，结果**题注整段消失**。
> 修了 A 引入 B，属于回退。教训：**改完必须读回验证，不能只信构建没报错。**

---

## 坑 2：pandoc 注入的 `\lstset` 会覆盖 header 的高亮配置

**现象**：LaTeX header 里写了多色 `lstset`，PDF 里代码**全黑**。

**根因**：pandoc 在 listings 环境下默认注入 `\lstset{defaultdialect=...}`，
执行顺序**在你的 header 之后** → 覆盖你的配置。

**修法**：用 `\AtBeginDocument{\lstset{...}}` 包裹，**晚于** pandoc 注入执行：

```latex
\usepackage{xcolor}
\definecolor{cKw}{HTML}{0000AA}    % 关键字 深蓝
\definecolor{cStr}{HTML}{B22222}   % 字符串 红
\definecolor{cCm}{HTML}{008000}    % 注释   绿
\definecolor{cNum}{HTML}{8A2BE2}   % 数字   紫
\definecolor{cFn}{HTML}{008B8B}    % 内置函数 青
\definecolor{cBg}{HTML}{F8F8F8}    % 背景   浅灰
\usepackage{listings}
\AtBeginDocument{%
\lstset{%
  frame=single, breaklines=true,
  basicstyle=\ttfamily\small\color{black},   % 必须显式 black
  keywordstyle=\color{cKw}\bfseries,
  stringstyle=\color{cStr},
  commentstyle=\color{cCm}\itshape,
  numberstyle=\color{cNum},
  identifierstyle=\color{black},
  emphstyle=\color{cFn},
  morekeywords={True,False,None},
  emph={print,len,range,min,max,sum,abs,sorted,enumerate,open,zip,...},
  literate={×}{$\times$}{1} {≤}{$\leq$}{1} {→}{$\rightarrow$}{1} {α}{$\alpha$}{1} ...%
}%
}
```

**关键点**：
- `basicstyle` 必须显式 `\color{black}`，否则非高亮段着色异常
- `literate` 必须加，否则源码里的 `→ Δ α β × ÷ ≤ ≥ ≈ ∈ ∑` 会让 xelatex 报错

---

## 坑 3：docx 文件锁（Windows 索引服务 / Office MRU）

**现象**：`shutil.copy2` / `os.replace` 覆盖 `论文.docx` 报
`WinError 32: 另一个程序正在使用此文件`。**即使 Word 当前打开的文档不是它**，锁依然存在。

**根因**：Windows Search Indexer 索引 docx、Office MRU 缓存、OneDrive 同步都会持锁。

**排查**：
```powershell
Get-Process winword -ErrorAction SilentlyContinue | Select-Object Id, MainWindowTitle
```
若 MainWindowTitle 不是目标文档 → 是 Office 后台服务在持锁。

**修法**：探测可写性，写到新文件名而不是覆盖：
```bash
DOCX_OUT="论文.docx"
if python -c "open('论文.docx','ab').close()" 2>/dev/null; then :; else
  DOCX_OUT="_论文_新.docx"
fi
```

**绝对禁止**：
- ❌ `rm` 目标文件（被 safe-delete 拦截，且会丢用户文件）
- ❌ `kill winword`（会丢用户其他未保存文档）
- ✅ 只等，或写新文件名 + 告知用户自己替换

---

## 坑 4：近乎等高柱的"对比"图视觉无效

**现象**：76832 vs 77367（差 0.7%），单张并列柱图肉眼几乎等高，评委判定"没做分析"。

**修法**：三幅子图
1. **(a) 绝对量级 + 截断纵轴** —— 纵轴自略低于最小值起，标注"纵轴自 X 起"，加 Δ 箭头
2. **(b) 相对变化率 %** —— 多指标 % 柱，红=升 / 蓝=降，附"原值→新值"
3. **(c) 结构对比** —— 并列柱（如燃油车 vs 新能源车），标题带占比 `11.11% → 14.29%`

参考实现 `scripts/fig_compare.py`，实测输出 77.9 KB，视觉对比明显。

---

## 坑 5：pandoc docx 默认把图/题注/表标题**左对齐**

**现象**：图片段默认 `w:jc=both` 或 left，题注同理。

**修法（必须 docx 后处理）**：
```python
def _center(p):
    pPr = p._element.get_or_add_pPr()
    jc = pPr.find(qn('w:jc'))
    if jc is None:
        jc = OxmlElement('w:jc'); pPr.append(jc)
    jc.set(qn('w:val'), 'center')

for p in d.paragraphs:
    if p._element.findall('.//' + qn('w:drawing')):
        _center(p)                              # 图本体
    elif p.style.name in {'Image Caption', 'Captioned Figure'}:
        _center(p)                              # pandoc 生成的题注
    elif p.text.strip() in exact_caption_set:   # 预先登记的表题清单
        _center(p)
```

**关键**：表题用**段落文本完全相等**精确匹配，
**不要**用 `text.startswith('图X-X')` —— 会误伤"图4-1 中实线为…"这种以图号开头的正文句，居中后很难看。

---

## 坑 6：代码附录 docx 的边框"变没了"

**现象**：只设了 `tbl.style = 'Table Grid'`，某次重出后边框消失。

**根因**：
1. `Table Grid` 样式在不同 Office 版本下边框定义不一致
2. 颜色默认 `auto` / 宽度默认 0.5pt，缩放时几乎不可见

**修法**：双保险 —— 既设 style，又显式设 tblBorders **和** tcBorders：
```python
tbl.style = 'Table Grid'
tblBorders = OxmlElement('w:tblBorders')
for edge in ('top','left','bottom','right','insideH','insideV'):
    b = OxmlElement(f'w:{edge}')
    b.set(qn('w:val'), 'single')
    b.set(qn('w:sz'), '12')          # 12 = 1.5pt ← 甜点值
    b.set(qn('w:space'), '0')
    b.set(qn('w:color'), '666666')   # 深灰，比黑色柔和比浅灰清晰
    tblBorders.append(b)
tbl._tbl.tblPr.append(tblBorders)
```

---

## 附：看不到 docx 渲染也能闭眼验收

```bash
# 1) LibreOffice headless 转 PDF
"C:/Program Files/LibreOffice/program/soffice.exe" --headless \
  --convert-to pdf --outdir _preview 论文.docx

# 2) pypdfium2 渲染关键页成 PNG
python -c "
import pypdfium2 as p
pdf = p.PdfDocument('_preview/论文.pdf')
print('页数', len(pdf))
pdf[15].render(scale=1.7).to_pil().save('p16.png')
"

# 3) 结构断言
python -c "
from docx import Document
d = Document('论文.docx')
print('Image Caption 段:', sum(1 for p in d.paragraphs if p.style.name=='Image Caption'))
print('表格数:', len(d.tables))
"
```
