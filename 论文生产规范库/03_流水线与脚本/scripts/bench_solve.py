# -*- coding: utf-8 -*-
"""估算 CA-IGA 重算耗时，避免盲目开长任务。"""
import time, solver

t_load = time.time()
data = solver.load_data()
print("load_data: %.1fs  active=%d green=%d" %
      (time.time()-t_load, len(data["active"]), len(data["green"])), flush=True)

for gens in (2, 3):
    t0 = time.time()
    res = solver.solve_problem(data, policy=1, greenR=10.0, pop=45, gens=gens, seed=1)
    dt = time.time() - t0
    print("gens=%d took %.2fs  cost=%.1f  conv_mean_len=%d" %
          (gens, dt, res["cost"], len(res.get("conv_mean", []))), flush=True)
    est80 = dt / gens * 80
    print("  -> est P1(45,80) = %.1f min" % (est80/60), flush=True)
    break
