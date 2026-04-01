# Robot Framework · JSONPath 与响应校验

## JSONPath 表达式

### 基础表达式

| 表达式 | 含义 | 示例 |
|-------|------|------|
| `$.data` | 根节点的 data 字段 | `$.data` |
| `$.data[*].field_name` | data 数组中所有元素的 field_name | `$.data[*].merchant_id` |
| `$[0]` | 数组第一个元素 | `$[0].name` |
| `$.data[0]` | data 数组第一个元素 | `$.data[0].merchant_no` |
| `$.data[?(@.type=='A')]` | 筛选 type='A' 的元素 | `$.data[?(@.status=='active')]` |
| `$..field_name` | 任意深度的 field_name | `$..merchant_id` |

### 常用场景

```robotframework
# 提取单个字段
${merchant_id}    Resp Dict Value    $.data.merchant_id

# 提取数组字段
${list}    Resp Dict Value    $.data[*].merchant_no

# 提取嵌套字段
${amount}    Resp Dict Value    $.data.detail.amount
```

## 响应校验关键字

- `Resp Dict Compare    ${resp}` - 校验响应字典
- `Resp Dict Value    $.path` - 提取字段值
- `Should Be Equal    ${actual}    ${expected}` - 断言相等
- `Should Not Be Empty    ${value}` - 断言非空

## 类型处理技巧

**单元素数组返回字符串问题**：
当使用 `Resp Dict Value    $.data[*].field_name` 时，若数组只有一个元素，可能返回字符串而非列表。

**判断方式**：
```robotframework
${length}    Get Length    ${result}
${str_length}    Get Length    ${result}    # 字符串化后的长度
${is_list}    Run Keyword If    ${length} != ${str_length}    Set Variable    ${True}    ELSE    Set Variable    ${False}
```

**处理方式**：若非列表，用 `Create List    ${result}` 转为列表。

## 禁止

- 不要在 Python 表达式中用变量值做 `isinstance()` 判断
- 不要忽略单元素数组的字符串返回问题