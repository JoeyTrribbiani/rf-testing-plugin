# -*- coding: utf-8 -*-
"""
Robot Framework 执行器
整合 runner、listener、parser，提供统一执行接口
"""
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPT_DIR = Path(__file__).parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from rf_runner import build_robot_command, run_robot_command, detect_python_for_execution
from rf_parser import parse_robot_output


class RFExecutor:
    """Robot Framework 执行器"""

    def __init__(self, python_path: Optional[str] = None):
        """
        初始化执行器

        Args:
            python_path: 指定 Python 环境路径
        """
        self.python_path = detect_python_for_execution(python_path)
        if not self.python_path:
            raise RuntimeError("No valid Python environment found")

        self.listener_path = str(SCRIPT_DIR / "rf_listener.py")

    def execute(
        self,
        robot_file: str,
        test_name: str = None,
        suite_name: str = None,
        include_tags: List[str] = None,
        exclude_tags: List[str] = None,
        variables: List[str] = None,
        variable_file: str = None,
        output_dir: str = "./output",
        log_level: str = "INFO"
    ) -> Dict[str, Any]:
        """
        执行 Robot Framework 测试

        Args:
            robot_file: .robot 文件路径
            test_name: 执行指定测试用例
            suite_name: 执行指定测试套件
            include_tags: 包含的标签
            exclude_tags: 排除的标签
            variables: 变量列表
            variable_file: 变量文件
            output_dir: 输出目录
            log_level: 日志级别

        Returns:
            执行结果字典
        """
        # 验证文件存在
        if not os.path.exists(robot_file):
            return {
                "success": False,
                "error": f"Robot file not found: {robot_file}",
                "statistics": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "tests": []
            }

        # 构建命令
        cmd = build_robot_command(
            robot_file=robot_file,
            python_path=self.python_path,
            test_name=test_name,
            suite_name=suite_name,
            include_tags=include_tags,
            exclude_tags=exclude_tags,
            variables=variables,
            variable_file=variable_file,
            output_dir=output_dir,
            log_level=log_level,
            listener=self.listener_path
        )

        # 执行命令
        cmd_result = run_robot_command(cmd)

        if cmd_result["error"]:
            return {
                "success": False,
                "error": cmd_result["error"],
                "statistics": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "tests": []
            }

        # 解析输出文件
        output_file = os.path.join(output_dir, "output.xml")

        if not os.path.exists(output_file):
            return {
                "success": cmd_result["success"],
                "error": "output.xml not generated",
                "statistics": {"total": 0, "passed": 0, "failed": 0, "skipped": 0},
                "tests": []
            }

        # 解析结果
        parsed = parse_robot_output(output_file)

        return {
            "success": cmd_result["success"],
            "exit_code": cmd_result["exit_code"],
            "output_dir": output_dir,
            "log_file": os.path.join(output_dir, "log.html"),
            "report_file": os.path.join(output_dir, "report.html"),
            "output_file": output_file,
            "python_path": self.python_path,
            "statistics": parsed.get("statistics", {}),
            "tests": parsed.get("tests", []),
            "suites": parsed.get("suites", [])
        }


def execute_robot_test(
    robot_file: str,
    python_path: str = None,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：执行 Robot Framework 测试

    Args:
        robot_file: .robot 文件路径
        python_path: Python 环境路径
        **kwargs: 其他执行参数

    Returns:
        执行结果字典
    """
    executor = RFExecutor(python_path=python_path)
    return executor.execute(robot_file, **kwargs)