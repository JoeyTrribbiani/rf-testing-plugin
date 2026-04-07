---
name: review
description: RF 用例审查 - 对生成的 Robot Framework 用例进行质量检查和规范审查
type: skill
---

# RF 用例审查技能

## 技能概述

本技能提供对 Robot Framework 测试用例的质量检查和规范审查能力，确保生成的用例符合企业标准和最佳实践。

## 适用场景

- 检查生成的 RF 用例是否符合规范
- 审查用例质量和可维护性
- 识别潜在的问题和改进点
- 执行代码合规性检查

## 审查维度

### 1. 命名规范检查

#### 变量命名
- 使用蛇形命名法: `${variable_name}`
- 避免使用单字符变量名
- 变量名应具有描述性

#### 关键字命名
- 使用驼峰命名法: `Keyword Name`
- 动词开头，描述清晰
- 避免过于笼统的命名

### 2. 文档格式检查

#### 三段式格式
- **概述**: 用例目的和业务背景
- **前置条件**: 执行前必须满足的条件
- **预期结果**: 明确的验证点和通过标准

#### Tag 使用规范
- 优先级标记: `P0`, `P1`, `P2`
- 评审状态: `待评审`, `已评审`, `已归档`
- 功能模块: 按业务模块分类

### 3. 技术规范检查

#### JSONPath 表达式
- 语法正确性
- 表达式简洁性
- 避免过度嵌套

#### 关键字使用
- 使用标准库关键字
- 自定义关键字有明确文档
- 避免重复造轮子

### 4. 质量指标检查

- 用例独立性（无依赖）
- 可重复执行
- 清晰的断言
- 适当的粒度

## 使用方式

### 全面审查
```
skill "rf-standards-check" "审查 [用例文件] 的规范性"
```

### 特定维度审查
```
skill "review" "检查 [用例文件] 的命名规范"
skill "review" "检查 [用例文件] 的文档格式"
skill "review" "检查 [用例文件] 的技术规范"
```

## 输出规范

审查报告应包含：
1. **审查摘要** - 通过/失败项统计
2. **问题列表** - 按严重程度分类
   - CRITICAL: 必须修复
   - HIGH: 建议修复
   - MEDIUM: 可以考虑
   - LOW: 可选优化
3. **改进建议** - 具体的修改建议
4. **修复示例** - 代码对比示例

## 关联指令

- `instructions/review/code-compliance-instructions.md`
- `instructions/review/quality-review-instructions.md`
- `instructions/review/security-review-instructions.md`
- `specs/Robot Framework 编写规范.md`
- `specs/RF 关键字编写规范.md`
