# Robot Framework 测试插件

基于 **AI-First 插件标准**构建的 Robot Framework 测试用例生成与转换插件，对标开发工作流提供测试工程师视角能力。

## 功能

- 🔍 **双模式启动**: 支持 TAPD 需求或 GitLab/GitHub 代码分析两种输入模式
- 📊 **代码分析**: 9步骤代码深度分析（结构/流程/影响面），识别改动点和测试范围
- 📝 **用例生成**: 基于测试点生成符合 RF 规范的用例脚本
- ✅ **质量保证**: RF 质量保证 Agent 检查用例质量和标准合规性
- 🔬 **规范检查**: 检查 RF 用例是否符合 JL 企业编写规范
- 📈 **结果分析**: 测试结果分析 Agent 识别失败模式和质量趋势
- 📊 **TAPD 转换**: 将 RF 用例转换为 TAPD 可导入格式
- 🔄 **工作流编排**: 支持完整的测试工作流和子流程

## 快速开始

### 1. 安装插件

通过 marketplace 安装插件：

```text
/plugin marketplace add %USERPROFILE%\.claude\plugins\rf-testing-plugin
/plugin install rf-testing
```

或使用一键安装脚本：

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

### 2. 配置环境变量

**推荐方式：使用安装脚本配置**

安装脚本会自动引导配置环境变量和 MCP 服务器，按提示输入即可。

**获取访问令牌：**

- **TAPD Token**: https://www.tapd.cn/personal_settings/index?tab=personal_token
- **GitLab Token**: https://gitlab.jlpay.com/-/user_settings/personal_access_tokens?name=rf-testing-plugin&scopes=api%2Cread_user

**手动配置：**

必需环境变量：
```bash
export TAPD_ACCESS_TOKEN="your-tapd-token"
```

可选环境变量（如需 GitLab/GitHub/YAPI 支持）：
```bash
# GitLab
export GITLAB_API_URL="https://gitlab.example.com/api/v4"
export GITLAB_PERSONAL_ACCESS_TOKEN="your-gitlab-token"

# GitHub
export GITHUB_TOKEN="your-github-token"

# YAPI
export YAPI_TOKEN="project_id:project_token"
```

**Windows 手动配置：**
1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在"用户变量"中添加上述变量
3. 重启终端或 Claude

**Linux/macOS 手动配置：**
```bash
# 添加到 ~/.bashrc 或 ~/.zshrc
export TAPD_ACCESS_TOKEN="your-tapd-token"
export GITLAB_API_URL="https://gitlab.example.com/api/v4"
export GITLAB_PERSONAL_ACCESS_TOKEN="your-gitlab-token"
export GITHUB_TOKEN="your-github-token"
export YAPI_TOKEN="project_id:project_token"

# 使配置生效
source ~/.bashrc  # 或 source ~/.zshrc
```

### 2. 安装依赖

#### 安装 uv（TAPD MCP 服务器依赖）

TAPD MCP 服务器需要 `uv` 工具来运行 `mcp-server-tapd`：

```bash
# macOS
brew install uv

# Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

验证安装：
```bash
uvx --version
```

#### 使用安装脚本（推荐）

安装脚本会自动：

1. 智能检测系统中所有符合条件的 Python 环境（3.7.16+）
2. 自动推荐最合适的 Python 版本
3. 自动检测 site-packages 目录
4. 自动安装所有依赖
5. 自动安装 JLTestLibrary
6. 可选配置环境变量和 MCP 服务器

**Windows:**
```cmd
install.bat
```

**Linux/macOS:**
```bash
chmod +x install.sh
./install.sh
```

#### 手动安装

详见 `requirements.txt`：

```bash
pip install -r requirements.txt
```

手动安装 JLTestLibrary：
```bash
unzip 03-scripts/JLTestLibrary.zip -d $HOME/Library/Python/3.7/site-packages/
```

### 4. 目录结构

```
rf-testing-plugin/
├── 00-JL-Skills/          # JL 公共库（指令、规范、模板）
├── 01-RF-Skills/          # RF 测试技能
├── 02-agents/             # 测试 agents
│   ├── testing-rf-quality-assurance.md   # RF 质量保证 agent
│   ├── testing-code-analyzer.md          # 代码分析 agent
│   ├── testing-change-detector.md        # 改动点识别 agent
│   └── testing-results-analyzer.md       # 结果分析 agent
├── 03-scripts/            # 实用脚本和资源
│   ├── JLTestLibrary.zip  # Robot Framework 自定义测试库
│   ├── robot2tapd.py
│   ├── batch_convert.sh
│   └── python_detector.py # Python 环境智能检测
├── 04-cases/              # 使用案例
├── 05-plugins/            # 插件目录
│   └── rf-testing/        # rf-testing 插件
│       ├── workflows/     # 工作流定义
│       │   ├── full-test-pipeline.md    # 双模式工作流
│       │   ├── requirement-to-rf.md
│       │   └── rf-to-tapd.md
│       ├── commands/      # 入口命令
│       ├── .mcp.json      # MCP 配置（TAPD、GitLab、YAPI）
│       └── README.md
├── docs/                  # 文档
├── .claude-plugin/        # Plugin 元数据
└── README.md
```

## MCP 服务器

插件集成以下 MCP 服务器：

### TAPD MCP 服务器

**功能：**
- **项目**：查询项目信息和配置
- **需求**：查询需求列表、创建新需求、更新需求字段、查询需求字段配置
- **缺陷**：查询缺陷列表、创建新缺陷、更新缺陷字段、查询缺陷字段配置
- **迭代**：查询迭代列表
- **评论**：业务对象添加评论

**配置：**
```json
{
  "mcpServers": {
    "tapd": {
      "command": "uvx",
      "args": ["mcp-server-tapd"],
      "env": {
        "TAPD_ACCESS_TOKEN": "${TAPD_ACCESS_TOKEN}"
      }
    }
  }
}
```

**依赖：** 需要安装 `uv` 工具（见上方安装说明）

### GitLab MCP 服务器

**功能：**
- 读取仓库信息
- 获取文件内容
- 创建提交和合并请求

**配置：**
```json
{
  "mcpServers": {
    "gitlab": {
      "command": "cmd",
      "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-gitlab"],
      "env": {
        "GITLAB_API_URL": "${GITLAB_API_URL}",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

## 使用方式

### 双模式启动

插件支持两种输入模式启动：

**模式 A: TAPD 需求模式**
```bash
/rf-testing:start <tapd-link>
```

**模式 B: GitLab/GitHub 代码分析模式**
```bash
/rf-testing:start <project-path>
```

如果不传参数，插件会询问用户选择输入方式。

### 完整测试流程

从输入到 TAPD 导出的完整流程。

```bash
/rf-testing:start <tapd-link>
```

如果不传链接，插件会直接向用户索要 TAPD 需求链接。

### 子工作流

#### 需求转用例

```bash
/rf-testing:requirement-to-rf <tapd-link>
```

#### RF 转 TAPD

```bash
/rf-testing:rf-to-tapd <robot-file-path>
```

## 核心技能

### rf-test

场景测试生成技能，对标开发工作流的测试闭环。

**流程**：
1. 从 TAPD 拉取需求内容
2. 识别测试场景和测试点
3. 生成 Robot Framework 用例
4. RF 质量保证检查
5. 检查 RF 规范
6. 转换为 TAPD 格式并导出

### rf-standards-check

RF 编写规范检查技能。

**检查项**：
- [Documentation] 标签格式（三段式）
- [Tags] 标签使用（优先级、评审状态）
- 变量命名规范（蛇形命名法：${变量名}）
- 关键字命名规范（驼峰命名法：关键字名）
- 内联注释使用
- JSONPath 表达式正确性

### rf-tapd-conversion

RF 用例转 TAPD 格式技能。

**转换步骤**：
1. 解析 RF 用例文件
2. 转换为 TAPD 格式
3. 生成 Excel 文件
4. 生成 Base64 编码

## RF 质量保证 Agent

`testing-rf-quality-assurance` agent 负责验证生成的 RF 用例是否符合 JL 企业标准和最佳实践。

### 检查项

- **变量命名**: 蛇形命名法 `${变量名}`
- **关键字命名**: 驼峰命名法 `关键字名`
- **文档格式**: 三段式格式（概述-前置条件-预期结果）
- **Tag 使用**: 包含优先级和评审状态
- **JSONPath 表达式**: 验证正确性

### 成功指标

- 90% 的 RF 用例首次评审通过质量门禁
- 95% 符合 JL 企业标准
- 质量评审周转时间 < 2 小时/用例

## 工作流节点

### MCP 节点

| 节点 | MCP 服务器 | 功能 |
|------|------------|------|
| mcp_fetch | tapd | 从 TAPD 拉取需求内容 |
| mcp_export | tapd | 将测试用例导出到 TAPD |

### 技能节点

| 节点 | 技能 | 功能 |
|------|------|------|
| skill_scenario | rf-test | 识别测试场景 |
| skill_points | rf-test | 识别测试点 |
| skill_generation | rf-test | 生成 RF 用例 |
| skill_validation | rf-standards-check | 检查 RF 规范 |
| skill_conversion | rf-tapd-conversion | RF 转 TAPD 格式 |

### Agent 节点

| 节点 | Agent | 功能 |
|------|-------|------|
| agent_rf_qa | testing-rf-quality-assurance | RF 质量保证检查 |
| agent_code_analyzer | testing-code-analyzer | 代码分析（9步骤） |
| agent_change_detector | testing-change-detector | 改动点识别 |
| agent_results | testing-results-analyzer | 测试结果分析 |

## 实用脚本

### robot2tapd.py

RF 用例转 TAPD Excel 格式脚本。

**用法**：
```bash
python 03-scripts/robot2tapd.py <robot_path> \
    --excel <output_excel> \
    --dir <用例目录> \
    --sheet <工作表名称> \
    --creator <创建人> \
    --out-b64 <base64_file>
```

### batch_convert.sh

批量转换脚本。

**用法**：
```bash
./03-scripts/batch_convert.sh <robot_dir> <output_dir> <creator>
```

### JLTestLibrary

Robot Framework 自定义测试库，位于 `03-scripts/JLTestLibrary.zip`。

**安装方式**：
```bash
# 解压到项目目录或 Python 环境的 site-packages
unzip 03-scripts/JLTestLibrary.zip -d <target_dir>
```

## Python 环境智能检测

安装脚本支持以下 Python 环境的自动检测：

| 环境类型 | 说明 | 示例路径 |
|---------|------|---------|
| Conda | 所有 conda 环境 | `conda: rf-env (3.7.18)` |
| System | 系统安装的 Python | `system: /usr/bin/python3.8` |
| Venv | 虚拟环境 | `venv: /path/to/venv` |

脚本会自动优先选择最接近 3.7.16+ 的版本，确保 JLTestLibrary 兼容性。

### 检测示例

```
检测到以下 Python 环境：

[推荐] 1. conda: rf-env (3.7.18)  [当前激活]
       2. conda: py37 (3.7.16)
       3. system: /usr/bin/python3.8 (3.8.10)

请选择目标 Python 环境 [1-3, 默认=1]:
```

## 模板和规范

### RF 用例模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-RF-TestCase.md`

包含：
- 用例文件结构
- Documentation 三段式格式
- Tags 标签规范
- 变量命名规范

### 关键字模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-RF-Keyword.md`

包含：
- 关键字结构标准
- 三要素规范（Documentation、Arguments、Return）
- 关键字分类和命名规范

### TAPD 报告模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-TAPD-Report.md`

包含：
- 报告结构
- 统计信息格式
- Markdown 表格格式

### 规范文档

- `RF 关键字编写规范.md`: 关键字编写标准
- `BuiltIn 库使用规范.md`: BuiltIn 库使用指南
- `JSONPath 使用指南.md`: JSONPath 语法和示例
- `DateTime 库使用规范.md`: DateTime 库使用指南
- `商户系统业务规范.md`: 商户系统业务领域规范

## 使用案例

详见 `04-cases/README.md`：

- 案例1：商户状态变更测试
- 案例2：批量转换现有用例
- 案例3：规范检查
- 案例4：仅需求转用例
- 案例5：仅 RF 转 TAPD

## 架构设计

遵循 **AI-First 插件标准**：

- ✅ Claude Plugin 元数据格式（`.claude-plugin/marketplace.json` + `plugin.json`）
- ✅ Mermaid flowchart 工作流编排
- ✅ MCP 配置（`.mcp.json`）
- ✅ 统一交互协议（INTERACTION_PROTOCOL.md）
- ✅ SKILL.md 格式的技能定义
- ✅ jl-skills 公共库（指令/规范/模板）
- ✅ MCP Task 集成（TAPD、GitLab）
- ✅ 测试 Agents 集成

## 配置参数

```json
{
  "tapd_workspace_id": "48200023",
  "output_dir": "./output",
  "creator": "测试工程师",
  "test_case_priority": "P0,P1,P2"
}
```

## 依赖

详见 `requirements.txt`

```bash
pip install -r requirements.txt
```

## 参考

- [AI-First 开发插件](https://gitlab.jlpay.com/pay-plus/base/ai-first)
- [Robot Framework 官方文档](https://robotframework.org/)
- [TAPD 平台](https://www.tapd.cn/)

## License

MIT