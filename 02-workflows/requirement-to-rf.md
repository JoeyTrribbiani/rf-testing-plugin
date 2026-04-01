# 需求转用例工作流

```mermaid
---
description: 从 TAPD 需求生成 RF 测试用例
allowed-tools: Write,Read,WebSearch,Skill,Grep,Glob,AskUserQuestion,Bash
---
flowchart TD
    start_node([开始])
    end_node([结束])

    mcp_fetch[[MCP: 从 TAPD 拉取需求内容]]
    skill_scenario[[Skill: 识别测试场景]]
    skill_points[[Skill: 识别测试点]]
    skill_generation[[Skill: 生成 RF 用例]]
    skill_validation[[Skill: 检查 RF 规范]]

    start_node --> mcp_fetch
    mcp_fetch --> skill_scenario
    skill_scenario --> skill_points
    skill_points --> skill_generation
    skill_generation --> skill_validation
    skill_validation --> end_node

    style start_node fill:#90EE90
    style end_node fill:#FFB6C1
    style mcp_fetch fill:#87CEEB
    style skill_scenario fill:#FFE4B5
    style skill_points fill:#FFE4B5
    style skill_generation fill:#FFE4B5
    style skill_validation fill:#FFE4B5
```

## 工作流说明

### 执行流程

1. **需求获取** - 从 TAPD 拉取需求内容
2. **场景识别** - 识别测试场景
3. **测试点识别** - 识别具体测试点
4. **用例生成** - 生成 RF 测试用例
5. **规范检查** - 检查用例规范

### 触发方式

```bash
# 通过 CLI 触发
/rf-requirement-to-testcase

# 通过 Agent 调用
execute_workflow("requirement-to-rf")
```

### 输入参数

| 参数 | 说明 | 必填 |
|------|------|------|
| requirement_url | TAPD 需求链接 | 是 |
| output_dir | 输出目录 | 否，默认为 ./output |
| creator | 创建人名称 | 否，默认为当前用户 |

### 输出结果

- RF 用例文件（.robot）
- 规范检查报告
- 用例统计信息