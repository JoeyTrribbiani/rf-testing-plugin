#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
JLTestLibrary 安装模块
自动检测和安装 JLTestLibrary 到目标 Python 环境
"""

import os
import sys
import subprocess
import zipfile
from typing import List, Tuple


class JLTestLibraryInstallError(Exception):
    """JLTestLibrary 安装失败"""
    pass


def check_jl_installed(site_packages_paths: List[str]) -> List[Tuple[str, bool]]:
    """
    检查 JLTestLibrary 是否已安装

    Args:
        site_packages_paths: site-packages 目录列表

    Returns:
        [(路径, 是否已安装), ...] 列表
    """
    result = []
    for path in site_packages_paths:
        jl_path = os.path.join(path, "JLTestLibrary")
        result.append((path, os.path.exists(jl_path)))
    return result


def install_jl_library(zip_path: str, target_dir: str, python_path: str) -> bool:
    """
    安装 JLTestLibrary 到目标目录

    Args:
        zip_path: JLTestLibrary.zip 路径
        target_dir: 目标 site-packages 目录
        python_path: Python 可执行文件路径（用于验证）

    Returns:
        是否安装成功
    """
    if not os.path.exists(zip_path):
        print(f"JLTestLibrary.zip 不存在: {zip_path}")
        return False

    # 检查是否已安装
    jl_path = os.path.join(target_dir, "JLTestLibrary")
    if os.path.exists(jl_path):
        print(f"JLTestLibrary 已存在: {jl_path}")
        return True

    # 解压
    print(f"解压 JLTestLibrary 到: {target_dir}")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
    except (zipfile.BadZipFile, OSError) as e:
        print(f"解压失败: {e}")
        return False

    # 验证安装
    try:
        result = subprocess.run(
            [python_path, "-c", "import JLTestLibrary; print('JLTestLibrary 安装成功')"],
            capture_output=True,
            text=True,
            timeout=10
        )
        if result.returncode == 0:
            print(result.stdout.strip())
            return True
        else:
            print(f"验证失败: {result.stderr}")
            return False
    except (subprocess.TimeoutExpired, OSError) as e:
        print(f"验证失败: {e}")
        return False


def main():
    """命令行主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="JLTestLibrary 安装工具")
    parser.add_argument("zip_path", help="JLTestLibrary.zip 路径")
    parser.add_argument("python_path", help="目标 Python 可执行文件路径")
    parser.add_argument("--target", help="目标 site-packages 目录（自动检测）")

    args = parser.parse_args()

    if args.target:
        target_dir = args.target
    else:
        # 自动检测 site-packages
        from python_detector import get_site_packages_paths
        paths = get_site_packages_paths(args.python_path)
        if not paths:
            print("错误: 无法检测 site-packages 目录", file=sys.stderr)
            sys.exit(1)
        target_dir = paths[0]

    # 检查已安装状态
    jl_status = check_jl_installed([target_dir])
    path, installed = jl_status[0]

    if installed:
        print(f"JLTestLibrary 已存在于: {path}")
        sys.exit(0)

    # 安装
    success = install_jl_library(args.zip_path, target_dir, args.python_path)
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()