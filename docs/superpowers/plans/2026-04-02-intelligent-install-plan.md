# 智能安装配置实现计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标**: 增强 install.sh 和 install.bat，实现 Python 多环境智能检测和 JLTestLibrary 自动安装

**架构**: 创建跨平台 Python 检测模块（python_detector.py）和 JLTestLibrary 安装模块（jl_installer.py），安装脚本调用这些模块进行智能检测和安装。

**Tech Stack**: Python 3.7.16+, Bash (Linux/macOS), Batch (Windows), subprocess, os, sys, glob

---

## 文件结构

| 文件路径 | 职责 | 类型 |
|---------|------|------|
| `03-scripts/python_detector.py` | Python 环境检测（conda/system/venv）、优先级排序、site-packages 路径检测 | 新建 |
| `03-scripts/jl_installer.py` | JLTestLibrary 安装、状态检测、验证 | 新建 |
| `install.sh` | 集成 python_detector 和 jl_installer，更新 Python 检测和 JLTestLibrary 安装流程 | 修改 |
| `install.bat` | 集成 python_detector 和 jl_installer，更新 Python 检测和 JLTestLibrary 安装流程 | 修改 |
| `INSTALL.md` | 更新安装文档，说明智能检测功能 | 修改 |
| `README.md` | 更新使用说明 | 修改 |

---

## Task 1: 创建 python_detector.py 核心模块

**Files:**
- Create: `03-scripts/python_detector.py`

- [ ] **Step 1: 创建文件头部和基础结构**

```python
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
```

- [ ] **Step 2: 添加版本解析函数**

```python
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
        # 版本信息在 stderr
        version_string = result.stderr.strip() or result.stdout.strip()
        return parse_python_version(version_string)
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        return None
```

- [ ] **Step 3: 添加 conda 环境检测函数**

```python
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
```

- [ ] **Step 4: 添加系统 Python 检测函数**

```python
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
```

- [ ] **Step 5: 添加虚拟环境检测函数**

```python
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
```

- [ ] **Step 6: 添加优先级计算和排序函数**

```python
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
```

- [ ] **Step 7: 添加 site-packages 检测函数**

```python
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
```

- [ ] **Step 8: 添加主检测函数和显示函数**

```python
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
    lines.append("检测到以下 Python 环境：")
    lines.append("")

    for i, env in enumerate(envs, 1):
        if i == 1:
            lines.append(f"[推荐] {i}. {env}")
        else:
            lines.append(f"       {i}. {env}")

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
        if i == 1:
            marker = "[推荐] "
        else:
            marker = "       "

        jl_status = " [JLTestLibrary 已存在]" if has_jl else ""
        lines.append(f"{marker}{i}. {path}{jl_status}")

    lines.append("")
    lines.append(f"请选择目标目录 [1-{len(paths)}, 默认=1]:")

    return '\n'.join(lines)
```

- [ ] **Step 9: 添加命令行主函数**

```python
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
```

- [ ] **Step 10: 提交 python_detector.py**

```bash
git add 03-scripts/python_detector.py
git commit -m "feat: 添加 Python 环境智能检测模块"
```

---

## Task 2: 创建 jl_installer.py 模块

**Files:**
- Create: `03-scripts/jl_installer.py`

- [ ] **Step 1: 创建文件头部和基础结构**

```python
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
import shutil
from typing import Optional, List, Tuple


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
```

- [ ] **Step 2: 提交 jl_installer.py**

```bash
git add 03-scripts/jl_installer.py
git commit -m "feat: 添加 JLTestLibrary 智能安装模块"
```

---

## Task 3: 更新 install.sh 集成智能检测

**Files:**
- Modify: `install.sh:39-53` (check_python_version 函数)

- [ ] **Step 1: 替换 check_python_version 函数**

```bash
# 检查 Python 环境（更新）
check_python_environment() {
    log_info "检测 Python 环境..."

    # 使用 Python 检测模块
    local detection_output
    detection_output=$(python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --format json 2>/dev/null)

    if [ $? -ne 0 ]; then
        log_error "Python 环境检测失败"
        return 1
    fi

    # 显示检测结果
    echo ""
    python3 "$PLUGIN_DIR/03-scripts/python_detector.py"
    echo ""

    # 获取用户选择
    read -p "请选择目标 Python 环境 [默认=1]: " choice
    choice=${choice:-1}

    # 解析选择结果
    SELECTED_ENV=$(echo "$detection_output" | python3 -c "
import json, sys
data = json.load(sys.stdin)
if len(data) >= $choice:
    print(json.dumps(data[$choice - 1]))
else:
    print('', end='')
")

    if [ -z "$SELECTED_ENV" ]; then
        log_error "无效的选择"
        return 1
    fi

    # 提取 Python 路径
    SELECTED_PYTHON_PATH=$(echo "$SELECTED_ENV" | python3 -c "import json,sys; print(json.load(sys.stdin)['python_path'])")
    SELECTED_PYTHON_VERSION=$(echo "$SELECTED_ENV" | python3 -c "import json,sys; print(json.load(sys.stdin)['version'])")

    log_info "已选择: Python $SELECTED_PYTHON_VERSION"
    log_info "路径: $SELECTED_PYTHON_PATH"
    echo ""

    # 设置 Python 和 pip 命令
    PYTHON_CMD="$SELECTED_PYTHON_PATH"
    PIP_CMD=$(python3 -c "import os; print(os.path.join(os.path.dirname('$SELECTED_PYTHON_PATH'), 'pip'))" | sed 's/python/pip/g')
}
```

- [ ] **Step 2: 更新 install_python_deps 函数使用检测到的 Python**

```bash
# 安装 Python 依赖（更新）
install_python_deps() {
    log_info "安装 Python 依赖..."

    local deps=("pandas" "openpyxl")

    for dep in "${deps[@]}"; do
        if "$PIP_CMD" show "$dep" &> /dev/null; then
            log_info "$dep 已安装"
        else
            log_info "安装 $dep..."
            "$PIP_CMD" install "$dep" || {
                log_error "安装 $dep 失败"
                exit 1
            }
        fi
    done

    # 安装 Robot Framework
    if "$PIP_CMD" show "robotframework" &> /dev/null; then
        log_info "robotframework 已安装"
    else
        log_info "安装 robotframework..."
        "$PIP_CMD" install "robotframework>=3.2.2,<4.0.0" || {
            log_error "安装 robotframework 失败"
            exit 1
        }
    fi

    log_info "Python 依赖安装完成"
}
```

- [ ] **Step 3: 更新 install_jltestlibrary 函数**

```bash
# 安装 JLTestLibrary（更新）
install_jltestlibrary() {
    log_info "安装 JLTestLibrary..."

    local jl_library="$PLUGIN_DIR/03-scripts/JLTestLibrary.zip"

    if [ ! -f "$jl_library" ]; then
        log_warn "JLTestLibrary.zip 不存在，跳过安装"
        return
    fi

    # 检测 site-packages 目录
    log_info "检测 site-packages 目录..."

    # 获取 site-packages 列表
    local sp_output
    sp_output=$(python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --site-packages --format json 2>/dev/null)

    if [ $? -ne 0 ]; then
        log_warn "无法自动检测 site-packages 目录，请手动安装"
        log_info "手动安装命令："
        log_info "  unzip $jl_library -d \$HOME/Library/Python/3.7/site-packages/"
        return
    fi

    # 显示 site-packages 选项
    echo ""
    python3 "$PLUGIN_DIR/03-scripts/python_detector.py" --site-packages 2>/dev/null | tail -n +2
    echo ""

    # 获取用户选择
    read -p "请选择目标目录 [默认=1]: " sp_choice
    sp_choice=${sp_choice:-1}

    # 解析选择的路径
    local target_dir
    target_dir=$(echo "$sp_output" | python3 -c "
import json, sys
data = json.load(sys.stdin)
paths = data.get('site_packages', [])
if len(paths) >= $sp_choice:
    print(paths[$sp_choice - 1])
")

    if [ -z "$target_dir" ]; then
        log_warn "无效的选择，跳过安装"
        return
    fi

    # 检查是否已安装
    local jl_path="$target_dir/JLTestLibrary"
    if [ -d "$jl_path" ]; then
        log_warn "JLTestLibrary 已存在于: $jl_path"
        return
    fi

    # 安装
    log_info "解压 JLTestLibrary 到: $target_dir"
    unzip -q "$jl_library" -d "$target_dir" || {
        log_error "解压失败，请检查权限"
        return
    }

    # 验证
    "$PYTHON_CMD" -c "import JLTestLibrary" 2>/dev/null || {
        log_error "JLTestLibrary 安装验证失败"
        return
    }

    log_info "JLTestLibrary 安装成功"
}
```

- [ ] **Step 4: 更新主流程函数**

```bash
# 主流程（更新）
main() {
    log_info "开始安装 $PLUGIN_NAME..."

    # 检查环境
    check_command git
    check_python_environment  # 替换原有的 python3/pip3 检查

    # 安装步骤
    install_python_deps
    clone_plugin
    configure_plugin
    install_jltestlibrary

    # 询问是否配置环境变量和 MCP
    echo ""
    read -p "是否现在配置环境变量和 MCP 服务器？(y/n): " DO_CONFIG
    if [[ $DO_CONFIG =~ ^[Yy]$ ]]; then
        configure_env_and_mcp
    fi

    # 验证
    if verify_installation; then
        print_usage
        log_info "安装成功！"
    else
        log_error "安装验证失败，请检查上述错误"
        exit 1
    fi
}
```

- [ ] **Step 5: 更新 verify_installation 函数使用检测到的 Python**

```bash
# 验证安装（更新）
verify_installation() {
    log_info "验证安装..."

    # 检查插件目录
    if [ ! -d "$PLUGIN_DIR" ]; then
        log_error "插件目录不存在: $PLUGIN_DIR"
        return 1
    fi

    # 检查插件文件
    local plugin_files=(
        "$PLUGIN_DIR/05-plugins/rf-testing/.mcp.json"
        "$PLUGIN_DIR/05-plugins/rf-testing/.claude-plugin/plugin.json"
        "$PLUGIN_DIR/05-plugins/rf-testing/commands/start.md"
    )

    for plugin_file in "${plugin_files[@]}"; do
        if [ -f "$plugin_file" ]; then
            log_info "✓ $(basename $plugin_file)"
        else
            log_warn "✗ 插件文件不存在: $plugin_file"
        fi
    done

    # 检查 Python 依赖
    "$PYTHON_CMD" -c "import pandas, openpyxl, robotframework" 2>/dev/null || {
        log_error "Python 依赖验证失败"
        return 1
    }

    log_info "✓ Python 依赖验证通过"

    return 0
}
```

- [ ] **Step 6: 删除原有的 check_python_version 和 check_command 对 python3/pip3 的检查**

```bash
# 删除原主流程中的以下行：
# check_command python3
# check_command pip3
# check_python_version
```

- [ ] **Step 7: 提交 install.sh**

```bash
git add install.sh
git commit -m "feat: 集成 Python 智能检测和 JLTestLibrary 自动安装"
```

---

## Task 4: 更新 install.bat 集成智能检测

**Files:**
- Modify: `install.bat:15-67`

- [ ] **Step 1: 替换 Python 检测部分**

```batch
REM 检查 Python 环境（更新）
:DetectPythonEnvironment
echo [INFO] 检测 Python 环境...

REM 调用 Python 检测模块
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json > "%TEMP%\env_detection.json" 2>nul

if errorlevel 1 (
    echo [ERROR] Python 环境检测失败
    echo [INFO] 请确保 Python 3.7.16+ 已安装
    exit /b 1
)

REM 显示检测结果
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py"
echo.

REM 获取用户选择
set /p "PYTHON_CHOICE=请选择目标 Python 环境 [默认=1]: "
if "%PYTHON_CHOICE%"=="" set PYTHON_CHOICE=1

REM 解析选择的 Python 路径
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['python_path'] if len(data) >= %PYTHON_CHOICE% else '')"') do set SELECTED_PYTHON=%%p

if "%SELECTED_PYTHON%"=="" (
    echo [ERROR] 无效的选择
    exit /b 1
)

REM 获取版本信息
for /f "tokens=*" %%v in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['version'])"') do set PYTHON_VERSION=%%v

echo [INFO] 已选择: Python %PYTHON_VERSION%
echo [INFO] 路径: %SELECTED_PYTHON%
echo.

REM 设置 Python 和 pip 命令
set PYTHON_CMD=%SELECTED_PYTHON%
for /f "tokens=*" %%i in ('python -c "import os; print(os.path.join(os.path.dirname(r'%SELECTED_PYTHON%'), 'pip'))"') do set PIP_CMD=%%i
if not exist "%PIP_CMD%" set PIP_CMD=pip

goto :eof
```

- [ ] **Step 2: 更新依赖安装部分**

```batch
REM 安装 Python 依赖（更新）
echo [INFO] 安装 Python 依赖...

REM 检查 pandas
"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas 已安装
)

REM 检查 openpyxl
"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl 已安装
)

REM 检查 robotframework
"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework 已安装
)

echo [INFO] Python 依赖安装完成
echo.
```

- [ ] **Step 3: 更新 JLTestLibrary 安装部分**

```batch
REM 安装 JLTestLibrary（更新）
echo [INFO] 安装 JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip 不存在，跳过安装
    goto configure_skills
)

REM 检测 site-packages 目录
echo [INFO] 检测 site-packages 目录...
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --format json > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] 无法自动检测 site-packages 目录，请手动安装
    echo [INFO] 手动安装命令：
    echo   unzip %JL_LIBRARY% -d %%USERPROFILE%%\AppData\Local\Programs\Python\Python37\Lib\site-packages\
    goto configure_skills
)

REM 显示 site-packages 选项
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages
echo.

REM 获取用户选择
set /p "SP_CHOICE=请选择目标目录 [默认=1]: "
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM 解析选择的路径
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\site_packages.json', encoding='utf-8')); print(data['site_packages'][%SP_CHOICE% - 1])"') do set TARGET_DIR=%%p

if "%TARGET_DIR%"=="" (
    echo [WARN] 无效的选择，跳过安装
    goto configure_skills
)

REM 检查是否已安装
if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary 已存在于: %TARGET_DIR%\JLTestLibrary
    goto configure_skills
)

REM 解压
echo [INFO] 解压 JLTestLibrary 到: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] 解压失败，请检查权限
    goto configure_skills
)

REM 验证
"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] JLTestLibrary 安装验证失败
) else (
    echo [INFO] JLTestLibrary 安装成功
)

echo.
```

- [ ] **Step 4: 更新主流程**

```batch
REM 主流程（更新）
echo [INFO] 开始安装 %PLUGIN_NAME%...
echo.

REM 调用 Python 环境检测
call :DetectPythonEnvironment

REM 检查 git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git 未安装，请先安装 git
    exit /b 1
)

REM 克隆插件仓库
echo [INFO] 克隆插件仓库...

if exist "%PLUGIN_DIR%" (
    echo [WARN] 插件目录已存在: %PLUGIN_DIR%
    set /p "REPLY=是否删除并重新克隆？(y/n): "
    if /i "!REPLY!"=="y" (
        rmdir /s /q "%PLUGIN_DIR%"
    ) else (
        echo [INFO] 跳过克隆步骤
        goto install_deps
    )
)

if not exist "%USERPROFILE%\.claude\plugins\" (
    mkdir "%USERPROFILE%\.claude\plugins\"
)

git clone "%PLUGIN_REPO%" "%PLUGIN_DIR%"
if errorlevel 1 (
    echo [ERROR] 克隆失败，请检查网络连接和仓库地址
    exit /b 1
)

echo [INFO] 插件克隆完成: %PLUGIN_DIR%
echo.

:install_deps
REM 安装 Python 依赖
call :InstallDependencies

REM 安装 JLTestLibrary
call :InstallJLTestLibrary

:configure_skills
REM 配置 Claude Skills（已弃用，使用 marketplace）
echo [INFO] 提示：新版本推荐通过 marketplace 安装插件
echo [INFO] 在 Claude Code 中执行：
echo   /plugin marketplace add .
echo   /plugin install rf-testing
echo.
```

- [ ] **Step 5: 添加辅助函数**

```batch
REM 安装依赖函数
:InstallDependencies
echo [INFO] 安装 Python 依赖...

"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas 已安装
)

"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl 已安装
)

"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework 已安装
)

echo [INFO] Python 依赖安装完成
echo.
goto :eof

REM 安装 JLTestLibrary 函数
:InstallJLTestLibrary
echo [INFO] 安装 JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip 不存在，跳过安装
    goto :eof
)

REM 检测 site-packages 目录
echo [INFO] 检测 site-packages 目录...
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --format json > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] 无法自动检测 site-packages 目录，跳过安装
    goto :eof
)

REM 显示选项
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages
echo.

set /p "SP_CHOICE=请选择目标目录 [默认=1]: "
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM 解析路径
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\site_packages.json', encoding='utf-8')); print(data['site_packages'][%SP_CHOICE% - 1])"') do set TARGET_DIR=%%p

if "%TARGET_DIR%"=="" (
    echo [WARN] 无效的选择，跳过安装
    goto :eof
)

REM 检查已安装
if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary 已存在，跳过安装
    goto :eof
)

REM 解压
echo [INFO] 解压到: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] 解压失败，请检查权限
    goto :eof
)

REM 验证
"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] 验证失败
) else (
    echo [INFO] JLTestLibrary 安装成功
)

echo.
goto :eof
```

- [ ] **Step 6: 更新验证部分使用检测到的 Python**

```batch
REM 验证安装
echo [INFO] 验证安装...

if not exist "%PLUGIN_DIR%" (
    echo [ERROR] 插件目录不存在: %PLUGIN_DIR%
    goto failed
)

REM 检查插件文件
set PLUGIN_FILES[0]=%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json
set PLUGIN_FILES[1]=%PLUGIN_DIR%\05-plugins\rf-testing\.claude-plugin\plugin.json
set PLUGIN_FILES[2]=%PLUGIN_DIR%\05-plugins\rf-testing\commands\start.md

for /L %%i in (0,1,2) do (
    if exist "!PLUGIN_FILES[%%i]!" (
        echo [INFO] 插件文件存在: %%~nxi!PLUGIN_FILES[%%i]!
    ) else (
        echo [WARN] 插件文件不存在: !PLUGIN_FILES[%%i]!
    )
)

REM 检查 Python 依赖（使用检测到的 Python）
"%PYTHON_CMD%" -c "import pandas, openpyxl, robotframework" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 依赖验证失败
    goto failed
)

echo [INFO] Python 依赖验证通过
echo.
```

- [ ] **Step 7: 提交 install.bat**

```bash
git add install.bat
git commit -m "feat: 集成 Python 智能检测和 JLTestLibrary 自动安装"
```

---

## Task 5: 更新 INSTALL.md 文档

**Files:**
- Modify: `INSTALL.md:36-43` (安装脚本功能列表)

- [ ] **Step 1: 更新安装脚本功能说明**

```markdown
安装脚本将自动完成：
- ✓ Python 3.7.16+ 环境智能检测（支持 conda、venv、多版本系统 Python）
- ✓ Python 环境优先选择（推荐最接近 3.7.16+ 的版本）
- ✓ site-packages 目录自动检测和选择
- ✓ Robot Framework 3.2.2 安装
- ✓ 基础依赖安装（pandas, openpyxl）
- ✓ JLTestLibrary 自动安装到正确位置
- ✓ 环境变量和 MCP 服务器一键配置
- ✓ 验证安装
```

- [ ] **Step 2: 添加智能检测说明章节**

在 "环境变量配置" 章节前添加：

```markdown
## Python 环境智能检测

安装脚本会自动检测系统中所有符合条件的 Python 环境（3.7.16+），包括：

- **Conda 环境**：自动检测所有 conda 环境，标记当前激活环境
- **系统 Python**：检测系统中安装的多个 Python 版本
- **虚拟环境（venv）**：检测当前激活的虚拟环境

### 优先级选择策略

脚本会按以下优先级自动推荐 Python 环境：

1. 当前激活的 conda 环境
2. 匹配 Python 3.7.x 的 conda 环境（最接近要求版本）
3. 匹配 Python 3.8.x 的系统 Python
4. 其他符合条件的 Python 版本

### 用户选择流程

```
1. 运行安装脚本
   ./install.sh  # 或 install.bat

2. 显示所有检测到的 Python 环境

   检测到以下 Python 环境：

   [推荐] 1. conda: rf-env (3.7.18)  [当前激活]
          2. conda: py37 (3.7.16)
          3. system: /usr/bin/python3.8 (3.8.10)

3. 用户确认或选择
   → 按回车使用推荐，或输入编号选择其他

4. 自动检测 site-packages 目录

   检测到 site-packages 目录：

   [推荐] 1. D:\...\python37\Lib\site-packages
          [JLTestLibrary 已存在]
          2. D:\...\Anaconda3\Lib\site-packages

5. 自动安装 JLTestLibrary 到选定目录
```

### 手动指定 Python

如果需要使用特定 Python，可以在运行脚本前设置环境变量：

```bash
# Linux/macOS
export RF_PYTHON_PATH=/path/to/python3

# Windows
set RF_PYTHON_PATH=C:\path\to\python.exe
```
```

- [ ] **Step 3: 更新 JLTestLibrary 安装说明**

```markdown
### 自定义库安装

**安装方式：**

JLTestLibrary 的安装现在由安装脚本自动处理：

1. 脚本会自动检测选定 Python 的 site-packages 目录
2. 显示所有可用的 site-packages 目录供选择
3. 自动解压 JLTestLibrary.zip 到目标目录
4. 验证安装结果

**手动安装（如需）：**

```bash
# 解压到 Python site-packages 目录
unzip 03-scripts/JLTestLibrary.zip -d $HOME/Library/Python/3.7/site-packages/

# Windows 系统
unzip 03-scripts/JLTestLibrary.zip -d %USERPROFILE%\AppData\Local\Programs\Python\Python37\Lib\site-packages\
```

**安装验证：**

```bash
# 使用选定的 Python 验证
python -c "import JLTestLibrary; print('JLTestLibrary 安装成功')"
```
```

- [ ] **Step 4: 提交 INSTALL.md**

```bash
git add INSTALL.md
git commit -m "docs: 更新安装文档，说明智能检测功能"
```

---

## Task 6: 更新 README.md

**Files:**
- Modify: `README.md:38-44`

- [ ] **Step 1: 更新快速开始章节**

```markdown
### 3. 安装依赖

#### 使用安装脚本（推荐）

安装脚本会自动：

1. 智能检测系统中所有符合条件的 Python 环境（3.7.16+）
2. 自动推荐最合适的 Python 版本
3. 自动检测 site-packages 目录
4. 自动安装所有依赖
5. 自动安装 JLTestLibrary
6. 可选配置环境变量和 MCP 服务器

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

#### 手动安装

详见 `requirements.txt`：

```bash
pip install -r requirements.txt
```

手动安装 JLTestLibrary：
```bash
unzip 03-scripts/JLTestLibrary.zip -d $HOME/Library/Python/3.7/site-packages/
```
```

- [ ] **Step 2: 添加 Python 环境检测说明**

在"配置步骤"章节后添加：

```markdown
## Python 环境智能检测

安装脚本支持以下 Python 环境的自动检测：

| 环境类型 | 说明 | 示例路径 |
|---------|------|---------|
| Conda | 所有 conda 环境 | `conda: rf-env (3.7.18)` |
| System | 系统安装的 Python | `system: /usr/bin/python3.8` |
| Venv | 虚拟环境 | `venv: /path/to/venv` |

脚本会自动优先选择最接近 3.7.16+ 的版本，确保 JLTestLibrary 兼容性。

### 检测示例

```
检测到以下 Python 环境：

[推荐] 1. conda: rf-env (3.7.18)  [当前激活]
       2. conda: py37 (3.7.16)
       3. system: /usr/bin/python3.8 (3.8.10)

请选择目标 Python 环境 [1-3, 默认=1]:
```
```

- [ ] **Step 3: 提交 README.md**

```bash
git add README.md
git commit -m "docs: 更新 README，说明智能检测功能"
```

---

## 验收标准

- [ ] python_detector.py 能正确检测 conda 环境
- [ ] python_detector.py 能正确检测系统 Python（多版本）
- [ ] python_detector.py 能正确检测 venv 环境
- [ ] 优先级排序符合设计策略
- [ ] site-packages 路径检测准确
- [ ] install.sh 集成成功，能在 Linux/macOS 上运行
- [ ] install.bat 集成成功，能在 Windows 上运行
- [ ] JLTestLibrary 自动安装到正确位置
- [ ] 已安装 JLTestLibrary 时正确跳过
- [ ] 文档更新完整