# -*- coding: utf-8 -*-
"""
Robot Framework 执行器
整合 runner、env_builder、parser，提供统一执行接口
参考 Cursor 的执行方式，使用临时环境脚本
"""
import os
from typing import Dict, List, Optional, Any
from pathlib import Path

# 添加 scripts 目录到 Python 路径
SCRIPT_DIR = Path(__file__).parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from rf_runner import (
    build_robot_command,
    run_robot_command_with_env,
    detect_python_for_execution
)
from rf_parser import parse_robot_output
from rf_env_builder import RFEnvBuilder


class RFExecutor:
    """Robot Framework 执行器"""

    def __init__(self, python_path: Optional[str] = None, use_env_script: bool = True):
        """
        初始化执行器

        Args:
            python_path: 指定 Python 环境路径
            use_env_script: 是否使用环境脚本（参考 Cursor 方式）
        """
        self.python_path = detect_python_for_execution(python_path)
        if not self.python_path:
            raise RuntimeError("No valid Python environment found")

        self.listener_path = str(SCRIPT_DIR / "rf_listener.py")
        self.use_env_script = use_env_script

        if use_env_script:
            self.env_builder = RFEnvBuilder(python_path)

    def prepare_env(self, work_dir: str, extra_vars: Optional[dict] = None) -> Optional[str]:
        """
        准备执行环境（生成环境脚本）

        Args:
            work_dir: 工作目录
            extra_vars: 额外的环境变量

        Returns:
            环境脚本路径，或 None
        """
        if not self.use_env_script:
            return None

        try:
            return self.env_builder.create_env_script(work_dir, extra_vars)
        except Exception as e:
            print(f"Warning: Failed to create env script: {e}")
            return None

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
        log_level: str = "INFO",
        dryrun: bool = False,
        env_vars: dict = None
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
            dryrun: 是否执行 dryrun
            env_vars: 额外的环境变量

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

        # 获取工作目录
        work_dir = os.path.dirname(os.path.abspath(robot_file))

        # 准备环境脚本
        env_script = None
        if self.use_env_script:
            env_script = self.prepare_env(work_dir, env_vars)

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
            listener=self.listener_path,
            dryrun=dryrun
        )

        # 执行命令
        cmd_result = run_robot_command_with_env(cmd, env_script)

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
            "env_script": env_script,
            "stdout": cmd_result["stdout"],
            "stderr": cmd_result["stderr"],
            "statistics": parsed.get("statistics", {}),
            "tests": parsed.get("tests", []),
            "suites": parsed.get("suites", [])
        }


def execute_robot_test(
    robot_file: str,
    python_path: str = None,
    use_env_script: bool = True,
    **kwargs
) -> Dict[str, Any]:
    """
    便捷函数：执行 Robot Framework 测试

    Args:
        robot_file: .robot 文件路径
        python_path: Python 环境路径
        use_env_script: 是否使用环境脚本（参考 Cursor 方式）
        **kwargs: 其他执行参数

    Returns:
        执行结果字典
    """
    executor = RFExecutor(python_path=python_path, use_env_script=use_env_script)
    return executor.execute(robot_file, **kwargs)


if __name__ == "__main__":
    # 测试
    import tempfile
    import shutil

    # 创建临时测试文件
    temp_dir = tempfile.mkdtemp()
    test_file = os.path.join(temp_dir, "test.robot")

    with open(test_file, "w", encoding="utf-8") as f:
        f.write("""*** Test Cases ***
简单测试
    Log    这是一个测试用例
    Should Be Equal    1    1
""")

    try:
        # 执行测试
        result = execute_robot_test(
            robot_file=test_file,
            output_dir=os.path.join(temp_dir, "output")
        )

        print("执行结果:")
        print(f"成功: {result['success']}")
        print(f"退出码: {result.get('exit_code')}")
        print(f"Python 路径: {result.get('python_path')}")
        print(f"环境脚本: {result.get('env_script')}")
        print(f"统计: {result.get('statistics')}")
    finally:
        shutil.rmtree(temp_dir)