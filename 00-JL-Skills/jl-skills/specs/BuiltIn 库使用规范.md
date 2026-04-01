# BuiltIn 库使用规范

## 文档说明

BuiltIn 是 Robot Framework 自带的库，提供了大量标准关键字。本文档说明如何高效使用 BuiltIn 库，避免重复造轮子。

**版本要求：** Robot Framework 3.2.2

**参考文档：** https://robotframework.org/robotframework/3.2.2/libraries/BuiltIn.html

---

## 1. 优先使用原则

- **禁止重复造轮子**：优先查找 BuiltIn 库中是否已有对应关键字
- **标准关键字优先**：使用 BuiltIn 标准关键字而非自定义实现
- **保持一致性**：在自定义关键字中获取 Robot Framework 或其他库实例应通过 `Get Library Instance`

---

## 2. 日志和调试

### 2.1 Log 关键字

```robotframework
# 记录关键步骤信息，明确日志级别
Log    开始执行商户查询    level=INFO
Log    调试信息    level=DEBUG
Log    操作失败    level=WARN
Log    系统错误    level=ERROR
```

### 2.2 Log Many 关键字

```robotframework
# 一次性记录多个变量值
Log Many    ${merch_no}    ${status}    ${result}    ${timestamp}
```

### 2.3 Comment 关键字

```robotframework
# 添加不执行的说明性注释
Comment    这是说明性注释，不会被执行
```

---

## 3. 列表操作

### 3.1 基本操作

```robotframework
# 获取列表长度
${length}    Get Length    ${list}

# 获取列表元素
${item}    Get From List    ${list}    0
${last}    Get From List    ${list}    -1

# 添加元素
Append To List    ${list}    new_item

# 合并列表
${combined}    Combine Lists    ${list1}    ${list2}

# 判断列表包含
List Should Contain Item    ${list}    ${item}

# 移除元素
Remove From List    ${list}    ${item}

# 清空列表
Remove Values From List    ${list}    value1    value2
```

### 3.2 常用场景

```robotframework
# 转换为列表
@{result}    Create List    item1    item2    item3

# 循环处理列表
FOR    ${item}    IN    @{result}
    Log    处理: ${item}
END
```

---

## 4. 字符串操作

### 4.1 基本操作

```robotframework
# 获取子字符串
${sub}    Get Substring    ${str}    0    5

# 替换字符串
${new_str}    Replace String    ${str}    old    new

# 分割字符串
@{parts}    Split String    ${str}    ,

# 连接字符串
${combined}    Catenate    ${str1}    ${str2}    ${str3}

# 转小写/大写
${lower}    Convert To Lower Case    ${str}
${upper}    Convert To Upper Case    ${str}
```

### 4.2 字符串验证

```robotframework
# 验证包含关系
Should Contain    ${str}    substring
Should Not Contain    ${str}    substring

# 验证相等
Should Be Equal    ${str1}    ${str2}

# 验证匹配
Should Match    ${str}    pattern

# 验证以...开头/结尾
Should Start With    ${str}    prefix
Should End With    ${str}    suffix
```

---

## 5. 字典操作

### 5.1 基本操作

```robotframework
# 创建字典
&{dict}    Create Dictionary    key1=value1    key2=value2

# 获取字典值
${value}    Get From Dictionary    ${dict}    key

# 设置字典值
Set To Dictionary    ${dict}    key    value

# 判断键存在
Dictionary Should Contain Key    ${dict}    key

# 获取所有键
@{keys}    Get Dictionary Keys    ${dict}

# 获取所有值
@{values}    Get Dictionary Values    ${dict}
```

---

## 6. 等待机制

### 6.1 固定等待

```robotframework
# 固定时间等待
Sleep    3s
Sleep    ${sleep_time}
```

### 6.2 动态等待

```robotframework
# 等待关键字成功执行，适用于异步操作
Wait Until Keyword Succeeds    30s    2s    查询状态    ${merch_no}

# 等待关键词出现
Wait Until Keyword Succeeds    10s    0.5s    Page Should Contain    加载完成
```

---

## 7. 评估表达式

### 7.1 基本用法

```robotframework
# 执行 Python 表达式，注意使用 `${{}}` 语法避免变量替换问题
${result}    Evaluate    ${a} + ${b}
${timestamp}    Evaluate    int(time.time())
${formatted}    Evaluate    '{0:02d}'.format(${value})

# 调用 Python 模块
${random}    Evaluate    random.randint(1, 100)    modules=random
```

---

## 8. 库实例获取

```robotframework
# 获取已导入库的实例，保持状态一致性
${builtins}    Get Library Instance    BuiltIn
${datetime}    Get Library Instance    DateTime
```

---

## 9. 库搜索顺序控制

```robotframework
# 当多个库或资源中存在同名关键字时，明确优先级
Set Library Search Order    MyCustomLib    SharedLib    BuiltIn
```

---

## 10. 断言关键字

### 10.1 常用断言

```robotframework
# 验证值相等
Should Be Equal    ${actual}    ${expected}    消息不匹配

# 验证值不相等
Should Not Be Equal    ${actual}    ${expected}

# 验证非空
Should Not Be Empty    ${result}    结果为空

# 验证条件为真
Should Be True    ${condition}    条件不满足

# 验证条件为假
Should Not Be True    ${condition}    条件不应为真

# 验证包含关系
Should Contain    ${text}    substring    文本不包含

# 验证数值比较
Should Be Equal As Integers    ${actual}    ${expected}

# 验证数值大小
Should Be Greater Than    ${actual}    ${expected}
Should Be Less Than    ${actual}    ${expected}
```

---

## 11. 类型转换

```robotframework
# 转换为字符串
${str_value}    Convert To String    ${int_value}

# 转换为整数
${int_value}    Convert To Integer    ${str_value}

# 转换为数字
${num_value}    Convert To Number    ${str_value}

# 转换为列表
@{list_value}    Convert To List    ${str_value}

# 转换为字典
&{dict_value}    Convert To Dictionary    ${json_str}

# 转换为布尔值
${bool_value}    Convert To Boolean    ${str_value}
```

---

## 12. 循环和条件执行

### 12.1 FOR 循环

```robotframework
# 遍历列表
FOR    ${item}    IN    @{list}
    Log    处理: ${item}
END

# 遍历字典
FOR    ${key}    IN    @{keys}
    ${value}    Get From Dictionary    ${dict}    ${key}
    Log    ${key} = ${value}
END

# 遍历范围
FOR    ${i}    IN RANGE    10
    Log    索引: ${i}
END
```

### 12.2 IF 条件

```robotframework
# 条件执行（Robot Framework 3.2.2 不支持原生 IF 语法）
# 使用 Run Keyword If 替代
Run Keyword If    ${condition}    关键字A
Run Keyword If    ${condition}    关键字A    ELSE    关键字B

# 条件赋值
${result}    Set Variable If    ${condition}    value1    value2
```

### 12.3 关键字执行控制

```robotframework
# 条件执行关键字
Run Keyword If    ${condition}    关键字A    关键字B

# 否定条件执行关键字
Run Keyword Unless    ${condition}    关键字

# 组合多个关键字
Run Keywords    关键字1    AND    关键字2    AND    关键字3

# 忽略关键字失败
Run Keyword And Ignore Error    可能失败的关键字

# 期望关键字失败
Run Keyword And Expect Error    应该失败的关键字
```

---

## 13. 变量操作

### 13.1 基本操作

```robotframework
# 设置变量
${var}    Set Variable    value

# 设置测试用例变量
Set Test Variable    ${var}    value

# 设置套件变量
Set Suite Variable    ${var}    value

# 设置全局变量（谨慎使用）
Set Global Variable    ${var}    value
```

### 13.2 变量作用域

| 变量类型 | 设置关键字 | 可见范围 | 用途 |
|-----------|-----------|----------|------|
| 局部变量 | `Set Variable` | 当前关键字或用例步骤内 | 优先使用，避免变量污染 |
| 测试用例变量 | `Set Test Variable` | 当前测试用例内 | 用例内多步骤共享 |
| 套件变量 | `Set Suite Variable` | 当前测试套件内 | 套件内用例间共享 |
| 全局变量 | `Set Global Variable` | 所有测试和套件中 | 谨慎使用，避免测试间相互影响 |

---

## 14. 最佳实践

### 14.1 使用原则

1. **优先使用标准关键字**：避免重复实现已有功能
2. **合理使用日志**：在关键步骤添加日志，提高可调试性
3. **使用断言验证**：使用 `Should Be Equal` 等断言关键字验证结果
4. **控制变量作用域**：优先使用局部变量，谨慎使用全局变量
5. **合理使用等待**：避免不必要的等待时间，使用动态等待

### 14.2 常见错误

1. **重复实现标准功能**：在使用自定义关键字前，先检查 BuiltIn 库
2. **过度使用全局变量**：避免测试间状态耦合
3. **忽略错误而非处理**：使用 `Run Keyword And Ignore Error` 时要有日志记录
4. **不使用断言**：所有验证步骤都应该有断言

---

**文档版本：** 1.0
**最后更新：** 2026-04-01