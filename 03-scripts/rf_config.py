# -*- coding: utf-8 -*-
"""
RF Testing Plugin 配置管理模块
用于保存和读取安装时选择的 Python 环境等配置
"""
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any


# 配置文件路径
CONFIG_DIR = Path.home() / ".claude" / "rf-testing-plugin"
CONFIG_FILE = CONFIG_DIR / "config.json"


def get_config() -> Dict[str, Any]:
    """
    读取配置文件

    Returns:
        配置字典，如果不存在则返回空字典
    """
    if not CONFIG_FILE.exists():
        return {}

    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {}


def save_config(config: Dict[str, Any]) -> bool:
    """
    保存配置到文件

    Args:
        config: 配置字典

    Returns:
        是否保存成功
    """
    try:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        return True
    except IOError:
        return False


def get_python_path() -> Optional[str]:
    """
    获取保存的 Python 路径

    Returns:
        Python 可执行文件路径，如果没有配置则返回 None
    """
    config = get_config()
    python_path = config.get('python_path')

    if python_path and os.path.exists(python_path):
        return python_path

    return None


def set_python_path(python_path: str) -> bool:
    """
    保存 Python 路径

    Args:
        python_path: Python 可执行文件路径

    Returns:
        是否保存成功
    """
    config = get_config()
    config['python_path'] = python_path
    return save_config(config)


def get_python_info() -> Optional[Dict[str, Any]]:
    """
    获取保存的 Python 环境信息

    Returns:
        包含 python_path, version, pip_path 等信息的字典
    """
    config = get_config()
    python_path = config.get('python_path')

    if not python_path or not os.path.exists(python_path):
        return None

    return {
        'python_path': python_path,
        'version': config.get('python_version'),
        'pip_path': config.get('pip_path'),
        'environment_type': config.get('environment_type')
    }


def set_python_info(
    python_path: str,
    version: str,
    pip_path: str,
    environment_type: str = "unknown"
) -> bool:
    """
    保存完整的 Python 环境信息

    Args:
        python_path: Python 可执行文件路径
        version: Python 版本
        pip_path: pip 可执行文件路径
        environment_type: 环境类型 (conda/system/venv)

    Returns:
        是否保存成功
    """
    config = get_config()
    config['python_path'] = python_path
    config['python_version'] = version
    config['pip_path'] = pip_path
    config['environment_type'] = environment_type
    return save_config(config)


def clear_config() -> bool:
    """
    清除配置

    Returns:
        是否清除成功
    """
    try:
        if CONFIG_FILE.exists():
            CONFIG_FILE.unlink()
        return True
    except IOError:
        return False


# CLI 接口
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="RF Testing Plugin Config Manager")
    parser.add_argument("--get-python", action="store_true", help="获取保存的 Python 路径")
    parser.add_argument("--set-python", help="设置 Python 路径")
    parser.add_argument("--get-info", action="store_true", help="获取完整的 Python 环境信息")
    parser.add_argument("--clear", action="store_true", help="清除配置")

    args = parser.parse_args()

    if args.get_python:
        path = get_python_path()
        if path:
            print(path)
        else:
            print("未配置 Python 路径", file=sys.stderr)
            sys.exit(1)

    elif args.set_python:
        if set_python_path(args.set_python):
            print(f"Python 路径已保存: {args.set_python}")
        else:
            print("保存失败", file=sys.stderr)
            sys.exit(1)

    elif args.get_info:
        import sys
        info = get_python_info()
        if info:
            print(json.dumps(info, indent=2, ensure_ascii=False))
        else:
            print("未配置 Python 环境", file=sys.stderr)
            sys.exit(1)

    elif args.clear:
        if clear_config():
            print("配置已清除")
        else:
            print("清除失败", file=sys.stderr)
            sys.exit(1)

    else:
        # 默认显示所有配置
        config = get_config()
        if config:
            print(json.dumps(config, indent=2, ensure_ascii=False))
        else:
            print("无配置")
