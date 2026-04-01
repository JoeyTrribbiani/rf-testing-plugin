# Robot Framework 测试插件

基于 **AI-First 插件标准**构建的 Robot Framework 测试用例生成与转换插件，对标开发工作流提供测试工程师视角能力。

## 功能

- 🔍 **需求分析**: 从 TAPD 拉取需求，识别测试场景和测试点
- 📝 **用例生成**: 基于测试点生成符合 RF 规范的用例脚本
- ✅ **规范检查**: 检查 RF 用例是否符合编写规范
- 📊 **TAPD 转换**: 将 RF 用例转换为 TAPD 可导入格式
- 🔄 **工作流编排**: 支持完整的测试工作流和子流程

## 快速开始

### 1. 安装依赖

```bash
pip install pandas openpyxl robotframework
```

### 2. 配置 MCP

确保 **TAPD MCP Server** 已部署并配置到 Claude Code。

### 3. 目录结构

```
rf-testing-plugin/
├── 00-JL-Skills/          # JL 公共库（指令、规范、模板）
├── 01-RF-Skills/          # RF 测试技能
├── 02-workflows/           # 工作流定义（Mermaid flowchart）
├── 03-scripts/             # 实用脚本
├── 04-cases/              # 使用案例
├── .claude-plugin/         # Plugin 元数据
└── README.md
```

### 4. 配置 Claude Skills

在 Claude `settings.json` 中引用技能：

```json
{
  "skills": [
    {
      "name": "rf-test",
      "path": "01-RF-Skills/skills/test/SKILL.md"
    },
    {
      "name": "rf-standards-check",
      "path": "01-RF-Skills/skills/rf-standards-check/SKILL.md"
    },
    {
      "name": "rf-tapd-conversion",
      "path": "01-RF-Skills/skills/tapd-conversion/SKILL.md"
    }
  ]
}
```

## 使用方式

### 完整测试流程

从 TAPD 需求到 TAPD 导出的完整流程。

```bash
/rf-test
```

### 需求转用例

从 TAPD 需求生成 RF 测试用例。

```bash
/rf-requirement-to-testcase
```

### RF 转 TAPD

将 RF 用例转换为 TAPD 格式。

```bash
/rf-to-tapd
```

### 仅规范检查

检查 RF 用例是否符合编写规范。

```bash
/rf-standards-check
```

## 核心技能

### rf-test

场景测试生成技能，对标开发工作流的测试闭环。

**流程**：
1. 从 TAPD 拉取需求内容
2. 识别测试场景和测试点
3. 生成 Robot Framework 用例
4. 检查 RF 规范
5. 转换为 TAPD 格式并导出

### rf-standards-check

RF 编写规范检查技能。

**检查项**：
- [Documentation] 标签格式（三段式）
- [Tags] 标签使用（优先级、评审状态）
- 变量命名规范
- 关键字命名规范
- 内联注释使用
- JSONPath 表达式正确性

### rf-tapd-conversion

RF 用例转 TAPD 格式技能。

**转换步骤**：
1. 解析 RF 用例文件
2. 转换为 TAPD 格式
3. 生成 Excel 文件
4. 生成 Base64 编码

## 工作流

### full-test-pipeline

完整测试工作流：TAPD 需求 → RF 用例 → 规范检查 → TAPD 导出

### requirement-to-rf

需求转用例工作流：TAPD 需求 → RF 用例生成 → 规范检查

### rf-to-tapd

RF 转 TAPD 工作流：RF 用例 → TAPD 转换 → 导出

## 实用脚本

### robot2tapd.py

RF 用例转 TAPD Excel 格式脚本。

**用法**：
```bash
python 03-scripts/robot2tapd.py <robot_path> \
    --excel <output_excel> \
    --dir <用例目录> \
    --sheet <工作表名称> \
    --creator <创建人> \
    --out-b64 <base64_file>
```

### batch_convert.sh

批量转换脚本。

**用法**：
```bash
./03-scripts/batch_convert.sh <robot_dir> <output_dir> <creator>
```

## 模板和规范

### RF 用例模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-RF-TestCase.md`

包含：
- 用例文件结构
- Documentation 三段式格式
- Tags 标签规范
- 变量命名规范

### 关键字模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-RF-Keyword.md`

包含：
- 关键字结构标准
- 三要素规范（Documentation、Arguments、Return）
- 关键字分类和命名规范

### TAPD 报告模板

模板位置：`00-JL-Skills/jl-skills/templates/JL-Template-TAPD-Report.md`

包含：
- 报告结构
- 统计信息格式
- Markdown 表格格式

### 规范文档

- `JSONPath 使用指南.md`: JSONPath 语法和示例
- `RF 关键字编写规范.md`: 关键字编写标准

## 使用案例

详见 `04-cases/README.md`：

- 案例1：商户状态变更测试
- 案例2：批量转换现有用例
- 案例3：规范检查
- 案例4：仅需求转用例
- 案例5：仅 RF 转 TAPD

## 架构设计

遵循 **AI-First 插件标准**：

- ✅ Claude Plugin 元数据格式（`.claude-plugin/marketplace.json` + `plugin.json`）
- ✅ Mermaid flowchart 工作流编排
- ✅ 统一交互协议（INTERACTION_PROTOCOL.md）
- ✅ SKILL.md 格式的技能定义
- ✅ jl-skills 公共库（指令/规范/模板）
- ✅ MCP Task 集成（TAPD）

## 依赖

- Python 3.10+
- pandas
- openpyxl
- robotframework
- TAPD MCP Server

## 参考

- [AI-First 开发插件](../ai-first-master/README.md)
- [Robot Framework 官方文档](https://robotframework.org/)
- [TAPD 平台](https://www.tapd.cn/)

## License

MIT