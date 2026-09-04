# -*- coding: utf-8 -*-
"""
B 题 飞行员空中弹射 —— 求解器 v2 (coder)
============================================================

口径依据（唯一真源，coder 不改）：
  1. 00_CONTRACT/FACTS.md（v2，2026-09-04 建模手拍板）
  2. 00_CONTRACT/SPEC.md（results.json schema）
  3. docs/decisions-2026-09-04.md（建模手对阶段①与 H8 的答疑）

物理模型要点
------------
* 四阶段：①火箭马达推力段 t∈[0,5s] ②自由上升 ③自由下落 ④开伞匀速落地
* 导轨（弹射筒）段**不单独建模**；v_e 作为 t=0 初始条件（沿导轨方向，相对飞机）
* 地面系初速： v(0) = (v0 − v_e·sinβ,  v_e·cosβ)      [β 向机尾倾为正]
* 火箭推力 T **沿导轨方向**（相对竖直向机尾偏 β），作用区间 t∈[0,5s]
      a_T = ( −T·sinβ/m ,  +T·cosβ/m )
* 二次阻力全程作用： F_d = ½ρ·CdA·v²，方向与速度相反
* 飞机随体系（H7/H8 判据）：
      s(t)     = x_plane(t) − x_pilot(t)      （人椅落后飞机多少，向机尾为正）
      y_rel(t) = y_pilot(t) − h0              （相对弹射点的竖直位移）

安全约束
--------
* H4 过载：火箭推力段内 **竖直方向（+Gz，脊柱方向）** 合成加速度/g ≤ a_lim(5)
      注：水平风阻量级 ~18g 属 −Gx（胸背向），人体耐受远高于 +Gz，
          不计入本题 5g 约束（依据 decisions §一 及题面"视力模糊/意识丧失"为 +Gz 症状）
* H5 氧限： y_max_abs < h0 + h_ox(3000)  即爬升高度 < 3000 m
* H6 开伞： 下落中 |v| ≤ v_open(97) 触发；开伞点绝对高度 ≥ h_margin(100)
* H7 碰撞： 人椅过垂尾纵向区间 s∈[s_vt, L_plane] 时须 y_rel > h_vt
            → vt_clear_min = min(y_rel − h_vt)（负值=撞垂尾）
* H8 灼伤： 人椅不得落入尾喷流锥
            顶点 (s=x_exh, y=−dy_nozzle)，轴沿 +s，半顶角 α，长 L_flame
            锥内 ⟺ |y_rel + dy_nozzle| ≤ (s − x_exh)·tanα
            → burn_clear_min = min( |y_rel+dy_nozzle| − (s−x_exh)·tanα )

产出：01_OUTBOX/coder/results.json（UTF-8 无 BOM）

用法：
    python solver.py
"""

import json
import math
import os
from datetime import datetime, timezone, timedelta

import numpy as np
from scipy.integrate import solve_ivp
from scipy.optimize import brentq

# ---------------------------------------------------------------------------
# 1. 参数（抄录自 00_CONTRACT/FACTS.md 3.1；键名与值均不得本地修改）
# ---------------------------------------------------------------------------
FACTS = {
    "m": 170.0,             # kg   人椅质量
    "g": 9.81,              # m/s^2
    "rho": 1.225,           # kg/m^3  （海平面常数，海拔修正列入敏感性）
    "CdA": 0.8,             # m^2
    "v_e": 16.0,            # m/s  导轨弹射初速（相对飞机，t=0 初始条件）
    "beta": 15.0,           # deg  导轨相对竖直、向机尾倾角
    "t1": 5.0,              # s    火箭推力时长
    "v0": 250.0,            # m/s  飞机巡航速度
    "h0_base": 8000.0,      # m    基准飞行高度
    "a_lim": 5.0,           # g    过载上限（+Gz，推力段）
    "h_ox": 3000.0,         # m    氧限：爬升高度须 < 此值
    "v_open": 97.0,         # m/s  开伞允许最大速度
    "v_t": 6.0,             # m/s  伞后终端速度
    "h_margin": 100.0,      # m    开伞点最低绝对高度
    "L_plane": 15.0,        # m    机身长（兼垂尾纵向区间后界）
    "x_exh": 9.0,           # m    导轨出口→尾喷口纵向距离
    "L_flame": 10.0,        # m    尾焰有效长度
    "alpha_exh": 12.5,      # deg  喷流锥半顶角
    "dy_nozzle": 0.5,       # m    喷口中心低于导轨出口的垂直距离
    "s_vt": 7.0,            # m    垂尾前缘距导轨出口纵向距离
    "h_vt": 5.5,            # m    垂尾顶端高出导轨出口
    "L_rail": 1.05,         # m    导轨行程（仅说明，不参与积分）
}

SEED = 42


# ---------------------------------------------------------------------------
# 2. 动力学
# ---------------------------------------------------------------------------

def drag_accel(vx, vy, p):
    """二次阻力产生的加速度（矢量），方向与速度相反。"""
    v = math.hypot(vx, vy)
    if v < 1e-12:
        return 0.0, 0.0
    k = 0.5 * p["rho"] * p["CdA"] * v / p["m"]
    return -k * vx, -k * vy


def derivatives(t, s, T, powered, p, beta_deg):
    """ODE 右端：s = [x, y, vx, vy]（地面系）"""
    x, y, vx, vy = s
    adx, ady = drag_accel(vx, vy, p)
    ax = adx
    ay = -p["g"] + ady
    if powered:
        be = math.radians(beta_deg)
        ax += -T * math.sin(be) / p["m"]   # 推力水平分量：向机尾（-x）
        ay += T * math.cos(be) / p["m"]   # 推力竖直分量：向上
    return [vx, vy, ax, ay]


def initial_state(p, h0, theta_deg=0.0):
    """t=0 初始状态（导轨出口处，弹射初速已赋予）。"""
    v_e, beta, v0 = p["v_e"], p["beta"], p["v0"]
    be, th = math.radians(beta), math.radians(theta_deg)
    # 飞机速度（Q1 水平：theta=0 → (v0, 0)）
    vpx = v0 * math.cos(th)
    vpy = v0 * math.sin(th)
    # 弹射相对速度（沿导轨，向机尾偏 beta）
    vex = -v_e * math.sin(be)
    vey = v_e * math.cos(be)
    return [0.0, h0, vpx + vex, vpy + vey]


# ---------------------------------------------------------------------------
# 3. 轨迹积分
# ---------------------------------------------------------------------------

def simulate(T, h0, p, theta_deg=0.0, t_end=200.0, dt=0.002):
    """积分一次弹射全过程（推力段 + 无推力段直到落地）。"""
    t1 = p["t1"]
    s0 = initial_state(p, h0, theta_deg)

    # --- 推力段 [0, t1] ---
    t_eval1 = np.arange(0.0, t1 + dt, dt)
    sol1 = solve_ivp(derivatives, (0.0, t1), s0, t_eval=t_eval1,
                     args=(T, True, p, p["beta"]),
                     method="RK45", rtol=1e-9, atol=1e-9)

    # --- 无推力段 [t1, ...] 直到落地 ---
    s1 = sol1.y[:, -1]

    def hit_ground(t, s, *args):
        return s[1]
    hit_ground.terminal = True
    hit_ground.direction = -1

    t_eval2 = np.arange(t1, t1 + t_end, dt)
    sol2 = solve_ivp(derivatives, (t1, t1 + t_end), s1, t_eval=t_eval2,
                     args=(0.0, False, p, p["beta"]),
                     method="RK45", rtol=1e-9, atol=1e-9,
                     events=hit_ground)

    # 合并
    t = np.concatenate([sol1.t, sol2.t])
    x = np.concatenate([sol1.y[0], sol2.y[0]])
    y = np.concatenate([sol1.y[1], sol2.y[1]])
    vx = np.concatenate([sol1.y[2], sol2.y[2]])
    vy = np.concatenate([sol1.y[3], sol2.y[3]])

    # ---- 推力段竖直过载（H4，+Gz）----
    be = math.radians(p["beta"])
    a_vert_g = []
    for i in range(len(sol1.t)):
        vxi, vyi = sol1.y[2, i], sol1.y[3, i]
        _, ady = drag_accel(vxi, vyi, p)
        ay = -p["g"] + ady + T * math.cos(be) / p["m"]
        a_vert_g.append(abs(ay) / p["g"])
    a_vert_g = np.array(a_vert_g)
    a_max_g = float(np.max(a_vert_g)) if len(a_vert_g) else 0.0

    # ---- 飞机随体系坐标（H7/H8）----
    th = math.radians(theta_deg)
    x_plane = p["v0"] * math.cos(th) * t      # 飞机水平位置（匀速）
    s_rel = x_plane - x                       # 人椅落后飞机的纵向距离（向机尾为正）
    y_rel = y - h0                            # 相对弹射点竖直位移

    # ---- H7：垂尾 ----
    s_vt, L_plane, h_vt = p["s_vt"], p["L_plane"], p["h_vt"]
    in_vt = (s_rel >= s_vt) & (s_rel <= L_plane)
    if np.any(in_vt):
        vt_clear_min = float(np.min(y_rel[in_vt] - h_vt))
        sep_x_min = vt_clear_min              # 语义：过障碍区间时的最小富裕距离（负=碰撞）
    else:
        vt_clear_min = None
        sep_x_min = None

    # ---- H8：尾喷流锥 ----
    x_exh, L_flame = p["x_exh"], p["L_flame"]
    alpha = math.radians(p["alpha_exh"])
    dy_n = p["dy_nozzle"]
    in_flame = (s_rel >= x_exh) & (s_rel <= x_exh + L_flame)
    if np.any(in_flame):
        idx = np.where(in_flame)[0]
        cone_r = (s_rel[idx] - x_exh) * math.tan(alpha)      # 锥在该纵向位置的半径
        d_cone = np.abs(y_rel[idx] + dy_n) - cone_r          # 正=在锥外（安全）
        burn_clear_min = float(np.min(d_cone))
        burn_ok = bool(burn_clear_min > 0.0)
    else:
        burn_clear_min = None
        burn_ok = True

    # ---- H6：开伞 ----
    v_open = p["v_open"]
    opened, t_open, h_open = False, None, None
    for i in range(len(t)):
        if vy[i] < 0.0 and math.hypot(vx[i], vy[i]) <= v_open:
            opened, t_open, h_open = True, float(t[i]), float(y[i])
            break
    h_open_margin = float(h_open) if opened else None   # 开伞点绝对高度（≥100 为合格）

    # ---- H5：最高绝对海拔 / 爬升高度 ----
    y_max_abs = float(np.max(y))
    climb = y_max_abs - h0

    return {
        "t": t, "x": x, "y": y, "vx": vx, "vy": vy,
        "s_rel": s_rel, "y_rel": y_rel,
        "a_max_g": a_max_g,
        "y_max_abs": y_max_abs, "climb": climb,
        "vt_clear_min": vt_clear_min, "sep_x_min": sep_x_min,
        "burn_clear_min": burn_clear_min, "burn_ok": burn_ok,
        "opened": opened, "t_open": t_open,
        "h_open": h_open, "h_open_margin": h_open_margin,
    }


# ---------------------------------------------------------------------------
# 4. 约束检查
# ---------------------------------------------------------------------------

def check_constraints(res, p, h0):
    """返回 (ok, binding, details)。binding = 最先卡住的约束名。"""
    d = {}
    # H4：推力段竖直过载 ≤ 5g
    d["H4_overload"] = res["a_max_g"] <= p["a_lim"] + 1e-9
    # H5：爬升高度 < 3000
    d["H5_oxygen"] = res["climb"] < p["h_ox"]
    # H6：成功开伞且开伞点绝对高度 ≥ 100
    d["H6_chute"] = bool(res["opened"] and res["h_open_margin"] is not None
                         and res["h_open_margin"] >= p["h_margin"])
    # H7：过垂尾区间时余量 > 0
    d["H7_vtail"] = (res["vt_clear_min"] is None) or (res["vt_clear_min"] > 0.0)
    # H8：不入锥
    d["H8_exhaust"] = bool(res["burn_ok"])

    ok = all(d.values())
    binding = None
    if not ok:
        for k, v in d.items():
            if not v:
                binding = k
                break
    return ok, binding, d


# ---------------------------------------------------------------------------
# 5. P1 求解
# ---------------------------------------------------------------------------

def feasible_at_T(T, h0, p, theta_deg=0.0):
    res = simulate(float(T), h0, p, theta_deg=theta_deg)
    ok, _, _ = check_constraints(res, p, h0)
    return ok


def solve_T_min(h0, p, T_lo=1000.0, T_hi=60000.0, n_scan=80, theta_deg=0.0):
    """
    扫描 + 二分求最小可行推力 T_min。

    物理结构：T 过小 → 爬升慢 → 撞垂尾（H7 卡）；
              T 过大 → 竖直过载超 5g（H4 卡）。
    故可行域为区间，T_min = 其下界。
    """
    Ts = np.linspace(T_lo, T_hi, n_scan)
    first_ok = None
    for T in Ts:
        if feasible_at_T(float(T), h0, p, theta_deg):
            first_ok = float(T)
            break

    if first_ok is None:
        return None, None

    idx = int(np.where(np.isclose(Ts, first_ok))[0][0])
    lo = float(Ts[idx - 1]) if idx > 0 else T_lo

    try:
        T_min = brentq(lambda T: (0.5 if feasible_at_T(T, h0, p, theta_deg) else -0.5),
                       lo, first_ok, xtol=1.0)
    except Exception:
        T_min = first_ok

    res = simulate(float(T_min), h0, p, theta_deg=theta_deg)
    return float(T_min), res


def solve_h_min(T_fix, p, h_hi=None, h_lo=50.0, n_scan=60, theta_deg=0.0):
    """
    Q1 第二问：固定推力 T_fix，求仍满足全部约束的**最低飞行高度** h_min。
    自高向低扫描 h0，取最低可行者。
    """
    if h_hi is None:
        h_hi = p["h0_base"]
    hs = np.linspace(h_hi, h_lo, n_scan)
    last_ok = None
    for h in hs:
        res = simulate(T_fix, float(h), p, theta_deg=theta_deg)
        ok, _, _ = check_constraints(res, p, float(h))
        if ok:
            last_ok = float(h)
        else:
            break     # 已到临界高度以下
    return last_ok


def solve_P1(p):
    """P1 主流程：先求 T_min，再求该推力下的 h_min。"""
    h0 = p["h0_base"]
    T_min, res = solve_T_min(h0, p)
    if T_min is None:
        print("⚠️ 基准高度下未找到可行推力，请检查参数/约束口径")
        return None, None

    ok, binding, details = check_constraints(res, p, h0)
    print(f"  T_min = {T_min:.2f} N  (可行={ok}, binding={binding})")
    print(f"  约束明细: {details}")
    print(f"  a_max_g={res['a_max_g']:.3f}  climb={res['climb']:.2f} m  "
          f"vt_clear={res['vt_clear_min']}  burn_clear={res['burn_clear_min']}")

    # h_min：固定 T=T_min 求最低可行高度
    h_min = solve_h_min(T_min, p)
    print(f"  h_min = {h_min}")

    P1 = {
        "T_min": round(float(T_min), 2),
        "h_min": round(float(h_min), 2) if h_min is not None else None,
        "a_max_g": round(float(res["a_max_g"]), 2),
        "y_max_abs": round(float(res["y_max_abs"]), 2),
        "sep_x_min": (round(float(res["sep_x_min"]), 2)
                      if res["sep_x_min"] is not None else None),
        "vt_clear_min": (round(float(res["vt_clear_min"]), 2)
                         if res["vt_clear_min"] is not None else None),
        "burn_clear_min": (round(float(res["burn_clear_min"]), 2)
                           if res["burn_clear_min"] is not None else None),
        "h_open_margin": (round(float(res["h_open_margin"]), 2)
                          if res["h_open_margin"] is not None else None),
        "burn_ok": bool(res["burn_ok"]),
    }
    return P1, res


# ---------------------------------------------------------------------------
# 6. 输出 results.json（严格按 SPEC schema，UTF-8 无 BOM）
# ---------------------------------------------------------------------------

def build_results(P1):
    now = datetime.now(timezone(timedelta(hours=8)))
    return {
        "meta": {
            "generated_at": now.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
            "seed": SEED,
            "solver_version": "v1.0",
            "reproducible": True,
        },
        "P1": P1 if P1 is not None else {
            "T_min": None, "h_min": None, "a_max_g": None,
            "y_max_abs": None, "sep_x_min": None,
            "vt_clear_min": None, "burn_clear_min": None,
            "h_open_margin": None, "burn_ok": None,
        },
        "P2": {
            "theta_sweep": [],
            "T_opt": [],
            "h_min": [],
            "safe": [],
            "theta_best": 0.0,
        },
        "sensitivity": {
            "v0":   {"x": [], "y": []},
            "h0":   {"x": [], "y": []},
            "beta": {"x": [], "y": []},
            "m":    {"x": [], "y": []},
        },
        "figures": [],
    }


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(here, "results.json")

    print("==> 求解 P1（Q1 水平飞行）...")
    P1, _ = solve_P1(FACTS)

    results = build_results(P1)
    with open(out_path, "w", encoding="utf-8") as f:      # UTF-8 无 BOM
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\n==> 已写出: {out_path}")
    if P1:
        print(json.dumps(P1, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
