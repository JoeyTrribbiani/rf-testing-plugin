# Robot Framework · 用户关键字编写

## 关键字结构标准

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

## 三要素规范

1. **Documentation（文档）**：必须包含，说明功能、参数、返回值
2. **Arguments（参数）**：明确参数列表和类型
3. **Return（返回）**：明确返回值，使用 `[Return]`

## 关键字分类

### 查询类
- 封装查询接口 → 校验返回 → 提取数据
- 支持通过 `resp` 参数自定义期望的 ret_code/ret_msg
- 返回提取的数据或设置套件变量

### 变更类
- 封装变更接口
- 请求体支持 `rep_param` 替换
- 校验用 `Resp Dict Compare`

### 数据准备类
- 组合多步完成数据准备
- 使用 `[Return]` 返回生成结果

## 命名规范

- 使用中文，体现业务含义（如 `查询商户信息`、`创建变更申请单`）
- 避免过于笼统的名称（如 `处理数据`、`执行操作`）

## 禁止

- 不要重复实现 BuiltIn 已有功能
- 不要忽略 Documentation 文档
- 不要在关键字中写复杂的业务逻辑，应拆分为多个关键字