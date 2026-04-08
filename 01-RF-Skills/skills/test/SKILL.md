---
name: rf-test
description: Robot Framework 场景测试生成技能，对标开发工作流的测试闭环
alwaysApply: false
---

# Robot Framework 测试工作流

## 初始化检查

我已准备好执行 RF 测试工作流。

**整体流程**:
- 阶段1：从 TAPD 拉取需求内容
- 阶段2：识别测试场景和测试点
- 阶段3：生成 Robot Framework 用例
- 阶段4：检查 RF 规范
- 阶段5：转换为 TAPD 格式并导出

---

🛑 **需要您的输入**

请提供以下信息：
1. **TAPD 需求链接**: 需求的完整 URL（如：https://tapd.example.com/workspace/48200023/requirement/REQ001）

**请提供 TAPD 需求链接：**
```

---

## 用例命名规范（强制）

生成 RF 测试用例时，必须遵循以下命名规范：

### 命名格式
- **格式**: `业务操作_具体场景` 或 `业务功能_操作类型`
- **分隔符**: 必须使用下划线 `_`，**禁止使用空格**
- **语言**: 使用中文描述业务场景

### 命名转换规则
生成用例名称时，必须执行以下转换：
1. 将描述中的空格替换为下划线 `_`
2. 去除首尾空格
3. 连续空格合并为一个下划线

**转换示例**:
| 原始描述 | 转换后名称 |
|----------|------------|
| `商户状态变更 正常变暂停` | `商户状态变更_正常变暂停` |
| `生成入网商户号 首次` | `生成入网商户号_首次` |
| `商户绑定套餐 开关授权收款套餐` | `商户绑定套餐_开关授权收款套餐` |
| `电签首次入网门店认证并加机` | `电签首次入网门店认证并加机` |

### 正确示例
- ✅ `商户状态变更_正常变暂停`
- ✅ `商户绑定套餐_开关授权收款套餐`
- ✅ `电签首次入网门店认证并加机`
- ✅ `生成入网商户号_首次`

### 错误示例
- ❌ `商户状态变更 正常变暂停` (包含空格)
- ❌ `商户状态变更-正常变暂停` (使用连字符而非下划线)
- ❌ `商户状态变更__正常变暂停` (连续下划线)

---

## 目录结构规范（强制）

生成 RF 测试用例时，必须创建标准目录结构，包含 4 个核心文件：

### 标准目录结构

```
<需求名称>_测试套件/
├── Settings.robot          # 套件设置和初始化
├── Keywords.robot          # 用户关键字定义
├── Variables.robot         # 变量定义
└── <需求名称>_测试用例.robot   # 测试用例
```

### 文件 1: Settings.robot

**用途**: 套件级配置和初始化

**必需内容**:
```robotframework
*** Settings ***
Documentation    <需求标题> 测试套件
Resource         Keywords.robot
Resource         Variables.robot
Suite Setup      套件初始化
Suite Teardown   套件清理

*** Keywords ***
套件初始化
    Log    初始化测试环境
    # 根据需求添加初始化逻辑

套件清理
    Log    清理测试环境
    # 根据需求添加清理逻辑
```

### 文件 2: Keywords.robot

**用途**: 用户关键字定义（业务封装）

**必需内容**:
```robotframework
*** Settings ***
Documentation    用户关键字定义
Resource         Variables.robot
Library          Collections
Library          RequestsLibrary

*** Keywords ***
# 根据测试点生成对应的业务关键字
# 每个关键字必须包含 [Documentation] 说明
```

### 文件 3: Variables.robot

**用途**: 变量定义（配置数据）

**必需内容**:
```robotframework
*** Settings ***
Documentation    变量定义

*** Variables ***
# 配置变量
${BASE_URL}       https://api.example.com
${API_TIMEOUT}    30
# 根据需求添加其他变量
```

### 文件 4: <需求名称>_测试用例.robot

**用途**: 测试用例定义

**必需内容**:
```robotframework
*** Settings ***
Documentation    <需求标题> 测试用例
Resource         Settings.robot

*** Test Cases ***
# 用例名称必须使用下划线分隔，禁止空格
# 示例: 商户状态变更_正常变暂停
```

### 生成要求

1. **必须生成 4 个文件**，禁止只生成单个文件
2. **文件命名规范**:
   - Settings.robot、Keywords.robot、Variables.robot 为固定名称
   - 测试用例文件命名为 `<需求名称>_测试用例.robot`
3. **文件引用关系**:
   - Settings.robot 引用 Keywords.robot 和 Variables.robot
   - Keywords.robot 引用 Variables.robot
   - 测试用例文件引用 Settings.robot
4. **内容完整性**:
   - 每个文件必须包含完整的 `*** Settings ***` 节
   - Documentation 标签必须填写

---

## 参考用例复用规范（强制）

如果用户提供了参考用例目录，必须分析并复用已有内容，避免重复实现。

### 复用原则

1. **优先复用**: 功能完全匹配的关键字直接复用
2. **引用复用**: 通过 Resource 引用已有文件，不复制内容
3. **谨慎修改**: 不要轻易修改 Variables.robot 中已存在的变量
4. **禁止重复**: 禁止重复实现已有功能的关键字

### 询问现有用例目录

在生成测试用例之前，必须询问用户：

```
请提供以下信息：

1. 是否有现有用例目录可供参考和学习风格？
   - 如果有，请提供目录路径
   - 如果没有，我将根据 JL 标准规范生成用例

2. 如果有现有用例目录，您希望：
   - 完全复用现有风格（关键字命名、变量命名、目录结构等）
   - 仅作参考，使用 JL 标准规范
   - 混合模式：复用关键字，使用规范命名

请提供信息：
```

### 分析步骤

**步骤 1: 扫描参考目录**
```
参考用例目录/
├── Settings.robot
├── Keywords.robot      <-- 提取关键字定义
├── Variables.robot     <-- 提取变量定义
└── *测试用例.robot
```

**步骤 2: 提取可复用内容**

从 `Keywords.robot` 提取：
- 关键字名称
- [Arguments] 参数列表
- [Documentation] 功能描述
- 实现逻辑概要

从 `Variables.robot` 提取：
- 变量名称
- 变量值
- 变量用途说明

**步骤 3: 风格学习**

- 用例命名风格（业务操作_具体场景 vs 其他格式）
- 变量命名风格（驼峰 vs 蛇形）
- 注释风格（中文 vs 英文）
- 目录结构（是否有特殊的文件组织方式）

**步骤 4: 匹配复用建议**

| 匹配程度 | 处理方式 | 示例 |
|----------|----------|------|
| 完全匹配 | 直接复用，通过 Resource 引用 | `商户详情查询` 已存在，直接引用 |
| 部分匹配 | 修改后复用，说明差异点 | `V4商户状态变更` 可复用 `商户状态变更` 逻辑 |
| 不匹配 | 新建关键字 | 全新业务功能 |

### 复用示例

**场景**: 需求涉及商户状态变更

**参考用例分析**:
```robotframework
# Keywords.robot 中已存在
商户状态变更
    [Documentation]    商户状态变更
    [Arguments]    ${merch_no}    ${status}
    ...
```

**复用决策**:
- ✅ 复用 `商户状态变更` 关键字
- ✅ 通过 `Resource  Keywords.robot` 引用
- ❌ 不新建 `V4商户状态变更` 除非逻辑不同

### 生成要求

1. **必须询问用户**：在生成测试用例前，询问是否有现有用例目录
2. **分析参考目录**：如果提供 `reference_cases_dir`，必须执行分析
3. **生成复用报告**：列出可复用关键字和变量清单
4. **遵循复用原则**：优先复用，禁止重复实现
5. **记录决策**：说明每个关键字的复用决策（复用/修改/新建）
6. **禁止单文件输出**：严禁将所有内容生成在一个 .robot 文件中

### 目录结构强制规范

**生成 RF 用例时必须创建以下标准目录结构**：

```
<需求名称>_测试套件/
├── Settings.robot          # 套件设置和初始化（固定文件名）
├── Keywords.robot          # 用户关键字定义（固定文件名）
├── Variables.robot         # 变量定义（固定文件名）
└── <需求名称>_测试用例.robot   # 测试用例（文件名与需求相关）
```

**错误示例（严禁）**:
```
output/
└── 商户入网标准系统-业务接入层-资料提交.robot  # ❌ 所有内容在一个文件
```

**正确示例（必须）**:
```
output/
└── 商户入网标准系统-业务接入层-资料提交_测试套件/
    ├── Settings.robot
    ├── Keywords.robot
    ├── Variables.robot
    └── 商户入网标准系统-业务接入层-资料提交_测试用例.robot
```

### 文件拆分规则

如果所有内容当前在一个文件中，按以下规则拆分：

1. **Settings.robot** 包含：
   - `*** Settings ***` 节（Suite Setup/Teardown）
   - 全局 Resource 引用

2. **Keywords.robot** 包含：
   - `*** Keywords ***` 节
   - 所有用户定义关键字

3. **Variables.robot** 包含：
   - `*** Variables ***` 节
   - 所有 `${变量}` 定义

4. **测试用例.robot** 包含：
   - `*** Test Cases ***` 节
   - 所有测试用例
   - 引用 Settings.robot

---

## 阶段1：从 TAPD 拉取需求内容

📊 **进度**: 1/5 从 TAPD 拉取需求内容
[████░░░░░░░░░░░░░] 20%

| ✅ 已完成 | 🔄 进行中 | ⏳ 待完成 |
|:----------|:----------|:----------|
|  | 从 TAPD 拉取需求内容 | 识别测试场景 | 生成 RF 用例 | 检查 RF 规范 | TAPD 转换与导出 |

---

### 本步骤内容

使用 TAPD MCP 调用指定工具获取需求内容：

**MCP 调用参数**：
- `server`: tapd
- `workspace_id`: 48200023
- `tool_name`: fetch_requirement

**预期解析结果**：
- `requirement_id`: 需求 ID（如：REQ001）
- `requirement_title`: 需求标题
- `requirement_content`: 需求完整内容（Markdown 格式）
- `service_name`: 涉及的服务名称
- `acceptance_criteria`: 验收标准

解析需求内容，提取关键信息。

---

🛑 **确认点**

需求内容解析是否正确？

请回复：
- **确认** → 进入下一步
- **修改 [具体内容]** → 我将调整解析结果
