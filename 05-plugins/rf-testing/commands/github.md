---
description: 从 GitHub 代码分析启动 RF 测试工作流
argument-hint: [repo-path]
---

使用 GitHub 代码分析模式启动 RF 测试工作流。

工作流定义：
@${CLAUDE_PLUGIN_ROOT}/workflows/full-test-pipeline.md

**使用方式**：

```
/rf-testing:github <repo-path>
```

**参数**：
- `repo-path`: GitHub 仓库路径（格式如 `owner/repo`）
- `branch_or_commit`: 分支名或 commit SHA（可选，默认 main/master）

**示例**：
```
/rf-testing:github myorg/myrepo
/rf-testing:github facebook/react
/rf-testing:github facebook/react main
```

**执行要求**：

1. **使用 git clone 获取代码**
   - 使用环境变量 `GITHUB_TOKEN`
   - 使用 token 认证方式
   - 下载到临时目录 `$TMPDIR/rf-testing/`

2. **Git clone 命令格式**:
   ```bash
   # Unix/Linux/macOS
   cd "$TMPDIR/rf-testing"
   rm -rf <repo-name>
   git clone --depth 1 \
     "https://${GITHUB_TOKEN}@github.com/<repo-path>.git" \
     2>&1

   # Windows
   cd %TEMP%\rf-testing
   rmdir /s /q <repo-name>
   git clone --depth 1 \
     https://%GITHUB_TOKEN%@github.com/<repo-path>.git
   ```

3. **如果指定了分支或 commit**:
   ```bash
   cd <repo-name>
   git fetch origin <branch_or_commit>
   git checkout <branch_or_commit>
   ```

4. **执行代码分析**（9步骤）
   - 结构分析（3步）: 技术栈 → 实体ER图 → 接口入口
   - 流程分析（3步）: 调用链 → 时序 → 复杂逻辑
   - 影响面分析（3步）: 依赖引用 → 数据影响 → 风险评估

5. **识别改动点和测试范围**

6. **生成 RF 测试用例**

**MCP 服务器**：git clone（备用方案）

**环境变量检查**：
- `GITHUB_TOKEN` - GitHub 访问令牌（必需）

如果缺少环境变量，明确提示用户配置。
