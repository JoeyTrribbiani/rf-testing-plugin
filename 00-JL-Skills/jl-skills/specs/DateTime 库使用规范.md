# DateTime 库使用规范

## 文档说明

DateTime 是 Robot Framework 自带的日期时间处理库。本文档说明如何使用 DateTime 库进行日期时间计算、格式化和验证。

**参考文档：** https://robotframework.org/robotframework/latest/libraries/DateTime.html

**版本要求：** Robot Framework 3.2.2+

---

## 1. 日期时间获取

### 1.1 当前日期时间

```robotframework
# 获取当前日期（默认格式：YYYY-MM-DD）
${current_date}    Get Current Date

# 获取当前时间戳（epoch 时间）
${timestamp}    Get Time

# 获取当前时间（自定义格式）
${formatted_date}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
${year_month}    Get Current Date    result_format=%Y-%m
```

### 1.2 日期转换

```robotframework
# 将字符串转换为日期
${date_obj}    Convert Date    2024-04-01    date

# 转换日期格式
${formatted}    Convert Date    ${date}    result_format=%d/%m/%Y

# 日期加减天数
${future_date}    Add Time To Date    ${date}    5 days
${past_date}    Subtract Date From Date    ${date}    10 days
```

---

## 2. 时间戳处理

### 2.1 时间戳转换

```robotframework
# 获取当前时间戳
${timestamp}    Get Time    epoch

# 从日期对象获取时间戳
${date_timestamp}    Convert Date To Timestamp    2024-04-01

# 从格式化字符串获取时间戳
${str_timestamp}    Convert Time To Timestamp    2024-04-01 00:00:00
```

### 2.2 时间戳格式化

```robotframework
# 格式化时间戳
${time_str}    Get Time    format=%Y-%m-%d %H:%M:%S

# 获取秒级时间戳
${seconds}    Get Time    epoch

# 获取毫秒级时间戳
${milliseconds}    Get Time    epoch    millisecond
```

---

## 3. 日期时间计算

### 3.1 时间加减

```robotframework
# 天数加减
${tomorrow}    Add Time To Date    ${date}    1 day
${next_week}    Add Time To Date    ${date}    7 days
${yesterday}    Subtract Date From Date    ${date}    1 day
${last_month}    Subtract Date From Date    ${date}    1 month

# 小时、分钟、秒数加减
${future}    Add Time To Date    ${date}    2 hours=30 minutes=1800 seconds

# 混合单位加减
${complex_future}    Add Time To Date    ${date}    1 day=2 hours=3 hours=4 minutes=5 minutes=6 seconds=600 seconds

# 负数加减
${past}    Subtract Date From Date    ${date}    5 days=2 hours
```

### 3.2 时间差计算

```robotframework
# 计算两个日期的差值（天数）
${diff_days}    Subtract Date Time From Date    ${end_date}    ${start_date}

# 比较两个日期
${is_after}    Subtract Date From Date    ${later_date}    ${earlier_date}
# ${is_after} 会是负数，说明 later_date 在 earlier_date 之后
```

---

## 4. 日期时间格式化

### 4.1 日期格式化

```robotframework
# 常用日期格式
${ymd}    Convert Date    ${date}    result_format=%Y-%m-%d
${mdy}    Convert Date    ${date}    result_format=%m/%d/%Y
${dmy}    Convert Date    ${date}    result_format=%d-%m-%Y
${chinese}    Convert Date    ${date}    result_format=%Y年%m月%d日

# 带时间格式
${datetime}    Convert Date    ${date}    result_format=%Y-%m-%d %H:%M:%S
${datetime_ms}    Convert Date    ${date}    result_format=%Y-%m-%d %H:%M:%S.%f
```

### 4.2 时间格式化

```robotframework
# 24小时制
${time_24h}    Get Time    format=%H:%M:%S

# 12小时制
${time_12h}    Get Time    format=%I:%M:%S %p

# 带日期时间
${full_datetime}    Get Time    format=%Y-%m-%d %H:%M:%S

# 自定义分隔符
${custom}    Get Time    format=年:月:日 时:分:秒
```

---

## 5. 日期时间验证

### 5.1 日期验证

```robotframework
# 两个日期的差值（天数、小时、分钟）
${diff}    Subtract Date Time From Date    ${date1}    ${date2}

# 验证日期顺序
Should Be True    ${diff} > ${0}    # date1 应该在 date2 之前
Should Be Equal As Integers    ${diff}    7    # 两个日期应该相差7天
```

### 5.2 时间验证

```robotframework
# 验证时间范围
${current}    Get Time    epoch
${start}    Convert Time To Timestamp    09:00:00
${end}    Convert Time To Timestamp    18:00:00

Should Be True    ${current} >= ${start}    # 当前时间应该在开始时间之后
Should Be True    ${current} <= ${end}    # 当前时间应该在结束时间之前
```

---

## 6. 时区处理

### 6.1 时区设置

```robotframework
# 设置时区（影响后续所有时间操作）
Set Time Zone    Asia/Shanghai
Set Time Zone    UTC
Set Time Zone    America/New_York
```

### 6.2 时区计算

```robotframework
# UTC 转换为指定时区
${shanghai_time}    Convert Time    ${utc_time}    Asia/Shanghai

# 获取当前时区
${current_zone}    Get Time Zone
```

---

## 7. 商户系统示例

### 7.1 日期计算示例

```robotframework
*** Test Cases ***
商户审核超期检查
    [Documentation]    【预置条件】已创建商户审核申请 【操作步骤】检查申请是否超过7天未处理 【预期结果】正确判断申请是否超期
    [Tags]    中    未评审

    # 获取当前日期
    ${current_date}    Get Current Date

    # 模拟申请创建日期（7天前）
    ${apply_date}    Subtract Date From Date    ${current_date}    7 days

    # 获取申请创建时间
    ${apply_time}    Convert Date To Timestamp    ${apply_date} 00:00:00

    # 验证是否超期（假设当前时间是审核时间）
    ${current_time}    Get Time    epoch
    ${days_diff}    Subtract Date Time From Date    ${current_time}    ${apply_time}

    # 计算天数
    ${days}    Evaluate    int(${days_diff} / 86400)

    # 验证
    Should Be True    ${days} >= 7
```

### 7.2 时间范围验证示例

```robotframework
*** Test Cases ***
业务时间限制验证
    [Documentation]    【预置条件】存在业务开始和结束时间配置 【操作步骤】验证当前时间是否在业务时间范围内 【预期结果】正确判断当前时间是否在范围内
    [Tags]    中    未评审

    # 获取当前时间
    ${current}    Get Time    epoch

    # 业务开始时间（早9点）
    ${business_start}    Convert Time To Timestamp    09:00:00

    # 业务结束时间（晚6点）
    ${business_end}    Convert Time To Timestamp    18:00:00

    # 验证时间范围
    Should Be True    ${current} >= ${business_start}
    Should Be True    ${current} <= ${business_end}
```

---

## 8. 最佳实践

### 8.1 使用建议

1. **统一格式**：在项目内统一使用相同的日期时间格式
2. **时区一致**：明确使用哪个时区，避免时间计算错误
3. **异常处理**：在日期计算中使用 TRY/EXCEPT 处理无效日期
4. **格式化输出**：日期时间输出时使用统一格式，便于日志分析
5. **验证边界**：对日期边界条件进行充分测试（月末、闰年等）

### 8.2 常见场景

| 场景 | 关键字 | 说明 |
|------|--------|------|
| 计算截止日期 | `Add Time To Date` | 从当前日期加上固定天数 |
| 验证超期 | `Subtract Date Time From Date` | 计算两个日期的差值，判断是否超期 |
| 格式化显示 | `Get Time` `Convert Date` | 转换为统一格式用于显示 |
| 时间范围验证 | 比较时间戳 | 验证时间是否在有效范围内 |

---

## 9. 常见问题

### 9.1 格式问题

**问题：** 使用错误的格式字符串
```robotframework
# 错误：月份应该是大写 M
${wrong}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
# 正确：月份应该是大写 M
${correct}    Get Current Date    result_format=%Y-%m-%d %H:%M:%S
```

### 9.2 时区问题

**问题：** 时区设置不一致
```robotframework
# 建议：在用例开始时设置统一的时区
[Setup]    Set Time Zone    Asia/Shanghai
```

### 9.3 日期计算问题

**问题：** 使用字符串进行日期加减
```robotframework
# 错误：直接使用字符串
${result}    Add Time To Date    2024-04-01    7 days

# 正确：先转换为日期对象
${date}    Convert Date    2024-04-01    date
${result}    Add Time To Date    ${date}    7 days
```

---

**文档版本：** 1.0
**最后更新：** 2026-04-01
