#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""premerge_check.py 的单元测试（不依赖 git，直接喂 diff 文本）。

防回归：2026-09-04 暴露的 bug——STATUS.md 校验把 writer/coder 自己的改动
也误报成"动了别人的条目"，导致全队 PR 全红。根因是正则捕获组 + 方括号比较
（见 PR #9 / 论文手提交的 premerge_check 修复补丁）。
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import premerge_check as pc  # noqa: E402


def test_findall_returns_bare_role():
    # 关键契约：捕获组让 findall 返回裸名（无方括号），修复就是基于这一点
    assert pc.OTHER_ROLE_TAG.findall("- [writer] 任务A") == ["writer"]
    assert pc.OTHER_ROLE_TAG.findall("+ [coder] 任务B") == ["coder"]
    # 中文/无标签行不应被当作角色条目
    assert pc.OTHER_ROLE_TAG.findall("- [待认领] 任务C") == []
    assert pc.OTHER_ROLE_TAG.findall("  普通说明文字") == []


def test_writer_own_line_ok():
    # writer 改自己那一行——修 bug 前这里会误报红
    diff = (
        "--- a/STATUS.md\n"
        "+++ b/STATUS.md\n"
        "@@ -1,3 +1,3 @@\n"
        "- [writer] 旧任务\n"
        "+ [writer] 新任务\n"
    )
    assert pc.status_violations(diff, "writer") == []


def test_writer_touching_coders_line_fails():
    # writer 真动了 coder 的条目——应当报错
    diff = (
        "--- a/STATUS.md\n"
        "+++ b/STATUS.md\n"
        "- [coder] 别人的任务\n"
        "+ [writer] 我的任务\n"
    )
    viol = pc.status_violations(diff, "writer")
    assert len(viol) == 1
    assert "动了别人的条目" in viol[0]


def test_untagged_pool_line_ok():
    # 待认领池里的无标签行，writer 搬运不报错
    diff = (
        "- 待认领：某任务\n"
        "+ [writer] 某任务（已认领）\n"
    )
    assert pc.status_violations(diff, "writer") == []


def test_function_flags_any_non_matching_tag():
    # 函数本身只看"标签≠当前角色"；modeler 豁免是 main 外层 role != "modeler" 的事
    diff = "- [coder] x\n"
    assert pc.status_violations(diff, "modeler") != []
    assert pc.status_violations(diff, "writer") != []
    assert pc.status_violations(diff, "coder") == []


if __name__ == "__main__":
    test_findall_returns_bare_role()
    test_writer_own_line_ok()
    test_writer_touching_coders_line_fails()
    test_untagged_pool_line_ok()
    test_function_flags_any_non_matching_tag()
    print("✅ 全部 premerge_check 单元测试通过")
