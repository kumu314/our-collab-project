# 接口规范（SPEC）

> **只有 captain 能改（通过 PR 合入 main）。** 这份文件定义了 coder 和 writer 之间的**契约接口**。
> 接口定死了，两个人才能并行干活而不用等对方。

---

## 一、核心思想：用接口代替等待

```
❌ 串行（慢）：coder 跑完 → 告诉 writer 数字 → writer 才开始写
✅ 并行（快）：先定死 results.json 的 schema
              → coder 按 schema 填数
              → writer 同时按 schema 写占位符
              → 统稿脚本一键回填
```

**schema 就是两个人的握手协议。** 定好之后谁也不用等谁。

---

## 二、results.json Schema（★ coder 必须严格遵守）

**路径**：`01_OUTBOX/coder/results.json`
**编码**：UTF-8，**无 BOM**（Windows PowerShell 5.1 写 JSON 默认带 BOM，会炸，见坑清单）

```json
{
  "meta": {
    "generated_at": "2026-09-03T14:20:00+08:00",
    "seed": 42,
    "solver_version": "v1.0",
    "reproducible": true
  },
  "P1": {
    "total_cost": 0.0,
    "cost_breakdown": {
      "startup": 0.0,
      "energy": 0.0,
      "time_window_penalty": 0.0,
      "carbon": 0.0
    },
    "vehicle_count": 0,
    "vehicle_used": {"type1": 0, "type2": 0, "type3": 0, "type4": 0, "type5": 0},
    "nev_count": 0,
    "carbon_kg": 0.0
  },
  "P2": {
    "total_cost": 0.0,
    "delta_vs_P1": 0.0,
    "delta_percent": 0.0,
    "nev_count": 0,
    "carbon_kg": 0.0
  },
  "P3": {
    "baseline": 0.0,
    "scenarios": {
      "cancel": 0.0,
      "add": 0.0,
      "tighten": 0.0
    }
  },
  "sensitivity": {
    "alpha": {"x": [], "y": []},
    "beta":  {"x": [], "y": []},
    "radius": {"x": [], "y": []}
  },
  "figures": [
    {"id": "fig4-1", "file": "fig4-1_convergence.png", "caption": "（中文题注）"},
    {"id": "fig5-1", "file": "fig5-1_routes.png",       "caption": "（中文题注）"}
  ]
}
```

### coder 的硬性约束
1. **字段名不许改、不许加、不许删**（writer 的占位符按这个写）
2. **数字不四舍五入到整数**（保留 2 位小数，统稿再定显示精度）
3. **跑不出来就写 `null`，不要编一个数填进去**
4. 每次重跑都要更新 `meta.generated_at` 和 `meta.seed`
5. 图文件必须由 coder 生成，`figures` 数组列出全部图 + **中文题注**

---

## 三、writer 的引用方式

```markdown
❌ 错误：总成本为 76832.06 元。
✅ 正确：总成本为 {{P1.total_cost}} 元。
✅ 正确：新能源车 {{P2.nev_count - P1.nev_count}} 辆，较问题一增加 {{P2.nev_count - P1.nev_count}} 辆。
```

**占位符语法**：`{{<results.json 里的路径>}}`

统稿时 captain 跑 `scripts/fill.py` 批量替换 —— 比三个人各自抄数字可靠 10 倍，
而且 coder 重跑出新数字时，**只需再跑一次脚本，全文自动更新**。

---

## 四、图与表的交付规范

### 图（coder 产）
| 项 | 规范 |
|---|------|
| 文件名 | `fig<图号>_<内容>.png`，如 `fig5-3_p1_vs_p2.png` |
| 分辨率 | dpi ≥ 150 |
| 中文化 | 轴标签 / 图例 / 标题**全部中文**（`plt.rcParams["font.family"]=["SimHei",...]`） |
| 题注 | 写在 `results.json` 的 `figures[].caption`，**writer 直接引用**，不自己编 |
| 对比图 | 两值差 <5% 时**不许用等高并列柱**，改用三幅子图（截断纵轴 / 相对变化率 / 结构对比） |

### 表（coder 产数据，writer 排版）
- coder 额外输出 `table<表号>_<内容>.csv`
- writer 按 CSV 内容排版成 Markdown 表，**数字从 CSV 复制，不手敲**

---

## 五、章节稿规范（writer 产）

| 项 | 规范 |
|---|------|
| 文件名 | `sec<章号>_<内容>.md`，如 `sec5_results.md` |
| 标题层级 | 顶级用中文数字（一、二、三…），子节用 `1.1` / `2.1` |
| 图表编号 | `图X-X` / `表X-X`，**分章编号** |
| 引用格式 | 「如图 X-X 所示」「如表 X-X 所示」，**禁写 `见 xxx.png`** |
| 数字 | 全部用 `{{占位符}}`，不手抄 |
| 长度 | 按 `docs/math-section-template.md`，不自由发挥 |

---

## 六、完成信号格式

每个角色完成一项后，在 **STATUS.md** 里更新自己的任务行（通过 PR 合入 main）：

```markdown
## 2026-09-03 14:20  coder
- [x] P1 主结果跑通 → `01_OUTBOX/coder/results.json`
- [x] 图4-1 → `01_OUTBOX/coder/fig4-1_convergence.png`
- [ ] P2（进行中，预计 16:00）
- ⚠️ 阻塞：无
- 📌 给 writer：P1 数字已出，可以写 5.1 了
```

**追加，不覆盖。** 看板靠 PR 流转，不要直接改别人的任务行。

---

## 七、统稿流程（captain 的 agent 做）

```bash
# 1. 拉齐所有人分支后，在 main 上：

# 2. 校验 schema
python scripts/check_schema.py 01_OUTBOX/coder/results.json

# 3. 回填占位符（writer 的稿子 + 模板 → 完整稿）
python scripts/fill.py

# 4. 数字对账（论文里每个数字都要在 results.json 里找到同源值）
python scripts/audit.py

# 5. 出 PDF / Word
bash build_pdf.sh && bash build_docx.sh
```

**check_schema.py / fill.py / audit.py 三个脚本放在 `scripts/`，由 captain 维护。**
