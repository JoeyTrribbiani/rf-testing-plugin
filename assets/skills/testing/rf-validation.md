# Robot Framework · 响应验证与断言

## 响应校验关键字

### Resp Dict Compare
```robotframework
# 校验完整响应
Resp Dict Compare    ${resp}

# 校验指定字段
Resp Dict Compare    ${resp}    ret_code=0000    ret_msg=成功
```

### Resp Dict Value
```robotframework
# 提取字段
${value}    Resp Dict Value    $.data.merchant_id

# 提取数组
${list}    Resp Dict Value    $.data[*].merchant_no
```

## 断言关键字

| 关键字 | 用途 | 示例 |
|--------|------|------|
| `Should Be Equal` | 断言相等 | `Should Be Equal    ${a}    ${b}` |
| `Should Not Be Equal` | 断言不等 | `Should Not Be Equal    ${a}    ${b}` |
| `Should Be True` | 断言为真 | `Should Be True    ${condition}` |
| `Should Not Be True` | 断言为假 | `Should Not Be True    ${condition}` |
| `Should Contain` | 断言包含 | `Should Contain    ${text}    keyword` |
| `Should Not Contain` | 断言不包含 | `Should Not Contain    ${text}    keyword` |
| `Should Be Empty` | 断言为空 | `Should Be Empty    ${list}` |
| `Should Not Be Empty` | 断言非空 | `Should Not Be Empty    ${list}` |
| `Should Match` | 正则匹配 | `Should Match    ${text}    pattern` |

## 响应结构

标准响应格式：
```json
{
  "ret_code": "0000",
  "ret_msg": "成功",
  "data": {
    ...
  }
}
```

## 校验顺序

1. 先校验 `ret_code` 和 `ret_msg`
2. 再校验 `data` 中的关键字段
3. 使用 JSONPath 精准定位字段

## 错误处理

```robotframework
# 容错执行
${status}    ${result}    Run Keyword And Ignore Error    可能失败的关键字
Run Keyword If    ${status}    Log    失败：${result}

# 条件执行
Run Keyword If    ${condition}    关键字A    ELSE    关键字B
```

## 禁止

- 不要忽略 ret_code 校验
- 不要用模糊的断言（如断言列表长度而非内容）
- 不要在关键字内部做复杂断言，应拆分为独立断言步骤