#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
audit.py —— 数字对账。论文里每个数字都要在 results.json / FACTS.md 找到同源值。

这是统稿流程的第 4 步，是「事后对齐」的终结者：脚本替你把全文数字过一遍，
标出「没出处」和「有出处但没写进论文」的两类问题。

两路检查：
  A. 草稿里每个数值 -> 是否在「已知值集合」中（容忍 0.01 绝对 / 0.1% 相对）
  B. 每个「已确认来源值」-> 是否在草稿里出现过（防漏报）

数据源：
  - 回填后的章节（默认仓库根 filled/，可 --src 指定单文件或目录）
  - 01_OUTBOX/coder/results.json
  - 00_CONTRACT/FACTS.md

输出：
  - 控制台汇总
  - filled/对账报告.md

用法：
    python audit.py [--src DIR_OR_FILE] [--results PATH] [--facts PATH]
"""

import argparse
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

ABS_TOL = 0.01
REL_TOL = 0.001


def collect_results_values(data, prefix="", out=None):
    if out is None:
        out = []
    if isinstance(data, dict):
        for k, v in data.items():
            collect_results_values(v, f"{prefix}.{k}" if prefix else k, out)
    elif isinstance(data, list):
        for i, v in enumerate(data):
            collect_results_values(v, f"{prefix}[{i}]", out)
    elif isinstance(data, bool):
        pass
    elif isinstance(data, (int, float)):
        out.append((float(data), prefix))
    return out


def collect_facts_values(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    m = re.search(r"##\s*三[、.]\s*数值.*?(?=##\s*四)", text, re.S)
    if not m:
        return out
    for line in m.group(0).splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        key_cell, val_cell, _u, _s, status = cells[0], cells[1], cells[2], cells[3], cells[4]
        key = re.findall(r"`([^`]+)`", key_cell)
        if not key:
            continue
        if "待" in status or "待" in val_cell:
            continue
        num = re.search(r"-?\d+(?:\.\d+)?", val_cell)
        if num:
            out.append((float(num.group()), f"FACTS.{key[0]}"))
    return out


def extract_draft_numbers(text):
    lines = [ln for ln in text.splitlines() if not ("](" in ln or ".png" in ln.lower())]
    lines = [re.sub(r"^#{1,6}\s+\d+(?:\.\d+)*\s*", "", ln) for ln in lines]
    cleaned = "\n".join(lines)
    cleaned = re.sub(r"[图表]\s*\d+\s*-\s*\d+", "", cleaned)
    results = []
    for ln in cleaned.splitlines():
        for mm in re.finditer(r"-?\d+(?:\.\d+)?", ln):
            val = float(mm.group())
            if 1800 <= val <= 2100:
                continue
            results.append((val, ln.strip()))
    return results


def close(a, b):
    if abs(a - b) <= ABS_TOL:
        return True
    return abs(a - b) / (abs(b) + 1e-9) <= REL_TOL


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=os.path.join(ROOT, "filled"),
                    help="回填后的草稿目录或单文件（默认 仓库根/filled）")
    ap.add_argument("--results", default=os.path.join(ROOT, "01_OUTBOX", "coder", "results.json"))
    ap.add_argument("--facts", default=os.path.join(ROOT, "00_CONTRACT", "FACTS.md"))
    args = ap.parse_args()

    results_vals = []
    if os.path.exists(args.results):
        with open(args.results, "r", encoding="utf-8-sig") as f:
            results_vals = collect_results_values(json.load(f))
    facts_vals = collect_facts_values(args.facts)
    known = results_vals + facts_vals
    known_values = [v for v, _ in known]

    if os.path.isdir(args.src):
        md_files = sorted(
            f for f in os.listdir(args.src)
            if f.endswith(".md") and f not in ("回填报告.md", "对账报告.md")
        )
        draft_text = "\n".join(
            open(os.path.join(args.src, f), "r", encoding="utf-8-sig").read() for f in md_files
        )
    else:
        draft_text = open(args.src, "r", encoding="utf-8-sig").read()

    draft_nums = extract_draft_numbers(draft_text)

    verified, unverified = [], []
    for val, ln in draft_nums:
        hit = next((src for v, src in known if close(val, v)), None)
        if hit:
            verified.append((val, hit))
        else:
            unverified.append((val, ln))

    used_values = {v for v, _ in verified}
    unused = [(v, src) for v, src in known if v not in used_values]

    print("=" * 60)
    print("数字对账报告")
    print("=" * 60)
    print(f"已知来源值总数 : {len(known)}（results.json {len(results_vals)} + FACTS {len(facts_vals)}）")
    print(f"草稿数值总数   : {len(draft_nums)}")
    print(f"  ✅ 已溯源     : {len(verified)}")
    print(f"  ❌ 未溯源     : {len(unverified)}")
    print(f"  ⚠️  来源值漏报 : {len(unused)}")

    if unverified:
        print("\n--- ❌ 未溯源的数字（论文里有、但任何来源都找不到）---")
        seen = set()
        for val, ln in unverified:
            if val in seen:
                continue
            seen.add(val)
            ctx = ln if len(ln) <= 80 else ln[:77] + "…"
            print(f"   · {val}  ←  {ctx}")

    if unused:
        print("\n--- ⚠️  有来源但论文没写（可能漏报）---")
        for v, src in unused:
            print(f"   · {src} = {v}")

    out_dir = args.src if os.path.isdir(args.src) else os.path.dirname(args.src)
    with open(os.path.join(out_dir, "对账报告.md"), "w", encoding="utf-8") as f:
        f.write("# 数字对账报告\n\n")
        f.write(f"- 已知来源值：**{len(known)}**（results.json {len(results_vals)} + FACTS {len(facts_vals)}）\n")
        f.write(f"- 草稿数值：**{len(draft_nums)}**；已溯源：**{len(verified)}**；未溯源：**{len(unverified)}**\n")
        f.write(f"- 来源值漏报：**{len(unused)}**\n\n")
        if unverified:
            f.write("## 未溯源数字\n\n")
            seen = set()
            for val, ln in unverified:
                if val in seen:
                    continue
                seen.add(val)
                f.write(f"- `{val}` —— {ln}\n")
        if unused:
            f.write("\n## 来源值漏报\n\n")
            for v, src in unused:
                f.write(f"- `{src}` = `{v}`\n")

    print(f"\n报告已写入：{os.path.join(out_dir, '对账报告.md')}")
    if unverified or unused:
        print("\n⚠️  有未溯源 / 漏报项，建议人工过一遍再出稿。")
    else:
        print("\n✅ 全部数字已溯源，无漏报。")


if __name__ == "__main__":
    main()
