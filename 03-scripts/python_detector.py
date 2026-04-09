#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Python 环境检测模块
跨平台检测 conda、系统 Python、虚拟环境（venv）
"""

import os
import sys
import subprocess
import shutil
import glob
from typing import List, Dict, Optional, Tuple
from pathlib import Path


class PythonEnvironment:
    """Python 环境信息"""

    def __init__(self, source: str, name: str, python_path: str, version: str,
                 major: int, minor: int, patch: int, is_active: bool = False):
        self.source = source  # "conda" | "system" | "venv"
        self.name = name      # 环境名称或路径
        self.python_path = python_path
        self.version = version
        self.major = major
        self.minor = minor
        self.patch = patch
        self.is_active = is_active

    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "source": self.source,
            "name": self.name,
            "python_path": self.python_path,
            "version": self.version,
            "major": self.major,
            "minor": self.minor,
            "patch": self.patch,
            "is_active": self.is_active
        }

    def __repr__(self) -> str:
        active_mark = " [当前激活]" if self.is_active else ""
        return f"{self.source}: {self.name} ({self.version}){active_mark}"


class PythonDetectionError(Exception):
    """Python 环境检测失败"""
    pass


class NoValidPythonError(PythonDetectionError):
    """未找到符合条件的 Python 环境"""
    pass


class SitePackagesDetectionError(PythonDetectionError):
    """site-packages 目录检测失败"""
    pass


def parse_python_version(version_string: str) -> Optional[Tuple[int, int, int]]:
    """
    解析 Python 版本字符串

    Args:
        version_string: 版本字符串，如 "3.7.16" 或 "Python 3.7.16"

    Returns:
        (major, minor, patch) 或 None
    """
    # 移除 "Python " 前缀
    version_string = version_string.replace("Python ", "").strip()

    parts = version_string.split('.')
    if len(parts) < 2:
        return None

    try:
        major = int(parts[0])
        minor = int(parts[1])
        patch = int(parts[2]) if len(parts) > 2 else 0
        return (major, minor, patch)
    except ValueError:
        return None


def get_python_version(python_path: str, verbose: bool = False) -> Optional[Tuple[int, int, int]]:
    """
    获取指定 Python 的版本

    Args:
        python_path: Python 可执行文件路径
        verbose: 是否输出详细错误信息

    Returns:
        (major, minor, patch) 或 None
    """
    # 方法1: 使用 sys.version（更可靠）
    try:
        result = subprocess.run(
            [python_path, "-c", "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"],
            capture_output=True,
            timeout=10
        )
        if result.returncode == 0 and result.stdout:
            version_string = result.stdout.decode('utf-8', errors='ignore').strip()
            version = parse_python_version(version_string)
            if version:
                return version
    except Exception as e:
        if verbose:
            print(f"[DEBUG] 方法1失败 {python_path}: {e}", file=sys.stderr)

    # 方法2: 使用 --version（备选方案）
    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            timeout=10
        )
        if result.returncode != 0:
            if verbose:
                print(f"[DEBUG] --version 返回码非零 {python_path}: {result.returncode}", file=sys.stderr)
            return None

        # 版本信息在 stderr (Python 2) 或 stdout (Python 3)
        version_bytes = result.stderr or result.stdout
        if not version_bytes:
            if verbose:
                print(f"[DEBUG] 无版本输出 {python_path}", file=sys.stderr)
            return None

        # 尝试多种编码
        for encoding in ['utf-8', 'gbk', 'cp936', 'latin-1']:
            try:
                version_string = version_bytes.decode(encoding, errors='strict').strip()
                if version_string:
                    # 提取版本号（处理额外信息）
                    import re
                    version_match = re.search(r'(\d+\.\d+\.\d+)', version_string)
                    if version_match:
                        version = parse_python_version(version_match.group(1))
                        if version:
                            return version
            except UnicodeDecodeError:
                continue

        if verbose:
            print(f"[DEBUG] 解码失败 {python_path}", file=sys.stderr)
        return None
    except subprocess.TimeoutExpired:
        if verbose:
            print(f"[DEBUG] 超时 {python_path}", file=sys.stderr)
        return None
    except FileNotFoundError:
        if verbose:
            print(f"[DEBUG] 文件不存在 {python_path}", file=sys.stderr)
        return None
    except Exception as e:
        if verbose:
            print(f"[DEBUG] 检测异常 {python_path}: {e}", file=sys.stderr)
        return None


def detect_conda_envs(verbose: bool = False) -> List[PythonEnvironment]:
    """
    检测所有 conda 环境

    Args:
        verbose: 是否输出详细错误信息

    Returns:
        符合条件的 conda 环境列表
    """
    envs = []

    # 获取 conda 命令路径
    conda_cmd = os.environ.get('CONDA_EXE', 'conda')
    if not shutil.which(conda_cmd):
        if verbose:
            print(f"[DEBUG] conda 命令未找到: {conda_cmd}", file=sys.stderr)
        return envs

    # 获取当前激活环境
    active_env_name = os.environ.get('CONDA_DEFAULT_ENV', '')

    # 列出所有环境
    try:
        result = subprocess.run(
            [conda_cmd, 'env', 'list'],
            capture_output=True,
            timeout=30
        )
        # 解码输出，忽略编码错误
        stdout_text = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ''
    except (subprocess.TimeoutExpired, OSError) as e:
        if verbose:
            print(f"[DEBUG] conda env list 失败: {e}", file=sys.stderr)
        return envs

    if verbose:
        print(f"[DEBUG] conda 环境列表:\n{stdout_text}", file=sys.stderr)

    # 解析环境列表
    for line in stdout_text.split('\n'):
        line = line.strip()
        if not line or line.startswith('#'):
            continue

        parts = line.split()
        if len(parts) < 1:
            continue

        # 提取环境路径（最后一个元素）
        env_path = parts[-1]
        # 提取环境名称（第一个元素，去除 * 标记）
        env_name = parts[0].rstrip('*') if '*' in parts[0] else parts[0]

        # 检测 Python 版本
        python_path = get_conda_python_path(env_path)
        if not python_path:
            if verbose:
                print(f"[DEBUG] 环境 {env_name} 未找到 Python 可执行文件", file=sys.stderr)
            continue

        version = get_python_version(python_path, verbose)
        if version and version >= (3, 7, 16):
            envs.append(PythonEnvironment(
                source="conda",
                name=env_name,
                python_path=python_path,
                version=f"{version[0]}.{version[1]}.{version[2]}",
                major=version[0],
                minor=version[1],
                patch=version[2],
                is_active=(env_name == active_env_name)
            ))
        elif verbose:
            print(f"[DEBUG] 环境 {env_name} Python 版本过低或检测失败", file=sys.stderr)

    return envs


def get_conda_python_path(env_path: str) -> Optional[str]:
    """
    获取 conda 环境的 Python 路径

    Args:
        env_path: conda 环境路径

    Returns:
        Python 可执行文件路径或 None
    """
    if os.name == 'nt':  # Windows
        python_path = os.path.join(env_path, 'python.exe')
    else:  # Linux/macOS
        python_path = os.path.join(env_path, 'bin', 'python')

    if os.path.exists(python_path):
        return python_path
    return None


def detect_system_python(verbose: bool = False) -> List[PythonEnvironment]:
    """
    检测系统安装的 Python

    Args:
        verbose: 是否输出详细错误信息

    Returns:
        符合条件的系统 Python 列表
    """
    envs = []
    seen_paths = set()

    # 1. 检测常见 Python 命令
    python_commands = ['python3', 'python', 'py']
    for cmd in python_commands:
        python_path = shutil.which(cmd)
        if python_path and python_path not in seen_paths:
            version = get_python_version(python_path, verbose)
            if version and version >= (3, 7, 16):
                envs.append(PythonEnvironment(
                    source="system",
                    name=python_path,
                    python_path=python_path,
                    version=f"{version[0]}.{version[1]}.{version[2]}",
                    major=version[0],
                    minor=version[1],
                    patch=version[2],
                    is_active=True  # 通过 which 找到的视为激活
                ))
                seen_paths.add(python_path)
            elif verbose:
                print(f"[DEBUG] {python_path} 版本检测失败或版本过低", file=sys.stderr)

    # 2. 从 Windows Registry 查找 Python（仅 Windows）
    if os.name == 'nt':
        registry_paths = get_python_from_registry()
        for path in registry_paths:
            if path and path not in seen_paths:
                version = get_python_version(path, verbose)
                if version and version >= (3, 7, 16):
                    envs.append(PythonEnvironment(
                        source="system",
                        name=f"Registry: {path}",
                        python_path=path,
                        version=f"{version[0]}.{version[1]}.{version[2]}",
                        major=version[0],
                        minor=version[1],
                        patch=version[2],
                        is_active=False
                    ))
                    seen_paths.add(path)

    # 3. 从 Python Launcher 查找（仅 Windows）
    if os.name == 'nt':
        launcher_paths = get_python_from_launcher()
        for path in launcher_paths:
            if path and path not in seen_paths:
                version = get_python_version(path, verbose)
                if version and version >= (3, 7, 16):
                    envs.append(PythonEnvironment(
                        source="system",
                        name=f"Launcher: {path}",
                        python_path=path,
                        version=f"{version[0]}.{version[1]}.{version[2]}",
                        major=version[0],
                        minor=version[1],
                        patch=version[2],
                        is_active=False
                    ))
                    seen_paths.add(path)

    # 4. 检测常见安装路径（glob 模式）
    search_paths = get_common_python_paths()
    for pattern in search_paths:
        if '*' in pattern:  # glob 模式
            for path in glob.glob(pattern):
                if path not in seen_paths:
                    version = get_python_version(path, verbose)
                    if version and version >= (3, 7, 16):
                        envs.append(PythonEnvironment(
                            source="system",
                            name=path,
                            python_path=path,
                            version=f"{version[0]}.{version[1]}.{version[2]}",
                            major=version[0],
                            minor=version[1],
                            patch=version[2],
                            is_active=False
                        ))
                        seen_paths.add(path)
        else:  # 直接路径
            if os.path.exists(pattern) and pattern not in seen_paths:
                version = get_python_version(pattern, verbose)
                if version and version >= (3, 7, 16):
                    envs.append(PythonEnvironment(
                        source="system",
                        name=pattern,
                        python_path=pattern,
                        version=f"{version[0]}.{version[1]}.{version[2]}",
                        major=version[0],
                        minor=version[1],
                        patch=version[2],
                        is_active=False
                    ))
                    seen_paths.add(pattern)

    return envs


def get_common_python_paths() -> List[str]:
    """
    获取常见的 Python 安装路径模式

    Returns:
        路径模式列表
    """
    if os.name == 'nt':  # Windows
        paths = [
            # 标准安装路径
            r'C:\Python3*\python.exe',
            r'C:\Python*\python.exe',
            r'C:\Program Files\Python*\python.exe',
            r'C:\Program Files (x86)\Python*\python.exe',
            # 用户安装路径
            os.path.expanduser(r'~/AppData/Local/Programs/Python/Python*/python.exe'),
            # 便携版路径（常见开发目录）
            r'D:\Python*\python.exe',
            r'E:\Python*\python.exe',
            r'D:\Programs\Python*\python.exe',
            r'E:\Programs\Python*\python.exe',
        ]

        # 添加用户指定的 Python 路径（从环境变量）
        if 'PYTHONPATH' in os.environ:
            for py_path in os.environ['PYTHONPATH'].split(os.pathsep):
                if py_path and 'python.exe' in py_path.lower():
                    paths.append(py_path)

        # 添加 PATH 环境变量中的 Python
        if 'PATH' in os.environ:
            for path_dir in os.environ['PATH'].split(os.pathsep):
                python_exe = os.path.join(path_dir, 'python.exe')
                if os.path.exists(python_exe) and python_exe not in paths:
                    paths.append(python_exe)

        return paths
    elif sys.platform == 'darwin':  # macOS
        return [
            '/usr/bin/python3*',
            '/usr/local/bin/python3*',
            '/opt/homebrew/bin/python3*',
            '/usr/local/opt/python3*/bin/python3*'
        ]
    else:  # Linux
        return [
            '/usr/bin/python3*',
            '/usr/local/bin/python3*',
            '/opt/python*/bin/python3*'
        ]


def get_python_from_registry() -> List[str]:
    """
    从 Windows Registry 中查找已安装的 Python

    Returns:
        Python 可执行文件路径列表
    """
    if os.name != 'nt':
        return []

    paths = []

    try:
        import winreg
    except ImportError:
        # pywin32 未安装，返回空列表
        return paths

    try:
        # 查找 Python 3.7+ 的注册表项
        for major in range(3, 20):  # Python 3.x
            for minor in range(0, 20):  # Python 3.0-3.19
                try:
                    # 1. HKLM\SOFTWARE\Python\PythonCore\x.x\InstallPath
                    key_path = f"SOFTWARE\\Python\\PythonCore\\{major}.{minor}\\InstallPath"
                    key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
                    install_path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)

                    python_exe = os.path.join(install_path, "python.exe")
                    if os.path.exists(python_exe):
                        paths.append(python_exe)
                except WindowsError:
                    pass

                try:
                    # 2. HKCU\SOFTWARE\Python\PythonCore\x.x\InstallPath（用户安装）
                    key_path = f"SOFTWARE\\Python\\PythonCore\\{major}.{minor}\\InstallPath"
                    key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path)
                    install_path, _ = winreg.QueryValueEx(key, "")
                    winreg.CloseKey(key)

                    python_exe = os.path.join(install_path, "python.exe")
                    if os.path.exists(python_exe):
                        paths.append(python_exe)
                except WindowsError:
                    pass
    except Exception as e:
        print(f"[DEBUG] Registry 查找失败: {e}", file=sys.stderr)

    return paths


def get_python_from_launcher() -> List[str]:
    """
    从 Python Launcher (py.exe) 配置中查找 Python

    Returns:
        Python 可执行文件路径列表
    """
    if os.name != 'nt':
        return []

    paths = []

    # 查找 py.exe
    py_exe = shutil.which('py')
    if not py_exe:
        return paths

    try:
        # 获取 py.exe 配置的 Python 版本列表
        result = subprocess.run(
            [py_exe, "-0"],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            lines = result.stdout.decode('utf-8', errors='ignore').strip().split('\n')
            for line in lines:
                if line.strip():
                    # 解析输出格式: "-V:X.Y * ... path"
                    parts = line.split()
                    if len(parts) >= 3:
                        # 提取 Python 版本标识
                        version_marker = parts[1]
                        # 使用 py.exe 执行特定版本获取路径
                        try:
                            path_result = subprocess.run(
                                [py_exe, version_marker],
                                capture_output=True,
                                timeout=5,
                                text=True
                            )
                            if path_result.returncode == 0:
                                python_path = path_result.stdout.strip()
                                if python_path and os.path.exists(python_path):
                                    paths.append(python_path)
                        except Exception:
                            pass
    except Exception as e:
        print(f"[DEBUG] py.exe 查找失败: {e}", file=sys.stderr)

    return paths


def detect_venv(verbose: bool = False) -> List[PythonEnvironment]:
    """
    检测当前激活的虚拟环境（venv）

    Args:
        verbose: 是否输出详细错误信息

    Returns:
        符合条件的虚拟环境列表
    """
    envs = []

    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        if verbose:
            print("[DEBUG] 未激活虚拟环境", file=sys.stderr)
        return envs

    # 确定 Python 可执行文件路径
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:  # Linux/macOS
        python_path = os.path.join(venv_path, 'bin', 'python')

    if not os.path.exists(python_path):
        if verbose:
            print(f"[DEBUG] 虚拟环境 Python 不存在: {python_path}", file=sys.stderr)
        return envs

    version = get_python_version(python_path, verbose)
    if version and version >= (3, 7, 16):
        envs.append(PythonEnvironment(
            source="venv",
            name=venv_path,
            python_path=python_path,
            version=f"{version[0]}.{version[1]}.{version[2]}",
            major=version[0],
            minor=version[1],
            patch=version[2],
            is_active=True
        ))
    elif verbose:
        print(f"[DEBUG] 虚拟环境 Python 版本过低或检测失败", file=sys.stderr)

    return envs


def calculate_priority(env: PythonEnvironment) -> int:
    """
    计算环境优先级

    优先级策略：
    1. 当前激活的 conda 环境 → 优先级 0-99
    2. 匹配 Python 3.7.x 的 conda 环境 → 优先级 100-199
    3. 匹配 Python 3.8.x 的系统 Python → 优先级 200-299
    4. 其他匹配版本 → 优先级 300-999

    Args:
        env: Python 环境对象

    Returns:
        优先级值（越小越高）
    """
    base = 0
    # 版本偏移：越接近 3.7.16 越好
    version_offset = (env.major - 3) * 100 + (env.minor - 7) * 10 + env.patch

    if env.source == "conda" and env.is_active:
        base = 0
    elif env.source == "conda" and env.major == 3 and env.minor == 7:
        base = 100
    elif env.source == "system" and env.major == 3 and env.minor == 8:
        base = 200
    else:
        base = 300

    return base + version_offset


def sort_environments(envs: List[PythonEnvironment]) -> List[PythonEnvironment]:
    """
    按优先级排序 Python 环境

    Args:
        envs: Python 环境列表

    Returns:
        排序后的列表
    """
    return sorted(envs, key=lambda e: calculate_priority(e))


def get_site_packages_paths(python_path: str) -> List[str]:
    """
    获取指定 Python 的 site-packages 目录列表

    Args:
        python_path: Python 可执行文件路径

    Returns:
        site-packages 目录路径列表
    """
    try:
        result = subprocess.run(
            [python_path, "-c", "import site; print('\\n'.join(site.getsitepackages()))"],
            capture_output=True,
            timeout=10
        )

        if result.returncode == 0:
            # 解码输出，忽略编码错误
            stdout_text = result.stdout.decode('utf-8', errors='ignore') if result.stdout else ''
            paths = stdout_text.strip().split('\n')
            return [p for p in paths if p and os.path.isdir(p)]
    except (subprocess.TimeoutExpired, OSError):
        pass

    # 备选方案：手动计算
    version = get_python_version(python_path)
    if version:
        return calculate_fallback_paths(python_path, version)

    return []


def calculate_fallback_paths(python_path: str, version: Tuple[int, int, int]) -> List[str]:
    """
    备选方案：手动计算 site-packages 路径

    Args:
        python_path: Python 可执行文件路径
        version: Python 版本 (major, minor, patch)

    Returns:
        site-packages 目录路径列表
    """
    paths = []

    # 判断是否为 conda 环境
    python_dir = os.path.dirname(python_path)
    if os.name == 'nt':
        env_dir = os.path.dirname(python_dir)
    else:
        env_dir = os.path.dirname(os.path.dirname(python_dir))

    # 检查是否包含 "conda" 或 "envs"
    if 'conda' in python_dir.lower() or 'envs' in python_dir:
        version_dir = f"python{version[0]}.{version[1]}"
        if os.name == 'nt':  # Windows
            paths.append(os.path.join(env_dir, "Lib", "site-packages"))
        else:  # Linux/macOS
            paths.append(os.path.join(env_dir, "lib", version_dir, "site-packages"))
    else:
        # 系统 Python 或 venv
        if os.name == 'nt':
            paths.append(os.path.join(env_dir, "Lib", "site-packages"))
        else:
            version_dir = f"python{version[0]}.{version[1]}"
            paths.append(os.path.join(env_dir, "lib", version_dir, "site-packages"))

    return [p for p in paths if os.path.isdir(p)]


def detect_all_python_environments(verbose: bool = False) -> List[PythonEnvironment]:
    """
    检测所有符合要求的 Python 环境

    Args:
        verbose: 是否输出详细错误信息

    Returns:
        排序后的 Python 环境列表

    Raises:
        NoValidPythonError: 未找到符合条件的 Python 环境
    """
    all_envs = []

    if verbose:
        print("=" * 60)
        print("开始检测 Python 环境...")
        print("=" * 60)

    # 收集所有来源的环境
    if verbose:
        print("\n[1/3] 检测 conda 环境...")
    try:
        conda_envs = detect_conda_envs(verbose)
        all_envs.extend(conda_envs)
        if verbose:
            print(f"  找到 {len(conda_envs)} 个 conda 环境")
    except Exception as e:
        if verbose:
            print(f"  conda 环境检测异常: {e}", file=sys.stderr)

    if verbose:
        print("\n[2/3] 检测虚拟环境...")
    try:
        venv_envs = detect_venv(verbose)
        all_envs.extend(venv_envs)
        if verbose:
            print(f"  找到 {len(venv_envs)} 个虚拟环境")
    except Exception as e:
        if verbose:
            print(f"  虚拟环境检测异常: {e}", file=sys.stderr)

    if verbose:
        print("\n[3/3] 检测系统 Python...")
    try:
        system_envs = detect_system_python(verbose)
        all_envs.extend(system_envs)
        if verbose:
            print(f"  找到 {len(system_envs)} 个系统 Python")
    except Exception as e:
        if verbose:
            print(f"  系统 Python 检测异常: {e}", file=sys.stderr)

    if not all_envs:
        msg = "未找到 Python 3.7.16+ 环境，请先安装"
        if verbose:
            print(f"\n[错误] {msg}", file=sys.stderr)
        raise NoValidPythonError(msg)

    # 去重
    seen_paths = set()
    unique_envs = []
    for env in all_envs:
        if env.python_path not in seen_paths:
            unique_envs.append(env)
            seen_paths.add(env.python_path)

    # 排序
    sorted_envs = sort_environments(unique_envs)

    if verbose:
        print("\n" + "=" * 60)
        print(f"检测完成，共找到 {len(sorted_envs)} 个符合要求的 Python 环境：")
        print("=" * 60)
        for i, env in enumerate(sorted_envs, 1):
            active_mark = " [当前激活]" if env.is_active else ""
            print(f"  {i}. {env.source}: {env.name} ({env.version}){active_mark}")
        print("=" * 60)

    return sorted_envs


def display_environments(envs: List[PythonEnvironment]) -> str:
    """
    生成环境选择界面的显示文本

    Args:
        envs: Python 环境列表

    Returns:
        显示文本
    """
    lines = []
    lines.append("检测到以下 Python 环境：")
    lines.append("")

    for i, env in enumerate(envs, 1):
        active_mark = " [当前激活]" if env.is_active else ""
        lines.append(f"{i}. {env.source}: {env.name} ({env.version}){active_mark}")

    lines.append("")
    lines.append(f"请选择目标 Python 环境 [1-{len(envs)}, 默认=1]:")

    return '\n'.join(lines)


def display_site_packages(paths: List[str], jl_installed: List[bool]) -> str:
    """
    生成 site-packages 选择界面的显示文本

    Args:
        paths: site-packages 路径列表
        jl_installed: 对应路径是否已安装 JLTestLibrary

    Returns:
        显示文本
    """
    lines = []
    lines.append("检测到 site-packages 目录：")
    lines.append("")

    for i, (path, has_jl) in enumerate(zip(paths, jl_installed), 1):
        jl_status = " [JLTestLibrary 已存在]" if has_jl else ""
        lines.append(f"{i}. {path}{jl_status}")

    lines.append("")
    lines.append(f"请选择目标目录 [1-{len(paths)}, 默认=1]:")

    return '\n'.join(lines)


def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Python 环境检测工具")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="输出格式")
    parser.add_argument("--site-packages", action="store_true",
                       help="检测 site-packages 目录")
    parser.add_argument("--python-path", type=str,
                       help="指定要检测 site-packages 的 Python 路径")

    args = parser.parse_args()

    try:
        # 检测 site-packages (单独模式)
        if args.site_packages:
            # 如果指定了 python-path，使用它；否则使用第一个环境
            target_python = args.python_path
            if not target_python:
                envs = detect_all_python_environments()
                if envs:
                    target_python = envs[0].python_path

            if target_python:
                paths = get_site_packages_paths(target_python)
                jl_installed = [
                    os.path.exists(os.path.join(p, "JLTestLibrary")) for p in paths
                ]

                if args.format == "json":
                    import json
                    print(json.dumps({
                        "site_packages": paths,
                        "jl_installed": jl_installed
                    }, indent=2))
                else:
                    print(display_site_packages(paths, jl_installed))
            return

        # 检测 Python 环境 (默认模式)
        envs = detect_all_python_environments()

        if args.format == "json":
            import json
            print(json.dumps([e.to_dict() for e in envs], indent=2))
        else:
            print(display_environments(envs))

    except PythonDetectionError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()