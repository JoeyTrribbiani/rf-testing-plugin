# 智能安装配置设计文档

**日期**: 2026-04-02
**目标**: 增强安装脚本，实现 Python 多环境智能检测和 JLTestLibrary 自动安装

## 背景与问题

当前安装脚本存在以下问题：

1. **Python 多环境检测不足**
   - 只检测默认的 `python` 或 `python3` 命令
   - 无法识别系统中存在的多个 Python 版本
   - 不支持 conda 环境检测

2. **JLTestLibrary 安装不智能**
   - 要求用户手动指定 site-packages 目录
   - 无法自动检测已安装状态
   - 路径硬编码，不匹配实际环境

3. **缺乏智能推荐**
   - 无法根据环境特征推荐最合适的 Python 版本
   - 用户需要手动判断和选择

## 设计方案：智能检测 + 单步确认（方案 B）

### 核心设计

```
统一检测所有 Python 来源 → 筛选符合条件的版本 → 按优先级排序
    → 显示推荐和备选列表 → 用户一次确认 → 自动计算目标路径
```

### 优先级策略

```
1. 当前激活的 conda 环境（优先级 0-99）
2. 匹配 Python 3.7.x 的 conda 环境（优先级 100-199）
3. 匹配 Python 3.8.x 的系统 Python（优先级 200-299）
4. 其他匹配 3.7.16+ 的 Python 版本（优先级 300-999）
```

选择策略：**最接近要求版本（3.7.16+）**，确保 JLTestLibrary 兼容性。

---

## 模块设计

### 1. Python 环境检测模块

#### 数据结构

```python
PythonEnvironment = {
    "source": "conda" | "system" | "venv",
    "name": str,           # 环境名称或路径
    "python_path": str,    # Python 可执行文件路径
    "version": str,        # "3.7.16"
    "major": int,          # 3
    "minor": int,          # 7
    "patch": int,          # 16
    "is_active": bool      # 是否为当前激活的环境
}
```

#### 检测函数

**detect_conda_envs()**

- 检测 conda 命令是否存在
- 列出所有 conda 环境
- 获取每个环境的 Python 版本
- 标记当前激活的环境
- 筛选 >= 3.7.16 的版本

**detect_system_python()**

- 检测常见 Python 命令（python3, python, py）
- 遍历系统常见安装路径：
  - Windows: `C:\Python*\`, `C:\Program Files\Python*\`
  - Linux: `/usr/bin/`, `/usr/local/bin/`
  - macOS: `/opt/homebrew/bin/`, `/usr/local/opt/`
- 解析版本并筛选

**detect_venv()**

- 检查 `VIRTUAL_ENV` 环境变量
- 获取虚拟环境的 Python 路径
- 检测版本并筛选

---

### 2. site-packages 检测模块

#### 检测方法

**get_site_packages_paths(python_path: str)**

```python
# 使用 Python 自身的 site 模块检测
subprocess.run([python_path, "-c", "import site; print('\\n'.join(site.getsitepackages()))"])
```

#### 备选方案

**calculate_fallback_paths(env: PythonEnvironment)**

- 对于 conda: `{env_dir}/lib/python{major}.{minor}/site-packages`
- 对于 Windows system: `{env_dir}/Lib/site-packages`

#### JLTestLibrary 状态检测

**check_jl_test_library(paths: List[str])**

- 检查每个 site-packages 目录下是否存在 JLTestLibrary
- 返回状态信息供用户确认

---

### 3. 优先级排序模块

#### 排序函数

```python
def calculate_priority(env: PythonEnvironment) -> int:
    base = 0
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
```

#### 显示格式

```
检测到以下 Python 环境：

[推荐] 1. conda: rf-env (3.7.18)  [当前激活]
       2. conda: py37 (3.7.16)
       3. system: /usr/bin/python3.8 (3.8.10)
       4. system: /usr/local/bin/python3.12 (3.12.0)

请选择目标 Python 环境 [1-4, 默认=1]:
```

---

### 4. JLTestLibrary 安装模块

#### 安装流程

```
1. 检查 JLTestLibrary.zip 是否存在
   - 不存在：跳过安装，继续执行

2. 获取选定 Python 的 site-packages 目录

3. 检查是否已安装 JLTestLibrary
   - 已存在：跳过安装

4. 解压到目标目录

5. 验证安装（import JLTestLibrary）

6. 显示结果
```

#### 显示格式

```
检测到 site-packages 目录：

[推荐] 1. D:\environment\Python\Anaconda3\envs\python37\Lib\site-packages
       [JLTestLibrary 已存在]
       2. D:\environment\Python\Anaconda3\Lib\site-packages

请选择目标目录 [1-2, 默认=1]:
```

---

### 5. 错误处理模块

#### 错误类型

```python
class PythonDetectionError(Exception):
    """Python 环境检测失败"""

class NoValidPythonError(PythonDetectionError):
    """未找到符合条件的 Python 环境"""

class SitePackagesDetectionError(PythonDetectionError):
    """site-packages 目录检测失败"""

class JLTestLibraryInstallError(PythonDetectionError):
    """JLTestLibrary 安装失败"""
```

#### 错误处理策略

| 错误类型 | 处理方式 | 用户提示 |
|---------|---------|---------|
| 未找到 >= 3.7.16 的 Python | 退出 | 请安装 Python 3.7.16+ |
| site-packages 检测失败 | 使用备选方案或提示用户 | 无法自动检测，请手动指定 |
| JLTestLibrary.zip 不存在 | 跳过 | JLTestLibrary.zip 不存在，跳过安装 |
| 解压失败 | 提示错误并跳过 | 解压失败，请检查权限 |

---

## 实现文件

### 新增文件

```
03-scripts/
├── python_detector.py          # Python 环境检测（跨平台）
└── jl_installer.py             # JLTestLibrary 安装辅助
```

### 修改文件

```
install.sh                       # 集成环境检测和智能安装
install.bat                      # 集成环境检测和智能安装
INSTALL.md                       # 更新安装文档
README.md                        # 更新使用说明
```

---

## 用户交互流程

```
1. 运行安装脚本
   ./install.sh  # 或 install.bat

2. 检测 Python 环境
   → 显示所有符合条件的 Python 环境
   → 自动推荐最合适的版本

3. 用户确认或选择
   → 按回车使用推荐，或输入编号选择其他

4. 检测 site-packages 目录
   → 显示选定 Python 的所有 site-packages 目录
   → 标记已安装 JLTestLibrary 的目录

5. 用户确认目标目录
   → 按回车使用推荐，或输入编号选择其他

6. 安装 JLTestLibrary
   → 自动解压到目标目录
   → 验证安装结果

7. 继续 MCP 配置等后续步骤
```

---

## 跨平台兼容性

### 平台检测

```python
def detect_platform() -> str:
    if os.name == 'nt':
        return 'windows'
    elif sys.platform == 'darwin':
        return 'macos'
    else:
        return 'linux'
```

### 路径处理

- Windows: 使用反斜杠，处理 drive letter
- Linux/macOS: 使用正斜杠，处理 Home 目录
- 统一使用 `os.path` 和 `pathlib` 进行跨平台操作

---

## 验收标准

1. ✅ 能正确检测 conda 环境（包括激活状态）
2. ✅ 能正确检测系统 Python（多个版本）
3. ✅ 能正确检测虚拟环境（venv）
4. ✅ 优先级排序符合设计策略
5. ✅ site-packages 路径检测准确（与选定环境一致）
6. ✅ JLTestLibrary 自动安装到正确位置
7. ✅ 已安装 JLTestLibrary 时正确跳过
8. ✅ 错误处理清晰，用户提示明确
9. ✅ Windows/Linux/macOS 跨平台兼容
10. ✅ 用户交互简洁，一次确认即可

---

## 实现注意事项

1. **性能**: 检测过程应该快速完成，避免长时间等待
2. **去重**: 同一 Python 路径不应重复显示
3. **默认值**: 总是提供合理的默认推荐
4. **回退**: 自动检测失败时提供备选方案或手动输入选项
5. **验证**: 每个步骤后进行验证，确保正确性