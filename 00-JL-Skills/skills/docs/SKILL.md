---
name: docs
description: 测试文档管理 - 测试工程师视角的文档管家，管理测试计划、测试用例、测试报告
type: skill
---

# 测试文档管理技能

## 技能概述

本技能提供测试工程师视角的文档管理能力，专注于测试相关文档的创建、更新和维护，包括测试计划、测试用例、测试报告等。

## 适用场景

- 创建和更新测试计划文档
- 管理测试用例文档
- 生成测试报告
- 维护测试相关架构决策记录

## 文档类型

### 1. 测试计划 (Test Plan)

**路径**: `docs/superpowers/plans/`

包含内容：
- 测试范围
- 测试策略
- 测试环境
- 测试进度
- 风险分析

### 2. 测试用例 (Test Cases)

**路径**: `docs/superpowers/specs/test-cases/`

包含内容：
- 功能测试用例
- 接口测试用例
- 性能测试用例
- 安全测试用例

### 3. 测试报告 (Test Report)

**路径**: `docs/superpowers/plans/reports/`

包含内容：
- 执行摘要
- 测试统计
- 缺陷分析
- 质量评估
- 改进建议

### 4. 架构决策记录 (ADR)

**路径**: `docs/superpowers/specs/adr/`

记录测试相关的架构决策：
- 测试框架选择
- 测试策略决策
- 工具选型决策

## 文档规范

### 文件命名
```
[日期]-[类型]-[描述].md

示例:
2026-04-03-plan-api-testing.md
2026-04-03-report-sprint-15.md
```

### 文档模板

使用 `templates/` 目录下的标准模板：
- `JL-Template-Scenario-Test-Case.md` - 测试用例模板
- `JL-Template-TAPD-Report.md` - 测试报告模板
- `JL-Template-ADR.md` - 架构决策记录模板

## 使用方式

### 创建测试计划
```
skill "docs" "创建 [模块名] 的测试计划"
```

### 创建测试报告
```
skill "docs" "生成 [日期范围] 的测试报告"
```

### 更新文档
```
skill "docs" "更新 [文档路径] 的 [内容类型]"
```

## 文档目录结构

```
docs/superpowers/
├── specs/                    # 设计文档
│   ├── test-cases/          # 测试用例
│   ├── adr/                 # 架构决策记录
│   └── conventions/         # 规范文档
├── plans/                    # 执行计划
│   ├── reports/             # 测试报告
│   └── schedules/           # 测试计划
└── archive/                  # 归档历史文档
```

## 关联文件

- `specs/DDD文档管家.md` - 文档管理规范
- `specs/COMMON_CONVENTIONS.md` - 通用约定
- `templates/JL-Template-*.md` - 文档模板

## 职责边界

- **不修改**: 业务代码、生产环境配置
- **专注**: 测试文档的创建和维护
- **协作**: 与测试团队共享文档更新
