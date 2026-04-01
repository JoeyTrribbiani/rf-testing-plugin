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
