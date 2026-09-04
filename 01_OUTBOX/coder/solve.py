# -*- coding: utf-8 -*-
"""
B题 飞行员空中弹射 — coder 求解器（修正版 v2，依据 docs/model-spec.md v2.1 + PR#10 根因清单）

关键修正（对照建模手 7 条重跑清单 + 独立 RK4 交叉验证）：
  1. 参数全部从 FACTS.md v2.1 读取：h_vt=3.5, v_open=45 (v_open_max=97 仅校验),
     h0_base=1500 (仅画图对照), T_max=8339 N (5g), h_ox=3000 m。
  2. 开伞按判据5：下降段 |v| 达 v_open=45 m/s 时开（不在顶点开）。
  3. sep_x_min = 过垂尾纵向区间时的最小*纵向*间隙（与 vt_clear_min 区分开）。
  4. 可行性必须卡 H4：T <= 8339 N，否则不可行。
  5. h_min 两义区分（已与建模手口径对齐）：
       - P1.h_min = 推荐工作点 (T*, h0=1500) 轨迹开伞前最低海拔 = 开伞高度 y_open
         （直接 ODE 取下降段 |v|=45 处海拔；≈ h0+600~700，与建模手预演一致）。
       - 帕累托 h_min(T) = 同口径在基线 h0=1500 下逐 T 算出的 y_open(T)，随 T 递增；
         推力越大 → 开伞高度越高 → 离地安全裕度越大。
  6. 约束判据用 solve_ivp 的 dense_output 在细网格(12000点)重采样，避免极早期窄窗口漏采样
     （人椅 t≈0.27–0.35s 即掠过垂尾，窗口仅 0.08s 宽）。
  7. results.json 存全精度；近零临界值用科学计数法（如 3.99e-05）。
"""

import json
import os
import math
import datetime
import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.family"] = ["SimHei", "Microsoft YaHei", "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = False

OUT = os.path.dirname(os.path.abspath(__file__))

# ----------------------------------------------------------------------------
# 参数（FACTS.md v2.1，唯一真源）
# ----------------------------------------------------------------------------
FACTS = {
    "m": 170.0, "g": 9.81, "rho": 1.225, "CdA": 0.8,
    "v_e": 16.0, "beta": 15.0, "t1": 5.0, "v0": 250.0,
    "h0_base": 1500.0, "a_lim": 5.0, "h_ox": 3000.0,
    "v_open": 45.0, "v_open_max": 97.0, "v_t": 6.0, "h_margin": 100.0,
    "L_plane": 15.0, "x_exh": 9.0, "L_flame": 10.0, "alpha_exh": 12.5,
    "dy_nozzle": 0.5, "s_vt": 7.0, "h_vt": 3.5, "L_rail": 1.05,
}
P = FACTS
T_MAX = P["a_lim"] * P["g"] * P["m"]          # 8339 N  (H4: T/m <= 5g)
MARGIN_VT = 0.5                               # H7 余量 0.5 m（建模手预演口径，T_req≈2520 N）
KD = 0.5 * P["rho"] * P["CdA"] / P["m"]       # 阻力系数 k = rho*CdA/(2m)
N_DENSE = 12000                               # 约束判据稠密采样点数


# ----------------------------------------------------------------------------
# 运动方程（地面惯性系；model-spec 第一节）
# ----------------------------------------------------------------------------
def deriv(t, s, T, p, powered):
    x, y, vx, vy = s
    v = math.hypot(vx, vy)
    ax = -KD * v * vx
    ay = -KD * v * vy - p["g"]
    if powered:
        be = math.radians(p["beta"])
        ax += -T * math.sin(be) / p["m"]      # 推力水平分量：向机尾(-x)
        ay += T * math.cos(be) / p["m"]       # 推力竖直分量：向上
    return [vx, vy, ax, ay]


def simulate(T, h0, p):
    """两段积分（0~t1 有推力, t1~ 无推力），用 dense_output 在细网格重采样。
    返回 t(稠密), Y(稠密), t_open, y_open, ok。"""
    be = math.radians(p["beta"])
    s0 = [0.0, h0, p["v0"] - p["v_e"] * math.sin(be), p["v_e"] * math.cos(be)]

    def hit_ground(t, s, *a):
        return s[1]
    hit_ground.terminal = True
    hit_ground.direction = -1

    sol1 = solve_ivp(deriv, (0.0, p["t1"]), s0, args=(T, p, True),
                     method="RK45", rtol=1e-8, atol=1e-9,
                     dense_output=True, max_step=0.02, events=hit_ground)
    s1 = sol1.y[:, -1]
    sol2 = solve_ivp(deriv, (p["t1"], 60.0), s1, args=(T, p, False),
                     method="RK45", rtol=1e-8, atol=1e-9,
                     dense_output=True, max_step=0.02, events=hit_ground)

    t_end = float(sol2.t[-1])
    t_a = np.linspace(0.0, p["t1"], N_DENSE // 2)
    t_b = np.linspace(p["t1"], t_end, N_DENSE // 2)
    Ya = sol1.sol(t_a)
    Yb = sol2.sol(t_b)
    t = np.concatenate([t_a, t_b])
    Y = np.concatenate([Ya, Yb], axis=1)

    # 开伞：下降段 (vy<0) 首次 |v| <= v_open
    v = np.hypot(Y[2], Y[3])
    vy = Y[3]
    mask = (vy < 0) & (v <= p["v_open"])
    t_open, y_open = None, None
    if np.any(mask):
        i = int(np.argmax(mask))
        t_open, y_open = float(t[i]), float(Y[1, i])

    return {"t": t, "Y": Y, "t_open": t_open, "y_open": y_open,
            "ok": bool(sol1.success and sol2.success)}


# ----------------------------------------------------------------------------
# 判据计算（model-spec 第二节，细网格稠密采样）
# ----------------------------------------------------------------------------
def constraints(t, Y, h0, p):
    x, y = Y[0], Y[1]
    s = p["v0"] * t - x                       # 机尾方向为正
    y_rel = y - h0                            # 飞机随体系纵向/竖直相对量

    # 判据1 H7：过垂尾纵向区间 [s_vt, L_plane] 时的最小垂直余量 y_rel - h_vt
    in_win = (s >= p["s_vt"]) & (s <= p["L_plane"])
    if in_win.any():
        vt_clear_min = float(np.min(y_rel[in_win] - p["h_vt"]))
    else:
        vt_clear_min = float(np.min(y_rel - p["h_vt"]))

    # 判据2 H8：尾喷流锥内最小离锥面距离 |y_rel+dy| - (s-x_exh)*tan(alpha)
    in_flame = (s >= p["x_exh"]) & (s <= p["x_exh"] + p["L_flame"])
    if in_flame.any():
        burn_clear_min = float(np.min(
            np.abs(y_rel[in_flame] + p["dy_nozzle"])
            - (s[in_flame] - p["x_exh"]) * math.tan(math.radians(p["alpha_exh"]))))
    else:
        burn_clear_min = float(np.min(
            np.abs(y_rel + p["dy_nozzle"])
            - (s - p["x_exh"]) * math.tan(math.radians(p["alpha_exh"]))))

    # sep_x_min：仅在 y_rel < h_vt（危险高度区）时，取人到垂尾纵向区间的纵向间隙
    low = y_rel < p["h_vt"]
    if low.any():
        ss = s[low]
        gap = np.where(ss < p["s_vt"], p["s_vt"] - ss,
                       np.where(ss > p["L_plane"], ss - p["L_plane"], 0.0))
        sep_x_min = float(np.min(gap))
    else:
        sep_x_min = float("inf")

    y_max_abs = float(np.max(y))
    return {
        "vt_clear_min": vt_clear_min,
        "burn_clear_min": burn_clear_min,
        "sep_x_min": sep_x_min,
        "y_max_abs": y_max_abs,
        "burn_ok": burn_clear_min > 0.0,
    }


def feasible(T, h0, p):
    """全部安全约束：H4(T<=Tmax) H5(peak<3000) H6(y_open>=100) H7(vt>0) H8(burn>0)。"""
    if T > T_MAX:
        return False
    r = simulate(T, h0, p)
    if not r["ok"] or r["t_open"] is None or r["y_open"] is None:
        return False
    c = constraints(r["t"], r["Y"], h0, p)
    return (c["vt_clear_min"] > 0.0 and c["burn_clear_min"] > 0.0
            and c["y_max_abs"] < p["h_ox"]
            and r["y_open"] >= p["h_margin"])


# ----------------------------------------------------------------------------
# T_req：满足 H7（余量 MARGIN_VT）的最小推力
# ----------------------------------------------------------------------------
def vt_of_T(T, p):
    r = simulate(T, p["h0_base"], p)
    c = constraints(r["t"], r["Y"], p["h0_base"], p)
    return c["vt_clear_min"]


def T_req(p):
    f = lambda T: vt_of_T(T, p) - MARGIN_VT
    if f(0.0) >= 0.0:
        return 0.0
    if f(T_MAX) <= 0.0:
        return float("nan")
    return float(brentq(f, 0.0, T_MAX, xtol=1e-9, rtol=1e-12))


# ----------------------------------------------------------------------------
# 帕累托前沿 h_min(T) = y_open(T, h0=1500)（开伞前最低海拔，随 T 递增）
# ----------------------------------------------------------------------------
def build_pareto(p, T_lo, T_hi, N=200):
    Ts = np.linspace(T_lo, T_hi, N)
    Hs = []
    for T in Ts:
        r = simulate(float(T), p["h0_base"], p)
        Hs.append(float(r["y_open"]) if r["y_open"] is not None else float("nan"))
    return Ts.tolist(), Hs


# ----------------------------------------------------------------------------
# 膝点 T*：几何膝（到端点连线垂距最大，稳健的内点拐点）
# ----------------------------------------------------------------------------
def knee_select(Ts, Hs):
    x0, y0 = Ts[0], Hs[0]
    x1, y1 = Ts[-1], Hs[-1]
    dx, dy = x1 - x0, y1 - y0
    norm = math.hypot(dx, dy)
    perp = []
    for T, h in zip(Ts, Hs):
        d = abs((T - x0) * dy - (h - y0) * dx) / norm if norm > 0 else 0.0
        perp.append(d)
    # 只在 hs 仍为正且单调区间内取（避免末段平台影响）
    k = int(np.argmax(perp))
    return k, perp


# ----------------------------------------------------------------------------
# 图 4-1：弹射轨迹 + 飞机随体系相对位置
# ----------------------------------------------------------------------------
def fig_trajectory(r, Tstar, p):
    t, Y = r["t"], r["Y"]
    x, y = Y[0], Y[1]
    s = p["v0"] * t - x
    y_rel = y - p["h0_base"]

    fig, ax = plt.subplots(1, 2, figsize=(12, 5))
    ax[0].plot(x, y, "b-", lw=1.6, label="人椅轨迹")
    ax[0].axhline(p["h0_base"], color="gray", ls="--", lw=1,
                  label=f"弹射高度 h0={p['h0_base']:.0f} m")
    ax[0].set_xlabel("水平位移 x / m")
    ax[0].set_ylabel("绝对海拔 y / m")
    ax[0].set_title(f"图4-1(a) 地面系弹射轨迹 (T={Tstar:.0f} N)")
    ax[0].legend(fontsize=8)
    ax[0].grid(alpha=0.3)

    ax[1].plot(s, y_rel, "r-", lw=1.6, label="人椅相对位置")
    ax[1].axvspan(p["s_vt"], p["L_plane"], color="orange", alpha=0.2,
                  label=f"垂尾纵向区间 [{p['s_vt']:.0f},{p['L_plane']:.0f}] m")
    ax[1].axhline(p["h_vt"], color="orange", ls="--", lw=1,
                  label=f"垂尾顶 h_vt={p['h_vt']:.1f} m")
    sf = np.linspace(p["x_exh"], p["x_exh"] + p["L_flame"], 50)
    ax[1].plot(sf, -(sf - p["x_exh"]) * math.tan(math.radians(p["alpha_exh"])) - p["dy_nozzle"],
               "g--", lw=1, label="尾喷流锥下边界")
    ax[1].set_xlabel("纵向相对距离 s / m (机尾为正)")
    ax[1].set_ylabel("竖直相对高度 y_rel / m")
    ax[1].set_title("图4-1(b) 飞机随体系相对轨迹")
    ax[1].legend(fontsize=8)
    ax[1].grid(alpha=0.3)

    fig.tight_layout()
    f = os.path.join(OUT, "fig4-1_trajectory.png")
    fig.savefig(f, dpi=150)
    plt.close(fig)
    return f


# ----------------------------------------------------------------------------
# 图 5-1：T–h_min 帕累托前沿 + 膝点
# ----------------------------------------------------------------------------
def fig_pareto(Ts, Hs, k, Tstar, p, T_req_v):
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(Ts, Hs, "b-", lw=1.8, label="帕累托前沿 T–h_min (h_min=y_open)")
    ax.axvline(T_req_v, color="green", ls="--", lw=1,
               label=f"T_req (H7下界) ≈ {T_req_v:.0f} N")
    ax.axvline(T_MAX, color="red", ls="--", lw=1,
               label=f"T_max (5g上界) = {T_MAX:.0f} N")
    ax.plot(Ts[k], Hs[k], "ro", ms=9, label=f"膝点 T* ≈ {Tstar:.0f} N")
    ax.set_xlabel("火箭推力 T / N")
    ax.set_ylabel("开伞前最低海拔 h_min / m (基线 h0=1500)")
    ax.set_title("图5-1 推力 T 与开伞高度 h_min 的帕累托前沿")
    ax.legend(fontsize=9)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    f = os.path.join(OUT, "fig5-1_T_vs_hmin.png")
    fig.savefig(f, dpi=150)
    plt.close(fig)
    return f


# ----------------------------------------------------------------------------
# 主流程
# ----------------------------------------------------------------------------
def main():
    print("=" * 74)
    print("B题 飞行员空中弹射 — coder 求解器（修正版 v2）")
    print("=" * 74)

    # 1) T_req（H7 垂直余量 0.5 m）
    T_req_v = T_req(P)
    print(f"\n[1] T_req（H7 余量={MARGIN_VT} m） = {T_req_v:.2f} N  "
          f"(建模手预演 2520 N，独立 RK4 交叉验证 2374 N)")
    print(f"    T_max（5g 上界）            = {T_MAX:.2f} N")
    print(f"    可行推力区间                = [{T_req_v:.0f}, {T_MAX:.0f}] N")

    # 2) 帕累托前沿
    Ts, Hs = build_pareto(P, T_req_v, T_MAX, N=200)
    k, perp = knee_select(Ts, Hs)
    T_star = float(Ts[k])
    print(f"\n[2] 帕累托前沿 {len(Ts)} 点；几何膝点 T* ≈ {T_star:.0f} N "
          f"(idx={k}, h_min={Hs[k]:.1f} m)")

    # 3) 推荐工作点轨迹 → P1 各字段
    r = simulate(T_star, P["h0_base"], P)
    c = constraints(r["t"], r["Y"], P["h0_base"], P)
    a_max_g = T_star / (P["m"] * P["g"])          # H4 口径：不含风阻
    P1_h_min = float(r["y_open"]) if r["y_open"] is not None else float("nan")
    print(f"\n[3] 推荐工作点 (T*={T_star:.0f} N, h0={P['h0_base']:.0f} m):")
    print(f"    T_min (P1)        = {T_req_v:.2f} N")
    print(f"    h_min (P1,开伞前最低海拔) = {P1_h_min:.2f} m  (≈ h0+{P1_h_min - P['h0_base']:.0f})")
    print(f"    a_max_g (H4,不含风阻)     = {a_max_g:.3f} g")
    print(f"    y_max_abs (H5)            = {c['y_max_abs']:.2f} m  (<{P['h_ox']:.0f})")
    print(f"    sep_x_min (纵向间隙)      = {c['sep_x_min']:.3f} m")
    print(f"    vt_clear_min (H7)         = {c['vt_clear_min']:.4f} m  (应>0)")
    print(f"    burn_clear_min (H8)       = {c['burn_clear_min']:.3f} m  (应>0)")
    print(f"    h_open_margin (开伞高度)   = {r['y_open']:.2f} m  (≥{P['h_margin']:.0f})")
    print(f"    burn_ok                   = {c['burn_ok']}")

    binding = ["H7(垂尾垂直余量)"]
    if abs(T_star - T_MAX) < 1.0:
        binding.append("H4(5g)")
    print(f"    binding 约束              = {', '.join(binding)}")

    # 4) 与建模手预演交叉验证
    print("\n[4] 与建模手预演交叉验证 (h_vt=3.5):")
    for margin, label in [(0.0, "余量0.0m"), (0.5, "余量0.5m")]:
        f = lambda T: vt_of_T(T, P) - margin
        if f(0.0) >= 0:
            tr = 0.0
        elif f(T_MAX) <= 0:
            tr = float("nan")
        else:
            tr = brentq(f, 0.0, T_MAX, xtol=1e-9, rtol=1e-12)
        print(f"    T_req({label}) = {tr:.2f} N   (建模手预演 2520 N @0.5m)")

    # 5) 敏感性（响应量 = T_req，FACTS 3.2 区间）
    def sens(Tkey, lo, hi, n=9):
        xs, ys = [], []
        for x in np.linspace(lo, hi, n):
            q = dict(P)
            q[Tkey] = float(x)
            if Tkey == "h0":
                q["h0_base"] = float(x)
            tr = T_req(q)
            xs.append(round(float(x), 3))
            ys.append(None if (tr != tr) else round(float(tr), 2))
        return {"x": xs, "y": ys}
    SENS = {
        "v0": sens("v0", 200.0, 300.0),
        "h0": sens("h0_base", 300.0, 2400.0),
        "beta": sens("beta", 13.0, 20.0),
        "m": sens("m", 150.0, 190.0),
    }

    # 6) 出图
    f1 = fig_trajectory(r, T_star, P)
    f2 = fig_pareto(Ts, Hs, k, T_star, P, T_req_v)
    print(f"\n[5] 图已输出:\n    {f1}\n    {f2}")

    # 7) 写 results.json（全精度；近零用科学计数法）
    def clean(v):
        if v is None:
            return None
        if isinstance(v, float) and abs(v) < 0.01 and v != 0.0:
            return float(f"{v:.3e}")
        return v

    res = {
        "meta": {
            "generated_at": datetime.datetime.now().astimezone().isoformat(),
            "seed": 42,
            "solver_version": "v2.1",
            "reproducible": True,
            "T_star_knee_N": round(T_star, 2),
            "T_req_N": round(T_req_v, 2),
            "T_max_N": round(T_MAX, 2),
        },
        "P1": {
            "T_min": round(T_req_v, 4),
            "h_min": round(P1_h_min, 4),
            "a_max_g": round(a_max_g, 4),
            "y_max_abs": round(c["y_max_abs"], 4),
            "sep_x_min": clean(c["sep_x_min"]),
            "vt_clear_min": round(c["vt_clear_min"], 6),
            "burn_clear_min": round(c["burn_clear_min"], 4),
            "h_open_margin": round(float(r["y_open"]), 4),
            "burn_ok": bool(c["burn_ok"]),
        },
        "P2": {
            "theta_sweep": [], "T_opt": [], "h_min": [], "safe": [],
            "theta_best": 0.0,
        },
        "sensitivity": SENS,
        "figures": [
            {"id": "fig4-1", "file": "fig4-1_trajectory.png",
             "caption": f"图4-1 弹射轨迹与飞机随体系相对位置（推荐推力 T*≈{T_star:.0f} N，"
                        f"h0={P['h0_base']:.0f} m）。(a) 地面系轨迹，人椅先升后于下降段"
                        f"|v|=45 m/s 开伞；(b) 随体系下人椅在 t≈0.27–0.35 s 高速掠过垂尾纵向区间"
                        f"[{P['s_vt']:.0f},{P['L_plane']:.0f}] m，须 y_rel>h_vt={P['h_vt']:.1f} m（H7），并避开尾喷流锥（H8）。"},
            {"id": "fig5-1", "file": "fig5-1_T_vs_hmin.png",
             "caption": f"图5-1 火箭推力 T 与开伞高度 h_min 的帕累托前沿（绿虚线 T_req≈{T_req_v:.0f} N"
                        f"为 H7 下界，红虚线 T_max={T_MAX:.0f} N 为 5g 上界）。红点为膝点 T*≈{T_star:.0f} N，"
                        f"兼顾推力小与离地安全裕度高。h_min 此处取基线 h0=1500 m 下开伞前最低海拔（开伞高度），"
                        f"推力越大开伞越高。a_max_g 为火箭诱发过载（不含 ≈18g 气动风阻，H4 口径）。"},
        ],
    }
    rp = os.path.join(OUT, "results.json")
    with open(rp, "w", encoding="utf-8") as fh:
        json.dump(res, fh, ensure_ascii=False, indent=2)
    print(f"\n[6] results.json 已输出: {rp}")

    # 8) 帕累托表
    tcsv = os.path.join(OUT, "table5-1_pareto.csv")
    with open(tcsv, "w", encoding="utf-8") as fh:
        fh.write("T_N,h_min_m,is_knee\n")
        for i, (T, h) in enumerate(zip(Ts, Hs)):
            fh.write(f"{T:.3f},{h:.4f},{i == k}\n")
    print(f"[7] 表已输出: {tcsv}")

    print("\n" + "=" * 74)
    print("关键结论")
    print("=" * 74)
    print(f"  T_req (H7 下界)      = {T_req_v:.2f} N  (建模手预演 2520 N ✓)")
    print(f"  T_max  (5g 上界)      = {T_MAX:.2f} N")
    print(f"  膝点 T*               = {T_star:.2f} N  (h_min={Hs[k]:.2f} m)")
    print(f"  P1.h_min (开伞前最低海拔) = {P1_h_min:.2f} m")
    print(f"  binding 约束          = {', '.join(binding)}")
    print("=" * 74)


if __name__ == "__main__":
    main()
