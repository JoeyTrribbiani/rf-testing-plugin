---
description: 完整 RF 测试工作流 - 支持 TAPD 需求或 GitLab/GitHub 代码分析双模式启动，自动修复，质量门禁
allowed-tools: Write,Read(dangerouslyDisableSandbox:true),WebSearch,Skill,Grep(dangerouslyDisableSandbox:true),Glob(dangerouslyDisableSandbox:true),AskUserQuestion,Bash(dangerouslyDisableSandbox:true)
---

**⚠️ 重要：工作流执行约束**

1. **必须严格按照阶段顺序执行** - 不能跳过任何阶段
2. **每个阶段必须明确输出状态** - ✅ 进行中 / ⏸️ 等待 / ❌ 失败 / ✅ 完成
3. **遇到错误必须立即停止并报告** - 不能继续执行后续阶段
4. **必须使用提供的Agent和Skill** - 不能自行选择其他工具
5. **必须验证输出结果** - 确保每个阶段的输出符合要求

```mermaid
flowchart TD
    start_node([开始])
    end_node([结束])

    subgraph 阶段0["阶段0: 输入选择"]
        input_select[[用户选择输入源]]
    end

    subgraph 阶段1_TAPD["阶段1-TAPD: 需求获取"]
        mcp_fetch[[MCP: 从 TAPD 拉取需求内容]]
    end

    subgraph 阶段1_GitLab["阶段1-GitLab: 代码获取与分析"]
        mcp_gitlab[[Git Clone: 获取代码]]
        code_analysis[[代码分析 - 9步骤]]
        change_detect[[识别改动点与范围]]
        mcp_yapi_gitlab[[MCP: 获取 YAPI 接口文档]]
    end

    subgraph 阶段2["阶段2: 测试设计"]
        skill_scenario[[Skill: 识别测试场景]]
        skill_points[[Skill: 识别测试点]]
    end

    subgraph 阶段3["阶段3: 用例生成与修复"]
        skill_generation[[Skill: 生成 RF 用例]]
        skill_rf_qa[[Skill: RF 质量保证与自动修复]]
        script_validate[[Script: 执行验证 dryrun]]
        decision_quality{质量门禁}
    end

    subgraph 阶段4["阶段4: 执行测试"]
        script_execute[[Script: 执行 RF 测试用例]]
    end

    subgraph 阶段5["阶段5: 结果分析"]
        skill_results[[Skill: 测试结果分析]]
    end

    subgraph 阶段6["阶段6: 生成 TAPD 格式"]
        skill_conversion[[Skill: RF 转 TAPD]]
        plugin_feedback[[插件体验评估]]
    end

    start_node --> input_select
    input_select -->|TAPD 需求| mcp_fetch
    input_select -->|GitLab/GitHub 代码| mcp_gitlab
    mcp_fetch --> skill_scenario
    mcp_gitlab --> code_analysis
    code_analysis --> change_detect
    change_detect --> mcp_yapi_gitlab
    mcp_yapi_gitlab --> skill_scenario
    skill_scenario --> skill_points
    skill_points --> skill_generation
    skill_generation --> skill_rf_qa
    skill_rf_qa --> script_validate
    script_validate --> decision_quality
    decision_quality -->|通过| script_execute
    decision_quality -->|不通过| skill_rf_qa
    script_execute --> skill_results
    skill_results --> skill_conversion
    skill_conversion --> plugin_feedback
    plugin_feedback --> end_node

    style start_node fill:#90EE90
    style end_node fill:#FFB6C1
    style input_select fill:#DDA0DD
    style mcp_fetch fill:#87CEEB
    style mcp_gitlab fill:#87CEEB
    style mcp_yapi_gitlab fill:#87CEEB
    style code_analysis fill:#FFE4B5
    style change_detect fill:#FFFACD
    style skill_scenario fill:#FFE4B5
    style skill_points fill:#FFE4B5
    style skill_generation fill:#FFE4B5
    style skill_rf_qa fill:#98FB98
    style script_validate fill:#FFA07A
    style decision_quality fill:#FFD700
    style script_execute fill:#DDA0DD
    style skill_results fill:#98FB98
    style skill_conversion fill:#FFE4B5
```

## 工作流执行指南

### 输入源选择

工作流支持两种输入模式启动：

1. **TAPD 需求模式** - 从 TAPD 拉取需求内容进行分析
2. **GitLab/GitHub 代码模式** - 从代码仓库获取代码变更进行分析

**选择逻辑（AI 自动检测）**:

在执行工作流第一步时，AI 必须先检测用户输入：

```javascript
// 输入源自动检测逻辑
const userInput = 用户传入的参数;

// 检测1: TAPD 需求链接
if (userInput.includes('tapd.cn') || userInput.includes('www.tapd')) {
    // TAPD 模式 - 直接提取 workspace_id 和 story_id
    workspaceId = userInput.match(/\/(\d+)\//)?.[1];
    storyId = userInput.match(/view\/(\d+)/)?.[1];
    // 跳过 input_select，直接进入 mcp_fetch
    执行分支 = 'TAPD';
}
// 检测2: GitLab URL 或路径
else if (userInput.includes('gitlab')) {
    // GitLab 模式
    projectPath = extractProjectPath(userInput);
    gitBaseUrl = extractGitBaseUrl(userInput);
    // 跳过 input_select，直接进入 mcp_gitlab
    执行分支 = 'GitLab';
}
// 检测3: GitHub URL 或路径
else if (userInput.includes('github.com')) {
    // GitHub 模式
    projectPath = extractProjectPath(userInput);
    // 跳过 input_select，直接进入 mcp_gitlab
    执行分支 = 'GitHub';
}
// 检测4: 无法识别
else {
    // 执行 input_select，询问用户选择
    执行分支 = 'UNKNOWN';
}
```

**重要**: AI 必须首先执行上述检测逻辑，根据检测结果直接进入对应分支，**不能先问用户选择输入方式**。

### MCP 工具节点

#### input_select(输入源选择)

- **描述**: 询问用户选择输入源类型
- **交互**: "请选择输入源：1) TAPD 需求  2) GitLab/GitHub 代码分析"
- **分支**:
  - 选择 1 → 进入 `mcp_fetch` 节点
  - 选择 2 → 进入 `mcp_gitlab` 节点

#### mcp_fetch(MCP 自动选择) - AI 工具选择模式

<!-- MCP_NODE_METADATA: {"mode":"aiToolSelection","serverId":"plugin:rf-testing:tapd","userIntent":"开始流程后不要理解工作，而是等待用户输入需求链接。\n不需要询问用户使用什么方式传达tapd需求，直接索取链接，不要让用户进行选择。\n根据链接查询对应的需求内容并拉取。workspace_id = 48200023，请注意解析出对应的服务名和需求id."} -->

**MCP 服务器**: tapd

**验证状态**: 有效

**用户意图（自然语言任务描述）**:

```
开始流程后不要理解工作，而是等待用户输入需求链接。
不需要询问用户使用什么方式传达tapd需求，直接索取链接，不要让用户进行选择。
根据链接查询对应的需求内容并拉取。workspace_id = 48200023，请注意解析出对应的服务名和需求id.
```

**执行方法**:

Claude Code 应分析上述任务描述，在运行时查询 MCP 服务器 "tapd" 获取当前工具列表。然后，选择最合适的工具，并根据任务要求确定适当的参数值。

#### mcp_gitlab(MCP 自动选择) - git clone 备用模式

<!-- MCP_NODE_METADATA: {"mode":"aiToolSelection","serverId":"gitlab","userIntent":"从 GitLab 获取指定仓库的代码。用户可选择指定分支（如 develop、master）或指定 commit。获取代码后用于分析改动点。\n注意：GitLab MCP 服务器 (@modelcontextprotocol/server-gitlab) 已被归档，使用 git clone 备用方案。使用系统环境变量中的 GITLAB_API_URL 和 GITLAB_PERSONAL_ACCESS_TOKEN 进行后续操作。"} -->

**说明**: GitLab MCP 服务器已归档，使用 git clone 备用方案

**验证状态**: 已降级，使用 git clone

**用户意图（自然语言任务描述）**:

```
从 GitLab 获取指定仓库的代码。
用户可选择指定分支（如 develop、master）或指定 commit。
获取代码后用于分析改动点。
注意：GitLab MCP 服务器 (@modelcontextprotocol/server-gitlab) 已被归档，使用 git clone 备用方案。
使用系统环境变量中的 GITLAB_API_URL 和 GITLAB_PERSONAL_ACCESS_TOKEN 进行后续操作。
```

**执行方法**:

1. **获取环境变量**:
   ```bash
   # 从系统环境变量获取
   GITLAB_TOKEN=${GITLAB_PERSONAL_ACCESS_TOKEN}
   ```

2. **解析项目信息**:
   - 从用户输入提取项目路径（如 `pay-plus/merch/access/merch-access-standard`）
   - 提取项目名称（最后一段，如 `merch-access-standard`）
   - 构建 GitLab 基地址

3. **执行 git clone**:
   ```bash
   # 确保临时目录存在
   mkdir -p "$TMPDIR/rf-testing"
   cd "$TMPDIR/rf-testing"

   # 清理旧代码（避免冲突）
   rm -rf <项目名称>

   # 使用 oauth2 认证方式 clone 代码（深度1，减少下载量）
   git clone --depth 1 \
     "https://oauth2:${GITLAB_TOKEN}@gitlab.jlpay.com/<项目路径>.git" \
     2>&1
   ```

4. **处理分支和 commit**（用户可选）:
   ```bash
   # 如果用户指定了分支
   if [ -n "$branch_or_commit" ]; then
       cd <项目名称>
       git fetch origin "$branch_or_commit"
       git checkout "$branch_or_commit"
   fi
   ```

**完整示例**:
```bash
# 环境变量
export GITLAB_PERSONAL_ACCESS_TOKEN="your_token_here"

# 项目信息
project_path="pay-plus/merch/access/merch-access-standard"
project_name="merch-access-standard"

# 执行 clone
cd "$TMPDIR/rf-testing"
rm -rf "$project_name"
git clone --depth 1 \
  "https://oauth2:${GITLAB_PERSONAL_ACCESS_TOKEN}@gitlab.jlpay.com/${project_path}.git" \
  2>&1
```

**Windows 命令示例**:
```batch
REM 环境变量
set GITLAB_TOKEN=%GITLAB_PERSONAL_ACCESS_TOKEN%

REM 项目信息
set PROJECT_PATH=pay-plus/merch/access/merch-access-standard
set PROJECT_NAME=merch-access-standard

REM 执行 clone
cd %TEMP%\rf-testing
rmdir /s /q %PROJECT_NAME%
git clone --depth 1 https://oauth2:%GITLAB_TOKEN%@gitlab.jlpay.com/%PROJECT_PATH%.git
```

**重要**:
- 必须使用 `oauth2:` 前缀配合 token
- 使用环境变量获取 token，不要硬编码
- 先清理旧代码再 clone
- 下载到临时目录 `$TMPDIR/rf-testing/` 或 `%TEMP%\rf-testing\`
- 使用 `--depth 1` 减少下载量

<!-- MCP_NODE_METADATA: {"mode":"aiToolSelection","serverId":"gitlab","userIntent":"从 GitLab 或 GitHub 获取指定仓库的代码。\n用户可选择指定分支（如 develop、master）或指定 commit。\n获取代码后用于分析改动点。"} -->

**MCP 服务器**: gitlab

**验证状态**: 有效

**用户意图（自然语言任务描述）**:

```
从 GitLab 或 GitHub 获取指定仓库的代码。
用户可选择指定分支（如 develop、master）或指定 commit。
获取代码后用于分析改动点。
```

**参数**:
- `project_path`: GitLab 项目路径（如 `group/project`）
- `branch_or_commit`: 分支名或 commit SHA
- `output_dir`: 代码输出目录（临时）

**执行方法**:

Claude Code 应分析上述任务描述，在运行时查询 MCP 服务器 "gitlab" 获取当前工具列表。然后，选择最合适的工具，并根据任务要求确定适当的参数值。

#### code_analysis(代码分析)

- **执行方法**: 使用 `Skill` 工具调用 analyze 指令
- **职责**: 使用 analyze 指令进行完整代码分析（9步骤）
- **重要**: 必须使用 `01-RF-Skills/jl-skills/instructions/` 目录下的 analyze 指令
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📊 开始代码分析阶段..."
  2. 使用 `Skill` 工具调用 `analyze:structure-analysis` 指令
  3. 使用 `Skill` 工具调用 `analyze:flow-analysis` 指令
  4. 使用 `Skill` 工具调用 `analyze:impact-analysis` 指令
  5. **✅ 阶段完成**: 输出 "📊 代码分析阶段完成，生成分析报告"
- **输出**: 完整代码分析报告（结构分析、流程分析、影响面分析）
- **重要**: 必须完成全部3个分析步骤后才能进入下一阶段

#### change_detect(改动点识别)

- **执行方法**: 基于代码分析报告手动分析
- **职责**: 基于代码分析结果识别改动点和测试范围
- **输入**: 代码分析报告、改动点（从改动清单中提取）
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🔍 开始改动点识别阶段..."
  2. 从代码分析报告中提取改动信息
  3. 识别新增/修改/删除的代码
  4. 分析改动点的依赖关系
  5. 生成测试建议（功能测试/回归测试）
  6. **✅ 阶段完成**: 输出 "🔍 改动点识别阶段完成，生成改动点清单"
- **输出**:
  - 改动点清单（新增/修改/删除的代码位置和类型）
  - 影响面分析（接口变更影响、数据模型变更影响）
  - 测试建议（高/中优先级测试点、回归测试范围）
  - 涉及的接口名称列表（用于后续 YAPI 查询）

#### mcp_yapi_gitlab(YAPI 接口文档获取 - GitLab 模式)

- **描述**: 根据改动点中涉及的接口名称，从 YAPI 获取接口详细信息
- **执行方法**: 使用 YAPI MCP 服务器
- **输入**: 涉及的接口名称列表（从改动点识别阶段提取）
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📡 开始获取 YAPI 接口文档..."
  2. 检查 YAPI MCP 是否可用
  3. 对每个接口名称调用搜索功能
  4. 获取接口详细信息（请求参数、响应格式、示例）
  5. **✅ 阶段完成**: 输出 "📡 YAPI 接口文档获取完成"
- **输出**: 接口详细信息文档
- **重要**: 必须在改动点识别后执行，才能精准获取接口信息

#### skill_scenario(识别测试场景)

- **提示**: skill "01-RF-Skills/skills/test/SKILL.md" "根据需求内容、代码分析结果和 YAPI 接口文档，识别测试场景"
- **输入**:
  - 需求内容（TAPD 模式）
  - 代码分析报告（GitLab 模式）
  - 改动点清单（GitLab 模式）
  - YAPI 接口文档（GitLab 模式）
- **执行时机**: 必须在前置分析完成后执行
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🎯 开始识别测试场景..."
  2. 分析需求或代码分析结果
  3. 识别正常场景、异常场景、边界场景
  4. **✅ 阶段完成**: 输出 "🎯 测试场景识别完成"
- **输出**: 测试场景列表

#### skill_reference(参考用例分析)

- **描述**: 在生成测试用例之前，询问用户是否有现有用例可供参考
- **目的**: 学习现有用例风格，复用已有关键字和变量，避免重复造轮子
- **执行时机**: 在测试点识别之后，用例生成之前
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📚 开始参考用例分析..."
  2. 询问用户：是否有现有用例目录？
  3. 如果有，提供目录路径
  4. 询问用户：希望完全复用现有风格，还是仅作参考？
  5. 分析参考用例：
     - 扫描 .robot 文件
     - 提取已有关键字
     - 提取已有变量
     - 学习命名风格和结构规范
  6. **✅ 阶段完成**: 输出 "📚 参考用例分析完成"
- **输出**:
  - 可复用关键字清单
  - 可复用变量清单
  - 风格学习报告
  - 复用建议报告

#### skill_points(识别测试点)

- **提示**: skill "01-RF-Skills/skills/test/SKILL.md" "根据测试场景、YAPI 接口文档和参考用例，识别具体测试点"
- **输入**:
  - 测试场景列表
  - YAPI 接口文档（如有）
  - 参考用例分析结果（如有）
- **执行时机**: 必须在测试场景识别完成后执行
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📋 开始识别测试点..."
  2. 为每个测试场景分析测试点
  3. 确定参数值、预期结果、前置条件
  4. **✅ 阶段完成**: 输出 "📋 测试点识别完成"
- **输出**: 测试点列表（含参数、预期、前置）

**输入（GitLab模式）**:
- 测试场景列表
- 改动点清单
- 影响面分析

#### skill_generation(生成 RF 用例)

- **提示**: skill "01-RF-Skills/skills/test/SKILL.md" "根据测试点、YAPI 接口文档和参考用例分析，生成 RF 测试用例"
- **重要**: 必须使用 `01-RF-Skills/skills/test/SKILL.md` 技能，不能自己编写用例
- **输入**:
  - 测试点列表
  - YAPI 接口文档（如有）
  - 参考用例分析结果（如有）
- **执行时机**: 必须在测试点识别和参考用例分析完成后执行
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📝 开始生成 RF 测试用例..."
  2. 根据测试点生成标准4文件结构
  3. 应用命名规范（下划线分隔）
  4. 复用参考用例中的关键字和变量
  5. **✅ 阶段完成**: 输出 "📝 RF 测试用例生成完成"
- **输出**: RF 用例文件（4个标准文件）

#### skill_rf_qa(RF 质量保证与自动修复)

- **执行方法**: 使用 `Skill` 工具调用 rf-standards-check 技能
- **职责**: 验证生成的 RF 用例是否符合 JL 企业标准和最佳实践，**自动修复可修复的问题**
- **重要**: 必须使用 `01-RF-Skills/skills/rf-standards-check/SKILL.md` 技能
- **自动修复能力**:
  1. **目录结构修复**: 自动创建缺失的 Settings.robot、Keywords.robot、Variables.robot
  2. **用例命名修复**: 自动将用例名称中的空格替换为下划线
  3. **Documentation 修复**: 自动调整三段式格式
  4. **变量命名修复**: 自动将驼峰命名改为蛇形命名
  5. **标签补充**: 自动补充缺失的 Tags 和 Timeout

**检查项**:
- 目录结构（4个标准文件）
- 用例命名（下划线分隔，无空格）
- 变量命名（蛇形命名法：${变量名}）
- 关键字命名（驼峰命名法：关键字名）
- 文档格式（三段式格式：概述-前置条件-预期结果）
- Tag 使用（优先级、评审状态）
- JSONPath 表达式正确性

**质量评分标准**:
- 90-100分：优秀，可直接进入下一阶段
- 70-89分：良好，修复轻微问题后进入下一阶段
- 50-69分：及格，必须修复问题后重新检查
- <50分：不合格，需要重写用例

**质量门禁**:
- 评分 >= 70分：通过，进入执行验证阶段
- 评分 < 70分：不通过，返回自动修复阶段

- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🔍 开始 RF 质量保证与自动修复..."
  2. 使用 Skill 工具调用 rf-standards-check 技能
  3. 应用自动修复规则
  4. **✅ 阶段完成**: 输出 "🔍 RF 质量保证与自动修复完成，评分: XX分"

#### skill_results(测试结果分析)

- **执行方法**: 使用 `Skill` 工具调用 test-results-analyzer 指令
- **职责**: 分析 RF 测试执行结果，识别失败模式、趋势和系统性质量问题
- **重要**: 必须使用 `00-JL-Skills/jl-skills/instructions/` 目录下的 test-results-analyzer 指令
- **输出**: 质量报告和改进建议
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "📊 开始测试结果分析..."
  2. 使用 Skill 工具调用 test-results-analyzer 指令
  3. 分析失败模式、质量趋势
  4. **✅ 阶段完成**: 输出 "📊 测试结果分析完成"

#### skill_conversion(RF 转 TAPD 格式)

- **执行方法**: 使用 `Skill` 工具调用 tapd-conversion 技能
- **职责**: 将 RF 用例转换为 TAPD Excel 格式，生成 Base64 编码
- **重要**: 必须使用 `01-RF-Skills/skills/tapd-conversion/SKILL.md` 技能
- **输入**: RF 用例文件路径
- **输出**: TAPD Excel 文件、Base64 编码
- **常见问题**: 如果输出 "成功处理 0 个测试用例"，说明 [Documentation] 缺少 `【预置条件】【操作步骤】【预期结果】` 三段式标记
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🔄 开始 RF 转 TAPD 格式..."
  2. 使用 Skill 工具调用 tapd-conversion 技能
  3. 生成 TAPD Excel 文件和 Base64 编码
  4. **✅ 阶段完成**: 输出 "🔄 RF 转 TAPD 格式完成"

#### plugin_feedback(插件体验建议)

- **描述**: 在所有流程完成后，Claude 给出对当前插件使用的实质性建议
- **执行时机**: TAPD 转换完成后
- **输出内容**:
  - 本次使用的体验评估
  - 遇到的问题和解决方案
  - 对插件的改进建议
  - 工作流执行情况（是否按定义执行）
  - 功能改进建议
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "💡 开始评估插件体验..."
  2. 评估本次使用体验
  3. 总结遇到的问题
  4. 提出改进建议
  5. **✅ 阶段完成**: 输出 "💡 插件体验评估完成"

### 脚本节点

#### script_validate(执行验证 dryrun)

- **脚本**: `03-scripts/rf_runner.py`
- **职责**: 使用 dryrun 模式验证 RF 用例语法正确性
- **执行命令**:
  ```bash
  python 03-scripts/rf_runner.py --dryrun --output-dir ./output <test_dir>
  ```
- **验证内容**:
  - 语法正确性
  - Resource 引用正确性
  - 关键字是否存在
  - 变量是否定义
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🔎 开始执行验证（dryrun）..."
  2. 检查 .robot 文件是否存在
  3. 执行 dryrun 命令
  4. 检查执行结果
  5. **✅ 阶段完成**: 输出 "🔎 执行验证（dryrun）完成"
- **输出**: dryrun 结果（通过/失败）
- **错误处理**:
  - 如果失败，输出详细的错误信息
  - 提供修复建议

#### script_execute(执行 RF 测试用例)

- **命令**: `/rf-testing:execute <robot-file> [选项]`
- **AI 执行方式**: 使用 Skill 工具调用 `rf-testing:execute`，让用户传入 robot 文件路径
- **不要**: 直接使用 Bash 工具执行 `conda activate` 和 `robot` 命令
- **职责**: 执行生成的 RF 测试用例，返回执行结果

**正确执行方式**（AI 应该这样做）：
```
● /rf-testing:execute test.robot --dryrun
```

**错误执行方式**（AI 不要这样做）：
```
● Bash(cd "..." && conda activate python37 && robot --dryrun ...)
```

**自动化执行，无需人工选择 Python 环境**

执行器参考 Cursor 的执行方式，使用临时环境脚本确保正确的 Python 环境：

1. **自动检测 Python 环境**
   - 优先使用安装时保存的 Python 配置
   - 如果没有配置，自动检测并优先选择 Python 3.7.x 版本

2. **创建临时环境脚本**
   - 在临时目录生成环境配置脚本（`%TEMP%/rf-ls-run/`）
   - 设置正确的 PATH 和 PYTHONPATH
   - 确保 JLTestLibrary 可导入

3. **执行 robot 命令**
   - 使用环境脚本启动 robot
   - 确保 site-packages 可访问

- **脚本**: `03-scripts/rf_executor.py` + `rf_runner.py`
- **命令行工具**: `03-scripts/rf_runner.py`
- **环境构建器**: `03-scripts/rf_env_builder.py`
- **函数**: `execute_robot_test()`
- **职责**: 执行生成的 RF 测试用例，返回执行结果
- **执行步骤**:
  1. **✅ 阶段开始**: 输出 "🚀 开始执行 RF 测试用例..."
  2. 检查 Python 环境配置
  3. 创建临时环境脚本
  4. 执行 robot 命令
  5. 解析执行结果
  6. **✅ 阶段完成**: 输出 "🚀 RF 测试用例执行完成"
- **参数**:
  - `robot_file`: .robot 文件路径（必需）
  - `python_path`: Python 环境路径（可选，自动检测）
  - `use_env_script`: 是否使用环境脚本（默认: True）
  - `test_name`: 执行指定测试用例（可选）
  - `suite_name`: 执行指定测试套件（可选）
  - `output_dir`: 输出目录（默认: ./output）
  - `dryrun`: 是否执行 dryrun 模式（默认: False）
  - `env_vars`: 额外的环境变量（可选）
- **返回值**:
  - `success`: 执行是否成功
  - `statistics`: 统计信息（总数/通过/失败/跳过）
  - `tests`: 测试用例列表
  - `log_file`: HTML 日志文件路径
  - `report_file`: HTML 报告文件路径
  - `python_path`: 实际使用的 Python 路径
  - `env_script`: 环境脚本路径
  - `stdout`: 标准输出
  - `stderr`: 标准错误

**临时环境脚本示例（Windows）**：
```batch
@echo off
REM Robot Framework 临时环境
REM 工作目录: d:\workspace\python\merch-services

REM 切换到工作目录
cd /d "d:\workspace\python\merch-services"

REM 设置 Python 路径
set PATH=C:\Users\XUJUNK~1\AppData\Local\miniconda3;C:\Users\XUJUNK~1\AppData\Local\miniconda3\Scripts;%PATH%
set PYTHON=C:\Users\XUJUNK~1\AppData\Local\miniconda3\python.exe

REM 设置 site-packages 路径
if exist "C:\Users\XUJUNK~1\AppData\Local\miniconda3\Lib\site-packages" set PYTHONPATH=C:\Users\XUJUNK~1\AppData\Local\miniconda3\Lib\site-packages;%PYTHONPATH%
```

## 工作流说明

### 执行流程

#### 模式 A: TAPD 需求模式

1. **输入选择** - 用户选择 TAPD 需求模式
2. **需求获取** - 从 TAPD 拉取需求内容
3. **接口文档** - 从 YAPI 获取接口文档（根据需求中的接口名称）
4. **测试设计** - 基于需求内容和接口文档，识别测试场景和测试点
5. **用例生成** - 生成符合 RF 规范的测试用例（4个标准文件）
6. **质量保证与自动修复** - RF 质量保证 Agent 检查并自动修复问题
7. **执行验证** - 使用 dryrun 验证用例语法正确性
8. **质量门禁** - 评分 >= 70分通过，否则返回修复
9. **执行测试** - 执行 RF 测试用例并验证
10. **结果分析** - 测试结果分析 Agent 分析质量指标
11. **TAPD 转换** - 将 RF 用例转换为 TAPD 格式（生成 Excel）

#### 模式 B: GitLab/GitHub 代码分析模式

**阶段1: 代码获取与分析（必须完整完成）**
1. **输入选择** - 用户选择代码分析模式
2. **代码获取** - 从 GitLab/GitHub 获取指定分支或 commit 的代码
3. **代码分析** - 使用 analyze 指令进行完整分析（9步骤，必须全部完成）
   - 结构分析（3步）: 技术栈 → 实体ER图 → 接口入口
   - 流程分析（3步）: 调用链 → 时序 → 复杂逻辑
   - 影响面分析（3步）: 依赖引用 → 数据影响 → 风险评估
4. **改动点识别** - 基于完整的代码分析报告，识别改动点和测试范围

**阶段2: 接口文档获取（基于改动点）**
5. **接口分析** - 从改动点清单中提取涉及的接口名称
6. **YAPI 文档** - 从 YAPI 获取接口详细信息（请求参数、响应格式、示例）

**阶段3: 测试设计（基于接口文档）**
7. **测试设计** - 基于改动点范围和接口文档，识别测试场景和测试点

**阶段4: 用例生成与验证**
8. **用例生成** - 生成符合 RF 规范的测试用例（4个标准文件）
9. **质量保证与自动修复** - RF 质量保证 Agent 检查并自动修复问题
10. **执行验证** - 使用 dryrun 验证用例语法正确性
11. **质量门禁** - 评分 >= 70分通过，否则返回修复

**阶段5: 执行与输出**
12. **执行测试** - 执行 RF 测试用例并验证
13. **结果分析** - 测试结果分析 Agent 分析质量指标
14. **TAPD 转换** - 将 RF 用例转换为 TAPD 格式（生成 Excel）

**阶段4: 执行与输出**
11. **执行测试** - 执行 RF 测试用例并验证
12. **结果分析** - 测试结果分析 Agent 分析质量指标
13. **TAPD 转换** - 将 RF 用例转换为 TAPD 格式（生成 Excel）

### 重要执行原则

**GitLab/GitHub 代码分析模式必须遵循**：
1. **代码分析必须完整** - 9步骤分析（结构3步 + 流程3步 + 影响面3步）必须全部完成
2. **改动点识别必须基于完整分析** - 不能跳过或简化代码分析阶段
3. **测试设计必须基于分析结果** - 测试场景和测试点必须基于改动点清单
4. **禁止混用阶段** - 代码分析和用例生成是不同的阶段，不能同时进行

### 配置参数

**输出目录规范**：
- **临时文件**（拉取的代码、中间结果）：使用系统临时目录下的 `rf-testing/` 子目录
  - Windows: `%TEMP%/rf-testing/` (如 `C:\Users\<username>\AppData\Local\Temp\rf-testing\`)
  - Linux/macOS: `$TMPDIR/rf-testing/` (如 `/tmp/rf-testing/`)
- **最终输出文件**（RF 用例、报告）：使用当前工作目录下的 `./output/`

```json
{
  "tapd_workspace_id": "48200023",
  "temp_dir": "${TMPDIR}/rf-testing/",
  "output_dir": "./output",
  "creator": "测试工程师",
  "test_case_priority": "P0,P1,P2",
  "gitlab": {
    "api_url": "${GITLAB_API_URL}",
    "token": "${GITLAB_PERSONAL_ACCESS_TOKEN}"
  },
  "github": {
    "token": "${GITHUB_TOKEN}"
  }
}
```

**重要提示**：
- 所有临时文件（包括从 GitLab/GitHub 拉取的代码）必须存放在系统临时目录下
- 最终生成的 RF 用例文件和报告存放在当前工作目录的 `./output/` 下
- 临时目录中的文件在任务完成后可以清理

### 输出结果

- RF 用例文件（标准4文件结构）
- 代码分析报告（GitLab模式）
- 改动点清单（GitLab模式）
- 质量保证报告（含自动修复记录）
- 执行验证报告（dryrun 结果）
- 测试执行报告
- HTML 日志和报告
- 测试结果分析报告
- TAPD Excel 文件
- 用例数量统计
