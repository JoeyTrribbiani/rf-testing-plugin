# TAPD 测试报告模板

## 报告结构

```markdown
# 测试报告

## 测试概述

- **测试时间**: ${date}
- **测试人员**: ${tester}
- **测试范围**: ${scope}
- **测试版本**: ${version}
- **测试环境**: ${environment}

## 测试统计

- **用例总数**: ${total_cases}
- **通过数**: ${passed}
- **失败数**: ${failed}
- **跳过数**: ${skipped}
- **通过率**: ${pass_rate}%

## 测试结果

| 序号 | 用例名称 | 用例目录 | 状态 | 用例等级 | 执行时间 | 备注 |
|------|----------|----------|------|----------|----------|------|
| 1 | ${case1} | ${dir1} | ${status1} | ${level1} | ${time1} | ${note1} |
| 2 | ${case2} | ${dir2} | ${status2} | ${level2} | ${time2} | ${note2} |

## 缺陷汇总

| 序号 | 缺陷ID | 用例名称 | 缺陷描述 | 严重程度 | 状态 |
|------|--------|----------|----------|----------|------|
| 1 | BUG-001 | ${case1} | ${desc1} | ${severity1} | ${status1} |

## 风险评估

- **高风险用例**: ${high_count} 个
- **阻塞问题**: ${block_count} 个
- **建议**: ${recommendations}

## 测试结论

${conclusion}

## 附录

- **详细日志**: ${log_file}
- **截图路径**: ${screenshot_path}
```

## 状态值说明

| 状态值 | 说明 | 图标 |
|--------|------|------|
| PASS | 通过 | ✅ |
| FAIL | 失败 | ❌ |
| SKIP | 跳过 | ⏭ |
| BLOCKED | 阻塞 | 🚫 |

## 严重程度说明

| 严重程度 | 说明 | 优先级 |
|----------|------|--------|
| 致命 | 系统崩溃或核心功能不可用 | P0 |
| 严重 | 主要功能受影响但可绕过 | P1 |
| 一般 | 次要功能缺陷，不影响核心流程 | P2 |
| 轻微 | 界面、文案等小问题 | P3 |

## 报告生成示例

```python
def generate_test_report(test_cases, defects):
    """生成测试报告"""

    # 统计信息
    total = len(test_cases)
    passed = len([c for c in test_cases if c.status == 'PASS'])
    failed = len([c for c in test_cases if c.status == 'FAIL'])
    skipped = len([c for c in test_cases if c.status == 'SKIP'])
    pass_rate = (passed / total * 100) if total > 0 else 0

    # 生成报告内容
    report = f"""# 测试报告

## 测试统计

- 用例总数: {total}
- 通过数: {passed}
- 失败数数: {failed}
- 跳过数: {skipped}
- 通过率: {pass_rate:.2f}%

## 测试结果

| 序号 | 用例名称 | 状态 | 用例等级 | 执行时间 |
"""

    for i, case in enumerate(test_cases, 1):
        report += f"| {i} | {case.name} | {case.status} | {case.level} | {case.duration}s |\n"

    return report
```

## Markdown 表格格式

### 基础表格

```markdown
| 列1 | 列2 | 列3 |
|------|------|------|
| 数据1 | 数据2 | 数据3 |
```

### 复杂内容表格

```markdown
| 列1 | 列2 | 列3 |
|------|------|------|
| 第1行<br>换行内容 | 正常内容 | **粗体内容** |
```

### 对齐方式

```markdown
# 左对齐（默认）
| 列1 | 列2 |
|:-----|:----|
| 数据1 | 数据2 |

# 居中对齐
| 列1 | 列2 |
|:----:|:---:|
| 数据1 | 数据2 |

# 右对齐
| 列1 | 列2 |
|-----:|----:|
| 数据1 | 数据2 |
```

## TAPD 导出格式

### Excel 列结构

| 列名 | 说明 | 必填 |
|--------|------|--------|
| 用例目录 | 用例所属目录 | 否 |
| 用例名称 | 用例标题 | 是 |
| 需求ID | 关联需求 ID | 否 |
| 前置条件 | 执行前需满足的条件 | 否 |
| 用例步骤 | 操作步骤描述 | 是 |
| 预期结果 | 执行后应达到的结果 | 是 |
| 用例类型 | 功能/性能/安全等 | 是 |
| 用例状态 | 正常/废弃 | 是 |
| 用例等级 | 高/中/低 | 是 |
| 创建人 | 创建人名称 | 是 |
| 是否自动化 | 是否可自动化 | 是 |
| 实现自动化 | 是否已实现 | 是 |
| 计划自动化 | 是否计划自动化 | 是 |

### Base64 编码

```python
import base64
import pandas as pd

# 读取 Excel
df = pd.read_excel('test_cases.xlsx')

# 转换为 Base64
excel_content = df.to_excel(index=False)
base64_str = base64.b64encode(excel_content).decode('utf-8')

# 保存
with open('test_cases.b64', 'w') as f:
    f.write(base64_str)
```

## 报告导出流程

1. **收集测试数据**
   - 用例执行结果
   - 缺陷信息
   - 日志和截图

2. **生成报告内容**
   - 填充模板
   - 计算统计数据
   - 生成表格

3. **保存报告**
   - Markdown 文件
   - Excel 文件
   - Base64 编码

4. **上传到 TAPD**
   - 使用 MCP 调用
   - 关联需求 ID
   - 关联缺陷 ID

## 报告模板扩展

### 带图表的报告

```markdown
## 测试趋势

![用例通过率趋势](trend_chart.png)

## 模块分布

![测试模块分布](module_chart.png)
```

### 带链接的报告

```markdown
## 详细日志

[查看完整日志](./logs/test.log)

## 失败用例

[用例1详情](./cases/case1.robot)
[用例2详情](./cases/case2.robot)
```

## 自动化报告生成

```python
def auto_generate_report(test_results, output_file):
    """自动化生成测试报告"""

    # 创建工作表
    workbook = xlsxwriter.Workbook(output_file)

    # 概览工作表
    overview_ws = workbook.add_worksheet('测试概览')
    add_overview(overview_ws, test_results)

    # 详细结果工作表
    detail_ws = workbook.add_worksheet('详细结果')
    add_details(detail_ws, test_results)

    # 缺陷工作表
    defect_ws = workbook.add_worksheet('缺陷汇总')
    add_defects(defect_ws, test_results)

    workbook.close()

    # 生成 Base64
    with open(output_file, 'rb') as f:
        base64_str = base64.b64encode(f.read()).decode('utf-8')

    return base64_str
```