# RF 用户关键字模板

## 关键字结构标准

```robotframework
*** Keywords ***
关键字名称
    [Documentation]    关键字功能描述
    ...    参数：
    ...    arg1 - 参数1说明
    ...    arg2 - 参数2说明
    ...    返回：
    ...    result - 返回值说明
    [Arguments]    ${arg1}    ${arg2}
    [Tags]    <tag1>    <tag2>
    ${result}    Some Operation    ${arg1}    ${arg2}
    [Return]    ${result}
```

## 三要素规范

### Documentation（文档）

必须包含以下内容：

1. **功能描述** - 关键字的主要功能
2. **参数说明** - 每个参数的含义和类型
3. **返回值说明** - 返回值的内容和类型

### Arguments（参数）

明确列出所有参数，支持以下写法：

```robotframework
# 固定参数
[Arguments]    ${arg1}    ${arg2}

# 可选参数（使用默认值）
[Arguments]    ${arg1}=default    ${arg2}=default

# 可变参数
[Arguments]    @{args}

# 混合参数
[Arguments]    ${required}    @{optional}
```

### Return（返回）

明确返回值，支持以下写法：

```robotframework
# 单个返回值（只能在关键字末尾使用一次）
[Return]    ${result}

# 多个返回值（只能在关键字末尾使用一次）
[Return]    ${value1}    ${value2}

# 返回字典（只能在关键字末尾使用一次）
${result}    Create Dictionary    key1=${value1}    key2=${value2}
[Return]    ${result}
```

**重要注意事项**：
- [Return] 只能在关键字末尾使用一次
- [Return] 不能出现在 [Arguments] 之后
- [Return] 不能出现在 [Tags] 之后
- 如果关键字不需要返回值，则不使用 [Return]

## 关键字分类

### 查询类关键字

```robotframework
*** Keywords ***
查询商户信息
    [Documentation]    查询商户基本信息，返回商户详情
    ...    参数：
    ...    merchant_no - 商户号
    ...    返回：
    ...    merchant_detail - 商户详情字典
    [Arguments]    ${merchant_no}
    [Tags]    query    merchant
    ${resp}    商户查询接口    ${merchant_no}
    Resp Dict Compare    ${resp}
    ${detail}    Resp Dict Value    $.data
    [Return]    ${detail}
```

### 变更类关键字

```robotframework
*** Keywords ***
变更商户状态
    [Documentation]    变更商户状态，支持正常/暂停/注销
    ...    参数：
    ...    merchant_no - 商户号
    ...    target_status - 目标状态（normal/paused/closed）
    ...    返回：
    ...    result - 变更结果
    [Arguments]    ${merchant_no}    ${target_status}
    [Tags]    update    merchant
    ${req_data}    Create Dictionary    merchant_no=${merchant_no}    status=${target_status}
    ${resp}    商户状态变更接口    ${req_data}
    Resp Dict Compare    ${resp}
    [Return]    ${resp}
```

### 数据准备类关键字

```robotframework
*** Keywords ***
创建测试商户
    [Documentation]    创建用于测试的商户数据
    ...    参数：
    ...    merchant_type - 商户类型
    ...    status - 商户状态
    ...    返回：
    ...    merchant_no - 生成的商户号
    [Arguments]    ${merchant_type}=normal    ${status}=active
    [Tags]    data    merchant
    ${merchant_no}    Generate Merchant No
    ${req_data}    Create Dictionary    merchant_no=${merchant_no}    type=${merchant_type}    status=${status}
    ${resp}    创建商户接口    ${req_data}
    Resp Dict Compare    ${resp}
    [Return]    ${merchant_no}
```

### 断言类关键字

```robotframework
*** Keywords ***
校验商户状态
    [Documentation]    校验商户状态是否符合预期
    ...    参数：
    ...    merchant_no - 商户号
    ...    expected_status - 预期状态
    [Arguments]    ${merchant_no}    ${expected_status}
    [Tags]    assertion
    ${resp}    查询商户信息    ${merchant_no}
    ${actual_status}    Resp Dict Value    $.data.status
    Should Be Equal    ${actual_status}    ${expected_status}
```

## 关键字复用技巧

### 关键字组合

```robotframework
*** Keywords ***
创建并校验商户
    [Documentation]    创建商户并校验创建成功
    [Arguments]    ${merchant_type}
    ${merchant_no}    创建测试商户    ${merchant_type}
    ${detail}    查询商户信息    ${merchant_no}
    [Return]    ${detail}
```

### 错误处理

```robotframework
*** Keywords ***
安全查询商户
    [Documentation]    安全地查询商户，处理可能的异常
    [Arguments]    ${merchant_no}
    ${result}    Run Keyword And Return Status    查询商户信息    ${merchant_no}
    Run Keyword If    '${result}' == 'PASS'    Log    查询成功    ELSE    Log    查询失败: ${result}
```

## 命名规范

### 中文命名（推荐）

```robotframework
# 使用中文，体现业务含义
查询商户信息
创建变更申请单
校验订单状态

# 避免过于笼统的名称
处理数据    # ❌ 不推荐
执行操作    # ❌ 不推荐

# 推荐明确具体的名称
查询商户基本信息    # ✅ 推荐
提交商户状态变更申请    # ✅ 推荐
```

### 英文命名

```verilog
# 使用驼峰或下划线
QueryMerchantInfo
CreateMerchant
ValidateOrderStatus

# 避免缩写
GetMchInfo    # ❌ 不推荐
CrtMch    # ❌ 不推荐

# 推荐完整拼写
QueryMerchantInfo    # ✅ 推荐
CreateMerchant    # ✅ 推荐
```

## 禁止事项

### 不要重复定义关键字

```robotframework
# ❌ 错误：重复定义
商户查询接口
    [Documentation]    查询商户信息
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant    ${merchant_no}
    [Return]    ${resp}

商户查询接口    # 重复定义
    [Documentation]    查询商户信息（重复）
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant/${merchant_no}
    [Return]    ${resp}

# ✅ 正确：使用不同名称或参数区分
商户查询接口
    [Documentation]    查询商户信息
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant    ${merchant_no}
    [Return]    ${resp}

商户详情查询接口
    [Documentation]    查询商户详情
    [Arguments]    ${merchant_id}
    ${resp}    GET    /api/merchant/${merchant_id}
    [Return]    ${resp}
```

### 不要重复实现 BuiltIn 功能

```robotframework
# ❌ 错误：重复实现已有功能
计算数值和
    [Arguments]    ${a}    ${b}
    ${result}    Evaluate    ${a} + ${b}
    [Return]    ${result}

# ✅ 正确：直接使用 BuiltIn
计算数值和
    [Arguments]    ${a}    ${b}
    ${result}    Evaluate    ${a} + ${b}
    [Return]    ${result}
```

### 不要忽略 Documentation

```robotframework
# ❌ 错误：缺少文档
我的关键字
    [Arguments]    ${param}

# ✅ 正确：包含完整文档
我的关键字
    [Documentation]    关键字功能描述
    ...    参数：
    ...    param - 参数说明
    [Arguments]    ${param}
```

### 不要在关键字中写复杂业务逻辑

```robotframework
# ❌ 错误：关键字中包含过多逻辑
复杂关键字
    [Arguments]    ${input}

    # 大量业务逻辑...

# ✅ 正确：拆分为多个关键字
步骤1关键字
    [Arguments]    ${input}

步骤2关键字
    [Arguments]    ${input}

步骤3关键字
    [Arguments]    ${input}
```

### 不要在关键字末尾多次使用 [Return]

```robotframework
# ❌ 错误：[Return] 多次出现
商户查询接口
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant    ${merchant_no}
    [Return]    ${resp}    # 第一个 [Return]
    ${data}    Resp Dict Value    $.data
    [Return]    ${data}    # 第二个 [Return]，会报错

# ✅ 正确：只在末尾使用一次 [Return]
商户查询接口
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant    ${merchant_no}
    ${data}    Resp Dict Value    $.data
    [Return]    ${data}    # 只在末尾使用一次
```

### 不要在 [Arguments] 或 [Tags] 之后立即使用 [Return]

```robotframework
# ❌ 错误：[Return] 位置错误
商户查询接口
    [Documentation]    查询商户信息
    [Arguments]    ${merchant_no}
    [Return]    ${resp}    # 错误位置
    ${resp}    GET    /api/merchant    ${merchant_no}

# ✅ 正确：[Return] 在关键字末尾
商户查询接口
    [Documentation]    查询商户信息
    [Arguments]    ${merchant_no}
    ${resp}    GET    /api/merchant    ${merchant_no}
    [Return]    ${resp}    # 正确位置
```

## 参数校验示例

```robotframework
*** Keywords ***
带参数校验的关键字
    [Documentation]    关键字功能，包含参数校验
    [Arguments]    ${param1}    ${param2}
    Should Not Be Empty    ${param1}
    Should Not Be Empty    ${param2}
    ${is_string}    Is Instance    ${param1}    str
    Should Be True    ${is_string}
    ${is_valid}    Validate Range    ${param2}    1    100
    Should Be True    ${is_valid}
    ${result}    Main Operation    ${param1}    ${param2}
    [Return]    ${result}
```

## 关键字模板集

### HTTP 请求模板

```robotframework
*** Keywords ***
发送 GET 请求
    [Documentation]    发送 GET 请求并返回响应
    ...    参数：
    ...    url - 请求URL
    ...    headers - 请求头（可选）
    ...    返回：
    ...    response - 响应对象
    [Arguments]    ${url}    ${headers}=${EMPTY}
    [Tags]    http    request
    Create Session    api_session
    ${response}    GET On Session    api_session    ${url}    headers=${headers}
    [Return]    ${response}


发送 POST 请求
    [Documentation]    发送 POST 请求并返回响应
    ...    参数：
    ...    url - 请求URL
    ...    data - 请求数据
    ...    headers - 请求头（可选）
    ...    返回：
    ...    response - 响应对象
    [Arguments]    ${url}    ${data}    ${headers}=${EMPTY}
    [Tags]    http    request
    Create Session    api_session
    ${response}    POST On Session    api_session    ${url}    json=${data}    headers=${headers}
    [Return]    ${response}
```

### JSONPath 提取模板

```robotframework
*** Keywords ***
从响应提取字段
    [Documentation]    从 JSON 响应中提取指定字段
    ...    参数：
    ...    response - 响应对象
    ...    jsonpath - JSONPath 表达式
    ...    返回：
    ...    value - 字段值
    [Arguments]    ${response}    ${jsonpath}
    [Tags]    jsonpath    extract
    ${value}    Resp Dict Value    ${jsonpath}
    [Return]    ${value}


从响应提取数组
    [Documentation]    从 JSON 响应中提取数组字段
    ...    参数：
    ...    response - 响应对象
    ...    jsonpath - JSONPath 表达式
    ...    返回：
    ...    values - 字段值列表
    [Arguments]    ${response}    ${jsonpath}
    [Tags]    jsonpath    extract
    ${values}    Resp Dict Value    ${jsonpath}
    ${is_list}    Evaluate    isinstance(${values}, list)
    ${result}    Run Keyword If    ${is_list}
    ...    Set Variable    ${values}
    ...    ELSE
    ...    Create List    ${values}
    [Return]    ${result}
```