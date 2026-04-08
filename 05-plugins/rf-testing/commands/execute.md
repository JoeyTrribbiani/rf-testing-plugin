---
description: 执行 RF 测试用例 - 支持完整执行、dryrun 验证、指定用例或标签
argument-hint: <robot-file> [--dryrun] [--test <name>] [--include <tags>] [--exclude <tags>]
---

## 命令格式

```bash
/rf-testing:execute <robot-file> [选项]
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

## 使用示例

### 基础执行
```bash
/rf-testing:execute test.robot
```

### Dryrun 验证语法
```bash
/rf-testing:execute test.robot --dryrun
```

### 执行指定测试用例
```bash
/rf-testing:execute test.robot --test "商户状态变更_正常变暂停"
```

### 执行指定标签的用例
```bash
/rf-testing:execute test.robot --include P0,P1
```

### 排除某些标签
```bash
/rf-testing:execute test.robot --exclude "WIP,TODO"
```

## 执行环境

该命令会自动：
1. 检测 Python 环境（优先使用安装时配置的 Python）
2. 创建临时环境脚本（设置 PATH、PYTHON、PYTHONPATH）
3. 执行 robot 命令
4. 解析执行结果

## 当前输入

用户输入: `<用户输入>`

请根据参数解析并执行 RF 测试用例。

## 相关文件

- 执行器: `03-scripts/rf_executor.py`
- 环境构建器: `03-scripts/rf_env_builder.py`
- 命令行工具: `03-scripts/rf_runner.py`