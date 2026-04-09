---
description: 从 GitLab 代码分析启动 RF 测试工作流
argument-hint: [project-path]
---

使用 GitLab 代码分析模式启动 RF 测试工作流。

工作流定义：
@${CLAUDE_PLUGIN_ROOT}/workflows/full-test-pipeline.md

**使用方式**：

```
/rf-testing:gitlab <project-path>
```

**参数**：
- `project-path`: GitLab 项目路径（格式如 `group/project`）
- `branch_or_commit`: 分支名或 commit SHA（可选，默认 main/master）

**示例**：
```
/rf-testing:gitlab pay-plus/base/ai-first
/rf-testing:gitlab pay-plus/merch/access/merch-access-standard develop
```

**⚠️ 重要：OAuth2 认证格式**

GitLab git clone 必须使用 OAuth2 格式，否则会报 "Authentication failed" 错误。

**错误格式**（会导致认证失败）：
```bash
git clone https://gitlab.jlpay.com/group/project.git
git clone https://${GITLAB_TOKEN}@gitlab.jlpay.com/group/project.git
```

**正确格式**（使用 oauth2: 前缀）：
```bash
git clone https://oauth2:${GITLAB_PERSONAL_ACCESS_TOKEN}@gitlab.jlpay.com/group/project.git
```

**错误示例**（不要使用）：
```
warning: missing OAuth configuration for gitlab.jlpay.com
remote: HTTP Basic: Access denied. The provided password or token is incorrect
fatal: Authentication failed
```

**执行要求**：

1. **使用 git clone 获取代码**
   - 必须使用环境变量 `GITLAB_PERSONAL_ACCESS_TOKEN`
   - **必须使用 oauth2 认证方式**（重要！）
   - 下载到临时目录 `$TMPDIR/rf-testing/`

2. **Git clone 命令格式**:
   ```bash
   # Unix/Linux/macOS
   cd "$TMPDIR/rf-testing"
   rm -rf <project-name>
   git clone \
     "https://oauth2:${GITLAB_PERSONAL_ACCESS_TOKEN}@gitlab.jlpay.com/<project-path>.git" \
     2>&1

   # Windows
   cd %TEMP%\rf-testing
   rmdir /s /q <project-name>
   git clone \
     https://oauth2:%GITLAB_PERSONAL_ACCESS_TOKEN%@gitlab.jlpay.com/<project-path>.git
   ```

   **⚠️ 注意**：
   - 必须包含 `oauth2:` 前缀
   - 使用双引号包裹 URL（避免 shell 解析问题）
   - 不使用 `--depth 1` 浅克隆，以便获取完整历史用于对比分析

3. **如果指定了分支或 commit**:
   ```bash
   cd <project-name>
   git fetch origin <branch_or_commit>
   git checkout <branch_or_commit>
   ```

4. **执行代码分析**（9步骤）
   - 结构分析（3步）: 技术栈 → 实体ER图 → 接口入口
   - 流程分析（3步）: 调用链 → 时序 → 复杂逻辑
   - 影响面分析（3步）: 依赖引用 → 数据影响 → 风险评估

5. **识别改动点和测试范围**

6. **生成 RF 测试用例**

**MCP 服务器**：git clone（MCP 已归档，使用备用方案）

**环境变量检查**：
- `GITLAB_PERSONAL_ACCESS_TOKEN` - GitLab 访问令牌（必需）

如果缺少环境变量，明确提示用户配置。
