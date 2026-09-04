#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
premerge_check.py —— PR 合入前的契约校验闸。

由整合人（modeler / 小羽）在合并前跑，也挂在 GitHub Actions 上自动跑。
不合规 -> 退出码非 0 -> PR 标红，禁止合并。

校验项：
  1. 角色合法（coder / writer / modeler）
  2. 分支命名合规（agent/<角色>/<任务>）
  3. 改动文件只在授权区域：
     - 00_CONTRACT/ scripts/ .workbuddy/ .github/ .gitignore 只有 modeler 能碰
     - 01_OUTBOX/<他人角色>/ 不许碰
  4. docs/work-<角色>.md 若在改动里，必须非空（防空文件应付）
  5. STATUS.md 的改动不许动别人的条目（认领/更新只准碰自己的行和「待认领」池）
  6. coder 改了 results.json 时，跑 check_schema.py 校验 schema

用法：
    python scripts/premerge_check.py --base <base_sha> --head <head_sha> --role <coder|writer|modeler>
"""

import argparse
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, ".."))

ROLES = {"modeler", "coder", "writer"}
CAPTAIN_ONLY_PREFIXES = ("00_CONTRACT/", "scripts/", ".workbuddy/", ".github/", ".gitignore")
OTHER_ROLE_TAG = re.compile(r"\[(modeler|coder|writer)\]")


def run(cmd):
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")


def changed_files(base, head):
    r = run(["git", "diff", "--name-only", f"{base}...{head}"])
    return [l.strip() for l in r.stdout.splitlines() if l.strip()]


def file_content(ref, path):
    r = run(["git", "show", f"{ref}:{path}"])
    return r.stdout if r.returncode == 0 else ""


def status_violations(diff_text, role):
    """解析 STATUS.md 的 git diff 文本，返回动了别人条目的违规说明列表。

    `OTHER_ROLE_TAG` 是带捕获组的正则，`re.findall` 返回的是**裸角色名**
    （如 "writer"，不含方括号）。历史上曾误写成 `tag != f"[{role}]"`，
    导致任何带角色标签的改动都被判成"别人的条目"，全队 PR 全红。
    这里必须与裸 `role` 比较，见 PR #9 修复。
    """
    violations = []
    for line in diff_text.splitlines():
        if not line.startswith(("+", "-")) or line.startswith(("+++", "---")):
            continue
        for tag in OTHER_ROLE_TAG.findall(line):
            if tag != role:
                violations.append(
                    f"STATUS.md 里动了别人的条目：{line.strip()[:60]}。"
                    "只准改自己的行和「待认领」池。"
                )
                break
    return violations


def errs(errors):
    if not errors:
        return
    print("=" * 60)
    print("❌ PR 契约校验未通过，请改完再提：")
    print("=" * 60)
    for e in errors:
        print(f"  ✗ {e}")
    print("=" * 60)
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", required=True)
    ap.add_argument("--head", required=True)
    ap.add_argument("--role", required=True)
    args = ap.parse_args()

    role = args.role.strip()
    errors = []

    if role not in ROLES:
        errs([f"角色 '{role}' 不合法，只能是 coder / writer / modeler。"
               f"分支名应为 agent/<角色>/<任务>，现在解析到的角色是 '{role}'。"])

    files = changed_files(args.base, args.head)
    if not files:
        errs(["没有检测到文件改动（可能 base/head 传反了）。"])

    for f in files:
        # 1. 只有 modeler 能改契约区
        if role != "modeler":
            if f.startswith(CAPTAIN_ONLY_PREFIXES):
                errors.append(f"你改了契约区文件 `{f}` —— 00_CONTRACT/scripts/.workbuddy/.github 只有 modeler 能改。"
                              "发现问题请在 STATUS.md 风险区登记，让 modeler 改。")
            # 2. 不许碰别人的目录
            m = re.match(r"01_OUTBOX/([^/]+)/", f)
            if m and m.group(1) != role:
                errors.append(f"你改了别人的目录 `{f}` —— 只能碰 01_OUTBOX/{role}/。")

    # 3. work-<角色>.md 非空
    work_file = f"docs/work-{role}.md"
    if work_file in files:
        content = file_content(args.head, work_file).strip()
        if not content:
            errors.append(f"`{work_file}` 是空文件 —— 试跑别交空壳，写点真实内容。")

    # 4. STATUS.md 别动别人的条目（modeler 拥有看板，豁免）
    if "STATUS.md" in files and role != "modeler":
        r = run(["git", "diff", f"{args.base}...{args.head}", "--", "STATUS.md"])
        errors.extend(status_violations(r.stdout, role))

    # 5. coder 改 results.json 时校验 schema
    if role == "coder" and "01_OUTBOX/coder/results.json" in files:
        res_path = os.path.join(ROOT, "01_OUTBOX", "coder", "results.json")
        r = run([sys.executable, os.path.join(ROOT, "scripts", "check_schema.py"), res_path])
        if r.returncode != 0:
            errors.append("results.json 没通过 schema 校验：\n" + r.stdout.strip()[-800:])

    errs(errors)

    print("=" * 60)
    print(f"✅ 契约校验通过（角色 {role}，{len(files)} 个文件改动）。")
    print("=" * 60)
    for f in files:
        print(f"   · {f}")


if __name__ == "__main__":
    main()
