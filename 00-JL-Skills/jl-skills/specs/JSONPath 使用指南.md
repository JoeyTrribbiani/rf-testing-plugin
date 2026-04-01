# Robot Framework · JSONPath 使用指南

## 文档说明

JSONPath 是一种用于查询 JSON 数据的语言，最初由 Stefan Gössner 在 2007 年提出，并于 2024 年被 IETF 标准化为 RFC 9535。

**官方文档链接：**
- **IETF RFC 9535（标准规范）**：https://datatracker.ietf.org/doc/html/rfc9535
- **Stefan Gössner 原始文章**：https://goessner.net/articles/JsonPath/
- **RFC Editor**：https://www.rfc-editor.org/rfc/rfc9535.html

**自定义库支持：**
本项目的自定义库 `Resp Dict Value` 和 `Resp Dict Compare` 完全支持 JSONPath 表达式。

---

## 1. JSONPath 基本语法

JSONPath 表达式以 `$` 开头，表示根节点。常用语法包括：

| 表达式 | 含义 | 示例 |
|-------|------|------|
| `$` | 根节点 | `$` |
| `$.property` | 访问根节点的属性 | `$.data` |
| `$.array[index]` | 访问数组元素（索引从0开始） | `$.data[0]` |
| `$.array[*]` | 访问数组所有元素（通配符） | `$.data[*].field_name` |
| `$..property` | 递归下降，匹配所有层级的指定属性 | `$..merchant_id` |
| `$.array[?(@.property == 'value')]` | 使用过滤器表达式筛选数组元素 | `$.data[?(@.status=='active')]` |
| `$.*` | 匹配根节点下的所有属性 | `$.*` |

---

## 2. JSONPath 过滤器表达式

过滤器表达式格式：`[?(@.property operator value)]`，用于筛选符合条件的数组元素。

### 2.1 支持的操作符

| 操作符 | 说明 | 示例 |
|-------|------|------|
| `==` | 等于（注意：数字1不等于字符串'1'） | `@.count == 10` |
| `!=` | 不等于 | `@.status != '1'` |
| `<` | 小于 | `@.amount < 100` |
| `<=` | 小于等于 | `@.amount <= 100` |
| `>` | 大于 | `@.count > 0` |
| `>=` | 大于等于 | `@.score >= 60` |
| `=~` | 正则表达式匹配 | `@.name =~/^test.*/i` |
| `in` | 属于 | `@.type in ['A', 'B']` |
| `nin` | 不属于（排除） | `@.status nin ['deleted', 'archived']` |
| `size` | 大小匹配（数组或字符串的长度） | `@.items size == 5` |
| `empty` | 判空（Null 或空值） | `@.data empty` |

### 2.2 逻辑运算符

| 运算符 | 说明 | 示例 |
|-------|------|------|
| `&&` | 逻辑与（AND） | `@.status == '1' && @.channel_id == '10011'` |
| `\|\|` | 逻辑或（OR） | `@.type == 'A' \|\| @.type == 'B'` |
| `!` | 逻辑非（NOT） | `!@.deleted` |

---

## 3. JSONPath 使用示例

### 3.1 基本使用

#### 提取单个字段
```robotframework
${merchant_id}    Resp Dict Value    $.data.merchant_id
${merchant_name}    Resp Dict Value    $.data.name
```

#### 提取数组字段
```robotframework
# 提取数组中所有元素的某个字段
${merchant_no_list}    Resp Dict Value    $.data[*].merchant_no

# 提取数组中特定索引的元素
${first_item}    Resp Dict Value    $.data[0]
```

#### 提取嵌套字段
```robotframework
${amount}    Resp Dict Value    $.data.detail.amount
${city}    Resp Dict Value    $.data.address.city
```

### 3.2 过滤器表达式

#### 简单过滤
```robotframework
# 等于过滤
${wechat_merch_no}    Resp Dict Value    $.chan_merch_info_list[?(@.status == '1')].chan_merch_no

# 不等于过滤
${active_items}    Resp Dict Value    $.items[?(@.status != 'deleted')]
```

#### 多条件过滤
```robotframework
# AND 条件
${result}    Resp Dict Value    $.data[?(@.type == 'active' && @.count > 10)].id

# OR 条件
${filtered}    Resp Dict Value    $.products[?(@.status == 'active' || @.status == 'pending')].name
```

#### 正则表达式匹配
```robotframework
# 匹配以 test 开头的名称（不区分大小写）
${matched}    Resp Dict Value    $.items[?(@.name =~/^test.*/i)].value

# 匹配包含 REES 的书籍（不区分大小写）
${books}    Resp Dict Value    $..book[?(@.author =~ /.*REES/i)]
```

#### 使用 in 操作符
```robotframework
# 筛选状态在指定列表中的元素
${filtered}    Resp Dict Value    $.products[?(@.status in ['active', 'pending'])].name

# 筛选类型不在指定列表中的元素
${others}    Resp Dict Value    $.items[?(@.type nin ['A', 'B'])]
```

#### 使用递归下降
```robotframework
# 在所有层级中查找指定字段
${all_merchant_ids}    Resp Dict Value    $..merchant_id

# 在所有层级中查找 book 数组并筛选
${books}    Resp Dict Value    $..book[?(@.author =~ /.*REES/i)]
```

### 3.3 响应验证中使用 JSONPath

```robotframework
# 验证特定字段值
Resp Dict Compare    {"$.ret_code":"00","$.ret_msg":"处理成功"}

# 验证数组中特定元素的字段
Resp Dict Compare    {"$.rows[?(@.merch_no=='${merch_no}')].status":"1","ret_code":"00"}

# 多字段验证
Resp Dict Compare    {"$.data.merchant_no":"M001","$.data.status":"active"}
```

---

## 4. 使用建议

1. **复杂过滤条件**：使用 `&&` 和 `||` 组合多个条件
2. **字符串比较**：注意使用引号包裹字符串值，如 `'value'`
3. **数字比较**：数字值不需要引号，如 `@.count > 10`
4. **嵌套属性**：可以使用点号访问嵌套属性，如 `@.user.profile.name`
5. **数组索引**：在过滤后可以使用索引访问特定元素，如 `[0]` 获取第一个匹配项
6. **递归搜索**：使用 `..` 可以在所有层级中搜索，适用于不确定嵌套深度的场景
7. **正则表达式**：正则表达式格式为 `/pattern/flags`，常用标志 `i`（不区分大小写）、`g`（全局匹配）

---

## 5. 注意事项

### 5.1 类型处理

当使用 `Resp Dict Value` 提取数组字段时，如果数组中只有一个元素，可能返回字符串而不是列表。需要判断类型并转换为列表：

```robotframework
${result}    Resp Dict Value    $.data[*].suffix_name
${length_result}    ${length_value}    Run Keyword And Ignore Error    Get Length    ${result}
${str_result}    Run Keyword And Ignore Error    Convert To String    ${result}
${str_length}    Get Length    ${str_result[1]}
${is_list}    Set Variable If    '${length_result}' == 'PASS' and '${str_result[0]}' == 'PASS' and ${length_value} != ${str_length}    ${True}    ${False}
@{result_list}    Run Keyword If    ${is_list}    Set Variable    ${result}    ELSE    Create List    ${result}
```

**类型判断原理：** 通过比较变量的长度和其字符串表示的长度来判断类型。如果长度不相等，说明是列表；如果相等，说明是字符串。

### 5.2 其他注意事项

- JSONPath 表达式中的字符串值必须用单引号或双引号包裹
- 数字和布尔值不需要引号
- 过滤器表达式中的 `@` 表示当前正在评估的数组元素
- 使用 `Resp Dict Compare` 时，JSONPath 表达式同样适用
- 递归下降 `..` 会搜索所有匹配的路径，可能返回多个结果
- 正则表达式支持可能因实现而异，建议参考具体库的文档

---

## 6. 常见场景示例

### 6.1 商户系统示例

```robotframework
# 查询特定状态的商户号
${active_merch_no}    Resp Dict Value    $.chan_merch_info_list[?(@.status == '1' && @.channel_id == '10011')].chan_merch_no

# 查询指定套餐的套餐ID
${package_id}    Resp Dict Value    $.rows[0].package_info_list[?(@.package_name=='${name}')].package_id

# 验证商户状态变更结果
Resp Dict Compare    {"$.data.status":"暂停","ret_code":"00"}
```

### 6.2 订单系统示例

```robotframework
# 查询特定金额范围的订单
${orders}    Resp Dict Value    $.orders[?(@.amount >= 100 && @.amount <= 1000)]

# 查询特定日期的订单
${date_orders}    Resp Dict Value    $.orders[?(@.create_date =~ /^2024-04-01/)]
```

### 6.3 用户系统示例

```robotframework
# 查询活跃用户
${active_users}    Resp Dict Value    $.users[?(@.status == 'active' && @.login_count > 0)]

# 查询特定角色的用户
${admin_users}    Resp Dict Value    $.users[?(@.role in ['admin', 'superadmin'])]
```

---

## 7. 附录：完整示例

### 7.1 商户状态变更场景

```robotframework
*** Test Cases ***
商户状态变更-正常变暂停
    [Documentation]    【预置条件】已存在状态为"正常"的商户 【操作步骤】提交商户状态变更申请，将商户状态从"正常"变更为"暂停" 【预期结果】商户状态成功变更为"暂停"，系统返回变更成功提示
    [Tags]    中    未评审

    # 查询当前商户状态
    ${current_status}    Resp Dict Value    $.data.status

    # 提交状态变更
    商户状态变更    {"merch_no":"${merch_no}","new_status":"暂停"}

    # 验证变更结果
    Resp Dict Compare    {"$.ret_code":"00","$.ret_msg":"处理成功"}

    # 验证商户状态已更新
    ${updated_status}    Resp Dict Value    $.data.status
    Should Be Equal    ${updated_status}    暂停
```

### 7.2 渠道商户号查询场景

```robotframework
*** Test Cases ***
查询渠道商户号-微信渠道
    [Documentation]    【预置条件】已绑定微信渠道的商户 【操作步骤】查询商户渠道信息，获取微信渠道商户号 【预期结果】成功返回微信渠道商户号
    [Tags]    中    未评审

    # 查询渠道商户信息
    商户渠道查询    ${merch_no}

    # 提取微信渠道商户号
    ${wechat_merch_no}    Resp Dict Value    $.chan_merch_info_list[?(@.status == '1' && @.channel_id == '10011')].chan_merch_no

    # 验证结果
    Should Not Be Empty    ${wechat_merch_no}
```

---

**文档版本：** 1.0
**最后更新：** 2026-04-01