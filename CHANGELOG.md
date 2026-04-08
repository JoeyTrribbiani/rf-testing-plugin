# 更新日志

本文档记录 rf-testing-plugin 的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.0.0/)，
版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [2.6.3] - 2026-04-08

### 新增（Added）

- 添加 RF 测试用例执行命令 `/rf-testing:execute`
  - 支持完整执行、dryrun 验证
  - 支持指定用例、标签过滤等参数
  - 自动检测 Python 环境并创建临时环境脚本
  - 工作流中 script_execute 节点明确使用 `/rf-testing:execute` 命令

### 修复（Fixed）

- 优化 GitLab 代码分析模式的工作流设计

- 优化 GitLab 代码分析模式的工作流设计
  - 问题: YAPI 接口文档获取位置不合理，导致请求的接口详情不正确
  - 原因: YAPI 获取在测试设计之后，无法基于改动点精准获取接口信息
  - 修复:
    - 将 YAPI 接口文档获取移动到改动点识别之后、测试设计之前
    - 从改动点清单中提取涉及的接口名称
    - 基于接口名称从 YAPI 获取详细信息（请求参数、响应格式、示例）
  - 新的流程顺序:
    ```
    代码获取 → 代码分析(9步骤) → 改动点识别 → YAPI接口文档 → 测试设计 → 测试点 → 用例生成
    ```
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

- 参考 Cursor 执行方式重写 Robot Framework 执行逻辑
  - 问题: 执行 RF 脚本时不稳定，环境变量设置不正确
  - 原因: 直接执行 robot 命令时，Python 环境和 site-packages 路径未正确设置
  - 修复:
    - 新增 `rf_env_builder.py` - 临时环境构建器
    - 更新 `rf_runner.py` - 支持使用环境脚本执行
    - 更新 `rf_executor.py` - 集成环境脚本功能
    - 临时环境脚本路径: `%TEMP%/rf-ls-run/` 或 `$TMPDIR/rf-ls-run/`
  - 执行方式:
    ```bash
    # Windows
    cmd /c "cd work_dir && call env_script && python -m robot ..."

    # Unix/Linux/macOS
    sh -c "cd work_dir && source env_script && python -m robot ..."
    ```
  - 环境脚本功能:
    - 设置正确的 PATH（Python 可执行文件目录）
    - 设置 PYTHON 变量
    - 设置 PYTHONPATH（site-packages 目录）
    - 支持额外的环境变量
  - 新增命令行参数:
    - `--dryrun`: dryrun 模式验证语法
    - `--no-env-script`: 不使用环境脚本（直接执行）
    - `--include`: 包含标签
    - `--exclude`: 排除标签
  - 涉及文件:
    - `03-scripts/rf_env_builder.py` (新增)
    - `03-scripts/rf_runner.py` (重写)
    - `03-scripts/rf_executor.py` (更新)

- 修复 GitLab 代码获取方式
  - 问题: GitLab MCP 服务器已归档，原工作流仍要求使用 MCP 服务器
  - 原因: `mcp_gitlab` 节点未明确指定使用 git clone 备用方案
  - 修复:
    - 更新 `full-test-pipeline.md`，添加详细的 git clone 执行方法
    - 使用 oauth2 认证方式获取代码
    - 必须从环境变量 `GITLAB_PERSONAL_ACCESS_TOKEN` 获取 token
    - 先清理旧代码再 clone（避免冲突）
    - 提供 Unix 和 Windows 双平台命令示例
  - Git clone 命令格式:
    ```bash
    cd "$TMPDIR/rf-testing"
    rm -rf <project_name>
    git clone --depth 1 \
      "https://oauth2:${GITLAB_PERSONAL_ACCESS_TOKEN}@gitlab.jlpay.com/<project_path>.git"
    ```
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`
    - `05-plugins/rf-testing/commands/gitlab.md`
    - `05-plugins/rf-testing/commands/github.md`

- 修复输入源自动检测逻辑
  - 问题: 当用户提供 GitLab URL 时，工作流仍要求输入 TAPD 需求链接
  - 原因: `mcp_fetch` 节点的元数据阻止了自动检测，导致 AI 先检查 MCP 服务器而不是检测输入类型
  - 修复:
    - 更新 `start.md`，添加明确的输入源检测代码示例
    - 更新 `full-test-pipeline.md`，在输入选择部分添加 AI 自动检测逻辑
    - 强调 AI 必须首先执行检测，根据检测结果直接进入对应分支
  - 检测逻辑:
    - TAPD: 包含 `tapd.cn` 或 `www.tapd` → 提取 workspace_id 和 story_id
    - GitLab: 包含 `gitlab` → 提取项目路径和 git baseUrl
    - GitHub: 包含 `github.com` → 提取项目路径
  - 涉及文件:
    - `05-plugins/rf-testing/commands/start.md`
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

- 新增安装脚本缓存清理功能
  - 问题: 插件更新后缓存未清理，导致 Claude Code 读取到旧版本内容
  - 修复: 在 `install.bat` 和 `install.sh` 中新增 Step 1.5 清理缓存
  - 缓存目录:
    - Windows: `%USERPROFILE%\.claude\plugins\cache\rf-testing-plugin`
    - Unix/Linux/macOS: `$HOME/.claude/plugins/cache/rf-testing-plugin`
  - 涉及文件:
    - `install.bat`
    - `install.sh`

- 增强工作流执行约束与进度反馈
  - 问题: AI 没有严格按照工作流定义执行步骤，缺少进度反馈
  - 原因: 工作流文档中的指令约束不够强制，缺少明确的执行检查点
  - 修复:
    - 在 `full-test-pipeline.md` 添加"⚠️ 重要：工作流执行约束"部分
    - 明确5条执行规则：阶段顺序、状态输出、错误停止、工具使用、结果验证
    - 所有节点添加执行步骤，使用 ✅ 状态指示
    - 输出格式：`阶段开始` → `执行动作` → `阶段完成`
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

- 转换 Agent 节点为 Skill 节点
  - 问题: 部分节点使用 Agent 调用，可能导致技能未被正确使用
  - 原因: Agent 和 Skill 的职责边界不够清晰
  - 修复:
    - 将 `agent_rf_qa` 改为 `skill_rf_qa`，使用 Skill 工具调用 rf-standards-check
    - 将 `agent_results` 改为 `skill_results`，使用 Skill 工具调用 test-results-analyzer
    - 更新 mermaid 流程图中的节点名称
    - 统一使用 Skill 工具调用所有技能节点
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

- 添加参考用例分析节点
  - 问题: 生成测试用例前缺少参考用例分析，导致可能重复造轮子
  - 原因: 工作流中没有收集现有用例风格的步骤
  - 修复:
    - 在测试点识别之前添加 `skill_reference` 节点
    - 询问用户是否有现有用例目录
    - 分析可复用关键字和变量
    - 学习命名风格和结构规范
    - 输出可复用关键字清单、可复用变量清单、风格学习报告
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`
    - `01-RF-Skills/skills/test/SKILL.md`

- 添加插件体验评估节点
  - 问题: 工作流完成后缺少插件使用评估，无法持续改进
  - 原因: 没有收集用户对插件使用体验的反馈机制
  - 修复:
    - 在 TAPD 转换完成后添加 `plugin_feedback` 节点
    - 评估本次使用体验
    - 总结遇到的问题和解决方案
    - 提出对插件的改进建议
    - 评估工作流执行情况（是否按定义执行）
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

## [2.6.1] - 2026-04-07

### 修复（Fixed）

- 修复 RF 用例模板多余空格问题
  - 问题: 生成用例时模板中有多余的空格，导致同一个用例有很多空格
  - 修复: 更新 JL-Template-RF-TestCase.md 和 JL-Template-RF-Keyword.md，移除多余空格和注释
  - 规范: Documentation 三段式使用紧凑格式（标记后无空格）
  - 规范: 关键字步骤使用紧凑格式（移除 # 步骤N 注释）
  - 涉及文件:
    - `00-JL-Skills/jl-skills/templates/JL-Template-RF-TestCase.md`
    - `00-JL-Skills/jl-skills/templates/JL-Template-RF-Keyword.md`

- 修复执行脚本使用保存的Python路径
  - 问题: 执行用例时未优先使用安装脚本中保存的Python安装目录
  - 修复: 验证 rf_runner.py 已正确集成 rf_config.py 的 get_python_path()
  - 改进: install.sh 保存完整的Python环境信息（python_path, version, pip_path, environment_type）
  - 涉及文件:
    - `03-scripts/rf_config.py`（已验证使用 get_python_path()）
    - `03-scripts/rf_runner.py`（已验证使用 detect_python_for_execution()）
    - `install.sh`（新增完整Python信息保存）

- 修复 Settings.robot Suite Setup/Teardown 位置问题
  - 问题: Settings.robot 中的 Suite Setup 和 Suite Teardown 出现在 resource 文件中
  - 修复: 明确 Suite Setup/Teardown 只能出现在测试套件文件中，不能在 Resource 引用的文件中
  - 新增: 自动修复逻辑，将 Keywords.robot 和 Variables.robot 中的 Suite Setup/Teardown 移动到 Settings.robot
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/requirement-to-rf.md`
    - `02-agents/testing-rf-quality-assurance.md`

- 修复 Keywords.robot [Return] 多次出现错误
  - 问题: [Return] 在关键字中多次出现导致错误
  - 修复: 明确 [Return] 使用规范，只能在关键字末尾使用一次
  - 新增: 模板中的 [Return] 使用说明和错误示例
  - 涉及文件:
    - `00-JL-Skills/jl-skills/templates/JL-Template-RF-Keyword.md`
    - `02-agents/testing-rf-quality-assurance.md`

- 修复关键字重复定义问题
  - 问题: 相同名称的关键字被多次定义
  - 修复: 新增关键字重复定义检查逻辑
  - 新增: 检测策略和自动修复策略
  - 涉及文件:
    - `02-agents/testing-rf-quality-assurance.md`
    - `00-JL-Skills/jl-skills/templates/JL-Template-RF-Keyword.md`

- 新增: 在生成测试用例前询问参考用例目录
  - 目的: 学习现有用例风格，复用已有关键字和变量，避免重复造轮子
  - 询问内容: 是否有现有用例目录？希望完全复用现有风格还是仅作参考？
  - 分析输出: 可复用关键字清单、可复用变量清单、风格学习报告、复用建议报告
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/requirement-to-rf.md`
    - `01-RF-Skills/skills/test/SKILL.md`

- 改进: RF 测试结果分析能力
  - 问题: 实际断言失败、执行失败时，没有去排查问题，而是直接说测试环境问题
  - 修复: 更新 testing-results-analyzer Agent，增强错误诊断能力
  - 新增: 错误分类（测试用例问题、环境问题、数据问题、接口问题）
  - 新增: 根因分析和具体修复建议
  - 新增: 标记需要人工介入的问题
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/rf-to-tapd.md`

### 文档（Documentation）

- 更新 RF 关键字模板，添加 [Return] 使用规范和禁止事项
- 更新 RF 用例模板，使用紧凑格式
- 更新工作流文档，增加参考用例分析节点
- 更新 QA Agent 文档，增加关键字重复定义检查

---

## [2.6.0] - 2026-04-07

### 修复（Fixed）

- 修复 RF 用例目录结构问题
  - 问题: 当前所有内容放在一个.robot文件，未按标准4文件结构生成
  - 修复: 更新 SKILL.md 和 Agent，强制要求生成标准目录结构
  - 标准结构: Settings.robot、Keywords.robot、Variables.robot、测试用例.robot
  - 涉及文件:
    - `01-RF-Skills/skills/test/SKILL.md`
    - `02-agents/testing-rf-quality-assurance.md`
    - `05-plugins/rf-testing/workflows/requirement-to-rf.md`

- 修复用例执行与TAPD转化顺序问题
  - 问题: 用例未执行完就开始转TAPD，未确保用例有价值
  - 修复: 在工作流中添加质量门禁节点，评分>=70分才能进入TAPD转化
  - 新增: script_validate 节点（dryrun验证）
  - 新增: decision_quality 质量门禁判断
  - 涉及文件: `05-plugins/rf-testing/workflows/full-test-pipeline.md`

- 修复 RF 规范检查未正确应用问题
  - 问题: agent没有正确判断规范问题，后续robotframework-rules才检测到
  - 修复: 将 robotframework-rules 技能完整合并到 testing-rf-quality-assurance Agent
  - 新增: 自动修复能力（目录结构、命名规范、Documentation格式等）
  - 涉及文件:
    - `02-agents/testing-rf-quality-assurance.md`（重写）
    - `01-RF-Skills/skills/rf-standards-check/SKILL.md`

- 修复工作流遇到问题时停止等待用户操作的问题
  - 问题: 遇到RF用例问题或执行问题时停下来让用户操作
  - 修复: Agent 优先自动修复问题，不询问用户
  - 自动修复范围: 命名规范、文档格式、目录结构、标签补充等
  - 仅当业务逻辑不明确或架构性问题时才停止报告
  - 涉及文件:
    - `02-agents/testing-rf-quality-assurance.md`
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`
    - `05-plugins/rf-testing/workflows/requirement-to-rf.md`

## [2.5.1] - 2026-04-07

### 修复（Fixed）

- 修复 `install.bat` 未复制插件文件到 Claude 目录的问题
  - 问题: 运行安装脚本后，插件文件未同步到 `%USERPROFILE%\.claude\plugins\rf-testing-plugin`
  - 原因: 文件复制逻辑位于 `:configure_mcp` 标签处，如果在 `:install_jl` 阶段中断，`:configure_mcp` 不会被执行
  - 修复: 将文件复制逻辑移到脚本最开始（Step 1），确保无论后续步骤是否成功，文件都会先被复制
  - 改进: 使用 PowerShell 复制文件，排除 `.claude` 和 `.git` 目录
  - 新增: 添加清理动作，复制前检查目标目录是否存在，询问用户是否删除后重新复制
  - 涉及文件: `install.bat`
- 修复 `install.bat` 中 `python_detector.py` 调用时的编码报错
  - 问题: 脚本调用 `python_detector.py` 时，输出到控制台出现 `UnicodeDecodeError`
  - 修复: 将 stderr 重定向到 nul，避免编码错误显示
  - 涉及文件: `install.bat`
- 修复 `python_detector.py` 编码问题导致的执行报错
  - 问题: Windows 环境下 `subprocess.run` 使用 `text=True` 可能因编码问题导致报错
  - 修复: 移除 `text=True` 参数，手动解码输出并忽略编码错误
  - 涉及函数: `get_python_version()`, `detect_conda_envs()`, `get_site_packages_paths()`
  - 涉及文件: `03-scripts/python_detector.py`
- 修复 Claude 插件目录文件版本不一致问题
  - 问题: `%USERPROFILE%\.claude\plugins\rf-testing-plugin` 中的文件是旧版本（4月7日 10:19），与工作目录（4月7日 13:04）不一致
  - 原因: Claude 插件目录中的 `install.bat` 是旧版本（会从 GitHub 克隆），工作目录中的 `install.bat` 是新版本（使用本地文件）
  - 修复: 手动同步工作目录的所有文件到 Claude 插件目录
  - 涉及文件: 全部文件

## [2.5.0] - 2026-04-03

### 修复（Fixed）

- 修复 skill 名称引用问题
  - 问题: `Skill(rf-tapd-conversion)` 报错 "Unknown skill"
  - 原因: `tapd-conversion` skill 位于 `01-RF-Skills/skills/`，系统无法自动发现
  - 修复: 将 `tapd-conversion` skill 复制到 `00-JL-Skills/skills/` 目录
  - 涉及文件: `00-JL-Skills/skills/tapd-conversion/SKILL.md` (新增)
- 修复 Agent 在工作流中未使用的问题
  - 问题: `testing-code-analyzer` 和 `testing-change-detector` Agent 在工作流中未被调用
  - 修复: 更新 `full-test-pipeline.md` 和 `code-based-test-pipeline.md`
    - `code_analysis` 节点: 明确指定使用 `testing-code-analyzer` Agent
    - `change_detect` 节点: 明确指定使用 `testing-change-detector` Agent
  - 涉及文件:
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`
    - `05-plugins/rf-testing/workflows/code-based-test-pipeline.md`
- 修复 RF 测试用例命名规范合规性问题
  - 新增用例命名规范（强制）：必须使用下划线 `_` 分隔，禁止使用空格
  - 新增命名转换规则：自动将描述中的空格替换为下划线
  - 在 `01-RF-Skills/skills/test/SKILL.md` 添加完整命名规范说明（第32-66行）
- 修复 RF 标准目录结构合规性问题
  - 新增目录结构规范（强制）：必须生成 4 个核心文件
    - `Settings.robot` - 套件设置和初始化
    - `Keywords.robot` - 用户关键字定义
    - `Variables.robot` - 变量定义
    - `<需求名称>_测试用例.robot` - 测试用例
  - 在 `01-RF-Skills/skills/test/SKILL.md` 添加完整目录结构模板（第68-166行）
- 修复参考用例复用机制缺失问题
  - 新增参考用例复用规范（强制）：优先复用、引用复用、谨慎修改、禁止重复
  - 新增 `skill_reference_analysis` 节点到 `requirement-to-rf.md` 工作流
  - 在 `01-RF-Skills/skills/test/SKILL.md` 添加复用分析步骤和决策矩阵（第169-235行）
- 修复 RF 执行输出文件不一致问题
  - 修复 `03-scripts/rf_runner.py`：添加明确的输出文件参数
    - `--output output.xml`
    - `--log log.html`
    - `--report report.html`
  - 分析确认：7207 个 NOT_RUN 状态是 Robot Framework 条件执行的正常行为
  - 分析确认：报告无法查看是浏览器安全限制，非文件生成问题
- 修复 Documentation 格式问题
  - 问题: 测试文件中的 `[Documentation]` 格式不正确，导致 TAPD 转换失败
  - 规范要求: 必须包含 `【预置条件】... 【操作步骤】... 【预期结果】...` 三段式
  - 修复: 在 `tapd-conversion` skill 中添加 Documentation 格式检查和修复指引
  - 涉及文件: `00-JL-Skills/skills/tapd-conversion/SKILL.md`
- 修复 TAPD 转化流程指引问题
  - 问题: 完成测试用例执行后，转化 TAPD 没有正确指引，转化用例脚本未正确使用
  - 修复: 更新 skill 和工作流，添加详细的脚本调用示例、参数说明、常见问题处理
  - 涉及文件:
    - `00-JL-Skills/skills/tapd-conversion/SKILL.md`
    - `05-plugins/rf-testing/workflows/rf-to-tapd.md`
    - `05-plugins/rf-testing/workflows/full-test-pipeline.md`

### 文档（Documentation）

- 新增 RF 标准合规性修复报告 `docs/rf-standards-fix-report.md`
  - 记录 4 个问题的分析和修复方案
  - 提供修复前后对比和验证方法
- 新增 RF 执行输出分析文档 `docs/rf-execution-output-analysis.md`
  - 分析 NOT_RUN 状态的根本原因
  - 解释报告查看问题的解决方案（使用本地 HTTP 服务器）

---

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

[2.5.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.4.0...v2.5.0
[2.4.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.3.0...v2.4.0
[2.3.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.2.0...v2.3.0
[2.2.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.1.0...v2.2.0
[2.1.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/JoeyTrribbiani/rf-testing-plugin/releases/tag/v1.0.0