# Robot Framework 基础规范

**重要说明**：
- 在本项目中，"rf"、"RF" 均指代 **Robot Framework**，而非"射频"（Radio Frequency）
- "Robot Framework" 是一个通用的自动化测试框架，支持关键字驱动的测试用例编写

## 用例结构

```robotframework
*** Settings ***
Documentation     用例描述
Library           SomeLibrary
Suite Setup       Log    套件前置
Suite Teardown    Log    套件清理
Force Tags        tag1    tag2

*** Variables ***
${VAR_NAME}       value

*** Test Cases ***
用例名称
    [Setup]    Log    前置
    步骤1
    步骤2
    [Teardown]    Log    清理

*** Keywords ***
关键字名称
    [Arguments]    ${arg1}    ${arg2}
    步骤
    [Return]    ${result}
```

## 编写规范

1. **Documentation（文档）**：用例必须有，说明测试目的和覆盖范围
2. **Tags（标签）**：用 `@{tag}` 标记，用于分类和筛选
3. **Setup/Teardown**：前置准备和后置清理，使用 `[Setup]` 和 `[Teardown]`
4. **变量命名**：使用 `${SCALAR_NAME}`、`@{LIST_NAME}` 格式，体现业务含义

## BuiltIn 常用关键字

- `Log` - 记录日志
- `Log Many` - 记录多个变量
- `Set Variable` - 设置变量
- `Get Length` - 获取长度
- `Should Be Equal` - 断言相等
- `Run Keyword If` - 条件执行
- `Run Keyword And Ignore Error` - 容错执行
- `FOR ... END` - 循环

## 禁止

- 不要使用 `TRY/EXCEPT`（仅 RF 5+ 支持）
- 不要忽略变量类型（单元素数组可能返回字符串）
- 不要在循环中做复杂计算
