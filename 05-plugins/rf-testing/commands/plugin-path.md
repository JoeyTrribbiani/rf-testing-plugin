---
description: 插件路径获取指引
argument-hint: [--path]
---

# 获取插件路径

获取 RF Testing Plugin 的安装路径，用于脚本执行时的路径引用。

## 使用方式

**AI 应优先使用环境变量**:
```bash
# 使用环境变量 CLAUDE_PLUGIN_ROOT
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py test.robot
```

**备用路径**（按优先级）:
1. `${CLAUDE_PLUGIN_ROOT}` - Claude Code 提供的插件根目录环境变量
2. `${CLAUDE_PLUGIN_ROOT}/../../03-scripts/` - 插件在 cache 中时的回退路径
3. `${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/` - plugins 子目录中的回退路径

## 环境变量说明

`CLAUDE_PLUGIN_ROOT` 是 Claude Code 在运行插件命令时自动设置的环境变量，指向插件根目录的绝对路径。

**AI 执行脚本时的注意事项**:
1. 优先使用 `${CLAUDE_PLUGIN_ROOT}` 环境变量
2. 如果路径不存在，尝试备用路径
3. 多个路径用 `||` 连接，确保至少一个能工作

## 执行示例

```bash
# 推荐方式（使用环境变量）
cd <robot-file-所在目录> && \
python ${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py test.robot --dryrun 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py test.robot --dryrun 2>&1 || \
python ${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py test.robot --dryrun 2>&1
```

## AI 执行步骤

1. **检查路径**: 验证 `${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py` 是否存在
2. **构建命令**:
   - 如果存在：使用 `${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py`
   - 如果不存在：尝试 `${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py`
   - 如果仍然不存在：尝试 `${CLAUDE_PLUGIN_ROOT}/../../plugins/rf-testing-plugin/03-scripts/rf_runner.py`
3. 使用 Bash 工具执行命令（使用 `||` 连接多个尝试）
4. 解析输出结果