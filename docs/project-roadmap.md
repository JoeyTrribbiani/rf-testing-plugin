---
name: rf-testing-plugin-roadmap
description: RF Testing Plugin 项目路线图 - 已实现、短期目标、长期目标
type: project
---

# RF Testing Plugin 项目路线图

**版本**: v2.6.3  
**更新时间**: 2026-04-09

---

## 已实现

### 核心功能（已完成）

1. **TAPD 需求拉取和测试场景识别**
   - TAPD MCP 服务器集成（使用官方 mcp-server-tapd）
   - 支持需求详情获取
   - 测试场景自动识别

2. **GitLab/GitHub 代码变更分析**
   - git clone + oauth2 认证方式（GitLab MCP 降级备用方案）
   - 代码分析 9 步骤（结构、流程、影响面）
   - 改动点识别 Agent
   - 职责分离：代码分析 → 改动点识别 → RF 用例生成

3. **YAPI 接口文档获取**
   - YAPI MCP 服务器集成
   - 基于改动点提取接口信息
   - 支持接口详情查询（请求参数、响应格式、示例）

4. **RF 用例生成**
   - 符合 JL 企业标准和规范
   - 标准 4 文件目录结构（Settings/Keywords/Variables/测试用例）
   - 参考用例分析和复用
   - 变量命名（蛇形）、关键字命名（驼峰）规范

5. **RF 质量保证 Agent**
   - robotframework-rules 技能整合
   - 自动修复能力（目录结构、命名规范、Documentation 格式、变量命名、标签补充）
   - 质量门禁机制（评分 >= 70 分通过）

6. **RF 用例执行**
   - rf_runner.py 命令行工具（支持 dryrun、标签过滤、变量传递）
   - rf_listener.py 事件监听器（实时输出测试进度）
   - rf_parser.py 结果解析器
   - rf_executor.py 执行器封装
   - rf_env_builder.py 临时环境构建器
   - Windows 执行优化（直接执行方式，避免环境脚本编码问题）

7. **RF 用例转 TAPD 格式**
   - robot2tapd.py 转换脚本
   - Excel 导出（符合 TAPD 导入规范）
   - Base64 编码输出
   - 优先级解析（直接使用 [Tags] 中的 P0/P1/高/中/低）

8. **完整测试工作流编排**
   - 双模式支持（TAPD 需求模式 + GitLab/GitHub 代码分析模式）
   - 输入源自动检测（AI 自动识别 TAPD/GitLab/GitHub）
   - 工作流执行约束（5 条规则）
   - 质量门禁机制（评分 >= 70 分）
   - 插件体验评估节点

### 工作流节点（已完成）

1. **MCP 节点**
   - mcp_fetch（TAPD 需求获取）
   - mcp_export（TAPD 导出）
   - mcp_gitlab（git clone 备用）

2. **Skill 节点**
   - skill_scenario（测试场景识别）
   - skill_points（测试点分析）
   - skill_generation（RF 用例生成）
   - skill_validation（RF 规范检查）
   - skill_conversion（RF 转 TAPD）
   - skill_rf_qa（RF 质量保证）
   - skill_results（结果分析）
   - skill_reference（参考用例分析）

3. **Agent 节点**
   - testing-code-analyzer（代码分析）
   - testing-change-detector（改动点识别）

4. **新增节点**
   - 参考用例分析节点
   - 插件体验评估节点

### 文档和脚本（已完成）

1. **Skills 创建完成**
   - analyze/SKILL.md（代码深度解析）
   - test/SKILL.md（场景测试生成）
   - review/SKILL.md（RF 用例审查）
   - docs/SKILL.md（测试文档管理）
   - rf-standards-check/SKILL.md（RF 规范检查）
   - tapd-conversion/SKILL.md（TAPD 转换）

2. **Instructions 和 Specs 复制完成**
   - 15 个 Instructions（analyze/test/review）
   - 8 个 Specs（规范文档）
   - 16 个 Templates（模板文件）

3. **安装和配置脚本**
   - python_detector.py（Python 环境智能检测）
   - jl_installer.py（JLTestLibrary 自动安装）
   - install.sh/install.bat（智能检测和自动安装）
   - 缓存清理功能

4. **命令和工作流**
   - /rf-testing:start（双模式启动）
   - /rf-testing:execute（RF 执行命令）
   - /rf-testing:gitlab（GitLab 代码分析）
   - /rf-testing:github（GitHub 代码分析）
   - /rf-testing:requirement-to-rf（需求转用例）
   - /rf-testing:rf-to-tapd（RF 转 TAPD）
   - full-test-pipeline.md（双模式工作流）
   - code-based-test-pipeline.md（代码分析工作流）
   - requirement-to-rf.md（需求到 RF 工作流）
   - rf-to-tapd.md（RF 到 TAPD 工作流）

5. **文档更新**
   - README.md 全面更新（命令详解、使用案例、故障排除）
   - INSTALL.md 安装指南
   - CHANGELOG.md 更新日志
   - MCP 配置（.mcp.json）

### 最近修复（2026-04-08 ~ 2026-04-09）

1. **RF 执行脚本修复**
   - rf_listener.py 添加 ROBOT_LISTENER_API_VERSION = 3
   - rf_runner.py Windows 执行优化
   - execute.md 命令执行说明更新

2. **TAPD 用例等级解析修复**
   - 直接使用 [Tags] 中的优先级标签值
   - 支持格式：P0、P1、高、中、低

3. **GitLab 代码获取方式修复**
   - GitLab MCP 服务器归档，改用 git clone + oauth2 认证

4. **输入源自动检测**
   - TAPD/GitLab/GitHub 自动识别

5. **工作流自动化增强**
   - 执行约束和质量门禁
   - Agent 节点转换为 Skill 节点

---

## 短期目标（预计 1-2 周）

### 功能完善

1. **完善 testing-results-analyzer Agent 的结果分析能力**
   - 增强错误分类逻辑（测试用例问题、环境问题、数据问题、接口问题）
   - 改进根因分析能力，提供具体修复建议
   - 标记需要人工介入的问题

2. **优化 YAPI 接口文档获取流程**
   - 基于改动点清单智能提取接口名称
   - 支持模糊搜索接口
   - 改进接口信息匹配精度

3. **增强错误处理和重试机制**
   - git clone 失败重试
   - MCP 服务器连接异常处理
   - 网络请求超时处理

4. **完善工作流的完整性验证**
   - 测试双模式工作流的实际使用
   - 验证所有节点的执行流程
   - 检查工作流约束的实际效果

### 文档和示例

5. **添加更多测试用例示例**
   - TAPD 需求模式完整示例
   - GitLab 代码分析模式完整示例
   - 各个命令的详细使用示例

6. **完善故障排除文档**
   - 添加常见错误场景和解决方案
   - 补充调试步骤

### 质量改进

7. **添加单元测试**
   - 测试核心脚本功能
   - 测试工作流节点逻辑

8. **性能优化**
   - 代码分析性能优化
   - 大量用例转换性能优化

---

## 长期目标（预计 1-3 个月）

### 智能化增强

1. **代码分析智能化**
   - 使用 NLP 技术深入理解代码结构
   - 自动识别复杂的业务逻辑
   - 智能推荐测试范围和优先级

2. **测试用例自动优化**
   - 基于历史执行数据优化用例
   - 自动检测和修复冗余用例
   - 智能推荐测试数据

3. **AI 辅助测试设计**
   - 基于需求自动生成测试策略
   - 智能推荐测试覆盖率指标
   - 自动分析测试盲区

### 用户体验

4. **收集和分析用户反馈**
   - 插件体验评估机制完善
   - 基于反馈持续优化工作流
   - 用户满意度追踪和改进

5. **可视化增强**
   - 添加进度可视化
   - 测试结果图形化展示
   - 代码分析报告可视化

### 系统稳定性

6. **建立自动化测试和监控体系**
   - 完整的端到端测试
   - 持续集成/持续部署（CI/CD）
   - 性能监控和告警

7. **跨平台兼容性完善**
   - Windows/Linux/macOS 全面测试
   - Docker 容器化支持
   - 各平台安装脚本完善

### 扩展性

8. **支持更多平台和工具**
   - 支持 Jira 需求管理
   - 支持 Swagger/OpenAPI 接口文档
   - 支持 JUnit/TestNG 其他测试框架

9. **插件生态系统**
   - 支持自定义 Skill 扩展
   - 支持自定义 Agent 扩展
   - 支持自定义工作流模板

10. **企业级功能**
    - 多租户支持
    - 权限管理
    - 审计日志
    - 数据安全和合规

11. **集成到现有 DevOps 平台**
    - 通过 Claude Code 本地可用源码集成到流水线
    - 实现测试自动化和持续优化更新
    - 支持 CI/CD 流水线集成
    - 自动测试生成和执行
    - 测试结果自动反馈和优化建议

### 技术债务处理

11. **GitLab MCP 服务器替代方案**
    - 寻找更稳定的代码托管集成方案
    - 评估其他 MCP 服务器可用性

12. **YAPI MCP 稳定性验证和优化**
    - 长期稳定性测试
    - 性能优化
    - 错误处理完善

---

## 技术债务

1. **GitLab MCP 服务器已归档**
   - 当前使用 git clone 备用方案
   - 需要寻找更稳定的替代方案

2. **YAPI MCP 稳定性**
   - 需要长期验证和优化
   - 考虑备用接口文档方案

3. **跨平台兼容性**
   - Windows/Linux/macOS 需要全面测试
   - 部分脚本可能需要平台适配

---

## 版本规划

### v2.7.0（短期）
- 完善 testing-results-analyzer
- 优化 YAPI 接口文档获取
- 增强错误处理

### v2.8.0（中期）
- 代码分析智能化
- 测试用例自动优化
- 用户反馈机制完善

### v3.0.0（长期）
- AI 辅助测试设计
- 可视化增强
- 企业级功能