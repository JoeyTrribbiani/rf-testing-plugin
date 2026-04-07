---
name: rf-test
description: 场景测试生成 - 基于需求或代码分析生成 Robot Framework 测试用例
type: skill
---

# 场景测试生成技能

## 技能概述

本技能提供从需求或代码分析生成 Robot Framework 测试用例的能力，支持测试场景识别、测试点分析和 RF 用例生成。

## 适用场景

- 从 TAPD 需求识别测试场景
- 从代码分析结果生成测试点
- 生成符合规范的 Robot Framework 用例
- 结合 YAPI 接口文档生成接口测试用例

## 核心能力

### 1. 测试场景识别

从需求或代码变更中识别测试场景：
- 功能场景（正常流程、异常流程）
- 边界场景（边界值、极限条件）
- 性能场景（并发、负载、压力）
- 安全场景（权限、注入、越权）

### 2. 测试点分析

将测试场景细化为具体测试点：
- 输入参数组合
- 预期输出结果
- 前置条件
- 后置清理

### 3. RF 用例生成

生成符合规范的 Robot Framework 用例：
- 使用三段式格式（概述-前置条件-预期结果）
- 遵循变量和关键字命名规范
- 包含必要的 Tag 标记

## 使用方式

### 从需求生成
```
skill "rf-test" "根据需求内容识别测试场景"
skill "rf-test" "根据测试场景识别测试点"
skill "rf-test" "根据测试点生成 RF 测试用例"
```

### 从代码分析生成
```
skill "rf-test" "根据代码分析结果识别测试场景"
skill "rf-test" "根据改动点生成回归测试用例"
```

## 输出规范

### 测试场景格式
```
## 场景 [编号]: [场景名称]
- 场景描述: [描述]
- 测试类型: [功能/边界/性能/安全]
- 优先级: [P0/P1/P2]
```

### 测试点格式
```
### 测试点 [编号]: [测试点名称]
- 前置条件: [条件]
- 输入数据: [数据]
- 预期结果: [结果]
- 关联接口: [接口名]
```

### RF 用例格式
```robot
*** Test Cases ***
[用例名称]
    [Documentation]    [概述]
    [Tags]    [标签]
    [前置条件关键字]
    [操作步骤]
    [预期结果验证]
```

## 关联指令

- `instructions/test/scenario-identification-instructions.md`
- `instructions/test/scenario-overview-instructions.md`
- `instructions/test/script-generation-instructions.md`
- `templates/JL-Template-Scenario-Test-Case.md`
