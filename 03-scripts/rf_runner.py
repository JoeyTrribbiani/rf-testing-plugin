# -*- coding: utf-8 -*-
"""
Robot Framework 执行脚本入口
支持命令行参数,构建并执行 robot 命令
"""
import argparse
import subprocess
import sys
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))

from python_detector import detect_python_environments


def build_robot_command(
    robot_file: str,
    python_path: str = None,
    test_name: str = None,
    suite_name: str = None,
    include_tags: List[str] = None,
    exclude_tags: List[str] = None,
    variables: List[str] = None,
    variable_file: str = None,
    output_dir: str = "./output",
    log_level: str = "INFO",
    listener: str = None
) -> List[str]:
    """
    构建 robot 命令

    Args:
        robot_file: .robot 文件路径
        python_path: Python 可执行文件路径
        test_name: 指定测试用例名称
        suite_name: 指定测试套件名称
        include_tags: 包含的标签列表
        exclude_tags: 排除的标签列表
        variables: 变量列表 [KEY:VAL, ...]
        variable_file: 变量文件路径
        output_dir: 输出目录
        log_level: 日志级别
        listener: listener 脚本路径

    Returns:
        robot 命令列表
    """
    cmd = [python_path or sys.executable, "-m", "robot"]

    # 添加 listener
    if listener:
        cmd.extend(["--listener", listener])

    # 添加日志级别
    cmd.extend(["--loglevel", log_level])

    # 添加输出目录
    cmd.extend(["--outputdir", output_dir])

    # 添加测试用例过滤
    if test_name:
        cmd.extend(["--test", test_name])
    if suite_name:
        cmd.extend(["--suite", suite_name])

    # 添加标签过滤
    if include_tags:
        for tag in include_tags:
            cmd.extend(["--include", tag])
    if exclude_tags:
        for tag in exclude_tags:
            cmd.extend(["--exclude", tag])

    # 添加变量
    if variables:
        for var in variables:
            cmd.extend(["--variable", var])
    if variable_file:
        cmd.extend(["--variablefile", variable_file])

    # 添加 .robot 文件路径
    cmd.append(robot_file)

    return cmd


def run_robot_command(cmd: List[str]) -> Dict[str, Any]:
    """
    执行 robot 命令

    Args:
        cmd: robot 命令列表

    Returns:
        执行结果字典
    """
    result = {
        "success": False,
        "exit_code": 1,
        "stdout": "",
        "stderr": "",
        "error": None
    }

    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        stdout, stderr = process.communicate()

        result["exit_code"] = process.returncode
        result["stdout"] = stdout
        result["stderr"] = stderr

        # Robot Framework 返回码 0 表示所有通过,其他表示有失败
        result["success"] = process.returncode == 0

    except FileNotFoundError as e:
        result["error"] = f"Python not found: {e}"
    except Exception as e:
        result["error"] = str(e)

    return result


def detect_python_for_execution(python_path: Optional[str] = None) -> Optional[str]:
    """
    检测或验证 Python 环境

    Args:
        python_path: 用户指定的 Python 路径

    Returns:
        有效的 Python 路径,或 None
    """
    if python_path:
        # 验证用户指定的路径
        if os.path.exists(python_path):
            return python_path
        return None

    # 自动检测
    envs = detect_python_environments()
    if envs:
        # 优先选择第一个(根据 python_detector 的排序逻辑)
        return envs[0]["python_path"]

    return None


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Robot Framework Test Runner"
    )
    parser.add_argument(
        "robot_file",
        help="Robot Framework test file (.robot)"
    )
    parser.add_argument(
        "--python",
        help="Python executable path"
    )
    parser.add_argument(
        "--test",
        help="Execute specific test"
    )
    parser.add_argument(
        "--suite",
        help="Execute specific suite"
    )
    parser.add_argument(
        "--include",
        action="append",
        help="Include tests by tag"
    )
    parser.add_argument(
        "--exclude",
        action="append",
        help="Exclude tests by tag"
    )
    parser.add_argument(
        "--variable",
        action="append",
        help="Set variable (KEY:VAL)"
    )
    parser.add_argument(
        "--variablefile",
        help="Load variables from file"
    )
    parser.add_argument(
        "--outputdir",
        default="./output",
        help="Output directory"
    )
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "NONE"],
        help="Log level"
    )
    parser.add_argument(
        "--listener",
        default=None,
        help="Listener script path"
    )

    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()

    # 验证 .robot 文件存在
    if not os.path.exists(args.robot_file):
        print(f"Error: Robot file not found: {args.robot_file}", file=sys.stderr)
        sys.exit(1)

    # 检测 Python 环境
    python_path = detect_python_for_execution(args.python)
    if not python_path:
        print("Error: No valid Python environment found", file=sys.stderr)
        sys.exit(1)

    # 默认使用内置 listener
    listener_path = args.listener or str(SCRIPT_DIR / "rf_listener.py")

    # 构建 robot 命令
    cmd = build_robot_command(
        robot_file=args.robot_file,
        python_path=python_path,
        test_name=args.test,
        suite_name=args.suite,
        include_tags=args.include,
        exclude_tags=args.exclude,
        variables=args.variable,
        variable_file=args.variablefile,
        output_dir=args.outputdir,
        log_level=args.loglevel,
        listener=listener_path
    )

    # 执行命令
    result = run_robot_command(cmd)

    if result["error"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if result["stderr"]:
        print(result["stderr"], file=sys.stderr)

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()