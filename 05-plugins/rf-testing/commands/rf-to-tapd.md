---
description: 仅 RF 转 TAPD 格式（子工作流）
argument-hint: [robot-file-path]
---

将 RF 用例文件转换为 TAPD 可导入的 Excel 格式。

工作流定义：
@${CLAUDE_PLUGIN_ROOT}/workflows/rf-to-tapd.md

**使用方式**：

```
/rf-testing:rf-to-tapd <robot-file-path>
```

**参数**：
- `robot-file-path`: RF 用例文件路径（可选，如未提供会询问）

**示例**：
```
/rf-testing:rf-to-tapd ./output/test_cases.robot
/rf-testing:rf-to-tapd D:\workspace\test.robot
```

**执行步骤**：

1. 验证 RF 用例格式
2. 检查 Documentation 三段式格式
3. 转换为 TAPD Excel 格式
4. 生成 Base64 编码（供 API 使用）

**输出**：
- TAPD Excel 文件（.xlsx）
- Base64 编码文件

**依赖**：
- 需要安装 pandas 和 openpyxl
- 需要正确格式的 RF 用例文件

**常见问题**：
如果输出 "成功处理 0 个测试用例"，说明 [Documentation] 缺少 `【预置条件】【操作步骤】【预期结果】` 三段式标记。
