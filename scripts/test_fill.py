#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""fill.py 的 fmt 单元测试（防近零临界值被四舍五入成 0 的回归）。

背景：coder 反馈 vt_clear_min 真值 3.99e-5 m（垂尾临界，仅差 0.04mm），
原 fmt 会渲染成 "0"/"0.00"，丢失「垂尾是紧约束」的物理信息。
SPEC 规则#2 改为「JSON 存全精度，显示由 fill.py 定」，近零值用科学计数法。
本测试锁定该行为，防止再回归。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fill  # noqa: E402


def test_near_zero_keeps_scientific():
    # 垂尾余量 3.99e-5 必须保留，不能变成 "0" 或 "0.00"
    assert fill.fmt(3.99e-5) == "3.99e-05"
    assert fill.fmt(0.005) == "5.00e-03"


def test_true_zero_is_zero():
    assert fill.fmt(0.0) == "0"


def test_normal_two_decimals():
    assert fill.fmt(0.5) == "0.50"
    assert fill.fmt(1.234) == "1.23"
    assert fill.fmt(8339.5) == "8339.50"


def test_integer_like_no_decimals():
    assert fill.fmt(2520.0) == "2520"
    assert fill.fmt(2100.0) == "2100"


if __name__ == "__main__":
    test_near_zero_keeps_scientific()
    test_true_zero_is_zero()
    test_normal_two_decimals()
    test_integer_like_no_decimals()
    print("✅ 全部 fill.fmt 单元测试通过")
