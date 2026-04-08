# -*- coding: utf-8 -*-
"""
Robot Framework 执行脚本入口
支持命令行参数，构建并执行 robot 命令
参考 Cursor 的执行方式，使用临时环境脚本
"""
import argparse
import subprocess
import sys
import os
import importlib.util
from typing import Dict, List, Optional, Any
from pathlib import Path

# 确保脚本目录在 Python 路径中（使用 __file__ 的绝对路径）
SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

# 尝试直接导入模块（使用 sys.path）
try:
    from python_detector import detect_all_python_environments
    from rf_env_builder import RFEnvBuilder
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"SCRIPT_DIR: {SCRIPT_DIR}")
    print(f"sys.path: {sys.path}")
    sys.exit(1)


def build_robot_command(
    robot_file: str,
    python_path: Optional[str] = None,
    test_name: Optional[str] = None,
    suite_name: Optional[str] = None,
    include_tags: Optional[List[str]] = None,
    exclude_tags: Optional[List[str]] = None,
    variables: Optional[List[str]] = None,
    variable_file: Optional[str] = None,
    output_dir: str = "./output",
    log_level: str = "INFO",
    listener: Optional[str] = None,
    dryrun: bool = False
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
        dryrun: 是否执行 dryrun

    Returns:
        robot 命令列表
    """
    cmd = [python_path or sys.executable, "-m", "robot"]

    # 添加 listener
    if listener:
        cmd.extend(["--listener", listener])

    # 添加日志级别
    cmd.extend(["--loglevel", log_level])

    # 添加 dryrun 选项
    if dryrun:
        cmd.append("--dryrun")

    # 添加输出目录和输出文件名（确保生成正确的文件）
    cmd.extend(["--outputdir", output_dir])
    cmd.extend(["--output", "output.xml"])
    cmd.extend(["--log", "log.html"])
    cmd.extend(["--report", "report.html"])

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


def run_robot_command_with_env(
    cmd: List[str],
    env_script: Optional[str] = None
) -> Dict[str, Any]:
    """
    使用环境脚本执行 robot 命令（参考 Cursor 方式）

    Args:
        cmd: robot 命令列表
        env_script: 环境脚本路径

    Returns:
        执行结果字典
    """
    result = {
        "success": False,
        "exit_code": 1,
        "stdout": "",
        "stderr": "",
        "error": None,
        "env_script": env_script
    }

    try:
        if env_script and os.path.exists(env_script):
            # Windows: 使用 cmd /c 调用批处理
            if os.name == "nt":
                work_dir = os.path.dirname(cmd[-1])  # .robot 文件所在目录
                # 将 cmd 列表转换为正确的字符串，避免编码问题
                # list2cmdline 在 Python 3.7 不支持 encoding 参数
                try:
                    cmd_bytes = subprocess.list2cmdline(cmd)
                    cmd_str = cmd_bytes.decode('mbcs')
                except (LookupError, UnicodeDecodeError):
                    # 回退到空格连接
                    cmd_str = " ".join(cmd)
                # 构建 Cursor 风格的命令
                full_cmd = [
                    "cmd", "/c",
                    f'cd /d "{work_dir}" && call "{env_script}" && {cmd_str}'
                ]
                process = subprocess.Popen(
                    full_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    shell=True
                )
                stdout, stderr = process.communicate()
            else:
                # Unix: 使用 source 脚本
                work_dir = os.path.dirname(cmd[-1])
                full_cmd = f'cd "{work_dir}" && source "{env_script}" && {" ".join(cmd)}'
                process = subprocess.Popen(
                    ["sh", "-c", full_cmd],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                stdout, stderr = process.communicate()
        else:
            # 直接执行（传统方式）
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


def run_robot_command(cmd: List[str]) -> Dict[str, Any]:
    """
    执行 robot 命令（直接方式）

    Args:
        cmd: robot 命令列表

    Returns:
        执行结果字典
    """
    return run_robot_command_with_env(cmd, env_script=None)


def detect_python_for_execution(python_path: Optional[str] = None) -> Optional[str]:
    """
    检测或验证 Python 环境

    优先级：
    1. 用户指定的路径
    2. 从配置文件读取的保存路径
    3. 自动检测（优先选择 3.7.x 版本）

    Args:
        python_path: 用户指定的 Python 路径

    Returns:
        有效的 Python 路径,或 None
    """
    # 1. 验证用户指定的路径
    if python_path:
        if os.path.exists(python_path):
            return python_path
        return None

    # 2. 尝试从配置文件读取
    try:
        from rf_config import get_python_path
        saved_path = get_python_path()
        if saved_path and os.path.exists(saved_path):
            return saved_path
    except ImportError:
        pass

    # 3. 自动检测，优先选择 Python 3.7.x 版本
    envs = detect_all_python_environments()
    if envs:
        for env in envs:
            version = env.get("version", "")
            if version.startswith("3.7"):
                return env["python_path"]
        return envs[0]["python_path"]

    return None


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="Robot Framework Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 执行测试用例（使用环境脚本）
  python rf_runner.py test.robot

  # dryrun 模式验证语法
  python rf_runner.py --dryrun test.robot

  # 执行指定测试用例
  python rf_runner.py --test "测试用例名称" test.robot

  # 使用自定义 Python
  python rf_runner.py --python /path/to/python test.robot

  # 包含标签
  python rf_runner.py --include P0 --include smoke test.robot
        """
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
        help="Output directory (default: ./output)"
    )
    parser.add_argument(
        "--loglevel",
        default="INFO",
        choices=["TRACE", "DEBUG", "INFO", "WARN", "NONE"],
        help="Log level (default: INFO)"
    )
    parser.add_argument(
        "--listener",
        default=None,
        help="Listener script path (default: use built-in listener)"
    )
    parser.add_argument(
        "--dryrun",
        action="store_true",
        help="Dry run mode: validate syntax without executing"
    )
    parser.add_argument(
        "--no-env-script",
        action="store_true",
        help="Don't use environment script (direct execution)"
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

    print(f"Using Python: {python_path}")

    # 获取工作目录（.robot 文件所在目录）
    work_dir = os.path.dirname(os.path.abspath(args.robot_file))

    # 创建环境脚本
    env_script = None
    if not args.no_env_script:
        try:
            builder = RFEnvBuilder(python_path)
            env_script = builder.create_env_script(work_dir)
            print(f"Created environment script: {env_script}")
        except Exception as e:
            print(f"Warning: Failed to create env script: {e}", file=sys.stderr)
            print("Using direct execution mode...", file=sys.stderr)

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
        listener=listener_path,
        dryrun=args.dryrun
    )

    # 打印执行命令
    print("Executing robot command:")
    print(" ".join(cmd))
    print()

    # 执行命令
    result = run_robot_command_with_env(cmd, env_script)

    # 输出结果
    if result["stdout"]:
        print(result["stdout"])

    if result["stderr"]:
        print(result["stderr"], file=sys.stderr)

    if result["error"]:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    if result["success"]:
        print("\nAll tests passed!")
    else:
        print(f"\nTests failed with exit code: {result['exit_code']}", file=sys.stderr)

    sys.exit(result["exit_code"])


if __name__ == "__main__":
    main()