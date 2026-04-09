# Robot Framework 测试插件

基于 **AI-First 插件标准**构建的 Robot Framework 测试用例生成、执行与转换插件，对标开发工作流提供测试工程师视角能力。

**当前版本：v2.7.1**

## 功能

- 🔍 **双模式启动**: 支持 TAPD 需求或 GitLab/GitHub 代码分析两种输入模式
- 🔗 **需求代码互补验证**: TAPD 模式下自动获取关联代码，验证是否符合需求
- 📊 **代码分析**: 9步骤代码深度分析（结构/流程/影响面），识别改动点和测试范围
- 📝 **用例生成**: 基于测试点生成符合 RF 规范的用例脚本
- 🚀 **用例执行**: 新增执行命令，支持 dryrun 验证和完整执行
- ✅ **质量保证**: RF 质量保证 Skill 检查用例质量和标准合规性
- 🔬 **规范检查**: 检查 RF 用例是否符合 JL 企业编写规范
- 📈 **结果分析**: 测试结果分析 Agent 识别失败模式和质量趋势
- 📊 **TAPD 转换**: 将 RF 用例转换为 TAPD 可导入格式
- 🔄 **工作流编排**: 支持完整的测试工作流和子流程，包含执行约束和质量门禁

## 快速开始

### 1. 安装插件

**方式1：本地安装（推荐）**

1. 下载或克隆插件到本地目录
2. 在 Claude Code 中执行：

```text
/plugin marketplace add <插件目录路径>
/plugin install rf-testing
```

示例（Windows）：
```text
/plugin marketplace add D:\workspace\python\rf-testing-plugin
/plugin install rf-testing
```

示例（Linux/macOS）：
```text
/plugin marketplace add ~/rf-testing-plugin
/plugin install rf-testing
```

**方式2：使用一键安装脚本**

安装脚本会自动配置 Python 依赖、环境变量和 MCP 服务器：

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

### 可用命令

| 命令 | 用途 | 示例 |
|------|------|------|
| `/rf-testing:start` | 启动完整测试工作流（自动识别输入类型） | `/rf-testing:start <tapd-link>` |
| `/rf-testing:gitlab` | 从 GitLab 代码分析启动 | `/rf-testing:gitlab group/project` |
| `/rf-testing:github` | 从 GitHub 代码分析启动 | `/rf-testing:github owner/repo` |
| `/rf-testing:requirement-to-rf` | 仅需求转 RF 用例 | `/rf-testing:requirement-to-rf <tapd-link>` |
| `/rf-testing:rf-to-tapd` | 仅 RF 转 TAPD 格式 | `/rf-testing:rf-to-tapd <robot-file>` |
| `/rf-testing:execute` | 执行 RF 测试用例 | `/rf-testing:execute test.robot --dryrun` |

### 命令详解

#### /rf-testing:start - 启动完整测试工作流

该命令会自动识别输入类型并启动对应的工作流分支：

**TAPD 需求模式**：
```bash
/rf-testing:start https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
```

**GitLab/GitHub 代码分析模式**：
```bash
/rf-testing:start mygroup/myproject
```

**工作流流程**：
1. 输入源自动检测（TAPD/GitLab/GitHub）
2. TAPD 分支：需求获取 → 测试设计 → 参考用例分析 → 测试用例生成 → RF 质量检查 → TAPD 转换
3. GitLab 分支：代码获取 → 代码分析（9步骤）→ 改动点识别 → 测试设计 → ...（后续同 TAPD 分支）
4. RF 质量门禁（评分 >= 70 才能继续）
5. dryrun 验证语法
6. 完整执行测试用例
7. 插件体验评估

#### /rf-testing:execute - 执行 RF 测试用例

该命令用于执行已生成的 Robot Framework 测试用例，支持多种执行选项：

**基本用法**：
```bash
/rf-testing:execute test.robot
```

**dryrun 模式（验证语法，不执行）**：
```bash
/rf-testing:execute test.robot --dryrun
```

**执行指定测试用例**：
```bash
/rf-testing:execute test.robot --test "测试用例名称"
```

**执行指定测试套件**：
```bash
/rf-testing:execute test.robot --suite "测试套件名称"
```

**按标签过滤**：
```bash
# 仅执行包含 P0 标签的用例
/rf-testing:execute test.robot --include P0

# 仅执行包含 P0 和 smoke 标签的用例
/rf-testing:execute test.robot --include P0 --include smoke

# 排除包含 slow 标签的用例
/rf-testing:execute test.robot --exclude slow
```

**设置变量**：
```bash
# 设置单个变量
/rf-testing:execute test.robot --variable ENV:test

# 设置多个变量
/rf-testing:execute test.robot --variable ENV:test --variable USER:admin
```

**使用变量文件**：
```bash
/rf-testing:execute test.robot --variablefile variables.py
```

**自定义输出目录**：
```bash
/rf-testing:execute test.robot --outputdir ./my_output
```

**设置日志级别**：
```bash
/rf-testing:execute test.robot --loglevel DEBUG
```

**可用日志级别**：TRACE, DEBUG, INFO, WARN, NONE

**完整选项示例**：
```bash
/rf-testing:execute test.robot \
  --test "登录测试" \
  --include P0 \
  --variable ENV:prod \
  --outputdir ./results \
  --loglevel DEBUG
```

**执行脚本功能**：

该命令会自动：
1. 检测 Python 环境（优先使用保存的环境或自动检测 3.7.x）
2. 创建临时环境脚本（设置 PYTHONPATH 等环境变量）
3. 执行 robot 命令
4. 生成测试报告（output.xml, log.html, report.html）

**工作流中的执行**：

在完整测试工作流中，执行步骤会自动调用此命令：

```markdown
## script_execute 节点

AI 应该执行以下命令来运行 RF 测试用例：

/rf-testing:execute <robot-file>

然后根据执行结果分析失败原因，必要时进行修复。
```

#### /rf-testing:gitlab - GitLab 代码分析

直接从 GitLab 项目启动代码分析模式：

```bash
/rf-testing:gitlab <project-path>
```

**示例**：
```bash
/rf-testing:gitlab pay-plus/base/ai-first
```

**代码分析流程（9步骤）**：
1. 技术栈识别（框架、库、工具）
2. 实体 ER 图分析（数据模型、关系）
3. 接口入口识别（API 端点、消息队列）
4. 调用链分析（模块间依赖、数据流）
5. 时序分析（执行流程、并发场景）
6. 复杂逻辑识别（条件判断、循环、异常处理）
7. 依赖引用分析（模块引用、外部依赖）
8. 数据影响分析（数据变更影响范围）
9. 风险评估（测试覆盖建议、质量风险）

#### /rf-testing:github - GitHub 代码分析

直接从 GitHub 仓库启动代码分析模式：

```bash
/rf-testing:github <repo-path>
```

**示例**：
```bash
/rf-testing:github facebook/react
```

流程与 GitLab 模式相同。

#### /rf-testing:requirement-to-rf - 需求转用例

仅执行需求到 RF 用例的转换，不执行测试：

```bash
/rf-testing:requirement-to-rf <tapd-link>
```

**流程**：
1. 从 TAPD 获取需求
2. 分析需求内容
3. 识别测试场景和测试点
4. 参考用例分析（可选）
5. 生成 RF 用例
6. RF 质量检查
7. 规范检查

#### /rf-testing:rf-to-tapd - RF 转 TAPD

仅执行 RF 用例到 TAPD 格式的转换：

```bash
/rf-testing:rf-to-tapd <robot-file-path>
```

**流程**：
1. 解析 RF 用例文件
2. 检查 Documentation 格式
3. 转换为 TAPD 格式
4. 生成 Excel 文件
5. 生成 Base64 编码

### 双模式启动

插件支持两种输入模式启动，会自动检测输入类型：

**模式 A: TAPD 需求模式**
```bash
/rf-testing:start https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
```

**模式 B: GitLab/GitHub 代码分析模式**
```bash
/rf-testing:start mygroup/myproject
```

**自动检测逻辑**：
- TAPD: URL 包含 `tapd.cn` 或 `www.tapd` → 自动提取 workspace_id 和 story_id
- GitLab: URL/路径包含 `gitlab` → 自动提取项目路径
- GitHub: URL/路径包含 `github.com` → 自动提取仓库路径

如果不传参数，插件会询问用户选择输入方式。

### 专用命令

#### GitLab 代码分析

直接从 GitLab 项目启动代码分析模式：
```bash
/rf-testing:gitlab <project-path>
```

示例：
```bash
/rf-testing:gitlab pay-plus/base/ai-first
```

#### GitHub 代码分析

直接从 GitHub 仓库启动代码分析模式：
```bash
/rf-testing:github <repo-path>
```

示例：
```bash
/rf-testing:github facebook/react
```

### 子工作流

#### 需求转用例

仅执行需求到 RF 用例的转换，不执行测试：
```bash
/rf-testing:requirement-to-rf <tapd-link>
```

#### RF 转 TAPD

仅执行 RF 用例到 TAPD 格式的转换：
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
| skill_rf_qa | rf-standards-check | RF 质量保证检查 |
| skill_results | test-results-analyzer | 测试结果分析 |
| skill_reference | test | 参考用例分析 |

### Agent 节点

| 节点 | Agent | 功能 |
|------|-------|------|
| agent_code_analyzer | testing-code-analyzer | 代码分析（9步骤） |
| agent_change_detector | testing-change-detector | 改动点识别 |

> 注意：`agent_rf_qa` 和 `agent_results` 已改为 Skill 节点，详见技能节点表。

### 工作流执行约束

完整测试工作流包含以下执行约束，确保流程质量和一致性：

1. **阶段顺序**：必须严格按照工作流定义的顺序执行节点，不得跳过
2. **状态输出**：每个阶段开始时输出 `阶段开始`，执行动作，完成后输出 `阶段完成`
3. **错误停止**：遇到错误时停止并报告问题，不得继续执行
4. **工具使用**：明确说明使用哪个工具调用哪个技能
5. **结果验证**：每个阶段完成后验证输出是否符合预期

**执行状态指示**：
- ✅ 表示步骤已完成
- ⚠️ 表示警告或注意事项
- ❌ 表示错误或失败

### 质量门禁

工作流包含质量门禁机制：

- **RF 质量检查评分 >= 70**：才能进入 TAPD 转换阶段
- **dryrun 验证通过**：确保用例语法正确才能执行
- **执行结果通过**：所有测试用例通过才能完成工作流

### 插件体验评估

工作流完成后会进行插件体验评估，收集以下信息：

- 本次使用体验总结
- 遇到的问题和解决方案
- 对插件的改进建议
- 工作流执行情况评估（是否按定义执行）

## 实用脚本

### rf_runner.py - Robot Framework 执行脚本

位于 `03-scripts/rf_runner.py`，是 RF 测试执行的核心脚本。

**功能**：
- 自动检测 Python 环境（优先使用保存的环境或自动检测 3.7.x）
- 创建临时环境脚本（设置 PYTHONPATH 等环境变量）
- 执行 robot 命令
- 生成测试报告（output.xml, log.html, report.html）

**参数说明**：
```
位置参数:
  robot_file          Robot Framework 测试文件 (.robot)

可选参数:
  --python PYTHON     Python 可执行文件路径
  --test TEST         执行指定测试用例
  --suite SUITE       执行指定测试套件
  --include TAG       包含标签（可多次使用）
  --exclude TAG       排除标签（可多次使用）
  --variable VAR      设置变量 KEY:VAL（可多次使用）
  --variablefile FILE 加载变量文件
  --outputdir DIR     输出目录（默认: ./output）
  --loglevel LEVEL    日志级别（默认: INFO）
  --listener PATH     Listener 脚本路径
  --dryrun            验证语法但不执行
  --no-env-script     不使用环境脚本（直接执行）
```

**使用示例**：
```bash
# 基本执行
python 03-scripts/rf_runner.py test.robot

# dryrun 模式
python 03-scripts/rf_runner.py test.robot --dryrun

# 执行指定用例
python 03-scripts/rf_runner.py test.robot --test "登录测试"

# 按标签过滤
python 03-scripts/rf_runner.py test.robot --include P0 --exclude slow

# 设置变量
python 03-scripts/rf_runner.py test.robot --variable ENV:test --variable USER:admin
```

**临时环境脚本**：

脚本会创建临时环境脚本用于设置执行环境：

- Windows: `%TEMP%/rf-ls-run/run_env_<timestamp>_<random>.bat`
- Unix/Linux/macOS: `$TMPDIR/rf-ls-run/run_env_<timestamp>_<random>.sh`

环境脚本功能：
- 切换到工作目录（.robot 文件所在目录）
- 设置正确的 PATH（Python 可执行文件目录）
- 设置 PYTHON 变量
- 设置 PYTHONPATH（site-packages 目录）
- 支持额外的环境变量

### rf_env_builder.py - 临时环境构建器

位于 `03-scripts/rf_env_builder.py`，负责创建临时环境脚本。

**使用方式**：
```python
from rf_env_builder import RFEnvBuilder, prepare_execution_env

# 方式1: 使用 RFEnvBuilder 类
builder = RFEnvBuilder(python_path="/path/to/python")
env_script = builder.create_env_script(work_dir="/path/to/work")

# 方式2: 使用便捷函数
env_info = prepare_execution_env(
    python_path="/path/to/python",
    work_dir="/path/to/work",
    extra_vars={"MY_VAR": "value"}
)
print(env_info["env_script"])
```

### rf_listener.py - RF 执行监听器

位于 `03-scripts/rf_listener.py`，实时捕获和输出测试进度。

**功能**：
- 捕获测试套件和测试用例的执行事件
- 实时输出测试进度（PASS/FAIL/SKIP 状态）
- 彩色输出和执行时间统计
- 提供测试汇总报告

### rf_parser.py - RF 结果解析器

位于 `03-scripts/rf_parser.py`，解析 Robot Framework 的 output.xml 文件。

**功能**：
- 提取统计信息（总数、通过、失败、跳过）
- 解析测试用例详情（名称、状态、耗时、标签、错误消息）
- 解析测试套件结构

**使用示例**：
```python
from rf_parser import RFResultParser

parser = RFResultParser("output/output.xml")
stats = parser.get_statistics()
print(f"总数: {stats['total']}, 通过: {stats['passed']}")

test_cases = parser.get_test_cases()
for case in test_cases:
    print(f"{case['name']}: {case['status']}")
```

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

### 案例 1：TAPD 需求转 RF 用例并执行

从 TAPD 需求开始，生成测试用例并执行验证：

```bash
/rf-testing:start https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
```

**工作流流程**：
1. 从 TAPD 获取需求详情
2. 分析需求内容，识别测试场景
3. 识别测试点
4. 询问是否有参考用例目录（可选）
5. 生成 RF 测试用例（4 文件结构）
6. RF 质量检查（评分 >= 70 才能继续）
7. dryrun 验证语法
8. 完整执行测试用例
9. 转换为 TAPD 格式
10. 插件体验评估

**输出文件**：
- `Settings.robot` - 套件设置
- `Keywords.robot` - 关键字定义
- `Variables.robot` - 变量定义
- `<需求名称>_测试用例.robot` - 测试用例
- `output/output.xml` - 执行结果
- `output/log.html` - 日志报告
- `output/report.html` - 测试报告

### 案例 2：GitLab 代码分析模式

从 GitLab 项目代码开始，分析改动并生成测试用例：

```bash
/rf-testing:gitlab pay-plus/base/ai-first
```

**工作流流程**：
1. 使用 git clone 获取代码（需要配置 `GITLAB_PERSONAL_ACCESS_TOKEN`）
2. 代码分析（9步骤）：
   - 技术栈识别
   - 实体 ER 图分析
   - 接口入口识别
   - 调用链分析
   - 时序分析
   - 复杂逻辑识别
   - 依赖引用分析
   - 数据影响分析
   - 风险评估
3. 改动点识别
4. 从 YAPI 获取接口文档（可选，需要配置 YAPI）
5. 测试设计
6. 识别测试点
7. 参考用例分析（可选）
8. 生成 RF 测试用例
9. RF 质量检查
10. dryrun 验证
11. 完整执行
12. 转换为 TAPD 格式

### 案例 3：仅需求转用例（不执行）

只需要生成用例，不需要执行和转换：

```bash
/rf-testing:requirement-to-rf https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
```

**流程**：获取需求 → 分析 → 生成用例 → 质量检查 → 完成

### 案例 4：仅 RF 转 TAPD

已有 RF 用例，需要转换为 TAPD 格式：

```bash
/rf-testing:rf-to-tapd ./test_cases/商户状态变更_测试用例.robot
```

**流程**：解析用例 → 检查格式 → 转换 → 生成 Excel

### 案例 5：dryrun 验证语法

验证 RF 用例语法是否正确，不实际执行：

```bash
/rf-testing:execute test.robot --dryrun
```

### 案例 6：执行指定测试用例

只执行某个特定的测试用例：

```bash
/rf-testing:execute test.robot --test "登录测试"
```

### 案例 7：按标签过滤执行

只执行包含特定标签的测试用例：

```bash
# 只执行 P0 级别的用例
/rf-testing:execute test.robot --include P0

# 执行 smoke 测试，排除 slow 用例
/rf-testing:execute test.robot --include smoke --exclude slow
```

### 案例 8：批量转换现有用例

将多个 RF 用例批量转换为 TAPD 格式：

```bash
./03-scripts/batch_convert.sh ./robot_files ./output/tapd "测试工程师"
```

**输出**：
- `./output/tapd/用例1.xlsx`
- `./output/tapd/用例2.xlsx`
- ...

### 案例 9：规范检查

检查 RF 用例是否符合 JL 企业规范：

```bash
/rf-testing:rf-standards-check test.robot
```

**检查项**：
- [Documentation] 格式（三段式）
- [Tags] 使用（优先级、评审状态）
- 变量命名（蛇形命名法）
- 关键字命名（驼峰命名法）
- JSONPath 表达式正确性

详见 `04-cases/README.md`

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

## 故障排除

### 命令执行问题

**问题：Claude 无法识别 `/rf-testing:execute` 命令**

确保插件已正确安装：
1. 检查插件目录是否存在：`%USERPROFILE%\.claude\plugins\rf-testing-plugin` (Windows) 或 `~/.claude/plugins/rf-testing-plugin` (Linux/macOS)
2. 重启 Claude Code
3. 重新添加 marketplace：
   ```text
   /plugin marketplace add <插件目录>
   /plugin install rf-testing
   ```

**问题：执行命令时找不到脚本**

由于工作目录可能不在插件目录，命令会动态检查脚本路径：
1. 先尝试 `${CLAUDE_PLUGIN_ROOT}/03-scripts/rf_runner.py`
2. 如果不存在，再尝试 `${CLAUDE_PLUGIN_ROOT}/../../03-scripts/rf_runner.py`

如果仍报错，检查：
1. 确认 `03-scripts/rf_runner.py` 文件存在
2. 确认 Python 环境配置正确

**问题：执行时提示找不到 Python**

脚本会自动检测 Python 环境，优先级：
1. 用户指定的 `--python` 参数
2. 安装时保存的 Python 路径
3. 自动检测（优先 3.7.x）

如果检测失败：
```bash
# 手动指定 Python 路径
/rf-testing:execute test.robot --python /path/to/python
```

**问题：中文路径显示乱码**

从 v2.6.3 开始，脚本已修复中文路径支持：
- 使用 `subprocess.list2cmdline` 正确处理命令编码
- 环境脚本使用 UTF-8 编码并添加 `chcp 65001`（Windows）

如果仍有问题，确保：
1. 终端编码设置为 UTF-8
2. 不在路径中使用特殊字符

### 工作流执行问题

**问题：工作流在某个节点停止**

工作流有严格的执行约束，遇到错误会停止：
1. 检查节点输出中的错误信息
2. AI 会自动尝试修复大部分问题
3. 仅在业务逻辑不明确或架构性问题时才会停止

**问题：RF 质量检查评分 < 70**

质量门禁要求评分 >= 70 才能继续：
1. 检查质量检查报告中的问题列表
2. AI 会自动修复常见问题（命名、文档格式、目录结构等）
3. 如果评分仍然不达标，需要人工介入检查用例设计

**问题：dryrun 验证失败**

dryrun 用于验证语法，不执行用例：
1. 检查错误信息，通常是语法问题
2. 常见问题：
   - 关键字未定义
   - 变量未定义
   - 语法错误（缩进、引号等）
3. 修复后重新执行 dryrun

### 环境配置问题

**问题：安装脚本复制文件失败**

如果 `install.bat` 或 `install.sh` 在复制文件时失败，可以手动复制：

**Windows 手动复制：**
```cmd
REM 删除已存在的插件目录（如果有）
rmdir /s /q %USERPROFILE%\.claude\plugins\rf-testing-plugin

REM 创建插件目录并复制文件
mkdir %USERPROFILE%\.claude\plugins\rf-testing-plugin
robocopy D:\workspace\python\rf-testing-plugin %USERPROFILE%\.claude\plugins\rf-testing-plugin /E /XD .claude .git
```

**Linux/macOS 手动复制：**
```bash
# 删除已存在的插件目录（如果有）
rm -rf ~/.claude/plugins/rf-testing-plugin

# 创建插件目录并复制文件
mkdir -p ~/.claude/plugins/rf-testing-plugin
rsync -av --exclude='.claude' --exclude='.git' ~/rf-testing-plugin/ ~/.claude/plugins/rf-testing-plugin/
```

**问题：安装脚本提示找不到 Python**

确保 Python 已安装并添加到 PATH：
```cmd
where python
```

如果未找到，请安装 Python 3.7.16+ 并勾选 "Add Python to PATH"。

**问题：安装后 Claude 无法识别插件**

1. 确认插件文件已复制到 `%USERPROFILE%\.claude\plugins\rf-testing-plugin` (Windows) 或 `~/.claude/plugins/rf-testing-plugin` (Linux/macOS)
2. 清理缓存：
   - Windows: 删除 `%USERPROFILE%\.claude\plugins\cache\rf-testing-plugin`
   - Linux/macOS: 删除 `~/.claude/plugins/cache/rf-testing-plugin`
3. 重启 Claude Code
4. 重新添加 marketplace：
   ```text
   /plugin marketplace add <插件目录>
   /plugin install rf-testing
   ```

### MCP 服务器问题

**问题：TAPD MCP 服务器连接失败**

确保：
1. `uv` 工具已安装：`uvx --version`
2. `TAPD_ACCESS_TOKEN` 环境变量已设置
3. Token 有效且具有所需权限

**问题：GitLab MCP 服务器不可用**

GitLab MCP 服务器已归档，工作流已改用 git clone 方式：
```bash
# 手动执行 git clone
cd $TMPDIR/rf-testing
rmrf <project_name>
git clone --depth 1 \
  "https://oauth2:${GITLAB_PERSONAL_ACCESS_TOKEN}@gitlab.jlpay.com/<project_path>.git"
```

### JLTestLibrary 问题

**问题：导入 JLTestLibrary 失败**

确保 JLTestLibrary 已安装到 Python 环境的 site-packages：
```bash
# 检查 site-packages 路径
python -c "import site; print(site.getsitepackages()[0])"

# 手动安装
unzip 03-scripts/JLTestLibrary.zip -d <site-packages路径>
```

**问题：执行脚本时找不到 JLTestLibrary**

脚本会自动设置 PYTHONPATH 到 site-packages 目录。如果仍有问题：
```bash
# 手动设置 PYTHONPATH
export PYTHONPATH=/path/to/site-packages:$PYTHONPATH
```

### 常见错误信息

**错误：`ImportError: cannot import name 'detect_python_environments'`**

已修复（v2.6.3），如果仍有此错误：
1. 确保使用最新版本的 `rf_runner.py` 和 `rf_env_builder.py`
2. 确认 `python_detector.py` 文件存在且包含 `detect_all_python_environments` 函数

**错误：`list2cmdline() got an unexpected keyword argument 'encoding'`**

已修复（v2.6.3），Python 3.7 的 subprocess.list2cmdline 不支持 encoding 参数。如果仍有此错误，请更新脚本。

**错误：`'str' object has no attribute 'decode'`**

已修复（v2.6.3），添加了 isinstance 检查。如果仍有此错误，请更新脚本。

## 参考

- [AI-First 开发插件](https://gitlab.jlpay.com/pay-plus/base/ai-first)
- [Robot Framework 官方文档](https://robotframework.org/)
- [TAPD 平台](https://www.tapd.cn/)

## License

MIT