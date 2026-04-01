# Robot Framework · 变量管理

## 变量类型

| 类型 | 格式 | 示例 |
|------|------|------|
| 标量变量 | `${NAME}` | `${merchant_no}` |
| 列表变量 | `@{NAME}` | `@{merchant_list}` |
| 字典变量 | `&{NAME}` | `&{merchant_info}` |
| 环境变量 | `%{NAME}` | `%{PATH}` |

## 变量作用域

| 作用域 | 说明 | 使用方式 |
|--------|------|----------|
| 测试用例变量 | 仅当前用例有效 | `${VAR}` |
| 套件变量 | 整个测试套件有效 | 在 `*** Variables ***` 中定义，用 `Set Suite Variable` |
| 全局变量 | 所有用例有效 | `Set Global Variable` |

## 常用操作

```robotframework
# 设置变量
${result}    Set Variable    value
@{list}    Create List    item1    item2
&{dict}    Create Dictionary    key1=value1    key2=value2

# 获取变量值
${value}    Get Variable Value    ${VAR}

# 设置套件变量
Set Suite Variable    ${suite_var}    value

# 获取列表元素
${item}    Get From List    @{list}    0

# 列表操作
Append To List    @{list}    new_item
${length}    Get Length    @{list}
```

## 变量替换规则

- `${VAR}` 在用例执行前替换为变量值
- `&{VAR}` 可以用 `&{VAR}[key]` 访问字典值
- `@{VAR}` 可以用 `@{VAR}[index]` 访问列表元素

## 禁止

- 不要混淆标量和列表变量格式
- 不要在循环外使用循环变量
- 不要忽略变量作用域