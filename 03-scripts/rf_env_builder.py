# -*- coding: utf-8 -*-
"""
Robot Framework 临时环境生成器
参考 Cursor 的执行方式，生成临时环境配置脚本
"""
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, List


class RFEnvBuilder:
    """RF 临时环境构建器"""

    def __init__(self, python_path: Optional[str] = None):
        """
        初始化环境构建器

        Args:
            python_path: 指定 Python 路径
        """
        self.python_path = self._resolve_python_path(python_path)
        if not self.python_path:
            raise RuntimeError("No valid Python environment found")

    def _resolve_python_path(self, python_path: Optional[str]) -> Optional[str]:
        """解析 Python 路径"""
        if python_path and os.path.exists(python_path):
            return python_path

        # 尝试从配置文件读取
        try:
            from rf_config import get_python_path
            saved_path = get_python_path()
            if saved_path and os.path.exists(saved_path):
                return saved_path
        except ImportError:
            pass

        # 自动检测
        from python_detector import detect_all_python_environments
        envs = detect_all_python_environments()
        if envs:
            return envs[0]["python_path"]

        return None

    def get_site_packages(self) -> Optional[Path]:
        """获取 site-packages 目录"""
        # 方法1: 直接构建路径（适用于标准 conda 环境）
        try:
            python_path = Path(self.python_path)
            env_dir = python_path.parent
            site_packages = env_dir / "Lib" / "site-packages"
            if site_packages.exists():
                return site_packages
        except Exception:
            pass

        # 方法2: 使用 site 模块查询
        try:
            result = subprocess.run(
                [self.python_path, "-c", "import site; print(site.getsitepackages()[0])"],
                capture_output=True,
                text=True,
                timeout=10,
                encoding="utf-8",
                errors="replace"
            )
            if result.returncode == 0 and result.stdout:
                site_packages = result.stdout.strip()
                if site_packages and os.path.exists(site_packages):
                    return Path(site_packages)
        except Exception:
            pass

        # 方法3: 尝试 gbk 编码（Windows 中文环境）
        try:
            result = subprocess.run(
                [self.python_path, "-c", "import site; print(site.getsitepackages()[0])"],
                capture_output=True,
                timeout=10
            )
            if result.returncode == 0 and result.stdout:
                site_packages = result.stdout.decode("gbk", errors="replace").strip()
                if site_packages and os.path.exists(site_packages):
                    return Path(site_packages)
        except Exception:
            pass

        return None

    def create_temp_batch(
        self,
        work_dir: str,
        extra_vars: Optional[dict] = None
    ) -> str:
        """
        创建 Windows 批处理文件

        Args:
            work_dir: 工作目录
            extra_vars: 额外的环境变量

        Returns:
            临时批处理文件路径
        """
        site_packages = self.get_site_packages()

        batch_content = f"""@echo off
chcp 65001 > nul
REM Robot Framework 临时环境
REM 工作目录: {work_dir}

REM 切换到工作目录
cd /d "{work_dir}"

REM 设置 Python 路径
set PATH="{Path(self.python_path).parent}";%PATH%

REM 设置 Python 路径（确保 python.exe 可用）
set PYTHON="{self.python_path}"

REM 设置 site-packages 路径（用于导入 JLTestLibrary）
"""

        if site_packages:
            batch_content += f'set PYTHONPATH="{site_packages}";%PYTHONPATH%\n'

        batch_content += "\nREM 额外的环境变量\n"

        if extra_vars:
            for key, value in extra_vars.items():
                batch_content += f'set {key}={value}\n'

        # 写入临时文件（使用 UTF-8 编码）
        temp_dir = Path(tempfile.gettempdir()) / "rf-ls-run"
        temp_dir.mkdir(exist_ok=True)

        # 生成唯一文件名
        import time
        import random
        file_id = f"{int(time.time())}_{random.randint(10000, 99999)}"
        batch_file = temp_dir / f"run_env_{file_id}.bat"

        with open(batch_file, "w", encoding="utf-8") as f:
            f.write(batch_content)

        return str(batch_file)

    def create_temp_shell(
        self,
        work_dir: str,
        extra_vars: Optional[dict] = None
    ) -> str:
        """
        创建 Unix Shell 脚本

        Args:
            work_dir: 工作目录
            extra_vars: 额外的环境变量

        Returns:
            临时 Shell 脚本路径
        """
        site_packages = self.get_site_packages()

        shell_content = f"""#!/bin/bash
# Robot Framework 临时环境
# 工作目录: {work_dir}

# 切换到工作目录
cd "{work_dir}" || exit 1

# 设置 Python 路径
export PATH="{Path(self.python_path).parent}:$PATH"
export PYTHON="{self.python_path}"

# 设置 site-packages 路径
if [ -d "{site_packages}" ]; then
    export PYTHONPATH="{site_packages}:$PYTHONPATH"
fi

# 额外的环境变量
"""

        if extra_vars:
            for key, value in extra_vars.items():
                shell_content += f'export {key}="{value}"\n'

        # 写入临时文件
        temp_dir = Path(tempfile.gettempdir()) / "rf-ls-run"
        temp_dir.mkdir(exist_ok=True)

        # 生成唯一文件名
        import time
        import random
        file_id = f"{int(time.time())}_{random.randint(10000, 99999)}"
        shell_file = temp_dir / f"run_env_{file_id}.sh"

        with open(shell_file, "w", encoding="utf-8") as f:
            f.write(shell_content)

        os.chmod(shell_file, 0o755)
        return str(shell_file)

    def create_env_script(self, work_dir: str, extra_vars: Optional[dict] = None) -> str:
        """
        创建环境脚本（自动检测平台）

        Args:
            work_dir: 工作目录
            extra_vars: 额外的环境变量

        Returns:
            临时脚本路径
        """
        if os.name == "nt":  # Windows
            return self.create_temp_batch(work_dir, extra_vars)
        else:  # Unix/Linux/macOS
            return self.create_temp_shell(work_dir, extra_vars)


def prepare_execution_env(
    python_path: Optional[str] = None,
    work_dir: Optional[str] = None,
    extra_vars: Optional[dict] = None
) -> dict:
    """
    准备执行环境

    Args:
        python_path: Python 路径
        work_dir: 工作目录
        extra_vars: 额外的环境变量

    Returns:
        环境信息字典
        {
            "python_path": "Python 可执行文件路径",
            "work_dir": "工作目录",
            "env_script": "临时环境脚本路径",
            "site_packages": "site-packages 目录",
            "pythonpath": "PYTHONPATH 环境变量"
        }
    """
    builder = RFEnvBuilder(python_path)

    work_dir = work_dir or os.getcwd()
    env_script = builder.create_env_script(work_dir, extra_vars)
    site_packages = builder.get_site_packages()

    return {
        "python_path": builder.python_path,
        "work_dir": work_dir,
        "env_script": env_script,
        "site_packages": str(site_packages) if site_packages else None,
        "pythonpath": str(site_packages) if site_packages else ""
    }


if __name__ == "__main__":
    # 测试
    env = prepare_execution_env()
    print("Python Path:", env["python_path"])
    print("Work Dir:", env["work_dir"])
    print("Env Script:", env["env_script"])
    print("Site Packages:", env["site_packages"])