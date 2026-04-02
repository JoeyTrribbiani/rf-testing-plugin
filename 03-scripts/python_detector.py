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


def get_python_version(python_path: str) -> Optional[Tuple[int, int, int]]:
    """
    获取指定 Python 的版本

    Args:
        python_path: Python 可执行文件路径

    Returns:
        (major, minor, patch) 或 None
    """
    try:
        result = subprocess.run(
            [python_path, "--version"],
            capture_output=True,
            text=True,
            timeout=5
        )
        # 检查命令是否成功
        if result.returncode != 0:
            return None
        # 版本信息在 stderr
        version_string = (result.stderr or "").strip() or (result.stdout or "").strip()
        if not version_string:
            return None
        return parse_python_version(version_string)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None


def detect_conda_envs() -> List[PythonEnvironment]:
    """
    检测所有 conda 环境

    Returns:
        符合条件的 conda 环境列表
    """
    envs = []

    # 获取 conda 命令路径
    conda_cmd = os.environ.get('CONDA_EXE', 'conda')
    if not shutil.which(conda_cmd):
        return envs

    # 获取当前激活环境
    active_env_name = os.environ.get('CONDA_DEFAULT_ENV', '')

    # 列出所有环境
    try:
        result = subprocess.run(
            [conda_cmd, 'env', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
    except (subprocess.TimeoutExpired, OSError):
        return envs

    # 解析环境列表
    for line in result.stdout.split('\n'):
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
            continue

        version = get_python_version(python_path)
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


def detect_system_python() -> List[PythonEnvironment]:
    """
    检测系统安装的 Python

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
            version = get_python_version(python_path)
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

    # 2. 检测常见安装路径
    search_paths = get_common_python_paths()
    for pattern in search_paths:
        for path in glob.glob(pattern):
            if path not in seen_paths:
                version = get_python_version(path)
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

    return envs


def get_common_python_paths() -> List[str]:
    """
    获取常见的 Python 安装路径模式

    Returns:
        路径模式列表
    """
    if os.name == 'nt':  # Windows
        return [
            r'C:\Python3*\python.exe',
            r'C:\Python*\python.exe',
            r'C:\Program Files\Python*\python.exe',
            r'C:\Program Files (x86)\Python*\python.exe',
            os.path.expanduser(r'~/AppData/Local/Programs/Python/Python*/python.exe')
        ]
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


def detect_venv() -> List[PythonEnvironment]:
    """
    检测当前激活的虚拟环境（venv）

    Returns:
        符合条件的虚拟环境列表
    """
    envs = []

    venv_path = os.environ.get('VIRTUAL_ENV')
    if not venv_path:
        return envs

    # 确定 Python 可执行文件路径
    if os.name == 'nt':  # Windows
        python_path = os.path.join(venv_path, 'Scripts', 'python.exe')
    else:  # Linux/macOS
        python_path = os.path.join(venv_path, 'bin', 'python')

    if os.path.exists(python_path):
        version = get_python_version(python_path)
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
            text=True,
            timeout=10
        )

        if result.returncode == 0:
            paths = result.stdout.strip().split('\n')
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


def detect_all_python_environments() -> List[PythonEnvironment]:
    """
    检测所有符合要求的 Python 环境

    Returns:
        排序后的 Python 环境列表

    Raises:
        NoValidPythonError: 未找到符合条件的 Python 环境
    """
    all_envs = []

    # 收集所有来源的环境
    all_envs.extend(detect_conda_envs())
    all_envs.extend(detect_venv())
    all_envs.extend(detect_system_python())

    if not all_envs:
        raise NoValidPythonError("未找到 Python 3.7.16+ 环境，请先安装")

    # 去重
    seen_paths = set()
    unique_envs = []
    for env in all_envs:
        if env.python_path not in seen_paths:
            unique_envs.append(env)
            seen_paths.add(env.python_path)

    # 排序
    return sort_environments(unique_envs)


def display_environments(envs: List[PythonEnvironment]) -> str:
    """
    生成环境选择界面的显示文本

    Args:
        envs: Python 环境列表

    Returns:
        显示文本
    """
    lines = []
    lines.append("Detected Python environments:")
    lines.append("")

    for i, env in enumerate(envs, 1):
        active_mark = " [Active]" if env.is_active else ""
        lines.append(f"{i}. {env.source}: {env.name} ({env.version}){active_mark}")

    lines.append("")
    lines.append(f"Select target Python environment, default is 1:")

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
    lines.append("Detected site-packages directories:")
    lines.append("")

    for i, (path, has_jl) in enumerate(zip(paths, jl_installed), 1):
        jl_status = " [JLTestLibrary exists]" if has_jl else ""
        lines.append(f"{i}. {path}{jl_status}")

    lines.append("")
    lines.append(f"Select target directory, default is 1:")

    return '\n'.join(lines)


def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="Python 环境检测工具")
    parser.add_argument("--format", choices=["text", "json"], default="text",
                       help="输出格式")
    parser.add_argument("--site-packages", action="store_true",
                       help="检测 site-packages 目录")

    args = parser.parse_args()

    try:
        # 检测 Python 环境
        envs = detect_all_python_environments()

        if args.format == "json":
            import json
            print(json.dumps([e.to_dict() for e in envs], indent=2))
        else:
            print(display_environments(envs))

        # 检测 site-packages
        if args.site_packages and envs:
            paths = get_site_packages_paths(envs[0].python_path)
            jl_installed = [
                os.path.exists(os.path.join(p, "JLTestLibrary")) for p in paths
            ]
            print()
            print(display_site_packages(paths, jl_installed))

    except PythonDetectionError as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()