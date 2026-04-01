# RF 脚本生成指令

指导 AI 如何基于测试点生成符合 RF 规范的用例脚本。

## 目标

将测试点转换为可执行的 Robot Framework 用例，遵循 `Robot Framework 编写规范.md`。

## 处理流程

1. **读取测试点列表**
   - 确认每个测试点的描述完整
   - 检查自动化可行性标记

2. **生成用例骨架**
   - 创建 `*** Test Cases ***` 段
   - 为每个测试点用例定义

3. **编写 [Documentation] 标签**
   - 必须为三段式：`【预置条件】... 【操作步骤】... 【预期结果】...`
   - 内容简洁，使用业务语言而非技术实现细节

4. **添加 [Tags] 标签**
   - 优先级：高/中/低
   - 评审状态：未评审/已评审

5. **编写用例步骤**
   - 使用已有的 Keywords.robot 中的关键字
   - 遵循 RF 编写规范
   - 添加必要的注释

## 用例结构模板

```robotframework
*** Test Cases ***
${TEST_CASE_NAME}
    [Documentation]    【预置条件】${PRECONDITION} 【操作步骤】${STEPS} 【预期结果】${EXPECTED}
    [Tags]    ${PRIORITY}    ${REVIEW_STATUS}
    
    # 前置准备步骤（如有）
    # Setup 步骤
    
    # 用例主步骤
    Step 1
    Step 2
    Step 3
    
    # 清理步骤（如有）
    # Teardown 步骤
```

## 关键字使用原则

1. **优先使用现有关键字**
   - 从 `Keywords.robot` 导入关键字
   - 避免重复实现
   
2. **命名规范**
   - 使用中文描述
   - 清晰表达功能意图

3. **参数设计**
   - 必填参数在前，可选参数在后
   - 使用默认值减少调用复杂度

4. **变量作用域**
   - 优先使用局部变量（`Set Variable`）
   - 需要跨用例共享时使用 `Set Suite Variable`
   - 谨慎使用全局变量（`Set Global Variable`）

## 注意事项

1. [Documentation] 内容必须在一行内
2. 不要在 [Documentation] 中写技术实现细节
3. 遵循 RF 编写规范中的命名、注释、错误处理等规则
4. 使用 JSONPath 表达式时参考 `JSONPath 使用指南.md`
5. 每个用例应该有清晰的验证步骤

## 模板引用

使用以下模板作为参考：
- `JL-Template-RF-TestCase.md` - RF 用例模板
- `JL-Template-RF-Keyword.md` - RF 关键字模板