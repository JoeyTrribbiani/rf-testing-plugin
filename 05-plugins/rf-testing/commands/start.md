---
description: 从 TAPD 需求链接启动 RF 测试工作流
argument-hint: [tapd-link]
---

使用插件内置的测试工作流处理当前任务。

工作流定义：
@${CLAUDE_PLUGIN_ROOT}/workflows/full-test-pipeline.md

子工作流：
- requirement-to-rf: 仅需求转 RF 用例
- rf-to-tapd: 仅 RF 转 TAPD 格式

安装与配置说明：
@${CLAUDE_PLUGIN_ROOT}/README.md

执行要求：
- 如果传入了参数 `$1`，直接把它当作 TAPD 需求链接开始流程。
- 如果没有传入参数，直接向用户索要 TAPD 需求链接，不要让用户选择输入方式。
- 开始前确认 `tapd` MCP 可用（检查 TAPD_ACCESS_TOKEN）。
- 如果 MCP 无法鉴权，明确提示用户检查环境变量。
- 然后严格按照内置工作流继续执行。

命令示例：
/rf-testing:start https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267