# RF 测试插件安装指南

## 快速安装

### 方法1：通过 Marketplace 安装（推荐）

```text
/plugin marketplace add .
/plugin install rf-testing
```

### 方法2：一键安装脚本（本地执行）

**前置条件：** 将插件下载到本地目录

**Linux / macOS:**

```bash
cd rf-testing-plugin
chmod +x install.sh
./install.sh
```

**Windows:**

```cmd
cd rf-testing-plugin
install.bat
```

安装脚本将自动完成：
- ✓ Python 3.7.16+ 环境智能检测（支持 conda、venv、多版本系统 Python）
- ✓ Python 环境优先选择（推荐最接近 3.7.16+ 的版本）
- ✓ site-packages 目录自动检测和选择
- ✓ Robot Framework 3.2.2 安装
- ✓ 基础依赖安装（pandas, openpyxl）
- ✓ JLTestLibrary 自动安装到正确位置
- ✓ 环境变量和 MCP 服务器一键配置
- ✓ 验证安装

### 方法3：手动安装

```bash
# 进入插件目录
cd rf-testing-plugin

# 安装 Python 依赖
pip install -r requirements.txt

# 验证安装
python -c "import pandas, openpyxl, robotframework; print('所有依赖安装成功！')"
```

## Python 环境智能检测

安装脚本会自动检测系统中所有符合条件的 Python 环境（3.7.16+），包括：

- **Conda 环境**：自动检测所有 conda 环境，标记当前激活环境
- **系统 Python**：检测系统中安装的多个 Python 版本
- **虚拟环境（venv）**：检测当前激活的虚拟环境

### 优先级选择策略

脚本会按以下优先级自动推荐 Python 环境：

1. 当前激活的 conda 环境
2. 匹配 Python 3.7.x 的 conda 环境（最接近要求版本）
3. 匹配 Python 3.8.x 的系统 Python
4. 其他符合条件的 Python 版本

### 用户选择流程

```
1. 运行安装脚本
   ./install.sh  # 或 install.bat

2. 显示所有检测到的 Python 环境

   检测到以下 Python 环境：

   [推荐] 1. conda: rf-env (3.7.18)  [当前激活]
          2. conda: py37 (3.7.16)
          3. system: /usr/bin/python3.8 (3.8.10)

3. 用户确认或选择
   → 按回车使用推荐，或输入编号选择其他

4. 自动检测 site-packages 目录

   检测到 site-packages 目录：

   [推荐] 1. D:\...\python37\Lib\site-packages
          [JLTestLibrary 已存在]
          2. D:\...\Anaconda3\Lib\site-packages

5. 自动安装 JLTestLibrary 到选定目录
```

### 手动指定 Python

如果需要使用特定 Python，可以在运行脚本前设置环境变量：

```bash
# Linux/macOS
export RF_PYTHON_PATH=/path/to/python3

# Windows
set RF_PYTHON_PATH=C:\path\to\python.exe
```

## 环境变量配置

### 一键配置（推荐）

使用安装脚本时，脚本会引导完成环境变量和 MCP 服务器的配置：

```bash
# 运行安装脚本后，脚本会询问
./install.sh  # Linux/macOS
install.bat   # Windows

# 按提示输入配置信息即可
```

脚本会自动：
1. 检测 Shell/环境类型
2. 收集 TAPD_ACCESS_TOKEN（必需）
3. 收集 GitLab 配置（可选）
4. 写入环境变量到系统配置
5. 创建 Claude MCP 服务器配置文件
6. 提供验证反馈

### 必需环境变量

```bash
export TAPD_ACCESS_TOKEN="your-tapd-token"
```

### 可选环境变量（GitLab/GitHub/YAPI 支持）

```bash
# GitLab
export GITLAB_API_URL="https://gitlab.example.com/api/v4"
export GITLAB_PERSONAL_ACCESS_TOKEN="your-gitlab-token"

# GitHub
export GITHUB_TOKEN="your-github-token"

# YAPI
export YAPI_TOKEN="project_id:project_token"
```

### 手动配置详情

**Linux/macOS:**

```bash
# 编辑 ~/.bashrc 或 ~/.zshrc
nano ~/.bashrc

# 添加以下内容
export TAPD_ACCESS_TOKEN="your-tapd-token"
export GITLAB_API_URL="https://gitlab.example.com/api/v4"
export GITLAB_PERSONAL_ACCESS_TOKEN="your-gitlab-token"
export GITHUB_TOKEN="your-github-token"
export YAPI_TOKEN="project_id:project_token"

# 使配置生效
source ~/.bashrc
```

**Windows:**

1. 右键"此电脑" → 属性 → 高级系统设置 → 环境变量
2. 在"用户变量"中点击"新建"
3. 添加变量名和值
4. 重启终端或 Claude

## Python 依赖

**版本要求：**
- Python 3.7.16+
**Robot Framework 版本：**
- Robot Framework 3.2.2

### 基础依赖

```bash
pip install pandas>=2.0.0 openpyxl>=3.1.0 robotframework==3.2.2
```

### 自定义库安装

**安装方式：**

JLTestLibrary 的安装现在由安装脚本自动处理：

1. 脚本会自动检测选定 Python 的 site-packages 目录
2. 显示所有可用的 site-packages 目录供选择
3. 自动解压 JLTestLibrary.zip 到目标目录
4. 验证安装结果

**手动安装（如需）：**

```bash
# 解压到 Python site-packages 目录
unzip 03-scripts/JLTestLibrary.zip -d $HOME/Library/Python/3.7/site-packages/

# Windows 系统
unzip 03-scripts/JLTestLibrary.zip -d %USERPROFILE%\AppData\Local\Programs\Python\Python37\Lib\site-packages\
```

**安装验证：**

```bash
# 使用选定的 Python 验证
python -c "import JLTestLibrary; print('JLTestLibrary 安装成功')"
```

## Python 依赖

### 1. 配置环境变量和 MCP（推荐）

使用安装脚本一键配置：

```bash
# 安装时配置
./install.sh  # Linux/macOS
install.bat   # Windows

# 按提示输入配置信息
```

脚本会自动：
- 写入环境变量到系统配置（~/.bashrc 或 Windows 环境变量）
- 创建 Claude MCP 配置文件（~/.claude/mcp.json）
- 配置 TAPD 和 GitLab MCP 服务器

### 2. 配置插件（已通过 marketplace 安装可跳过）

编辑 `~/.claude/settings.json`，添加 skills 引用：

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

### 3. 配置 MCP（已通过安装脚本配置可跳过）

**安装脚本自动配置：**

脚本会自动创建 `~/.claude/mcp.json` 文件，包含以下配置：

```json
{
  "mcpServers": {
    "tapd": {
      "command": "uvx",
      "args": ["mcp-server-tapd"],
      "env": {
        "TAPD_ACCESS_TOKEN": "${TAPD_ACCESS_TOKEN}",
        "TAPD_API_BASE_URL": "https://api.tapd.cn",
        "TAPD_BASE_URL": "https://www.tapd.cn",
        "BOT_URL": ""
      }
    },
    "gitlab": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-gitlab"],
      "env": {
        "GITLAB_API_URL": "${GITLAB_API_URL}",
        "GITLAB_PERSONAL_ACCESS_TOKEN": "${GITLAB_PERSONAL_ACCESS_TOKEN}"
      }
    }
  }
}
```

**手动配置检查：**
```bash
# 检查 MCP 服务器状态
claude mcp list
```

### 3. 验证安装

```bash
# 验证插件安装
/rf-testing:start

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
│       │   ├── RF 关键字编写规范.md
│       │   ├── JSONPath 使用指南.md
│       │   ├── BuiltIn 库使用规范.md
│       │   ├── DateTime 库使用规范.md
│       │   └── business/     # 业务规则目录
│       │       └── 商户系统业务规范.md
│       └── templates/       # 模板文件
├── 01-RF-Skills/          # RF 技能
├── 02-agents/             # 测试 agents
│   ├── testing-rf-quality-assurance.md
│   ├── testing-code-analyzer.md
│   ├── testing-change-detector.md
│   └── testing-results-analyzer.md
├── 03-scripts/            # 实用脚本和资源
│   ├── JLTestLibrary.zip  # Robot Framework 自定义测试库
│   ├── robot2tapd.py
│   └── batch_convert.sh
├── 04-cases/              # 使用案例
├── 05-plugins/            # 插件目录
│   └── rf-testing/        # rf-testing 插件
│       ├── workflows/     # 工作流定义
│       ├── commands/      # 入口命令
│       ├── .mcp.json      # MCP 配置
│       └── README.md
├── docs/                  # 文档
├── .claude-plugin/        # Plugin 元数据
│   └── marketplace.json   # Marketplace 配置
├── requirements.txt       # Python 依赖
└── README.md              # 插件说明
```

## 使用方式

### 完整测试流程

```text
/rf-testing:start <tapd-link>
```

### 子工作流

```text
/rf-testing:requirement-to-rf <tapd-link>
/rf-testing:rf-to-tapd <robot-file-path>
```

## 规范文档结构

| 文档 | 说明 | 位置 |
|------|------|------|
| RF 关键字编写规范.md | 全局通用规范，包含用例编写风格、变量管理、错误处理等 | 00-JL-Skills/jl-skills/specs/ |
| JSONPath 使用指南.md | JSONPath 语法和示例 | 00-JL-Skills/jl-skills/specs/ |
| BuiltIn 库使用规范.md | BuiltIn 库关键字说明 | 00-JL-Skills/jl-skills/specs/ |
| DateTime 库使用规范.md | DateTime 库使用说明 | 00-JL-Skills/jl-skills/specs/ |
| 商户系统业务规范.md | 商户系统业务模式索引和详细内容 | 00-JL-Skills/jl-skills/specs/business/ |

## MCP 服务器

插件配置了以下 MCP 服务器：

| 服务器 | 用途 | 配置位置 |
|--------|------|----------|
| tapd | TAPD 需求获取和用例导出 | 05-plugins/rf-testing/.mcp.json |
| gitlab | GitLab 代码获取（可选） | 05-plugins/rf-testing/.mcp.json |
| github | GitHub 代码获取（可选） | 05-plugins/rf-testing/.mcp.json |
| yapi-auto-mcp | YAPI 接口文档获取（可选） | 05-plugins/rf-testing/.mcp.json |

## 卸载

### 卸载 Claude 插件

```bash
# 通过 Claude 插件管理器卸载
/plugin uninstall rf-testing
```

### 卸载 Python 依赖

```bash
pip uninstall pandas openpyxl robotframework
```

## 故障排除

### 问题1：插件未加载

**解决方案**：
- 确认已通过 marketplace 安装
- 检查 marketplace 配置
- 重启 Claude

### 问题2：MCP 连接失败

**解决方案**：
- 检查环境变量配置
- 确认 TAPD_ACCESS_TOKEN 已设置
- 检查网络连接
- 查看 Claude 日志

### 问题3：脚本执行失败

**解决方案**：
- 检查 Python 版本（需要 3.7.16+）
- 重新安装依赖
- 检查文件权限

### 问题4：自定义库安装失败

**解决方案**：
- 确认 JLTestLibrary.zip 位于 `03-scripts/` 目录
- 检查目标目录权限
- 验证解压路径

### 问题5：规范文档不更新

**解决方案**：
- 参考规范文档：`00-JL-Skills/jl-skills/specs/`
- 业务规则索引：`00-JL-Skills/jl-skills/specs/business/`
- 全局规范：`RF 关键字编写规范.md`