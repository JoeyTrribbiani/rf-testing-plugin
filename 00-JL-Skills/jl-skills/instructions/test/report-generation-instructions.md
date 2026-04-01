# 测试报告生成指令

指导 AI 如何生成测试报告和 TAPD 导出内容。

## 目标

生成测试执行报告和 TAPD 可导入的测试用例格式。

## 报告生成流程

1. **汇总收集的测试信息**
   - 测试用例数量
   - 通过率统计
   - 失败用例列表
   - 覆盖的功能模块

2. **生成测试报告**
   - 测试概述（时间、人员、范围）
   - 测试结果统计表
   - 问题汇总
   - 建议和改进点

3. **准备 TAPD 导入格式**
   - 将 RF 用例转换为 TAPD Excel 格式
   - 调用 `robot2tapd.py` 脚本
   - 生成 base64 编码

## 报告格式模板

```markdown
# Robot Framework 测试报告

## 测试概述

- **测试时间**: ${date}
- **测试人员**: ${tester}
- **测试范围**: ${scope}
- **测试用例总数**: ${total_cases}
- **通过率**: ${pass_rate}%

## 测试结果

| 模块 | 用例总数 | 通过 | 失败 | 通过率 |
|------|---------|------|------|--------|
| 模块1 | ${count1} | ${pass1} | ${fail1} | ${rate1}% |
| 模块2 | ${count2} | ${pass2} | ${fail2} | ${rate2}% |

## 问题汇总

| 序号 | 用例名称 | 问题描述 | 严重程度 | 状态 |
|------|---------|---------|---------|--------|
| 1 | ${case1} | ${issue1} | ${severity1} | ${status1} |

## 改进建议

1. [建议1]
2. [建议2]
3. [建议3]
```

## TAPD 导入格式

调用 `robot2tapd.py` 脚本生成 TAPD 可导入格式：

```bash
python 03-scripts/robot2tapd.py ${robot_file} \
    --excel ${output_excel} \
    --creator ${creator_name} \
    --out-b64 ${base64_file}
```

输出：
- TAPD Excel 文件
- Base64 编码字符串
- 用例数量统计

## 报告维度

1. **测试覆盖度**
   - 功能模块覆盖
   - 场景覆盖
   - 边界条件覆盖

2. **测试质量**
   - 用例规范性
   - 关键字复用
   - 代码风格一致性

3. **自动化可行性**
   - 可自动化的用例占比
   - 需要特殊环境的用例
   - 手动测试用例

## 模板引用

- `JL-Template-TAPD-Report.md` - TAPD 报告模板
- `TAPD_spec.md` - TAPD 导入规范（在 tapd-conversion/references/ 下）