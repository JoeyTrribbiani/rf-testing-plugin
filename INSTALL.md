# RF 测试插件安装指南

## 快速安装

### 方法1：克隆安装

```bash
# 克隆仓库
git clone <repository-url> rf_plugin_for_claude
cd rf_plugin_for_claude

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python -c "import pandas, openpyxl, robotframework; print('所有依赖安装成功！')"
```

### 方法2：使用 Claude 插件管理器

```bash
# 通过 Claude 插件管理器安装
claude plugin install rf-testing-plugin
```

## 依赖安装

```bash
# Python 依赖
pip install pandas openpyxl robotframework

# 验证安装
python 03-scripts/robot2tapd.py --help
```

## 配置步骤

### 1. 配置 Claude Skills

编辑 `~/.claude/settings.json`：

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

### 2. 配置 TAPD MCP

确保 TAPD MCP Server 已安装并运行：

```bash
# 检查 MCP 服务器状态
claude mcp list
```

### 3. 验证安装

```bash
# 验证技能加载
/rf-standards-check

# 验证脚本可用
python 03-scripts/robot2tapd.py --help
```

## 目录结构说明

安装后的目录结构：

```
rf_plugin_for_claude/
├── 00-JL-Skills/          # JL 公共库（无需额外配置）
├── 01-RF-Skills/          # RF 技能（已通过 skills.json 配置）
├── 02-workflows/           # 工作流定义
├── 03-scripts/             # 实用脚本
├── 04-cases/              # 使用案例
├── .claude-plugin/         # 插件元数据
└── README.md
```

## 卸载

### 卸载 Claude 插件

```bash
# 通过 Claude 插件管理器卸载
claude plugin uninstall rf-testing-plugin
```

### 卸载 Python 依赖

```bash
pip uninstall pandas openpyxl robotframework
```

## 故障排除

### 问题1：技能未加载

**解决方案**：
- 检查 settings.json 路径是否正确
- 检查 SKILL.md 文件是否存在
- 重启 Claude

### 问题2：脚本执行失败

**解决方案**：
- 检查 Python 版本（需要 3.10+）
- 重新安装依赖
- 检查文件权限

### 问题3：MCP 连接失败

**解决方案**：
- 检查 TAPD MCP Server 是否运行
- 检查配置文件格式
- 查看 Claude 日志