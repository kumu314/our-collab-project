# 代码附录 Word 规范

> 用户级 skill 副本：`~/.workbuddy/skills/code-appendix-word/SKILL.md`
> 本文件在该 skill 基础上，按 2026-09-03 用户反馈（"太挤""注释没用""边框没了"）做了修订。

---

## 一、结构：一个 .py 文件 = 一个 1×1 边框表格

```python
tbl = doc.add_table(rows=1, cols=1)
tbl.style = 'Table Grid'
cell = tbl.cell(0, 0)
# 每行代码 = cell.add_paragraph()
```

**为什么不是别的方式**：
- ❌ 每行一个 table row → 太挤，每行都有边框线
- ❌ 段落边框 `add_border()` → 只能加给单段落，多段落要逐一加，且跨页断掉

---

## 二、排版参数（2026-09-03 修订版）

| 项 | 原 skill | **修订后** | 修订原因 |
|---|---------|-----------|---------|
| 字号 | 7.5pt | **8.5pt** | 用户反馈"太挤" |
| 行距 | 1.15 | **1.5** | 同上，且 def/class 前插空段 spacer |
| 字体 | Consolas | Consolas | 不变 |
| 页边距 | 左右 1.8cm / 上下 1.2cm | 不变 | — |
| 边框宽度 | 未明确 | **sz=12（1.5pt）** | 用户反馈"边框没了"（0.75pt 太细看不出） |
| 边框颜色 | 默认 auto | **666666** | 深灰：比黑色柔和，比浅灰清晰 |

**留白做法**：
```python
p.paragraph_format.line_spacing = 1.5
# 在 def / class / @ 装饰器 前插入空段
```

---

## 三、配色方案（论文附录友好，打印机也能分辨）

```python
K = RGBColor(0, 0, 170)      # 关键词   深蓝
C = RGBColor(0, 128, 0)      # 注释     绿
S = RGBColor(178, 34, 34)    # 字符串   红
N = RGBColor(138, 43, 226)   # 数字     紫
D = RGBColor(0, 128, 128)    # 装饰器/内置函数 青
```

**tokenize 顺序**（顺序错了会互相吞）：
```
注释 > docstring > 字符串 > 装饰器 > 数字 > 标识符
```

---

## 四、注释清理规则 ⭐ 用户明确要求"没用的注释和特殊符号都不要"

### 删除（DROP_KEYWORDS）
教学、调试、解释、费曼、帮你理解、来源、作者、Author、code-hand、sub-agent、
并行工作流、Day 2、完整初稿、定稿示例、正式参赛、小羽、WorkBuddy、AI 工具、草稿…

### 删除（前缀匹配 DROP_PREFIX）
`# ---` `# ===` `# ___` `#***` `# 备忘` `# 自我纠错` `# 流程演练`

### 长度截断
- 单行注释 > 80 字 → 删
- docstring > 220 字 → 截断

### 特殊符号（正则删除）
```python
SPECIAL_PATTERN = re.compile(r'[★☆♥♦♣♠✗✓✘✚✦◆■▲△▼▽◯◎●]')
```

### 保留（这些是有价值的注释）
`为什么` `关键` `BUG:` `FIXME:` `TODO:` `兼容`

> **判断标准**：注释解释的是"**为什么这么做**"→ 保留；
> 注释解释的是"**这行代码在干什么**"→ 删（代码本身就是答案）。

---

## 五、全量不截断 ⭐ 曾踩严重坑

**事故**：脚本里 `[:250]` 截断，把 `solver.py` 中 `solve_problem`
（CA-IGA 主体，约 353 行起）**整个切掉** —— 附录里没有核心算法。

**规范**：
- **必须全量**，不设行数上限
- 验收：附录必须含核心算法函数名
  ```bash
  python -c "
  from docx import Document
  d = Document('附录_全部Python代码.docx')
  t = '\n'.join(p.text for tb in d.tables for r in tb.rows for c in r.cells for p in c.paragraphs)
  for fn in ('solve_problem', 'ox_crossover', 'conv_mean'):
      print(fn, 'OK' if fn in t else '❌ 缺失')
  "
  ```

本次实测：`solver.py 475 行 + run_all.py 269 行 = 744 行`，产物 85 KB / 16 页。

---

## 六、源码本身也要先清干净

因为附录会把源码**全文印进论文**，所以源码里不能有任何内部痕迹（详见
`01_官方红线与合规/禁用词与不当内容清单.md` 第五节）：

| 位置 | 原 | 改 |
|------|-----|-----|
| docstring | `Author: code-hand sub-agent...` | 中性描述 + 可复现性说明 |
| 输出目录 | `OUT = "D:/WorkBuddy_output/..."` | `OUT = os.path.dirname(os.path.abspath(__file__))` |
| 数据目录 | `desktop = "C:/Users/lenovo/Desktop"` | 相对搜索 `./data` → 脚本目录 → cwd → 父目录 → 环境变量 |
| 注释 | `# 0. Assumptions (documented; stated in code_results.md)` | `# 0. Model assumptions and parameters (see Section 2 of the paper)` |

---

## 七、标准作业流程

1. 先清源码（去绝对路径、去内部角色名）
2. `python sync_appendix_pdf.py` —— 把清好的源码注入 md 附录
3. `python make_code_appendix_docx.py` —— 出独立 docx
4. 验收：行数 / 核心函数存在性 / 边框 XML / 颜色 run 数

```bash
python -c "
from docx import Document
d = Document('附录_全部Python代码.docx')
print('表格数:', len(d.tables))              # 应 = 源码文件数
xml = d.tables[0]._tbl.xml
print('含 tblBorders:', 'tblBorders' in xml)
import re
print('边框:', re.findall(r'<w:(?:top|left) w:val=\"([^\"]+)\" w:sz=\"([^\"]+)\"', xml)[:2])
"
```
