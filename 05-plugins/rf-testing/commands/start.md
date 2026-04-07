---
description: 启动 RF 测试工作流 - 支持 TAPD 需求或 GitLab/GitHub 代码分析
argument-hint: [tapd-link|gitlab-project-path|github-repo-path]
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

**输入源识别逻辑**：
- 如果参数是 TAPD 链接（包含 tapd.cn）→ 走 TAPD 需求模式
- 如果参数是 GitLab 项目路径（格式如 group/project）→ 走代码分析模式
- 如果参数是 GitHub 仓库路径（格式如 owner/repo）→ 走代码分析模式
- 如果没有传入参数，询问用户选择输入方式：
  1. TAPD 需求链接
  2. GitLab/GitHub 代码分析

**TAPD 模式要求**：
- 确认 `tapd` MCP 可用（检查 TAPD_ACCESS_TOKEN）
- 如果 MCP 无法鉴权，明确提示用户检查环境变量

**GitLab 模式要求**：
- 确认 `gitlab` MCP 可用（检查 GITLAB_API_URL 和 GITLAB_PERSONAL_ACCESS_TOKEN）
- 获取项目路径、分支名或 commit SHA
- 如果 MCP 无法鉴权，明确提示用户检查环境变量

**GitHub 模式要求**：
- 确认 `github` MCP 可用（检查 GITHUB_TOKEN）
- 获取仓库路径、分支名或 commit SHA
- 如果 MCP 无法鉴权，明确提示用户检查环境变量

然后严格按照内置工作流继续执行。

命令示例：
/rf-testing:start https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
/rf-testing:start mygroup/myproject
/rf-testing:start owner/repo