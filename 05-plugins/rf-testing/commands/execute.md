---
description: 执行 RF 测试用例 - 支持完整执行、dryrun 验证、指定用例或标签
argument-hint: <robot-file> [--dryrun] [--test <name>] [--include <tags>] [--exclude <tags>]
---

## 执行方式

**AI 必须使用 Bash 工具执行 `rf_runner.py` 脚本，不要直接执行 robot 命令！**

```bash
# 基础格式
python <插件路径>/03-scripts/rf_runner.py <robot-file> [选项]

# 示例
python 03-scripts/rf_runner.py test.robot --dryrun
python 03-scripts/rf_runner.py test.robot --include P0
```

## 参数说明

### 必需参数
- `<robot-file>`: RF 测试用例文件路径（.robot 文件或包含 .robot 的目录）

### 可选参数
- `--dryrun`: 仅验证语法，不实际执行
- `--test <name>`: 执行指定的测试用例名称
- `--suite <name>`: 执行指定的测试套件名称
- `--include <tags>`: 仅执行包含指定标签的用例（逗号分隔）
- `--exclude <tags>`: 排除包含指定标签的用例（逗号分隔）
- `--output-dir <path>`: 输出目录（默认: ./output）
- `--no-env-script`: 不使用环境脚本（直接执行）
- `--python-path <path>`: 指定 Python 环境路径

## 当前输入

用户输入: `<用户输入>`

**AI 执行步骤**:
1. 解析用户输入，获取 robot 文件路径和选项
2. 构建执行命令: `python 03-scripts/rf_runner.py <robot-file> [选项]`
3. 使用 Bash 工具执行命令
4. 解析输出结果

**重要**:
- ✅ 使用 Bash 工具执行 `rf_runner.py`
- ❌ 不要直接执行 `conda activate && robot` 命令
- ❌ 不要执行 `python -m robot` 命令

## 相关文件

- 执行器: `03-scripts/rf_executor.py`
- 环境构建器: `03-scripts/rf_env_builder.py`
- 命令行工具: `03-scripts/rf_runner.py`