# -*- coding: utf-8 -*-
"""图5-3 问题1 与 问题2 对比图。

原图把 76832.06 与 77367.24（差 0.70%）画成两根几乎等高的柱子，
视觉上看不出差别。这里改成三幅子图：
  (a) 总成本：纵轴截断（不从 0 起，图上明确标注），两根柱的高低差可见；
  (b) 四项指标的相对变化率（%）：这是真正有区分度的对比；
  (c) 车辆结构（燃油 / 新能源）绝对量对比：政策效应最直观的体现。
"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _carbon_kg(sol):
    """碳排放量（kg）= 碳成本 / 碳价。"""
    import solver
    return sol["breakdown"]["carbon"] / solver.CARBON_COST


def draw(results, out_path, carbon_fn=None):
    # carbon_fn 与 run_all.py 中的 carbon_kg 同签名：入参是 sol 字典
    ck = carbon_fn or _carbon_kg
    c1 = results["P1"]["cost"]; c2 = results["P2"]["cost"]
    k1 = ck(results["P1"]["sol"]); k2 = ck(results["P2"]["sol"])
    u1 = results["P1"]["used_types"]; u2 = results["P2"]["used_types"]
    ev1 = u1[4] + u1[5]; ev2 = u2[4] + u2[5]
    fu1 = u1[1] + u1[2] + u1[3]; fu2 = u2[1] + u2[2] + u2[3]

    pct = lambda a, b: 100.0 * (b - a) / a

    fig = plt.figure(figsize=(13.2, 4.3))

    # ---------- (a) 总成本：截断纵轴 ----------
    ax = fig.add_subplot(1, 3, 1)
    bars = ax.bar(["问题1", "问题2"], [c1, c2], width=0.52,
                  color=["#4C72B0", "#C44E52"], edgecolor="black", linewidth=0.6)
    lo = min(c1, c2) * 0.9995
    hi = max(c1, c2) * 1.0012
    ax.set_ylim(lo, hi)
    for b, v in zip(bars, [c1, c2]):
        ax.text(b.get_x() + b.get_width() / 2, v, "%.2f" % v,
                ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("总成本（元）")
    ax.set_title("(a) 总成本对比", fontsize=11)
    ax.text(0.5, 0.03, "纵轴自 %.0f 元起（非从 0 起）" % lo,
            transform=ax.transAxes, ha="center", fontsize=8, color="dimgray")
    ax.annotate("", xy=(1, c2), xytext=(1, c1),
                arrowprops=dict(arrowstyle="<->", color="darkred", lw=1.2))
    ax.text(1.06, (c1 + c2) / 2, "Δ+%.2f 元\n(+%.2f%%)" % (c2 - c1, pct(c1, c2)),
            color="darkred", fontsize=9, va="center")

    # ---------- (b) 相对变化率 ----------
    ax = fig.add_subplot(1, 3, 2)
    names = ["总成本", "碳排放", "新能源车数", "燃油车数"]
    vals = [pct(c1, c2), pct(k1, k2), pct(ev1, ev2), pct(fu1, fu2)]
    cols = ["#C44E52" if v >= 0 else "#55A868" for v in vals]
    y = range(len(names))
    ax.barh(list(y), vals, color=cols, edgecolor="black", linewidth=0.6, height=0.55)
    ax.set_yticks(list(y)); ax.set_yticklabels(names, fontsize=10)
    ax.axvline(0, color="black", lw=0.8)
    span = max(abs(min(vals)), abs(max(vals))) * 1.6
    ax.set_xlim(-span, span)
    for i, v in enumerate(vals):
        off = span * 0.04 if v >= 0 else -span * 0.04
        ax.text(v + off, i, "%+.2f%%" % v, va="center",
                ha="left" if v >= 0 else "right", fontsize=9)
    ax.set_xlabel("问题2 相对问题1 的变化率（%）")
    ax.set_title("(b) 政策效应的相对变化", fontsize=11)
    ax.invert_yaxis()

    # ---------- (c) 车辆结构 ----------
    ax = fig.add_subplot(1, 3, 3)
    import numpy as np
    x = np.arange(2); w = 0.34
    b1 = ax.bar(x - w / 2, [fu1, fu2], w, label="燃油车",
                color="#C44E52", edgecolor="black", linewidth=0.6)
    b2 = ax.bar(x + w / 2, [ev1, ev2], w, label="新能源车",
                color="#55A868", edgecolor="black", linewidth=0.6)
    ax.set_xticks(x); ax.set_xticklabels(["问题1", "问题2"])
    ax.set_ylabel("使用车辆数")
    top = max(fu1, fu2, ev1, ev2)
    ax.set_ylim(0, top * 1.28)
    for bs in (b1, b2):
        for b in bs:
            ax.text(b.get_x() + b.get_width() / 2, b.get_height(),
                    "%d" % b.get_height(), ha="center", va="bottom", fontsize=9)
    ax.legend(loc="upper right", fontsize=9)
    ax.set_title("(c) 车辆结构对比", fontsize=11)

    fig.suptitle("图5-3 问题1 与 问题2 方案对比", fontsize=12)
    fig.tight_layout(rect=[0, 0, 1, 0.94])
    fig.savefig(out_path, dpi=130)
    plt.close(fig)
    return out_path
