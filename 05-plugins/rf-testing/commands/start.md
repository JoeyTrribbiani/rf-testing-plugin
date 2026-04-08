---
description: 启动 RF 测试工作流 - 自动识别 TAPD 需求或 GitLab/GitHub 代码分析
argument-hint: [tapd-link|gitlab-url|github-url|project-path]
---

## 输入源自动检测

首先检测用户输入的类型，然后执行相应流程。

**步骤 1: 输入源检测**

根据参数内容自动检测：

```python
# 检测逻辑
user_input = "<用户输入的参数>"

if "tapd.cn" in user_input or "www.tapd" in user_input:
    mode = "TAPD"
    # 提取 workspace_id 和 story_id
    workspace_id = user_input.split("/")[4]  # 48200023
    story_id = user_input.split("/")[-1]     # 1148200023001077267
    print(f"检测到 TAPD 需求链接，workspace_id={workspace_id}, story_id={story_id}")

elif "gitlab" in user_input:
    mode = "GitLab"
    # 提取项目路径
    project_path = user_input.replace("https://", "").split("/", 1)[1] if "://" in user_input else user_input
    git_base_url = user_input.split("/")[2] if "://" in user_input else "gitlab.jlpay.com"
    print(f"检测到 GitLab 项目路径: {project_path}, 基地址: {git_base_url}")

elif "github.com" in user_input:
    mode = "GitHub"
    # 提取项目路径
    project_path = user_input.replace("https://", "").split("/", 1)[1] if "://" in user_input else user_input
    print(f"检测到 GitHub 项目路径: {project_path}")

else:
    mode = "UNKNOWN"
    print("无法识别输入类型，请提供:")
    print("  1. TAPD 需求链接 (如 https://www.tapd.cn/...)")
    print("  2. GitLab 项目链接 (如 https://gitlab.jlpay.com/...)")
    print("  3. GitHub 仓库链接 (如 https://github.com/...)")
```

**步骤 2: 根据模式执行**

### TAPD 模式
- 工作流: `@${CLAUDE_PLUGIN_ROOT}/workflows/requirement-to-rf.md`
- 环境变量: `TAPD_ACCESS_TOKEN`
- 执行:
  1. 从 TAPD 拉取需求内容
  2. 识别测试场景和测试点
  3. 生成 RF 测试用例
  4. RF 质量保证与自动修复
  5. 执行验证 (dryrun)
  6. 质量门禁判断
  7. 执行测试
  8. 结果分析
  9. 转换为 TAPD 格式

### GitLab 模式
- 工作流: `@${CLAUDE_PLUGIN_ROOT}/workflows/full-test-pipeline.md` (GitLab 分支)
- 环境变量: `GITLAB_API_URL`, `GITLAB_PERSONAL_ACCESS_TOKEN`
- 执行:
  1. 使用 git clone 获取代码
  2. 代码分析 (9步骤: 结构→流程→影响面)
  3. 改动点识别
  4. 识别测试场景和测试点
  5. 生成 RF 测试用例
  6. RF 质量保证与自动修复
  7. 执行验证 (dryrun)
  8. 质量门禁判断
  9. 执行测试
  10. 结果分析
  11. 转换为 TAPD 格式

### GitHub 模式
- 工作流: `@${CLAUDE_PLUGIN_ROOT}/workflows/full-test-pipeline.md` (GitHub 分支)
- 环境变量: `GITHUB_TOKEN`
- 执行: 与 GitLab 模式类似，但使用 GitHub MCP 服务器

## 当前输入

用户输入: `<用户输入>`

请执行上述检测逻辑，确定模式后继续执行对应流程。