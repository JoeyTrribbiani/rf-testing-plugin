# RF 测试用例模板

## 用例文件模板

```robotframework
*** Settings ***
Documentation    测试用例模板 - 遵循 JL 编写规范
Library           Collections
Library           RequestsLibrary
Library           JSONLibrary
Resource          Keywords.robot

Force Tags        ${SUITE_PRIORITY}


*** Variables ***
${BASE_URL}       https://api.example.com
${MERCHANT_NO}    TEST001


*** Test Cases ***
用例名称示例
    [Documentation]    【预置条件】已存在状态为正常的商户【操作步骤】调用商户查询接口，获取商户基本信息【预期结果】成功返回商户详情，状态为正常
    [Tags]    P0    approved    REQ-001
    ${resp}    商户查询接口    ${MERCHANT_NO}
    Resp Dict Compare    ${resp}
    ${merchant_id}    Resp Dict Value    $.data.merchant_id
    Should Not Be Empty    ${merchant_id}
    Log    商户ID: ${merchant_id}


异常场景示例 - 参数缺失
    [Documentation]    【预置条件】无【操作步骤】调用商户查询接口，不传入商户号参数【预期结果】返回参数校验错误，ret_code 不为 0
    [Tags]    P1    approved
    ${resp}    商户查询接口    ${EMPTY}
    Should Be Equal    ${resp}[ret_code]    40001
    Should Contain    ${resp}[ret_msg]    商户号不能为空


边界值示例 - 最大长度
    [Documentation]    【预置条件】无【操作步骤】创建商户，商户号为最大长度字符串【预期结果】创建失败，返回长度校验错误
    [Tags]    P2    approved    REQ-002
    ${max_merchant_no}    Set Variable If    ${MAX_LENGTH}    ${MAX_MERCHANT_NO}
    ${resp}    创建商户接口    ${max_merchant_no}
    Should Be Equal    ${resp}[ret_code]    40002


批量测试示例 - 使用 FOR 循环
    [Documentation]    【预置条件】存在多个不同状态的商户【操作步骤】批量查询不同状态的商户【预期结果】所有商户查询成功
    [Tags]    P1    approved    REQ-003
    @{merchant_list}    Create List    TEST001    TEST002    TEST003
    FOR    ${merchant_no}    IN    @{merchant_list}
        Log    查询商户: ${merchant_no}
        ${resp}    商户查询接口    ${merchant_no}
        Resp Dict Compare    ${resp}
    END
```

## Documentation 三段式规范

```robotframework
[Documentation]    【预置条件】<执行前的条件>【操作步骤】<具体操作步骤>【预期结果】<预期结果>
```

### 示例

| 场景 | Documentation |
|------|---------------|
| 正常流程 | 【预置条件】已存在状态为正常的商户【操作步骤】调用商户查询接口，获取商户基本信息【预期结果】成功返回商户详情，状态为正常 |
| 异常流程 | 【预置条件】无【操作步骤】调用商户查询接口，不传入商户号参数【预期结果】返回参数校验错误 |
| 边界测试 | 【预置条件】无【操作步骤】创建商户，商户号为空字符串【预期结果】创建失败，返回参数必填错误 |

## Tags 标签规范

### 必需标签

```robotframework
[Tags]    <优先级>    <评审状态>    <需求ID（可选）>
```

### 标签值说明

| 类别 | 标签值 | 说明 |
|------|--------|------|
| 优先级 | P0 / P1 / P2 | 高 / 中 / 低 |
| 评审状态 | approved / wip / deprecated | 已通过 / 编写中 / 已废弃 |
| 需求ID | REQ-XXX | 关联的需求 ID |

### 示例

```robotframework
# 核心功能用例
[Tags]    P0    approved    REQ-001

# 编写中的用例
[Tags]    P1    wip    REQ-002

# 已废弃用例
[Tags]    P2    deprecated
```

## 变量命名规范

### 全局变量

```robotframework
# 常量使用大写
${BASE_URL}
${API_TIMEOUT}
${MAX_LENGTH}

# 配置变量使用小写
${merchant_no}
${user_id}
${test_data}
```

### 局部变量

```robotframework
# 使用有意义的名称
${merchant_id}
${order_amount}
${response_time}
```

## 步骤编写规范

### 单行步骤

```robotframework
${resp}    商户查询接口    ${MERCHANT_NO}
```

### 多行步骤（使用续行符）

```robotframework
${resp}    Create Session
    ...    api_session
    ...    ${BASE_URL}
    ...    verify=True
```

### 复杂逻辑

```robotframework
# 使用 Run Keyword If 处理条件
Run Keyword If    '${status}' == 'active'
    ...    激活商户    ${merchant_id}
    ...    ELSE
    ...    暂停商户    ${merchant_id}

# 使用 FOR 循环处理列表
@{items}    Create List    item1    item2    item3
FOR    ${item}    IN    @{items}
    Log    处理: ${item}
END
```

## 注释规范

### 行内注释

```robotframework
${resp}    商户查询接口    ${MERCHANT_NO}    # 查询商户信息
```

### 块注释

```robotframework
# ==================== 准备测试数据 ====================
${test_merchant}    Set Variable    TEST001

# ==================== 执行测试用例 ====================
${resp}    商户查询接口    ${test_merchant}

# ==================== 验证测试结果 ====================
Resp Dict Compare    ${resp}
```

## Setup 和 Teardown

```robotframework
*** Test Cases ***
使用 Setup 和 Teardown 的用例
    [Documentation]    【预置条件】无 【操作步骤】执行测试，自动处理前后置操作 【预期结果】测试执行完成
    [Tags]    P1    approved
    [Setup]    初始化测试环境    ${TEST_DATA}
    [Teardown]    清理测试数据    ${TEST_DATA}

    # 测试步骤
    ${resp}    测试接口

    # 断言
    Should Be Equal    ${resp}[status]    success
```

## 错误处理

```robotframework
*** Test Cases ***
包含错误处理的用例
    [Documentation]    【预置条件】无 【操作步骤】执行可能失败的操作，捕获并处理异常 【预期结果】根据异常类型返回不同结果
    [Tags]    P1    approved

    ${result}    Run Keyword And Ignore Error    可能失败的操作
    ${status}    ${value}    Set Variable    ${result}

    Run Keyword If    '${status}' == 'PASS'
    ...    Log    操作成功: ${value}
    ...    ELSE
    ...    Log    操作失败: ${value}
    ...    Should Be Equal    ${value}    预期的错误信息
```