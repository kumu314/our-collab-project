#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_schema.py —— 校验 results.json 是否符合 00_CONTRACT/SPEC.md 第二节定义的 schema。

这是统稿流程的第 2 步。schema 没过 = coder 产出结构和契约对不上，必须阻断，
否则后面 fill / audit 全是基于错误结构跑的。

用法：
    python check_schema.py [path/to/results.json]

不传路径时，默认找脚本上级目录的 01_OUTBOX/coder/results.json。

退出码：
    0 = 通过（有 warning 也算通过）
    1 = 有 error（应阻断统稿）
"""

import json
import os
import sys

# ===== 期望 schema（来自 00_CONTRACT/SPEC.md 第二节，逐字段对照；2026-09-04 弹射题版）=====
EXPECTED = {
    "meta": {
        "generated_at": str,
        "seed": (int, float),
        "solver_version": str,
        "reproducible": bool,
    },
    "P1": {
        "T_min": (int, float),          # N 最小推力
        "h_min": (int, float),          # m 最低飞行高度
        "a_max_g": (int, float),        # g 推力段最大过载
        "y_max_abs": (int, float),      # m 轨迹最高绝对海拔
        "sep_x_min": (int, float),      # m 与垂尾/机尾的最小纵向间隙（≥0 安全）
        "vt_clear_min": (int, float),   # m 过垂尾时的最小垂直余量 y - h_vt（>0 安全）
        "burn_clear_min": (int, float), # m 离喷流锥面的最小距离（>0 安全）
        "h_open_margin": (int, float),  # m 开伞点高度裕量（≥100）
        "burn_ok": bool,                # 是否全程避开尾喷流锥
    },
    "P2": {
        "theta_sweep": list,            # ° 扫描倾角列表
        "T_opt": list,                  # N 各 θ 最优推力（不可行为 null）
        "h_min": list,                  # m 各 θ 最低飞行高度
        "safe": list,                   # bool 各 θ 是否可行
        "theta_best": (int, float),     # ° 最优倾角
    },
    "sensitivity": {
        "v0":   {"x": list, "y": list},
        "h0":   {"x": list, "y": list},
        "beta": {"x": list, "y": list},
        "m":    {"x": list, "y": list},
    },
    "figures": list,
}


def _is_type(v, expected):
    if v is None:
        return True
    if isinstance(expected, tuple):
        return any(isinstance(v, t) for t in expected)
    return isinstance(v, expected)


def _validate(node, expected, path, errors, warnings):
    if isinstance(expected, dict) and "figures" in expected and path == "figures":
        if not isinstance(node, list):
            errors.append(f"{path}: 应为 list，实际 {type(node).__name__}")
            return
        for i, item in enumerate(node):
            if not isinstance(item, dict):
                errors.append(f"{path}[{i}]: 元素应为 dict")
                continue
            for req in ("id", "file", "caption"):
                if req not in item:
                    errors.append(f"{path}[{i}]: 缺字段 '{req}'")
                elif not isinstance(item[req], str):
                    errors.append(f"{path}[{i}].{req}: 应为字符串")
        return

    if isinstance(expected, dict):
        if not isinstance(node, dict):
            errors.append(f"{path}: 应为 object，实际 {type(node).__name__}")
            return
        for k, sub in expected.items():
            if k not in node:
                errors.append(f"{path}.{k}: 缺失必填字段")
            else:
                _validate(node[k], sub, f"{path}.{k}", errors, warnings)
        for k in node:
            if k not in expected:
                warnings.append(f"{path}.{k}: 契约未定义的额外字段（确认是否该加进 SPEC）")
        return

    if isinstance(expected, list):
        if not isinstance(node, list):
            errors.append(f"{path}: 应为 list，实际 {type(node).__name__}")
        return

    if not _is_type(node, expected):
        errors.append(f"{path}: 类型错误，期望 {expected}，实际 {type(node).__name__}")
        return

    if isinstance(node, int) and not isinstance(node, bool):
        low = path.lower()
        if any(tag in low for tag in ("percent",)) and node > 100:
            warnings.append(
                f"{path} = {node}: 看起来被四舍五入成整数了（SPEC 要求保留 2 位小数，除非确为 0）"
            )


def main():
    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        path = os.path.normpath(os.path.join(here, "..", "01_OUTBOX", "coder", "results.json"))

    print(f"==> 校验 schema: {path}")

    if not os.path.exists(path):
        print("❌ 文件不存在。coder 还没产出 results.json？先跑通求解再统稿。")
        sys.exit(1)

    with open(path, "rb") as f:
        head = f.read(3)
    has_bom = head == b"\xef\xbb\xbf"
    if has_bom:
        print("⚠️  文件带 UTF-8 BOM（Windows 写的）。fill/audit 用 utf-8-sig 能读，但建议 coder 改无 BOM 写出。")

    with open(path, "r", encoding="utf-8-sig") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失败：{e}")
            sys.exit(1)

    errors, warnings = [], []
    _validate(data, EXPECTED, "root", errors, warnings)

    if warnings:
        print("\n⚠️  Warnings（不阻断）:")
        for w in warnings:
            print(f"   - {w}")

    if errors:
        print(f"\n❌ Errors（{len(errors)} 处，阻断统稿）:")
        for e in errors:
            print(f"   - {e}")
        sys.exit(1)

    print("\n✅ schema 校验通过。可以进入 fill.py 回填。")


if __name__ == "__main__":
    main()
