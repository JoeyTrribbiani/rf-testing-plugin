---
description: 仅需求转 RF 用例（子工作流）
argument-hint: [tapd-link]
---

从 TAPD 需求生成 RF 测试用例，不包含执行和导出步骤。

工作流定义：
@${CLAUDE_PLUGIN_ROOT}/workflows/requirement-to-rf.md

**使用方式**：

```
/rf-testing:requirement-to-rf <tapd-link>
```

**参数**：
- `tapd-link`: TAPD 需求链接（可选，如未提供会询问）

**示例**：
```
/rf-testing:requirement-to-rf https://www.tapd.cn/48200023/prong/stories/view/1148200023001077267
```

**执行步骤**：

1. 从 TAPD 拉取需求内容
2. 识别测试场景
3. 识别测试点
4. 从 YAPI 获取接口文档（如有）
5. 生成 RF 用例
6. RF 质量保证检查
7. 检查 RF 规范

**输出**：
- RF 用例文件（.robot）
- 质量保证报告
- 规范检查报告

**注意**：此命令不会执行测试用例，也不会导出到 TAPD。
