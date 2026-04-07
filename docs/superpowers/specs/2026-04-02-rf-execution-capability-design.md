# RF 测试用例执行能力设计文档

> 创建时间：2026-04-02
> 设计者：Claude
> 版本：1.0

---

## 1. 概述

### 1.1 目标

为 rf-testing-plugin 添加以下能力：
- **RF 执行能力**：执行 Robot Framework 测试用例，支持开发调试和测试验证
- **YAPI 文档集成**：通过 YAPI MCP 访问接口文档，获取接口定义用于测试

### 1.2 约束

- RF 执行必须在 Python 3.7+ 环境执行
- 复用现有的 `python_detector.py` 进行环境检测
- 遵循交互协议：单步输出、看板进度、确认点规则
- 保留 RF 原生报告（log.html, report.html）
- YAPI MCP 通过 npx 运行，需要 Node.js 环境
- 参考 Cursor RDA 机制但简化实现

### 1.3 集成位置

在现有工作流中扩展阶段：

```
阶段1：从 TAPD 拉取需求内容
    ↓
阶段2：识别测试场景和测试点
    ↓
【新增】阶段2.5：从 YAPI 获取接口文档
    ↓
阶段3：生成 Robot Framework 用例
    ↓
阶段4：检查 RF 规范
    ↓
【新增】阶段5：执行测试用例并验证
    ↓
阶段6：测试结果分析
    ↓
阶段7：转换为 TAPD 格式
```

### 1.4 MCP 服务器集成

项目中集成两个 MCP 服务器：

| MCP 服务器 | 功能 | 运行方式 |
|-----------|------|----------|
| tapd | 需求管理、测试用例管理 | mcp-server-tapd |
| yapi-auto-mcp | 接口文档查询、接口管理 | npx yapi-auto-mcp |

---

## 2. 架构设计

### 2.1 组件结构

```
03-scripts/
├── python_detector.py      # [已存在] Python 环境检测
├── rf_runner.py             # [新增] RF 执行脚本入口
├── rf_listener.py           # [新增] 自定义 Robot listener
├── rf_parser.py             # [新增] 结果解析模块
└── rf_executor.py          # [新增] 执行器封装
```

### 2.2 数据流

```
Claude
  │
  ├─> 工作流触发执行
  │
  ├─> rf_runner.py
  │     ├─> python_detector.py (检测 Python 环境)
  │     ├─> robot --listener rf_listener.py
  │     └─> output.xml, log.html, report.html
  │
  ├─> rf_parser.py
  │     └─> 解析 output.xml → JSON 结果
  │
  └─> 结构化结果 (用例列表、状态、错误信息)
       +
  └─> 原始报告路径 (log.html, report.html)
```

---

## 3. 核心模块设计

### 3.1 rf_runner.py - 执行脚本入口

**职责**：
- 解析命令行参数
- 调用 python_detector 检测 Python 环境
- 构建并执行 robot 命令
- 返回执行结果和报告路径

**接口**：
```python
def run_robot_test(
    robot_file: str,
    python_path: str = None,
    test_name: str = None,
    suite_name: str = None,
    include_tags: List[str] = None,
    exclude_tags: List[str] = None,
    variables: Dict[str, str] = None,
    variable_file: str = None,
    output_dir: str = "./output",
    log_level: str = "INFO"
) -> Dict
```

**返回值**：
```python
{
    "success": bool,
    "exit_code": int,
    "output_dir": str,
    "log_file": str,
    "report_file": str,
    "output_file": str,
    "duration": float,
    "python_path": str
}
```

### 3.2 rf_listener.py - 自定义 Robot listener

**职责**：
- 捕获 Robot Framework 执行事件（start、end、pass、fail、skip）
- 实时输出执行进度
- 记录用例执行结果

**事件接口**：
```python
class RFListener:
    def start_suite(self, name, attrs): ...
    def end_suite(self, name, attrs): ...
    def start_test(self, name, attrs): ...
    def end_test(self, name, attrs): ...
    def start_keyword(self, name, attrs): ...
    def end_keyword(self, name, attrs): ...
    def log_message(self, message): ...
```

**参考来源**：
- `c:\Users\xujunkang\.cursor\extensions\robocorp.robotframework-lsp-1.13.0\src\robotframework_debug_adapter\events_listener.py`

### 3.3 rf_parser.py - 结果解析模块

**职责**：
- 解析 `output.xml` 文件
- 提取用例列表、状态、耗时、错误信息
- 返回结构化 JSON 结果

**接口**：
```python
def parse_robot_output(output_file: str) -> Dict
```

**返回值**：
```python
{
    "statistics": {
        "total": int,
        "passed": int,
        "failed": int,
        "skipped": int,
        "duration": float
    },
    "suites": List[Dict],
    "tests": List[Dict]
}
```

**测试结构**：
```python
{
    "name": "用例名称",
    "status": "PASS|FAIL|SKIP",
    "duration": float,
    "tags": List[str],
    "doc": str,
    "message": str,  # 失败原因
    "keywords": List[Dict]
}
```

### 3.4 rf_executor.py - 执行器封装

**职责**：
- 整合 runner、listener、parser
- 提供统一的执行接口
- 处理错误和异常

**接口**：
```python
def execute_robot_test(
    robot_file: str,
    options: Dict = None
) -> Dict
```

---

## 4. 工作流集成

### 4.1 新增阶段：执行测试用例并验证

**阶段节点**：
```markdown
### mcp_execute(MCP 自动选择) - AI 工具选择模式

**MCP 服务器**: 无（使用本地脚本）

**用户意图**:
```
执行生成的 RF 测试用例，验证用例可运行性。
使用 Python 3.7+ 环境，支持按粒度选择执行。
```

**执行方法**:
1. 调用 `03-scripts/rf_runner.py` 执行测试
2. 使用 `03-scripts/rf_parser.py` 解析结果
3. 输出结构化结果和原始报告路径
```

### 4.2 MCP 配置修正

**问题**：当前工作流使用 serverId 为 `tapd`，但 Claude 识别为 `plugin:rf-testing:tapd`

**修正**：
```json
{
  "mode": "aiToolSelection",
  "serverId": "plugin:rf-testing:tapd",
  "serverName": "tapd"
}
```

---

## 5. 交互协议集成

### 5.1 阶段输出格式

```markdown
## 阶段5：执行测试用例并验证

📊 **进度**: 5/7 执行测试用例并验证
[████████░░░░░░░░░] 71%

| ✅ 已完成 | 🔄 进行中 | ⏳ 待完成 |
|:----------|:----------|:----------|
| 从 TAPD 拉取需求 |  | 识别测试场景 | 生成 RF 用例 | 检查 RF 规范 | 执行测试用例并验证 | 测试结果分析 | TAPD 转换与导出 |

---

### 本步骤内容

执行 RF 测试用例：

**执行的测试文件**: `<robot_file_path>`

**Python 环境**: `<detected_python_path>`

**执行参数**:
| 参数 | 值 |
|------|-----|
| 用例选择 | `--test "<test_name>"` 或 `--suite "<suite_name>"` |
| 标签过滤 | `--include smoke --exclude slow` |
| 输出目录 | `--outputdir ./output` |

**执行进度**:
- [ ] 准备执行环境
- [ ] 启动 Robot Framework
- [ ] 运行测试用例
- [ ] 解析执行结果
- [ ] 生成结构化报告

---

### 本步骤输出

#### 执行结果

| 用例名称 | 状态 | 耗时 | 错误信息 |
|----------|------|------|----------|
| 正常流程-商户查询 | ✅ PASS | 1.2s | - |
| 异常流程-参数缺失 | ✅ PASS | 0.8s | - |
| 边界值-最大长度 | ❌ FAIL | 0.5s | Assertion Error: 长度校验失败 |

#### 统计信息

| 指标 | 值 |
|------|-----|
| 总用例数 | 3 |
| 通过数 | 2 |
| 失败数 | 1 |
| 跳过数 | 0 |
| 总耗时 | 2.5s |

#### 报告文件

- **HTML 日志**: `./output/log.html`
- **HTML 报告**: `./output/report.html`
- **XML 输出**: `./output/output.xml`

---

🛑 **确认点**

执行结果是否符合预期？失败的用例是否为预期失败？

请回复：
- **确认** → 进入下一步（测试结果分析）
- **重新执行** → 使用不同参数重新执行
- **查看详情** → 查看具体用例的详细日志
```

### 5.2 临时环境脚本

参考 Cursor 的 `run_env_xxx.bat`，创建临时的环境设置脚本：

```batch
@echo off

SET "PYTHONPATH=;D:\workspace\python\rf-testing-plugin\03-scripts"
<detected_python_path> %*
```

---

## 6. 命令行参数支持

### 6.1 rf_runner.py 支持的参数

```bash
python rf_runner.py <robot_file> [options]

选项:
  --python PATH         指定 Python 可执行文件路径
  --test NAME           执行指定测试用例（支持通配符）
  --suite NAME          执行指定测试套件
  --include TAG         按标签包含执行
  --exclude TAG         按标签排除执行
  --variable KEY:VAL    设置运行时变量
  --variablefile FILE   从文件加载变量
  --outputdir DIR       指定输出目录
  --loglevel LEVEL      日志级别（TRACE/DEBUG/INFO/WARN/NONE）
  --dryrun             仅检查语法，不执行
  --rerunfailed FILE    重跑失败用例
  --exitonfailure       遇到失败立即停止
```

### 6.2 使用示例

```bash
# 基础执行
python rf_runner.py test.robot

# 执行单个用例
python rf_runner.py --test "正常流程-商户查询" test.robot

# 按标签过滤
python rf_runner.py --include smoke --exclude slow test.robot

# 指定 Python 环境和输出目录
python rf_runner.py --python d:\env\python37\python.exe --outputdir ./results test.robot

# 设置变量
python rf_runner.py --variable env:dev --variablefile vars.yaml test.robot
```

---

## 7. 错误处理

### 7.1 环境检测失败

**场景**：未找到 Python 3.7+ 环境

**处理**：
1. 调用 `python_detector.py` 检测所有可用环境
2. 显示检测到的环境列表
3. 提示用户选择或手动指定路径
4. 如果仍然没有，提示用户先安装

### 7.2 用例文件不存在

**场景**：指定的 `.robot` 文件不存在

**处理**：
1. 检查文件路径是否正确
2. 提示可能的正确路径
3. 取消执行并返回错误信息

### 7.3 执行失败

**场景**：robot 命令执行失败（非用例失败）

**处理**：
1. 捕获 robot 命令的错误输出
2. 检查是否为语法错误
3. 提供修复建议
4. 如果是环境问题，提示检查依赖

### 7.4 结果解析失败

**场景**：`output.xml` 解析失败

**处理**：
1. 检查文件是否存在
2. 尝试使用 XML 库解析
3. 如果解析失败，提供原始文件路径
4. 提示手动查看

---

## 8. 测试与验证

### 8.1 单元测试

测试各个模块的核心功能：
- `python_detector` 的环境检测
- `rf_listener` 的事件捕获
- `rf_parser` 的 XML 解析

### 8.2 集成测试

测试完整的执行流程：
- 准备测试用例文件
- 调用 `rf_runner.py` 执行
- 验证输出文件生成
- 验证结果解析正确

### 8.3 验收标准

- [ ] 支持执行单个测试用例
- [ ] 支持执行整个测试套件
- [ ] 支持按标签过滤
- [ ] 支持设置运行时变量
- [ ] 正确解析执行结果
- [ ] 保留 RF 原生报告
- [ ] 自动检测 Python 3.7+ 环境
- [ ] 支持手动指定 Python 路径
- [ ] 错误处理完善

---

## 9. 后续扩展

### 9.1 调试能力增强

- 添加断点支持
- 实时查看变量值
- 单步执行关键字

### 9.2 并发执行

- 支持并行执行多个用例
- 缩短整体执行时间

### 9.3 报告增强

- 生成自定义格式的测试报告
- 集成到项目文档系统
- 支持趋势分析

---

## 10. YAPI MCP 集成

### 10.1 概述

YAPI-MCP 提供 YApi 接口文档的访问能力，让 Claude 能够：
- 查询接口文档（按名称、路径、标签搜索）
- 获取接口详情（请求参数、响应格式、示例）
- 管理接口定义（创建、更新接口）
- 列出项目和分类

### 10.2 配置方式

**MCP 配置文件**（`.mcp.json`）：
```json
{
  "mcpServers": {
    "yapi-auto-mcp": {
      "command": "npx",
      "args": ["-y", "yapi-auto-mcp", "--stdio"],
      "env": {
        "YAPI_BASE_URL": "${YAPI_BASE_URL}",
        "YAPI_TOKEN": "${YAPI_TOKEN}"
      }
    }
  }
}
```

### 10.3 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `YAPI_BASE_URL` | YAPI 服务器地址 | `https://yapi.example.com` |
| `YAPI_TOKEN` | 访问令牌（格式：`projectId:token`） | `123:abc456,456:def789` |

### 10.4 支持的 MCP 工具

| 工具 | 功能 |
|------|------|
| `search_interfaces` | 搜索接口（按名称、路径、标签） |
| `get_interface_detail` | 获取接口详情 |
| `list_projects` | 列出所有项目 |
| `list_categories` | 列出分类 |
| `create_interface` | 创建接口定义 |
| `update_interface` | 更新接口定义 |

### 10.5 工作流集成

**新增阶段 2.5：从 YAPI 获取接口文档**

```markdown
### yapi_fetch(MCP 自动选择) - AI 工具选择模式

**MCP 服务器**: yapi-auto-mcp

**用户意图**:
```
根据需求中的接口名称，从 YAPI 获取接口文档。
提取接口的请求参数、响应格式、示例数据等。
```

**执行方法**:
1. 调用 yapi MCP 的 `search_interfaces` 工具搜索接口
2. 调用 `get_interface_detail` 获取接口详情
3. 解析接口文档，提取关键信息
```
```

---

## 11. 安装依赖更新

### 11.1 新增依赖

#### YAPI MCP 服务器

**安装方式**：通过 npx 直接使用（无需本地安装）

**前提条件**：
- Node.js 环境（npm/npx）
- YAPI 服务器访问权限

**配置步骤**：
1. 设置环境变量 `YAPI_BASE_URL` 和 `YAPI_TOKEN`
2. MCP 配置已包含在 `.mcp.json` 中
3. 重启 Claude Code 后自动加载

#### Robot Framework 执行组件

**Python 依赖**（已包含在 requirements.txt 中）：
- robotframework>=3.2.2,<4.0.0
- pandas>=2.0.0
- openpyxl>=3.1.0

**新增 Python 依赖**：
```txt
# 结果解析
xmltodict>=0.13.0

# RDA listener 核心功能（简化版）
websocket-client>=1.0.0
```

### 11.2 安装脚本更新

#### install.sh 更新

添加 YAPI MCP 配置提示：
```bash
echo [INFO] 配置 YAPI MCP 服务器..."
echo [INFO] 请设置以下环境变量："
echo "   YAPI_BASE_URL  - YAPI 服务器地址"
echo "   YAPI_TOKEN      - 访问令牌（格式：projectId:token）"
```

#### install.bat 更新

添加 YAPI MCP 配置提示：
```bat
echo [INFO] Configuring YAPI MCP server...
echo [INFO] Please set the following environment variables:
echo   YAPI_BASE_URL - YAPI server URL
echo   YAPI_TOKEN      - Access token (format: projectId:token)
```

---

## 12. 参考资料

- Robot Framework 用户指南: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html
- Robot Framework 命令行参数: https://robotframework.org/robotframework/latest/RobotFrameworkUserGuide.html#command-line-options
- Cursor RDA 源码: `c:\Users\xujunkang\.cursor\extensions\robocorp.robotframework-lsp-1.13.0\src\robotframework_debug_adapter\`
- YAPI-MCP 仓库: https://github.com/lzsheng/Yapi-MCP
- 项目交互协议: `00-JL-Skills/jl-skills/instructions/INTERACTION_PROTOCOL.md`
- JL-Skills 模板: `00-JL-Skills/jl-skills/templates/`
- RF-Skills 测试技能: `01-RF-Skills/skills/test/SKILL.md`