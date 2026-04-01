# Robot Framework 编写规范

## 文档说明

本文档定义了 Robot Framework 自动化用例的编写规范，涵盖用例编写风格、关键字编写标准、变量管理规范以及技术技巧。

**版本要求：**
- Robot Framework 3.2.2
- Python 3.7.16+
- 自定义库：robotframework-jljltestlibrary（需从私有 PyPI 安装）

**参考文档：**
- Robot Framework 3.2.2 官方文档：https://robotframework.org/robotframework/3.2.2/libraries/BuiltIn.html
- Robot Framework 3.2.2 DateTime 库：https://robotframework.org/robotframework/3.2.2/libraries/DateTime.html
- JSONPath RFC 9535：https://datatracker.ietf.org/doc/html/rfc9535
- JSONPath 原始文章：https://goessner.net/articles/JsonPath/

---

## 1. 用例编写规范

### 1.1 用例结构标准

#### 基本结构

每个测试用例应包含以下标准结构：

```robotframework
*** Test Cases ***
用例名称
    [Documentation]    【预置条件】<描述> 【操作步骤】<描述> 【预期结果】<描述>
    [Tags]    优先级    评审状态
    [Timeout]    超时时间
    [Setup]    前置操作
    [Teardown]    清理操作
    # 用例步骤
    步骤1
    步骤2
    步骤3
```

#### 标签使用规范

**`[Documentation]` 标签：**
- **格式要求**：必须包含【预置条件】【操作步骤】【预期结果】三部分，且在同一行
- **内容要求**：
  - 预置条件：描述执行用例前需要满足的前提条件
  - 操作步骤：用业务语言描述操作，避免技术实现细节
  - 预期结果：描述用例执行后应该达到的结果
- **示例**：
  ```robotframework
  [Documentation]    【预置条件】已存在状态为"正常"的商户 【操作步骤】提交商户状态变更申请，将商户状态从"正常"变更为"暂停" 【预期结果】商户状态成功变更为"暂停"，系统返回变更成功提示
  ```

**`[Tags]` 标签：**
- 标记用例优先级：`高`、`中`、`低`
- 标记评审状态：`未评审`、`已评审`
- 示例：`[Tags]    高    未评审`

**`[Timeout]` 标签：**
- 设置用例超时时间，通常为 `5 minutes`
- 根据用例复杂度调整，避免用例执行时间过长

**`[Setup]` 标签：**
- 用例级别的前置准备
- 使用 `Run Keyword And Ignore Error` 处理可能失败的操作
- 示例：`[Setup]    服务健康检查    ${merch_access_standard_node}`

**`[Teardown]` 标签：**
- 用例级别的清理工作，确保测试环境恢复
- 使用 `Run Keyword If Test Failed` 在用例失败时执行清理
- 示例：`[Teardown]    Run Keyword If Test Failed    清理测试数据`

#### 用例命名规范

- 使用中文描述业务场景
- 命名格式：`业务操作_具体场景` 或 `业务功能_操作类型`
- 示例：
  - `商户绑定套餐_开关授权收款套餐`
  - `电签首次入网门店认证并加机`
  - `生成入网商户号_首次`

---

### 1.2 用例编写风格

#### 注释使用

- 使用 `Comment` 关键字添加步骤说明，描述操作意图而非技术实现
- 在关键步骤前后添加注释，说明业务逻辑
- 示例：
  ```robotframework
  Comment    先查询子商户详情
  商户详情查询    ${merch_no}
  Comment    修改后数据比对
  ```

#### 步骤组织

- 用例步骤应清晰、简洁，每个步骤完成一个明确的业务操作
- 避免在一个步骤中完成多个不相关的操作
- 使用关键字封装复杂逻辑，提高用例可读性

#### 数据验证

- 每个用例都应包含明确的验证点
- 使用断言关键字验证结果：`Should Be Equal`、`Should Not Be Empty`、`Should Be True` 等
- 验证响应数据时使用 `Resp Dict Compare` 或 `Resp Dict Value`

---

## 2. 变量管理规范

### 2.1 变量作用域

Robot Framework 支持四种变量作用域：

1. **局部变量**（`Set Variable`）
   - 仅在当前关键字或用例步骤内有效
   - **优先使用**，避免变量污染

2. **测试用例变量**（`Set Test Variable`）
   - 在当前测试用例内可见
   - 适用于用例内多步骤共享

3. **套件变量**（`Set Suite Variable`）
   - 在当前测试套件内可见
   - 适用于套件内用例间共享

4. **全局变量**（`Set Global Variable`）
   - 在所有测试和套件中可见
   - **应谨慎使用**，避免测试间相互影响

### 2.2 变量作用域选择原则

- **局部变量**：优先使用，仅在当前步骤内有效
- **测试用例变量**：适用于用例内多步骤共享数据
- **套件变量**：适用于套件内用例间共享数据（如查询结果）
- **全局变量**：仅在必要时使用，避免测试间状态耦合

### 2.3 变量声明方式

#### 基本声明

```robotframework
# 局部变量
${local_var}    Set Variable    值

# 测试用例变量
Set Test Variable    ${test_var}    值

# 套件变量
Set Suite Variable    ${suite_var}    值

# 全局变量（谨慎使用）
Set Global Variable    ${global_var}    值
```

#### 变量类型

**标量变量（${}）：**
- 字符串、数字、布尔值等单值
- 示例：`${merch_no}    Set Variable    M123456789`

**列表变量（@{}）：**
- 多个值的集合
- 示例：`@{status_list}    Create List    1    2    3`

**字典变量（&{}）：**
- 键值对集合
- 示例：`&{params}    Create Dictionary    key1=value1    key2=value2`

#### 变量命名规范

- 使用有意义的名称，体现业务含义
- 使用下划线分隔单词：`${merch_no}`、`${status_list}`
- 避免使用缩写，除非是通用术语
- 布尔变量使用 `is_`、`has_` 前缀：`${is_valid}`、`${has_permission}`

### 2.4 变量使用技巧

#### Python 表达式计算

- 使用 `${{}}` 进行 Python 表达式计算，避免变量替换问题
- 示例：
  ```robotframework
  ${result}    Set Variable    ${{1 + 2}}
  ${timestamp}    Set Variable    ${{int(time.time())}}
  ```

#### 变量转换

- 使用 `Convert To String`、`Convert To Integer`、`Convert To List` 等进行类型转换
- 示例：
  ```robotframework
  ${str_value}    Convert To String    ${int_value}
  ${int_value}    Convert To Integer    ${str_value}
  @{list_value}    Convert To List    ${str_value}
  ```

#### Run Keyword If 赋值注意事项

- `Run Keyword If` 如果要赋值，变量名必须在最前面
- 如果使用同名变量进行条件判断并赋值，在 ELSE 分支中需要使用 `Set Variable ${变量名}` 来承接前面的值，否则变量会被清空
- 示例：
  ```robotframework
  ${suffix_name_list}    Run Keyword If    ${is_list} and ${list_length} == 0    Resp Value    data    ELSE    Set Variable    ${suffix_name_list}
  ${is_black}    Run Keyword If    ${is_black} == ${true}    Set Variable If    "${status}[0][status]" == "2"    ${false}    ${is_black}
  ```

---

## 3. 错误处理技巧

### 3.1 异常场景验证

- 使用 `Resp Dict Compare` 验证错误返回码和错误消息
- 示例：
  ```robotframework
  Resp Dict Compare    {"ret_code":"V1","ret_msg":"商户号与渠道商户号不存在绑定关系"}
  ```

### 3.2 条件判断

- 使用 `Run Keyword If` 进行条件判断
- 使用 `Set Variable If` 进行条件赋值
- 示例：
  ```robotframework
  ${is_exist}    Set Variable If    '${fail_reason}' in ${resoult_message}    ${True}    ${False}
  ```

### 3.3 用例失败处理

- 使用 `Run Keyword If Test Failed` 在用例失败时自动清理
- 示例：
  ```robotframework
  [Teardown]    Run Keyword If Test Failed    V4商户申请单状态修改    ${apply_id}    5
  ```

### 3.4 TRY/EXCEPT/FINALLY 语法（Robot Framework 5+）

- 优先使用 `TRY / EXCEPT / FINALLY` 语法处理异常，提高可读性
- 示例：
  ```robotframework
  TRY
      执行可能失败的操作
  EXCEPT    AS    ${error}
      Log    操作失败: ${error}
      执行清理操作
  FINALLY
      最终清理
  END
  ```

**兼容旧版本：**
- 兼容旧版本时，可使用 `Run Keyword And Expect Error` 或 `Run Keyword And Ignore Error`
- 使用 `Run Keyword And Ignore Error` 处理可能失败的前置或清理操作

---

## 4. 异步处理技巧

### 4.1 等待机制

- 使用 `Sleep` 处理异步操作等待
- 变更类操作通常等待 `10` 秒（自动审核需要时间）
- 入网类操作通常等待 `${sd_sleep_time}` 秒（根据配置更灵活）
- 变更审核类操作通常等待 `${sd_change_auth_sleeptime}` 秒（根据配置更灵活）
- 查询类操作通常等待 `2-5` 秒
- 报备类操作通常等待 `3-5` 秒

### 4.2 等待关键字

- `Wait Until Keyword Succeeds` - 等待关键字成功执行，适用于异步操作
- 示例：
  ```robotframework
  Wait Until Keyword Succeeds    30s    2s    查询状态    ${merch_no}
  ```

### 4.3 数据准备

- 使用 `Suite Setup` 准备套件级别的测试数据
- 使用 `[Setup]` 准备用例级别的测试数据
- 使用 `Run Keyword And Ignore Error` 处理可能失败的前置操作

---

## 5. 技术技巧总结

### 5.1 变量替换

- 在自定义库中使用 `BuiltIn.replace_variables()` 处理变量替换
- 支持访问当前可用变量并处理字符串中包含的变量表达式（如 `${VAR}`）
- 适用于需要动态解析变量的场景

### 5.2 返回值处理

- Robot Framework 5+ 推荐使用 `RETURN` 语法返回值
- 兼容旧版本时，可使用 `[Return]` 或 `Return From Keyword`
- 支持返回多个值，用多个空格分隔

### 5.3 关键字复用

- 封装通用逻辑为关键字，提高代码复用性
- 使用参数和默认值增强关键字灵活性
- 支持参数替换（`replace_param`）和响应验证（`resp`）

### 5.4 性能优化

- 避免不必要的等待时间
- 合理使用变量作用域，减少内存占用
- 使用 `Run Keywords` 组合原子操作，减少关键字调用次数

### 5.5 可维护性

- 使用清晰的命名，体现业务含义
- 添加必要的注释，说明业务逻辑
- 保持代码结构清晰，避免过度嵌套
- 及时更新文档，记录最佳实践

---

## 6. 最佳实践总结

### 6.1 用例编写

1. **结构清晰**：每个用例包含完整的标签和清晰的步骤
2. **描述准确**：Documentation 标签准确描述业务场景
3. **验证充分**：每个用例包含明确的验证点
4. **清理及时**：使用 Teardown 确保环境恢复

### 6.2 关键字编写

1. **命名规范**：使用中文描述，清晰表达功能
2. **参数设计**：必填参数在前，可选参数在后，支持默认值
3. **错误处理**：合理使用错误处理机制，提高健壮性
4. **文档完善**：详细说明参数和返回值

### 6.3 变量管理

1. **作用域选择**：优先使用局部变量，谨慎使用全局变量
2. **命名规范**：使用有意义的名称，体现业务含义
3. **类型明确**：明确变量类型，避免类型混淆

### 6.4 代码质量

1. **可读性**：代码清晰，注释充分
2. **可维护性**：结构合理，易于修改
3. **可复用性**：封装通用逻辑，提高复用
4. **健壮性**：错误处理完善，异常场景覆盖

---

## 附录：参考资源

- Robot Framework 官方文档：https://robotframework.org/
- BuiltIn 库文档：https://robotframework.org/robotframework/3.2.2/libraries/BuiltIn.html
- DateTime 库文档：https://robotframework.org/robotframework/3.2.2/libraries/DateTime.html
- JSONPath RFC 9535：https://datatracker.ietf.org/doc/html/rfc9535
- 业务规范索引：[business/商户系统业务规范.md](./business/商户系统业务规范.md)

---

**文档版本：** 1.0
**最后更新：** 2026-04-01
