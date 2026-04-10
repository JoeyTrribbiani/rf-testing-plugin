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


def _convert_path_for_windows(path: str) -> str:
    """
    将路径转换为 Windows 兼容格式

    优先级：
    1. win32api.GetShortPathName（如果有 pywin32）
    2. ctypes 调用 kernel32.GetShortPathNameW（标准库）
    3. 原始路径（作为兜底）

    Args:
        path: 原始路径

    Returns:
        Windows 兼容的路径
    """
    if os.name != "nt":
        return path

    # 方法1: win32api
    try:
        import win32api
        short_path = win32api.GetShortPathName(path)
        if short_path:
            return short_path
    except (ImportError, Exception):
        pass

    # 方法2: ctypes
    try:
        import ctypes
        from ctypes import wintypes

        kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
        GetShortPathNameW = kernel32.GetShortPathNameW
        GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetShortPathNameW.restype = wintypes.DWORD

        buf_size = GetShortPathNameW(path, None, 0)
        if buf_size > 0:
            buf = ctypes.create_unicode_buffer(buf_size)
            result = GetShortPathNameW(path, buf, buf_size)
            if result > 0 and result <= buf_size:
                return buf.value
    except Exception:
        pass

    # 方法3: 返回原始路径
    return path


def _ensure_path_exists(path: str) -> str:
    """
    确保路径存在，如果不存在则抛出异常

    Args:
        path: 要检查的路径

    Returns:
        路径本身
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"路径不存在: {path}")
    return path


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
    dryrun: bool = False,
    clean_output: bool = False
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
        clean_output: 是否清理输出目录

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
        # Windows 上优先使用直接执行方式（避免环境脚本的编码和路径问题）
        if os.name == "nt":
            work_dir = os.path.dirname(cmd[-1])  # .robot 文件所在目录

            # 修复中文路径问题：使用短路径格式
            short_work_dir = _convert_path_for_windows(work_dir)
            if short_work_dir != work_dir:
                work_dir = short_work_dir

            # 修复中文路径问题：确保路径使用正确的编码
            # 将命令列表转换为短路径格式
            try:
                cmd_short = []
                for item in cmd:
                    # 转换为短路径
                    if not item.startswith("-") and os.path.exists(item):
                        short_path = _convert_path_for_windows(item)
                        cmd_short.append(short_path)
                    else:
                        cmd_short.append(item)
                cmd = cmd_short
            except (ImportError, Exception):
                pass  # 短路径转换失败，使用原始命令

            # 设置正确的编码环境变量
            env = os.environ.copy()
            env['PYTHONIOENCODING'] = 'utf-8'
            env['PYTHONUTF8'] = '1'

            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=work_dir,
                env=env
            )
            stdout, stderr = process.communicate()
        elif env_script and os.path.exists(env_script):
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
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean output directory before execution"
    )

    return parser.parse_args()


def clean_output_directory(output_dir: str) -> None:
    """
    清理输出目录中的临时文件，保留核心结果文件

    Args:
        output_dir: 输出目录路径
    """
    import shutil

    if not os.path.exists(output_dir):
        return

    # 保留的文件
    keep_files = {"output.xml", "log.html", "report.html"}

    # 遍历目录，删除非保留文件
    for root, dirs, files in os.walk(output_dir, topdown=False):
        for file in files:
            if file not in keep_files:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                except Exception as e:
                    pass  # 忽略删除错误

    # 删除空目录
    for root, dirs, files in os.walk(output_dir, topdown=False):
        for dir_name in dirs:
            dir_path = os.path.join(root, dir_name)
            try:
                if not os.listdir(dir_path):
                    os.rmdir(dir_path)
            except Exception:
                pass


def main():
    """主函数"""
    args = parse_args()

    # 验证 .robot 文件存在
    if not os.path.exists(args.robot_file):
        print(f"Error: Robot file not found: {args.robot_file}", file=sys.stderr)
        sys.exit(1)

    # 清理输出目录（如果启用）
    if args.clean:
        output_dir = os.path.abspath(args.outputdir)
        clean_output_directory(output_dir)
        print(f"Cleaned output directory: {output_dir}")

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
        dryrun=args.dryrun,
        clean_output=args.clean
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