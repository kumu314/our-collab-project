# -*- coding: utf-8 -*-
"""只重画图5-3（对比图），直接读 results_cache.pkl，不重跑 4 分钟的遗传算法。"""
import os, pickle
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
plt.rcParams["axes.unicode_minus"] = False
plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "SimSun", "sans-serif"]

import fig_compare

OUT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(OUT, "results_cache.pkl"), "rb") as f:
    results = pickle.load(f)

p = fig_compare.draw(results, os.path.join(OUT, "p1_vs_p2.png"))
print("redrawn:", p, os.path.getsize(p), "bytes")
