# RF 测试插件安装指南

## 快速安装

### 方法1：一键安装（推荐）

**Linux / macOS:**

```bash
# 下载并执行安装脚本
curl -fsSL https://raw.githubusercontent.com/JoeyTrribbiani/rf-testing-plugin/master/install.sh | bash

# 或手动下载后执行
git clone https://github.com/JoeyTrribbiani/rf-testing-plugin.git
cd rf-testing-pluginugs
chmod +x install.sh
./install.sh
```

**Windows:**

```cmd
# 下载并执行安装脚本
git clone https://github.com/JoeyTrribbiani/rf-testing-plugin.git
cd rf-testing-plugin
install.bat
```

安装脚本将自动完成：
- ✓ Python 3.7.16+ 环境检查
- ✓ Robot Framework 3.2.2 安装
- ✓ 基础依赖安装（pandas, openpyxl）
- ✓ 自定义库安装（robotframework-jljltestlibrary）
- ✓ 克隆插件仓库到 `~/.claude/plugins/rf-testing-plugin`
- ✓ 配置 Claude Skills 到 settings.json
- ✓ 验证安装

### 方法2：手动安装

```bash
# 克隆仓库
git clone https://github.com/JoeyTrribbiani/rf-testing-plugin.git
cd rf-testing-plugin

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python -c "import pandas, openpyxl, robotframework, robotframework_jljltestlibrary; print('所有依赖安装成功！')"
```

## Python 依赖

**版本要求：**
- Python 3.7.16+
**Robot Framework 版本：**
- Robot Framework 3.2.2

### 基础依赖

```bash
pip install pandas>=2.0.0 openpyxl>=3.1.0
```

### 自定义库（可选）

项目包含自定义库 `JLTestLibrary.zip`，提供特定业务关键字。

**安装方式：**

1. **从项目根目录安装（推荐）：**
   ```bash
   # 解压到 Python site-packages 目录
   unzip JLTestLibrary.zip -d "$HOME/AppData/Local/Programs/Python/Python310/Lib/site-packages/"

   # 或者解压到当前项目依赖目录
   unzip JLTestLibrary.zip -d ./Lib/site-packages/
   ```

2. **从私有 PyPI 安装（需要确认）：**
   ```bash
   pip install
     robotframework-jljltestlibrary==0.0.1.dev50+ge870d58
     -U -i https://nexus.jlpay.com/repository/local-pypi/simple
     --trusted-host nexus.jlpay.com
   ```
   
   **注意：**
   - 私有 PyPI 镜像地址和版本号需要根据实际情况确认
   - 建议先联系运维获取正确的安装信息
   - 安装前请确认网络连接和权限

**安装验证：**

```bash
# 验证基础依赖
python -c "import pandas, openpyxl, robotframework; print('基础依赖安装成功')"

# 验证自定义库
python -c "import; print('自定义库安装成功')"
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
rf-testing-plugin/
├── 00-JL-Skills/          # JL 公共库（无需额外配置）
│   └── jl-skills/
│       ├── instructions/    # 交互协议指令
│       ├── specs/           # 规范文档（全局+业务）
│       │   ├── Robot Framework 编写规范.md
│       │   ├── JSONPath 使用指南.md
│       │   ├── BuiltIn 库使用规范.md
│       │   ├── DateTime 库使用规范.md
│       │   └── business/     # 业务规则目录
│       │       └── 商户系统业务规范.md
│       └── templates/       # 模板文件
├── 01-RF-Skills/          # RF 技能（已通过 skills.json 配置）
├── 02-workflows/           # 工作流定义
├── 03-scripts/             # 实用脚本
├── 04-cases/              # 使用案例
├── .claude-plugin/        # Plugin 元数据
├── requirements.txt         # Python 依赖
├── JLTestLibrary.zip       # 自定义库（可选）
└── README.md              # 插件说明
```

## 规范文档结构

| 文档 | 说明 | 位置 |
|------|------|------|
| Robot Framework 编写规范.md | 全局通用规范，包含用例编写风格、变量管理、错误处理等 | 00-JL-Skills/jl-skills/specs/ |
| JSONPath 使用指南.md | JSONPath 语法和示例 | 00-JL-Skills/jl-skills/specs/ |
| BuiltIn 库使用规范.md | BuiltIn 库关键字说明 | 00-JL-Skills/jl-skills/specs/ |
| DateTime 库使用规范.md | DateTime 库使用说明 | 00-JL-Skills/jl-skills/specs/ |
| 商户系统业务规范.md | 商户系统业务模式索引和详细内容 | 00-JL-Skills/jl-skills/specs/business/ |

## 卸载

### 卸载 Claude 插件

```bash
# 通过 Claude 插件管理器卸载
claude plugin uninstall rf-testing-plugin
```

### 卸载 Python 依赖

```bash
pip uninstall pandas openpyxl robotframework robotframework-jljltestlibrary
```

## 故障排除

### 问题1：技能未加载

**解决方案**：
- 检查 settings.json 路径是否正确
- 检查 SKILL.md 文件是否存在
- 重启 Claude

### 问题2：脚本执行失败

**解决方案**：
- 检查 Python 版本（需要 3.7.16+）
- 重新安装依赖
- 检查文件权限

### 问题3：MCP 连接失败

**解决方案**：
- 检查 TAPD MCP Server 是否运行
- 检查配置文件格式
- 查看 Claude 日志

### 问题4：自定义库安装失败

**解决方案**：
- 确认 PyPI 镜像地址和版本号
- 检查网络连接
- 检查 Python 版本兼容性
- 联系运维获取正确安装信息

### 问题5：规范文档不更新

**解决方案**：
- 参考规范文档：`00-JL-Skills/jl-skills/specs/`
- 业务规则索引：`00-JL-Skills/jl-skills/specs/business/`
- 全局规范：`Robot Framework 编写规范.md`
