---
description: 执行 RF 测试用例 - 支持完整执行、dryrun 验证、指定用例或标签
argument-hint: <robot-file> [--dryrun] [--test <name>] [--include <tags>] [--exclude <tags>]
---

## 执行方式

**AI 必须使用 Bash 工具执行 `rf_runner.py` 脚本，不要直接执行 robot 命令！**

```bash
# 基础格式（使用插件根目录变量）
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py <robot-file> [选项]

# 如果上述路径不存在，尝试以下回退路径（按优先级）：
# 1. 向上查找（插件在 cache 中时）
python ${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py <robot-file> [选项]
# 2. 使用插件根目录下的 plugins 路径
python ${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py <robot-file> [选项]

# 示例
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py test.robot --dryrun
```

**AI 执行步骤**:
1. **检查路径**: 使用 Bash 检查 `${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py` 是否存在
2. **构建命令**:
   - 如果存在：使用 `${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py`
   - 如果不存在：尝试 `${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py`
   - 如果仍然不存在：尝试 `${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py`
3. 使用 Bash 工具执行命令（使用 `||` 连接多个尝试）
4. 解析输出结果

**推荐的 Bash 执行命令格式**：
```bash
cd <robot-file-所在目录> && \
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py <robot-file> [选项] 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py <robot-file> [选项] 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py <robot-file> [选项] 2>&1
```

**重要**:
- `${CLAUDE_PLUGIN_ROOT}` 是插件根目录的绝对路径，AI 会在运行时自动解析
- 如果插件在 cache 目录中（如 `rf-testing-plugin/rf-testing/1.0.0/`），需要向上查找
- ✅ 使用 Bash 工具执行 `rf_runner.py`
- ❌ 不要直接执行 `conda activate && robot` 命令
- ❌ 不要执行 `python -m robot` 命令

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
2. 切换到 robot 文件所在目录（使用 `cd`）
3. 使用 Bash 工具执行命令（包含多个路径尝试）
4. 解析输出结果

**示例执行**：
```bash
cd <robot-file-所在目录> && \
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py test.robot --dryrun 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py test.robot --dryrun 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py test.robot --dryrun 2>&1
```

**重要**:
- ✅ 使用 `${CLAUDE_PLUGIN_ROOT}` 变量引用插件根目录
- ✅ 使用 Bash 工具执行 `rf_runner.py`
- ✅ 先 `cd` 到 robot 文件所在目录
- ✅ 使用 `||` 连接多个路径尝试
- ❌ 不要直接执行 `conda activate && robot` 命令
- ❌ 不要执行 `python -m robot` 命令

## 相关文件

- 执行器: `03-scripts/rf_executor.py`
- 环境构建器: `03-scripts/rf_env_builder.py`
- 命令行工具: `03-scripts/rf_runner.py`
- 监听器: `03-scripts/rf_listener.py`