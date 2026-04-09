# -*- coding: utf-8 -*-
"""
插件根目录查找工具
用于在不同安装场景下找到插件根目录
"""
import os
import sys
from pathlib import Path


def find_plugin_root() -> str:
    """
    查找插件根目录

    查找顺序（按优先级）:
    1. CLAUDE_PLUGIN_ROOT 环境变量
    2. __file__ 的父目录（直接执行时）
    3. __file__ 的上上级（在 scripts 目录时）
    4. 安装目录的绝对路径

    Returns:
        插件根目录的绝对路径
    """
    # 方法1: 环境变量
    if "CLAUDE_PLUGIN_ROOT" in os.environ:
        plugin_root = os.environ["CLAUDE_PLUGIN_ROOT"]
        if os.path.exists(os.path.join(plugin_root, "03-scripts")):
            return plugin_root

    # 方法2: 从 __file__ 推断
    current_file = Path(__file__).resolve()

    # 检查是否直接在 03-scripts 目录中
    if current_file.name == "find_plugin_root.py" and "03-scripts" in str(current_file.parent):
        candidate = current_file.parent.parent  # scripts 的父目录是插件根
        if os.path.exists(os.path.join(candidate, "03-scripts")):
            return str(candidate)

    # 方法3: 检查 cache 目录
    # Claude Code 通常将插件安装在 ~/.claude/plugins/<plugin-name>/
    claude_plugins = Path.home() / ".claude" / "plugins"
    if claude_plugins.exists():
        # 查找可能的位置
        for candidate in [
            claude_plugins / "rf-testing-plugin",
            claude_plugins / "cache" / "anthropic-agent-skills" / "rf-testing-plugin",
            claude_plugins / "claude-code-skills" / "rf-testing-plugin",
        ]:
            if candidate.exists() and (candidate / "03-scripts").exists():
                return str(candidate)

    # 方法4: 检查当前工作目录
    cwd = Path.cwd()
    # 如果当前目录包含 03-scripts，可能是开发目录
    if (cwd / "03-scripts").exists():
        # 检查父目录是否是插件根目录（包含 00-JL-Skills、01-RF-Skills 等）
        if (cwd / "00-JL-Skills").exists() and (cwd / "01-RF-Skills").exists():
            return str(cwd)

    # 方法5: 从 sys.path 查找
    for path in sys.path:
        path_obj = Path(path)
        # 跳过标准库路径
        if "site-packages" in str(path_obj):
            continue
        # 检查是否包含 03-scripts
        if (path_obj / "03-scripts").exists():
            # 检查是否是插件根目录
            if (path_obj / "00-JL-Skills").exists() or (path_obj / "01-RF-Skills").exists():
                return str(path_obj)

    # 如果都找不到，返回当前文件的上级目录作为默认值
    return str(current_file.parent.parent)


def get_script_path(script_name: str) -> str:
    """
    获取脚本文件的绝对路径

    Args:
        script_name: 脚本文件名（如 'rf_runner.py'）

    Returns:
        脚本文件的绝对路径，如果找不到返回 None
    """
    plugin_root = find_plugin_root()
    script_path = os.path.join(plugin_root, "03-scripts", script_name)

    if os.path.exists(script_path):
        return script_path

    # 尝试备用路径
    for backup in [
        os.path.join(plugin_root, "../../03-scripts", script_name),  # cache 中
        os.path.join(plugin_root, "../03-scripts", script_name),  # plugins 子目录
    ]:
        if os.path.exists(backup):
            return backup

    return None


if __name__ == "__main__":
    plugin_root = find_plugin_root()
    print(f"插件根目录: {plugin_root}")

    # 测试查找脚本
    for script in ["rf_runner.py", "rf_listener.py", "rf_parser.py"]:
        path = get_script_path(script)
        print(f"{script}: {path or '未找到'}")