# RF 测试插件使用案例

## 案例1：商户状态变更测试

### 需求

TAPD 需求链接：`https://tapd.example.com/workspace/48200023/requirement/REQ001`

需求描述：商户支持状态变更，从正常状态变更为暂停状态，需要测试变更流程的完整性和正确性。

### 执行步骤

1. 执行完整测试流程：
   ```bash
   /rf-test
   ```

2. 输入 TAPD 需求链接

3. 等待 AI 完成以下步骤：
   - 从 TAPD 拉取需求内容
   - 识别测试场景和测试点
   - 生成 RF 测试用例
   - 检查 RF 规范
   - 转换为 TAPD 格式

4. 确认生成的 RF 用例符合规范

5. 确认 TAPD 转换结果

### 预期输出

**RF 用例文件** (`商户状态变更.robot`)：
```robotframework
*** Test Cases ***
商户状态变更-正常到暂停
    [Documentation]    【预置条件】已存在状态为正常的商户 【操作步骤】调用商户状态变更接口，提交状态变更为暂停的申请，等待审核通过 【预期结果】商户状态成功变更为暂停，可进行暂停状态操作
    [Tags]    P0    approved    REQ-001

    ${resp}    商户状态变更接口    ${MERCHANT_NO}    paused
    Resp Dict Compare    ${resp}

    ${status}    Resp Dict Value    $.data.status
    Should Be Equal    ${status}    paused
```

**TAPD Excel 文件** (`商户状态变更.xlsx`)

**用例统计**：
- 正常用例: 3 个
- 异常用例: 5 个
- 边界用例: 2 个

---

## 案例2：批量转换现有用例

### 场景

已有 RF 用例文件，需要批量转换为 TAPD 格式并导入到 TAPD 平台。

### 执行步骤

1. 使用批量转换脚本：
   ```bash
   ./03-scripts/batch_convert.sh ./cases/ ./output "测试工程师"
   ```

2. 检查输出目录中的 Excel 文件

3. 将 Base64 编码文件上传到 TAPD

### 预期输出

- 所有 `.robot` 文件都有对应的 `.xlsx` 文件
- 所有 `.xlsx` 文件都有对应的 `.b64` 文件
- 转换统计信息：
  ```
  总计: 10
  成功: 10
  失败: 0
  ```

---

## 案例3：规范检查

### 场景

开发人员提交了 RF 用例代码，需要检查是否符合团队编写规范。

### 执行步骤

1. 执行规范检查技能：
   ```bash
   /rf-standards-check
   ```

2. 指定要检查的 RF 文件路径

3. 查看检查报告

### 预期输出

**检查报告**：
```
========== RF 规范检查报告 ==========

文件: ./cases/商户查询.robot

检查项:
✅ [Documentation] 格式正确（三段式）
✅ [Tags] 标签使用正确
✅ 变量命名符合规范
✅ 关键字命名符合规范
✅ 内联注释使用得当
✅ JSONPath 表达式正确

发现问题:
❌ 第 15 行：缺少内联注释
   建议：添加 # 调用查询接口

❌ 第 22 行：JSONPath 表达式可优化
   建议：使用 $.data.merchant_id 替代 $..merchant_id

总结:
- 检查通过: 5/6
- 需要修复: 1 项
- 建议优化: 1 项
```

---

## 案例4：仅需求转用例

### 场景

只需要从 TAPD 需求生成 RF 用例，不需要转换到 TAPD 格式。

### 执行步骤

1. 执行需求转用例工作流：
   ```bash
   /rf-requirement-to-testcase
   ```

2. 输入 TAPD 需求链接

3. 确认生成的用例

### 预期输出

- RF 用例文件（.robot）
- 用例统计信息
- 场景和测试点列表

---

## 案例5：仅 RF 转 TAPD

### 场景

已有 RF 用例文件，只需要转换为 TAPD 格式导出。

### 执行步骤

1. 执行 RF 转 TAPD 工作流：
   ```bash
   /rf-to-tapd
   ```

2. 指定 RF 用例文件路径

3. 配置输出参数

### 预期输出

- TAPD Excel 文件
- Base64 编码文件
- 用例数量统计

---

## 常见问题

### Q1: TAPD 需求链接在哪里获取？

**A**: 在 TAPD 平台打开需求详情页，浏览器地址栏即为需求链接。

### Q2: 转换后的 Excel 文件格式不对？

**A**: 检查以下事项：
1. RF 用例的 [Documentation] 是否为三段式格式
2. 是否使用了正确的标签
3. 文件编码是否为 UTF-8

### Q3: 批量转换时如何指定不同的创建人？

**A**: 在命令行中指定第三个参数：
```bash
./batch_convert.sh ./cases ./output "张三"
```

### Q4: 如何跳过规范检查？

**A**: 使用 `rf-to-tapd` 工作流直接转换，不经过规范检查步骤。

### Q5: Base64 编码太长无法复制？

**A**: 使用 `--out-b64` 参数保存到文件：
```bash
python 03-scripts/robot2tapd.py test.robot --out-b64 test.b64
```