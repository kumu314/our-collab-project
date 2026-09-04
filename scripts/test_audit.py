#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""audit.py 数字提取的误报回归测试（writer PR #12 反馈）。

writer 在 PR #12 发现：audit.py 会把三类内容误判为「未溯源数字」，
淹没真正的问题：
  1. Markdown 有序列表编号（1. 2. 3. / 1.1. 2.3.）
  2. LaTeX 下标（$h_0$ / $v_0$ / $_{...}$）
  3. 行内代码里的路径（`00_CONTRACT/FACTS.md` 里的 00）

本测试锁定 extract_draft_numbers 不再提取这些噪声，同时仍能提取真数字。
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from audit import extract_draft_numbers


def _vals(text):
    return [v for v, _ in extract_draft_numbers(text)]


def test_ordered_list_numbers_ignored():
    assert 1.0 not in _vals("1. 第一项\n2. 第二项\n3. 第三项")


def test_nested_list_numbers_ignored():
    assert 1.0 not in _vals("1.1 子项\n2.3 子项")


def test_latex_subscript_ignored():
    # $h_0$ / $v_0$ 里的下标 0 不应被当成未溯源数字
    assert 0.0 not in _vals("速度 $v_0$ 与高度 $h_0$ 相关")


def test_inline_code_path_ignored():
    # 行内代码 00_CONTRACT/FACTS.md 里的 00 不应被当成数字
    assert 0.0 not in _vals("见 `00_CONTRACT/FACTS.md` 第 3 节")
    # 但同一行的真实数字 3 应保留
    assert 3.0 in _vals("见 `00_CONTRACT/FACTS.md` 第 3 节")


def test_real_number_still_extracted():
    assert 58.3 in _vals("自由下落终端速度 58.3 m/s")


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  ✓ {name}")
    print("OK")
