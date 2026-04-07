# 更新日志

本文档记录 rf-testing-plugin 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.4.0] - 2026-04-03

### 新增（Added）

- 新增工作流双模式支持
  - 支持 TAPD 需求模式启动
  - 支持 GitLab/GitHub 代码分析模式启动
  - 新增输入源选择节点（阶段0）
- 新增代码分析流程（9步骤）
  - 结构分析：技术栈 → 实体ER图 → 接口入口
  - 流程分析：调用链 → 时序 → 复杂逻辑
  - 影响面分析：依赖引用 → 数据影响 → 风险评估
- 新增 3 个测试 Agent
  - `testing-code-analyzer.md`: 代码分析 Agent
  - `testing-change-detector.md`: 改动点识别 Agent
  - `testing-results-analyzer.md`: 结果分析 Agent
- 新增 4 个 Skill 定义
  - `analyze/SKILL.md`: 代码深度解析技能
  - `test/SKILL.md`: 场景测试生成技能
  - `review/SKILL.md`: RF 用例审查技能
  - `docs/SKILL.md`: 测试文档管理技能
- 复制 ai-first-master 技能体系
  - 15 个 instructions（analyze/test/review）
  - 8 个 specs（COMMON_CONVENTIONS, DDD文档管家等）
  - 16 个 templates（RF 用例、关键字、报告等）

### 变更（Changed）

- 更新 `.mcp.json` MCP 服务器配置
  - TAPD: 改为使用 `uvx mcp-server-tapd` 方式
  - GitLab: 移除 Windows 特定的 `cmd /c`，改为标准 npx 调用
  - 新增 GitHub MCP 服务器配置
- 更新安装脚本（`install.sh` 和 `install.bat`）
  - 添加 GitHub Token 配置步骤（可选）
  - 更新 MCP JSON 生成逻辑，使用新的 MCP 配置格式
  - 添加 GitHub MCP 服务器动态配置
- 更新 `full-test-pipeline.md` 工作流
  - 新增阶段0：输入源选择（TAPD / GitLab / GitHub）
  - 新增 GitLab 分支：代码获取 → 代码分析 → 改动点识别
  - 两个分支在测试设计阶段汇合
- 更新 `start.md` 命令入口
  - 参数提示扩展：`[tapd-link|gitlab-project-path|github-repo-path]`
  - 新增输入源识别逻辑
  - 新增 GitLab/GitHub 环境检查要求
- 更新 `README.md`
  - 添加双模式启动说明
  - 更新目录结构（新增 Agents）
  - 添加 GitHub/YAPI 环境变量说明
- 更新 `INSTALL.md`
  - 添加 GitHub Token 配置说明
  - 添加 YAPI Token 配置说明
  - 更新 MCP 服务器列表

### 文档（Documentation）

- 新增工作流改造设计文档 `docs/superpowers/specs/2026-04-03-workflow-refactor-design.md`

---

## [2.3.0] - 2026-04-02

### 新增（Added）

- 新增 RF 执行模块 `03-scripts/rf_runner.py`：Robot Framework 执行脚本入口
  - 支持命令行参数构建 robot 命令
  - 集成 Python 环境自动检测（`python_detector.py`）
  - 支持测试用例过滤、标签过滤、变量传递等完整参数
  - 默认集成 `rf_listener.py` 监听器实时输出测试进度
- 新增 RF 事件监听器 `03-scripts/rf_listener.py`
  - 捕获测试套件和测试用例的执行事件
  - 实时输出测试进度（PASS/FAIL/SKIP 状态）
  - 彩色输出和执行时间统计
  - 提供测试汇总报告
- 新增 RF 结果解析器 `03-scripts/rf_parser.py`
  - 解析 Robot Framework 的 output.xml 文件
  - 提取统计信息（总数、通过、失败、跳过）
  - 解析测试用例详情（名称、状态、耗时、标签、错误消息）
  - 解析测试套件结构
- 新增 RF 执行器封装 `03-scripts/rf_executor.py`
  - 整合 runner、listener、parser 提供统一执行接口
  - 支持便捷函数 `execute_robot_test()`
  - 自动检测 Python 环境
- 新增 YAPI MCP 服务器集成，支持接口文档查询和管理
- 更新 `full-test-pipeline.md` 工作流
  - 新增阶段 2.5：从 YAPI 获取接口文档
  - 新增阶段 5：执行 RF 测试用例并验证
  - 重新编号后续阶段（原阶段4→6，原阶段5→7）
- 更新 `.mcp.json` 配置，添加 `yapi-auto-mcp` 服务器
- 更新 `install.sh`，添加 YAPI 配置收集步骤（步骤 [3/5]）
- 更新 `install.bat`，添加 YAPI 配置收集和环境变量写入
- 更新 `requirements.txt`，添加 YAPI MCP 安装说明（通过 npx 运行）

### 修复（Fixed）

- 移除未使用的 `datetime` 导入（`rf_listener.py`, `rf_parser.py`）
- 移除未使用的 `start_time` 属性（`rf_listener.py`）
- 为所有可选参数添加正确的 `Optional` 类型注解（`rf_runner.py`）
- 修复 rf_parser.py 中 XML 数值属性转换的 ValueError 问题
  - 添加 try-except 块处理非数值数据
  - 使用安全的默认值（0 或 0.0）

### 变更（Changed）

- 修正 TAPD MCP 服务器配置，使用 `mcp-server-tapd` 直接命令，移除 env 配置
- 更新 `install.sh` MCP JSON 生成逻辑，支持可选服务器动态拼接
- 更新 `install.bat` MCP JSON 生成逻辑，支持可选服务器动态拼接
- 更新配置验证输出，显示已配置和未配置的 MCP 服务器状态
- 更新环境变量说明，添加 YAPI_BASE_URL 和 YAPI_TOKEN

### 文档（Documentation）

- 新增 RF 执行能力设计文档 `docs/superpowers/specs/2026-04-02-rf-execution-capability-design.md`
  - 定义 RF 执行模块：rf_runner.py、rf_listener.py、rf_parser.py、rf_executor.py
  - 添加 YAPI MCP 集成章节（第 10 节）
  - 添加安装依赖更新章节（第 11 节）

---

## [2.2.0] - 2026-04-02

### 变更（Changed）

- 更新 `.mcp.json` 配置，使用官方 `mcp-server-tapd` 包（通过 uvx 运行）
- 删除自定义 TAPD MCP 服务器实现
- 更新 `requirements.txt`，添加 uv 安装说明

### 删除（Removed）

- 删除 `03-scripts/tapd-mcp-server.py` 自定义 MCP 服务器

### TAPD MCP 功能

官方 `mcp-server-tapd` 支持的功能：
- **项目**：查询项目信息和配置
- **需求**：查询需求列表、创建新需求、更新需求字段、查询需求字段配置
- **缺陷**：查询缺陷列表、创建新缺陷、更新缺陷字段、查询缺陷字段配置
- **迭代**：查询迭代列表
- **评论**：业务对象添加评论

### 安装要求

- TAPD MCP 服务器需要 `uvx`（通过 uv 安装）
  ```bash
  # macOS
  brew install uv

  # Linux
  curl -LsSf https://astral.sh/uv/install.sh | sh

  # Windows
  powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
  ```

---

## [2.1.0] - 2026-04-02

### 新增（Added）

- 新增 Python 环境智能检测模块 `03-scripts/python_detector.py`
  - 支持检测 conda 环境、系统 Python、venv 虚拟环境
  - 优先级选择策略（激活 conda > 3.7.x conda > 3.8.x system > 其他）
  - site-packages 目录自动检测
  - JSON 和文本输出格式
- 新增 JLTestLibrary 智能安装模块 `03-scripts/jl_installer.py`
  - 自动检测 site-packages 目录
  - 已安装状态检查
  - 安装验证
- 新增 Python 智能检测章节到 `INSTALL.md`
- 新增 Python 环境智能检测说明到 `README.md`

### 变更（Changed）

- 更新 `install.sh`，集成 Python 智能检测和 JLTestLibrary 自动安装
  - 替换 `check_python_version()` 为 `check_python_environment()`
  - 更新 `install_python_deps()` 使用检测到的 Python
  - 更新 `install_jltestlibrary()` 自动检测 site-packages
  - 更新 `verify_installation()` 使用检测到的 Python
- 更新 `install.bat`，集成 Python 智能检测和 JLTestLibrary 自动安装
  - 新增 `DetectPythonEnvironment` 函数
  - 新增 `InstallDependencies` 函数
  - 新增 `InstallJLTestLibrary` 函数
  - 所有依赖安装使用检测到的 Python 和 pip
- 更新 `INSTALL.md` 安装脚本功能列表
- 更新 `README.md` 安装依赖章节，突出安装脚本功能

### 修复（Fixed）

- python_detector.py 修复 subprocess 返回码检查
- python_detector.py 修复 None 处理问题
- jl_installer.py 移除未使用的导入（shutil、Optional）

### 文档（Documentation）

- 新增智能安装设计文档 `docs/superpowers/specs/2026-04-02-intelligent-install-design.md`
- 新增智能安装实施计划 `docs/superpowers/plans/2026-04-02-intelligent-install-plan.md`

---

## [2.0.0] - 2026-04-02

### 重大变更（Breaking Changes）

- 目录结构调整：删除 `02-workflows/`，新增 `05-plugins/rf-testing/` 和 `02-agents/`
- 命令入口变更：统一使用 `/rf-testing:start` 替代旧命令
- JLTestLibrary.zip 位置变更：从根目录移至 `03-scripts/`

### 新增（Added）

- 新增独立插件目录 `05-plugins/rf-testing/`，符合 AI-First 插件标准
- 新增 MCP 配置 `.mcp.json`，支持 TAPD 和 GitLab MCP 服务器
- 新增入口命令 `commands/start.md`，提供 `/rf-testing:start` 命令
- 新增 RF 质量保证 Agent `02-agents/testing-rf-quality-assurance.md`
- 新增工作流 MCP 节点定义，对标参考项目结构
- 新增插件元数据 `.claude-plugin/plugin.json`
- 新增插件说明文档 `05-plugins/rf-testing/README.md`

### 变更（Changed）

- 更新 `full-test-pipeline.md` 工作流，集成 RF 质量保证和测试结果分析节点
- 更新 `requirement-to-rf.md` 工作流，集成 RF 质量保证节点
- 更新 `rf-to-tapd.md` 工作流，集成测试结果分析节点
- 更新 `.claude-plugin/marketplace.json`，插件源指向 `./05-plugins/rf-testing`
- 更新 `README.md`，反映新的目录结构和使用方式
- 更新 `INSTALL.md`，添加 marketplace 安装和环境变量配置说明
- 更新 `03-scripts/README.md`，新增 JLTestLibrary 安装说明
- 更新 `04-cases/README.md`，反映新的命令和工作流

### 删除（Removed）

- 删除 `02-workflows/` 目录（已迁移到 `05-plugins/rf-testing/workflows/`）
- 删除旧命令别名（统一使用 `/rf-testing:start`）
- 删除根目录的 `JLTestLibrary.zip`（已移至 `03-scripts/`）

### 修复（Fixed）

- 修正目录编号，避免重复（05-agents → 02-agents）
- 确保所有引用位置正确更新

### 文档（Documentation）

- 新增重构设计文档 `docs/superpowers/specs/2026-04-01-rf-testing-refactor-design.md`
- 新增 `03-scripts/README.md` 实用脚本文档

## [1.0.0] - 2025-12-24

### 新增（Added）

- 初始版本发布
- 支持 TAPD 需求转 RF 用例
- 支持 RF 用例转 TAPD 格式
- 支持 RF 编写规范检查
- 包含 JL 公共库和 RF 技能
- 提供实用脚本和资源

---

[2.4.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/releases/tag/v1.0.0