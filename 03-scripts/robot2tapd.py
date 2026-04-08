#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
通用脚本：从 Robot Framework 的 [Documentation] 解析【预置条件】【操作步骤】【预期结果】，
生成 TAPD 通用模板 Excel 并输出 base64。
用法：python robot2excel_tapd_base64.py <robot_path> [--excel <path>] [--dir <用例目录>] [--sheet <名称>] [--creator <创建人>] [--out-b64 <.txt路径>]
"""
import os
import re
import sys
import base64
import argparse
import pandas as pd

TAPD_COLUMNS = [
    "用例目录", "用例名称", "需求ID", "前置条件", "用例步骤", "预期结果",
    "用例类型", "用例状态", "用例等级", "创建人", "是否自动化", "实现自动化", "计划自动化"
]

DEFAULT_ROW = {
    "需求ID": "",
    "用例类型": "功能测试",
    "用例状态": "正常",
    "用例等级": "P1",  # 默认值，会从 [Tags] 中覆盖
    "创建人": "徐俊康",
    "是否自动化": "是",
    "实现自动化": "是",
    "计划自动化": "是",
}

# 优先级排序：按优先级顺序选择第一个匹配的标签
PRIORITY_ORDER = ["P0", "P1", "高", "中", "低"]

SEP = " - "  # 用例目录段之间的分隔符


def default_case_directory_from_path(robot_path):
    """
    根据 .robot 文件路径生成默认用例目录，格式示例：
    "[V4.0]商户系统 - 业务接入层 - 资料提交 - 其他补充材料"
    - 路径中的 V4.0 用方括号包起来；
    - 各段用 " - "（空格-空格）连接；
    - 若最后一段（文件名 stem）自身含 "-"，只保留最后一个 "-" 后的部分，避免重复且保证分隔符统一。
    """
    path_no_ext = os.path.splitext(robot_path)[0].strip()
    parts = re.split(r"[/\\]+", path_no_ext)
    if not parts:
        return ""
    # 最后一段为文件名 stem；若内含 "-" 则只取最后一段（如 其他补充材料），避免 "V4.0商户系统-业务接入层-资料提交-其他补充材料" 整段导致格式错乱
    last = parts[-1].strip()
    if "-" in last:
        parts[-1] = last.split("-")[-1].strip() or last
    formatted = []
    for p in parts:
        if not p:
            continue
        if p.startswith("V4.0"):
            p = "[V4.0]" + p[4:]
        formatted.append(p)
    return SEP.join(formatted)


def parse_documentation_to_case(doc_text):
    """从 [Documentation] 内容解析出 前置条件、用例步骤、预期结果。"""
    doc_text = (doc_text or "").strip()
    if not doc_text or doc_text.strip() == "【预置条件】【操作步骤】【预期结果】":
        return None
    precondition = ""
    steps = ""
    expects = ""
    if "【预置条件】" in doc_text and "【操作步骤】" in doc_text:
        precondition = doc_text.split("【预置条件】")[1].split("【操作步骤】")[0].strip()
    if "【操作步骤】" in doc_text and "【预期结果】" in doc_text:
        steps = doc_text.split("【操作步骤】")[1].split("【预期结果】")[0].strip()
    if "【预期结果】" in doc_text:
        expects = doc_text.split("【预期结果】")[1].strip()
    return {"前置条件": precondition, "用例步骤": steps, "预期结果": expects}


def parse_robot_cases_from_documentation(robot_path):
    """读取 .robot 文件，按用例名 + [Documentation] + [Tags] 解析为 TAPD 所需字段。"""
    with open(robot_path, encoding="utf-8") as f:
        lines = f.readlines()
    cases = []
    current_case_name = None
    documentation = ""
    tags = []
    for line in lines:
        line = line.rstrip("\n")
        stripped = line.strip()
        # 新用例：非空行且不以 *** / ... 开头，且不以 [ 开头（非标签行）
        if re.match(r"^[^\s\[].*", line) and not line.startswith("***") and not line.startswith("..."):
            if current_case_name is not None and documentation:
                parsed = parse_documentation_to_case(documentation)
                if parsed:
                    # 从 tags 中提取优先级（直接使用标签值，不做映射）
                    priority = "P1"  # 默认值
                    for tag in tags:
                        # 优先匹配 P0/P1 格式
                        if tag.upper() in ["P0", "P1"]:
                            priority = tag.upper()
                            break
                        # 其次匹配中文格式
                        elif tag in ["高", "中", "低"]:
                            priority = tag
                            break
                    cases.append({
                        "用例名称": current_case_name,
                        "用例等级": priority,
                        **parsed
                    })
            current_case_name = stripped
            documentation = ""
            tags = []
            continue
        if stripped.startswith("[Documentation]"):
            documentation = stripped.replace("[Documentation]", "").strip()
            continue
        if stripped.startswith("[Tags]"):
            tags_str = stripped.replace("[Tags]", "").strip()
            tags = [t.strip() for t in tags_str.split() if t.strip()]
            continue
    # 处理最后一个用例
    if current_case_name and documentation:
        parsed = parse_documentation_to_case(documentation)
        if parsed:
            # 从 tags 中提取优先级（直接使用标签值，不做映射）
            priority = "P1"  # 默认值
            for tag in tags:
                # 优先匹配 P0/P1 格式
                if tag.upper() in ["P0", "P1"]:
                    priority = tag.upper()
                    break
                # 其次匹配中文格式
                elif tag in ["高", "中", "低"]:
                    priority = tag
                    break
            cases.append({"用例名称": current_case_name, "用例等级": priority, **parsed})
    return cases


def build_excel_and_base64(robot_path, excel_path, case_directory="", sheet_name="项目池测试用例导入模板", creator="徐俊康", default_row=None):
    default_row = default_row or {}
    row_defaults = {**DEFAULT_ROW, **default_row, "创建人": creator}
    # 从默认值中移除用例等级，因为我们从用例标签中获取
    row_defaults.pop("用例等级", None)
    cases = parse_robot_cases_from_documentation(robot_path)
    data = []
    for case in cases:
        row = {
            "用例目录": case_directory,
            "用例名称": case["用例名称"],
            "用例等级": case.get("用例等级", "中"),  # 从解析的用例中获取，默认为中
            "前置条件": case["前置条件"],
            "用例步骤": case["用例步骤"],
            "预期结果": case["预期结果"],
            **row_defaults
        }
        data.append(row)
    df = pd.DataFrame(data, columns=TAPD_COLUMNS)
    os.makedirs(os.path.dirname(os.path.abspath(excel_path)) or ".", exist_ok=True)
    with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name=sheet_name[:31])
    with open(excel_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return cases, excel_path, b64


def main():
    parser = argparse.ArgumentParser(description="Robot [Documentation] -> TAPD Excel -> base64")
    parser.add_argument("robot_path", help=".robot 文件路径")
    parser.add_argument("--excel", "-e", default="自动化用例导出.xlsx", help="输出 Excel 路径")
    parser.add_argument("--dir", "-d", default="", help="用例目录（TAPD）；不传则按 robot 路径自动生成，如 [V4.0]商户系统 - 业务接入层 - 商户变更 - 身份信息变更")
    parser.add_argument("--sheet", "-s", default="项目池测试用例导入模板", help="Excel 工作表名称")
    parser.add_argument("--creator", "-c", default="徐俊康", help="创建人")
    parser.add_argument("--out-b64", "-b", default="", help="base64 输出到该 .txt 文件")
    args = parser.parse_args()
    case_directory = args.dir.strip() if args.dir else default_case_directory_from_path(args.robot_path)
    cases, excel_path, b64 = build_excel_and_base64(
        args.robot_path, args.excel, case_directory=case_directory, sheet_name=args.sheet, creator=args.creator
    )
    print(f"成功处理 {len(cases)} 个测试用例")
    print(f"Excel 已生成：{excel_path}")
    print("\n------ 下面是 base64 字符串，复制到需要的地方即可 ------")
    print(b64)
    if args.out_b64:
        with open(args.out_b64, "w", encoding="utf-8") as f:
            f.write(b64)
        print(f"\nbase64 已保存到：{args.out_b64}")
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
