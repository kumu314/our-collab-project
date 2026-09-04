#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
fill.py —— 把 writer 章节稿里的 {{...}} 占位符回填成真实数字。

这是统稿流程的第 3 步。coder 和 writer 并行产出，占位符是他们的「握手点」，
这里一次性把全文数字换成 results.json / FACTS.md 的真值。

数据源：
  - 01_OUTBOX/coder/results.json   -> {{P1.T_min}}、{{P2.theta_best}}
  - 00_CONTRACT/FACTS.md            -> {{FACTS.m}}

占位符语法（详见 00_CONTRACT/SPEC.md 第三节）：
  {{P1.total_cost}}                 从 results.json 取路径值
  {{P1.a_max_g - P2.theta_best}}  支持四则运算（路径之间）
  {{FACTS.m}}        从 FACTS.md「数值」表取键

输出（默认仓库根 filled/）：
  - filled/secXX_*.md        每个章节回填后的版本
  - filled/草稿_回填版.md     按文件名排序拼接的完整草稿
  - filled/回填报告.md        解析统计 + 未解析占位符清单

用法：
    python fill.py [--writer-dir DIR] [--results PATH] [--facts PATH] [--out DIR]
"""

import argparse
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))


def fmt(v):
    if isinstance(v, bool):
        return str(v)
    if isinstance(v, int):
        return str(v)
    if isinstance(v, float):
        # 近零临界值（如垂尾余量 3.99e-5 m）：用科学计数法保留有效位，
        # 避免被 2 位小数四舍五入成 0 而丢失「紧约束」信息（SPEC 规则#2）。
        if v != 0.0 and abs(v) < 0.01:
            return f"{v:.2e}"
        if abs(v - round(v)) < 1e-9:
            return str(int(round(v)))
        s = f"{v:.2f}"
        if s.endswith(".00"):
            return s[:-3]
        return s
    return str(v)


def load_results(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def get_path(data, dotted):
    cur = data
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            raise KeyError(dotted)
        cur = cur[part]
    return cur


def load_facts(path):
    out = {}
    if not os.path.exists(path):
        return out
    with open(path, "r", encoding="utf-8-sig") as f:
        text = f.read()
    m = re.search(r"##\s*三[、.]\s*数值.*?(?=##\s*四)", text, re.S)
    if not m:
        return out
    block = m.group(0)
    for line in block.splitlines():
        if not line.strip().startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 5:
            continue
        key_cell, val_cell, _unit, _src, status = cells[0], cells[1], cells[2], cells[3], cells[4]
        key = re.findall(r"`([^`]+)`", key_cell)
        if not key:
            continue
        key = key[0]
        if "待" in status or "待" in val_cell or val_cell in ("⬜", "—", ""):
            out[key] = (None, status)
            continue
        num = re.search(r"-?\d+(?:\.\d+)?", val_cell)
        if num:
            out[key] = (float(num.group()), status)
        else:
            out[key] = (None, status)
    return out


PLACEHOLDER = re.compile(r"\{\{(.*?)\}\}")
SAFE_CHARS = set("0123456789.+-*/() ")


def resolve_expr(expr, data):
    tokens = re.findall(r"[A-Za-z_][\w.]*", expr)
    safe = expr
    for tok in set(tokens):
        val = get_path(data, tok)
        if val is None:
            raise ValueError(f"路径 {tok} 为 null（coder 未产出）")
        if not isinstance(val, (int, float)) or isinstance(val, bool):
            raise ValueError(f"路径 {tok} 不是数值（={val!r}）")
        safe = safe.replace(tok, repr(float(val)))
    if not all(c in SAFE_CHARS for c in safe):
        raise ValueError(f"表达式含非法字符：{safe!r}")
    return eval(safe, {"__builtins__": {}}, {})


def resolve(inner, data, facts):
    inner = inner.strip()
    if inner.startswith("FACTS."):
        key = inner[len("FACTS."):]
        if key not in facts:
            raise KeyError(f"FACTS 数值表里没有键 '{key}'")
        val, status = facts[key]
        if val is None:
            raise ValueError(f"FACTS.{key} 尚未产出（状态：{status}）")
        return val
    return resolve_expr(inner, data)


def fill_text(text, data, facts, report):
    def repl(m):
        inner = m.group(1)
        try:
            val = resolve(inner, data, facts)
            report["resolved"] += 1
            return fmt(val)
        except Exception as e:
            report["unresolved"].append((inner, str(e)))
            return m.group(0)
    return PLACEHOLDER.sub(repl, text)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--writer-dir", default=os.path.join(ROOT, "01_OUTBOX", "writer"))
    ap.add_argument("--results", default=os.path.join(ROOT, "01_OUTBOX", "coder", "results.json"))
    ap.add_argument("--facts", default=os.path.join(ROOT, "00_CONTRACT", "FACTS.md"))
    ap.add_argument("--out", default=os.path.join(ROOT, "filled"))
    args = ap.parse_args()

    data = load_results(args.results)
    if data is None:
        print(f"❌ 找不到 results.json：{args.results}\n   coder 还没产出？或先跑 check_schema.py。")
        sys.exit(1)
    facts = load_facts(args.facts)

    os.makedirs(args.out, exist_ok=True)
    sec_files = sorted(
        f for f in os.listdir(args.writer_dir)
        if re.match(r"sec.*\.md$", f) and f != "章节模板.md"
    )
    if not sec_files:
        print(f"⚠️  {args.writer_dir} 下没有 sec*.md（writer 还没交稿？）")
        sys.exit(0)

    report = {"resolved": 0, "unresolved": []}
    filled_all = []
    for fn in sec_files:
        with open(os.path.join(args.writer_dir, fn), "r", encoding="utf-8-sig") as f:
            text = f.read()
        filled = fill_text(text, data, facts, report)
        out_path = os.path.join(args.out, fn)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(filled)
        filled_all.append(filled)
        print(f"   ✔ 回填 {fn}")

    combined = "\n\n".join(filled_all)
    with open(os.path.join(args.out, "草稿_回填版.md"), "w", encoding="utf-8") as f:
        f.write(combined)

    with open(os.path.join(args.out, "回填报告.md"), "w", encoding="utf-8") as f:
        f.write("# 回填报告\n\n")
        f.write(f"- 已解析占位符：**{report['resolved']}**\n")
        f.write(f"- 未解析占位符：**{len(report['unresolved'])}**\n\n")
        if report["unresolved"]:
            f.write("## 未解析（留在原文，需人工处理）\n\n")
            for inner, why in report["unresolved"]:
                f.write(f"- `{{{{ {inner} }}}}` —— {why}\n")

    print(f"\n✅ 回填完成。")
    print(f"   章节文件 -> {args.out}/secXX_*.md")
    print(f"   完整草稿 -> {args.out}/草稿_回填版.md")
    print(f"   报告     -> {args.out}/回填报告.md")
    if report["unresolved"]:
        print(f"\n⚠️  {len(report['unresolved'])} 个占位符未解析（见回填报告）。coder 没产出的就先留着，别瞎填。")
    else:
        print("   全部占位符已解析。")


if __name__ == "__main__":
    main()
