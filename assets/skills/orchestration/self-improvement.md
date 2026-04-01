# 自我改进技能（Self-Improvement）

**触发关键词**: 自我改进, 学习, 错误日志, 复盘, 持续改进, 经验总结

> 本技能用于记录学习、错误和修正，实现持续改进。适用于命令失败、用户纠正、发现缺失功能、API 失败、知识过时、发现更好方法等场景。

---

## 快速参考

| 场景 | 操作 |
|------|------|
| 命令/操作失败 | 记录到 `.learnings/ERRORS.md` |
| 用户纠正你 | 记录到 `.learnings/LEARNINGS.md`，类别为 `correction` |
| 用户想要缺失功能 | 记录到 `.learnings/FEATURE_REQUESTS.md` |
| API/外部工具失败 | 记录到 `.learnings/ERRORS.md`，包含集成详情 |
| 知识过时 | 记录到 `.learnings/LEARNINGS.md`，类别为 `knowledge_gap` |
| 发现更好方法 | 记录到 `.learnings/LEARNINGS.md`，类别为 `best_practice` |

---

## 何时记录

**自动触发场景**：

**用户纠正**（→ 学习记录，`correction` 类别）：
- "不对，这样不行..."
- "实际上，应该..."
- "你理解错了..."
- "这个过时了..."

**功能请求**（→ 功能请求）：
- "能不能也..."
- "我希望你能..."
- "有没有办法..."
- "为什么不能..."

**知识缺口**（→ 学习记录，`knowledge_gap` 类别）：
- 用户提供你不知道的信息
- 你引用的文档已过时
- API 行为与你的理解不同

**错误**（→ 错误记录）：
- 命令返回非零退出码
- 异常或堆栈跟踪
- 意外的输出或行为
- 超时或连接失败

---

## 记录格式

### 学习记录条目

追加到 `.learnings/LEARNINGS.md`：

```markdown
## [LRN-YYYYMMDD-XXX] category

**记录时间**: ISO-8601 时间戳
**优先级**: low | medium | high | critical
**状态**: pending
**区域**: frontend | backend | infra | tests | docs | config

### 摘要
一行描述学到了什么

### 详情
完整上下文：发生了什么、哪里错了、什么是正确的

### 建议行动
具体的修复或改进措施

### 元数据
- 来源: conversation | error | user_feedback
- 相关文件: path/to/file.ext
- 标签: tag1, tag2
- 参见: LRN-20250110-001（如果与现有条目相关）

---
```

### 错误记录条目

追加到 `.learnings/ERRORS.md`：

```markdown
## [ERR-YYYYMMDD-XXX] skill_or_command_name

**记录时间**: ISO-8601 时间戳
**优先级**: high
**状态**: pending
**区域**: frontend | backend | infra | tests | docs | config

### 摘要
简要描述失败了什么

### 错误
```
实际错误消息或输出
```

### 上下文
- 尝试的命令/操作
- 使用的输入或参数
- 相关环境细节

### 建议修复
如果可识别，可能解决此问题的方案

### 元数据
- 可复现: yes | no | unknown
- 相关文件: path/to/file.ext
- 参见: ERR-20250110-001（如果重复出现）

---
```

### 功能请求条目

追加到 `.learnings/FEATURE_REQUESTS.md`：

```markdown
## [FEAT-YYYYMMDD-XXX] capability_name

**记录时间**: ISO-8601 时间戳
**优先级**: medium
**状态**: pending
**区域**: frontend | backend | infra | tests | docs | config

### 请求的功能
用户想要做什么

### 用户上下文
为什么需要这个，他们在解决什么问题

### 复杂度估算
simple | medium | complex

### 建议实现
如何构建这个功能，可能扩展什么

### 元数据
- 频率: first_time | recurring
- 相关功能: existing_feature_name

---
```

---

## ID 生成规则

格式：`TYPE-YYYYMMDD-XXX`
- **TYPE**: `LRN`（学习）、`ERR`（错误）、`FEAT`（功能）
- **YYYYMMDD**: 当前日期
- **XXX**: 序号或随机 3 个字符（如 `001`、`A7B`）

示例：`LRN-20250305-001`、`ERR-20250305-A3F`、`FEAT-20250305-002`

---

## 解决条目

当问题被修复时，更新条目：

1. 将 `**状态**: pending` 改为 `**状态**: resolved`
2. 在元数据后添加解决块：

```markdown
### 解决方案
- **解决时间**: 2025-01-16T09:00:00Z
- **提交/PR**: abc123 或 #42
- **备注**: 所做事情的简要描述
```

其他状态值：
- `in_progress` - 正在处理
- `wont_fix` - 决定不处理（在备注中说明原因）
- `promoted` - 已提升到项目文档（CLAUDE.md、AGENTS.md 等）

---

## 提升到项目记忆

当学习内容广泛适用（非一次性修复）时，将其提升为永久项目记忆。

### 何时提升

- 学习适用于多个文件/功能
- 任何贡献者（人类或 AI）都应该知道的知识
- 防止重复错误
- 记录项目特定约定

### 提升目标

| 目标 | 适用内容 |
|------|---------|
| `CLAUDE.md` | 项目事实、约定、陷阱（所有 Claude 交互） |
| `AGENTS.md` | Agent 特定工作流、工具使用模式、自动化规则 |
| `.github/copilot-instructions.md` | GitHub Copilot 的项目上下文和约定 |

### 如何提升

1. **提炼**：将学习内容提炼为简洁的规则或事实
2. **添加**：到目标文件的适当章节（如需要则创建文件）
3. **更新**：原始条目
   - 将 `**状态**: pending` 改为 `**状态**: promoted`
   - 添加 `**提升到**: CLAUDE.md` 或 `AGENTS.md`

---

## 优先级指南

| 优先级 | 何时使用 |
|--------|---------|
| `critical` | 阻塞核心功能、数据丢失风险、安全问题 |
| `high` | 重大影响、影响常见工作流、重复出现的问题 |
| `medium` | 中等影响、存在变通方案 |
| `low` | 小不便、边缘情况、锦上添花 |

---

## 区域标签

用于按代码库区域过滤学习内容：

| 区域 | 范围 |
|------|-------|
| `frontend` | UI、组件、客户端代码 |
| `backend` | API、服务、服务端代码 |
| `infra` | CI/CD、部署、Docker、云 |
| `tests` | 测试文件、测试工具、覆盖率 |
| `docs` | 文档、注释、README |
| `config` | 配置文件、环境、设置 |

---

## 最佳实践

1. **立即记录** - 上下文在问题发生后最清晰
2. **具体描述** - 未来的 Agent 需要快速理解
3. **包含复现步骤** - 尤其是错误
4. **链接相关文件** - 使修复更容易
5. **建议具体修复** - 而非"调查"
6. **使用一致的类别** - 支持过滤
7. **积极提升** - 如果有疑问，添加到项目文档
8. **定期审查** - 陈旧的学习失去价值

---

## 在本项目中使用

### 设置学习目录

在项目根目录创建 `.learnings/` 目录：

```bash
mkdir -p .learnings
```

### 创建日志文件

- `LEARNINGS.md` — 修正、知识缺口、最佳实践
- `ERRORS.md` — 命令失败、异常
- `FEATURE_REQUESTS.md` — 用户请求的功能

### 定期审查

在自然断点处审查 `.learnings/`：
- 开始新的重大任务之前
- 完成功能后
- 在有过去学习记录的区域工作时
- 活跃开发期间每周一次

### 快速状态检查

```bash
# 统计待处理项目
grep -h "Status.*pending" .learnings/*.md | wc -l

# 列出高优先级待处理项目
grep -B5 "Priority.*high" .learnings/*.md | grep "^## \["
```

---

## 复现模式检测

如果记录的内容与现有条目相似：

1. **先搜索**：`grep -r "关键词" .learnings/`
2. **链接条目**：在元数据中添加 `**参见**: ERR-20250110-001`
3. **提高优先级**：如果问题持续出现
4. **考虑系统性修复**：重复问题通常表示：
   - 缺少文档（→ 提升到项目文档）
   - 缺少自动化（→ 添加到 AGENTS.md）
   - 架构问题（→ 创建技术债务票据）

---

## Gitignore 选项

**本地保留学习内容**（每个开发者独立）：
```gitignore
.learnings/
```

**仓库中共享学习内容**（团队共享）：
不添加到 .gitignore - 学习内容成为共享知识。

**混合模式**（追踪模板，忽略条目）：
```gitignore
.learnings/*.md
!.learnings/.gitkeep
```

---

## Hook 集成

通过 agent hooks 启用自动提醒。这是 **可选功能** - 需要显式配置。

### 快速设置（Claude Code / Codex）

在项目中创建 `.claude/settings.json`：

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }]
  }
}
```

这会在每个提示后注入学习评估提醒（约 50-100 token 开销）。

### 完整设置（含错误检测）

```json
{
  "hooks": {
    "UserPromptSubmit": [{
      "matcher": "",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/activator.sh"
      }]
    }],
    "PostToolUse": [{
      "matcher": "Bash",
      "hooks": [{
        "type": "command",
        "command": "./skills/self-improvement/scripts/error-detector.sh"
      }]
    }]
  }
}
```

### 可用 Hook 脚本

| 脚本 | Hook 类型 | 用途 |
|------|-----------|------|
| `scripts/activator.sh` | UserPromptSubmit | 任务后提醒评估学习内容 |
| `scripts/error-detector.sh` | PostToolUse (Bash) | 命令错误时触发 |

---

## 自动技能提取

当学习内容有价值成为可复用技能时，使用提供的辅助工具提取。

### 技能提取标准

满足以下任一条件时，学习内容可提取为技能：

| 标准 | 描述 |
|------|------|
| **重复出现** | 有 `See Also` 链接指向 2+ 个相似问题 |
| **已验证** | 状态为 `resolved` 且有可工作的修复方案 |
| **非显而易见** | 需要实际调试/调查才能发现 |
| **广泛适用** | 非项目特定；可在多个代码库中使用 |
| **用户标记** | 用户说"保存为技能"或类似内容 |

### 提取工作流

1. **识别候选**：学习内容满足提取标准
2. **运行辅助工具**（或手动创建）：
   ```bash
   ./skills/self-improvement/scripts/extract-skill.sh skill-name --dry-run
   ./skills/self-improvement/scripts/extract-skill.sh skill-name
   ```
3. **自定义 SKILL.md**：用学习内容填充模板
4. **更新学习条目**：状态设为 `promoted_to_skill`，添加 `Skill-Path`
5. **验证**：在新会话中读取技能，确保其自包含

### 手动提取

如果偏好手动创建：

1. 创建 `skills/<skill-name>/SKILL.md`
2. 使用 `assets/SKILL-TEMPLATE.md` 中的模板
3. 遵循 [Agent Skills 规范](https://agentskills.io/specification)：
   - YAML frontmatter 包含 `name` 和 `description`
   - 名称必须与文件夹名称匹配
   - 技能文件夹内不要有 README.md

### 技能质量门控

提取前验证：

- [ ] 解决方案已测试且可工作
- [ ] 无需原始上下文即可清晰描述
- [ ] 代码示例自包含
- [ ] 无项目特定硬编码值
- [ ] 遵循技能命名约定（小写、连字符）

---

## 多 Agent 支持

本技能在不同 AI 编程 agent 中使用 agent 特定激活。

### Claude Code

**激活方式**：Hooks（UserPromptSubmit、PostToolUse）
**设置**：`.claude/settings.json` 中的 hook 配置
**检测**：通过 hook 脚本自动

### Codex CLI

**激活方式**：Hooks（与 Claude Code 相同模式）
**设置**：`.codex/settings.json` 中的 hook 配置
**检测**：通过 hook 脚本自动

### GitHub Copilot

**激活方式**：手动（无 hook 支持）
**设置**：添加到 `.github/copilot-instructions.md`：

```markdown
## Self-Improvement

解决非显而易见的问题后，考虑记录到 `.learnings/`：
1. 使用 self-improvement skill 格式
2. 用 See Also 链接相关条目
3. 将高价值学习内容提升为技能

询问："Should I log this as a learning?"
```

**检测**：会话结束时手动审查

### Agent 无关指导

无论使用什么 agent，在以下情况应用自我改进：

1. **发现非显而易见的事情** - 解决方案不是立即可见的
2. **纠正自己** - 初始方法错误
3. **学习项目约定** - 发现未记录的模式
4. **遇到意外错误** - 特别是诊断困难的情况
5. **发现更好方法** - 改进了原始解决方案

### Copilot Chat 集成

Copilot 用户在相关时可在提示中添加：

> 完成此任务后，评估是否应该使用 self-improvement skill 格式将学习内容记录到 `.learnings/`

或使用快速提示：
- "Log this to learnings"
- "Create a skill from this solution"
- "Check .learnings/ for related issues"

---

## 与 bugs.jsonl 集成

本项目的 `bugs.jsonl` 文件用于记录已修复的错误复盘。当错误被修复后：

1. **先记录到 `.learnings/ERRORS.md`** - 详细错误信息和上下文
2. **修复后生成 bugs.jsonl 条目** - 结构化复盘记录
3. **更新 .learnings/ 条目** - 状态改为 `resolved`，添加解决方案链接

这样确保：
- 错误首先被记录以便修复
- 修复后生成结构化复盘供未来参考
- 学习条目保留详细上下文供理解根因
