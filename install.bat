@echo off
REM RF Testing Plugin 一键安装脚本 (Windows)
REM 用途: 自动安装和配置 rf-testing-plugin

setlocal enabledelayedexpansion

REM 插件配置
set PLUGIN_NAME=rf-testing-plugin
set PLUGIN_REPO=https://github.com/JoeyTrribbiani/rf-testing-plugin.git
set PLUGIN_DIR=%USERPROFILE%\.claude\plugins\%PLUGIN_NAME%

echo [INFO] 开始安装 %PLUGIN_NAME%...
echo.

REM 调用 Python 环境检测
call :DetectPythonEnvironment

REM 检查 git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git 未安装，请先安装 git
    exit /b 1
)

REM 克隆插件仓库
echo [INFO] 克隆插件仓库...

if exist "%PLUGIN_DIR%" (
    echo [WARN] 插件目录已存在: %PLUGIN_DIR%
    set /p "REPLY=是否删除并重新克隆？(y/n): "
    if /i "!REPLY!"=="y" (
        rmdir /s /q "%PLUGIN_DIR%"
    ) else (
        echo [INFO] 跳过克隆步骤
        goto install_deps
    )
)

if not exist "%USERPROFILE%\.claude\plugins\" (
    mkdir "%USERPROFILE%\.claude\plugins\"
)

git clone "%PLUGIN_REPO%" "%PLUGIN_DIR%"
if errorlevel 1 (
    echo [ERROR] 克隆失败，请检查网络连接和仓库地址
    exit /b 1
)

echo [INFO] 插件克隆完成: %PLUGIN_DIR%
echo.

:install_deps
REM 安装 Python 依赖
call :InstallDependencies

REM 安装 JLTestLibrary
call :InstallJLTestLibrary

REM 配置 Claude Skills（已弃用，使用 marketplace）
echo [INFO] 提示：新版本推荐通过 marketplace 安装插件
echo [INFO] 在 Claude Code 中执行：
echo   /plugin marketplace add .
echo   /plugin install rf-testing
echo.

REM 一键配置环境变量和 MCP
echo.
echo ========================================
echo   配置环境变量和 MCP 服务器
echo ========================================
echo.
set /p DO_CONFIG=是否现在配置环境变量和 MCP 服务器？(y/n):
if /i not "%DO_CONFIG%"=="y" goto verify_install

REM 收集 TAPD 配置
echo.
echo [1/4] 配置 TAPD 访问令牌
echo ----------------------------------------
set /p TAPD_TOKEN=请输入 TAPD_ACCESS_TOKEN:

if "%TAPD_TOKEN%"=="" (
    echo [WARN] TAPD_ACCESS_TOKEN 不能为空
    echo [WARN] 可以稍后手动配置，跳过此步骤
    set /p SKIP_CONFIG=是否跳过配置？(y/n):
    if /i "%SKIP_CONFIG%"=="y" goto verify_install
)

REM 收集 GitLab 配置（可选）
echo.
echo [2/4] 配置 GitLab（可选，按 Enter 跳过）
echo ----------------------------------------
set /p GITLAB_URL=请输入 GITLAB_API_URL（默认：https://gitlab.jlpay.com/api/v4）:
if "%GITLAB_URL%"=="" set GITLAB_URL=https://gitlab.jlpay.com/api/v4

set /p GITLAB_TOKEN=请输入 GITLAB_PERSONAL_ACCESS_TOKEN（可选）:

REM 写入环境变量（用户级别）
echo.
echo [3/4] 写入系统环境变量...
setx TAPD_ACCESS_TOKEN "%TAPD_TOKEN%" >nul
setx GITLAB_API_URL "%GITLAB_URL%" >nul
if not "%GITLAB_TOKEN%"=="" setx GITLAB_PERSONAL_ACCESS_TOKEN "%GITLAB_TOKEN%" >nul
echo [INFO] 环境变量已写入系统

REM 创建 MCP 配置
echo.
echo [4/4] 配置 Claude MCP 服务器...
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
set MCP_FILE=%CLAUDE_CONFIG_DIR%\mcp.json

REM 创建目录
if not exist "%CLAUDE_CONFIG_DIR%" mkdir "%CLAUDE_CONFIG_DIR%"

REM 构建 JSON 配置（使用临时文件）
set JSON_TEMP=%TEMP%\mcp_config.json

echo {> "%JSON_TEMP%"
echo   "mcpServers": {>> "%JSON_TEMP%"
echo     "tapd": {>> "%JSON_TEMP%"
echo       "command": "uvx",>> "%JSON_TEMP%"
echo       "args": ["mcp-server-tapd"],>> "%JSON_TEMP%"
echo       "env": {>> "%JSON_TEMP%"
echo         "TAPD_ACCESS_TOKEN": "%TAPD_TOKEN%",>> "%JSON_TEMP%"
echo         "TAPD_API_BASE_URL": "https://api.tapd.cn",>> "%JSON_TEMP%"
echo         "TAPD_BASE_URL": "https://www.tapd.cn",>> "%JSON_TEMP%"
echo         "BOT_URL": "">> "%JSON_TEMP%"
echo       }>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
if not "%GITLAB_TOKEN%"=="" (
echo     ,>> "%JSON_TEMP%"
echo     "gitlab": {>> "%JSON_TEMP%"
echo       "command": "cmd",>> "%JSON_TEMP%"
echo       "args": ["/c", "npx", "-y", "@modelcontextprotocol/server-gitlab"],>> "%JSON_TEMP%"
echo       "env": {>> "%JSON_TEMP%"
echo         "GITLAB_API_URL": "%GITLAB_URL%",>> "%JSON_TEMP%"
echo         "GITLAB_PERSONAL_ACCESS_TOKEN": "%GITLAB_TOKEN%">> "%JSON_TEMP%"
echo       }>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
)
echo   }>> "%JSON_TEMP%"
echo }>> "%JSON_TEMP%"

move "%JSON_TEMP%" "%MCP_FILE%" >nul
echo [INFO] MCP 配置已写入: %MCP_FILE%

echo.
echo ========================================
echo [验证] 配置完成
echo ========================================
echo.
echo [INFO] 环境变量已写入系统环境变量
echo [INFO] MCP 配置已写入: %MCP_FILE%
echo.
echo [WARN] 需要重启终端或 Claude 才能生效
echo.

REM 验证安装
echo [INFO] 验证安装...

if not exist "%PLUGIN_DIR%" (
    echo [ERROR] 插件目录不存在: %PLUGIN_DIR%
    goto failed
)

REM 检查插件文件
set PLUGIN_FILES[0]=%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json
set PLUGIN_FILES[1]=%PLUGIN_DIR%\05-plugins\rf-testing\.claude-plugin\plugin.json
set PLUGIN_FILES[2]=%PLUGIN_DIR%\05-plugins\rf-testing\commands\start.md

for /L %%i in (0,1,2) do (
    if exist "!PLUGIN_FILES[%%i]!" (
        echo [INFO] 插件文件存在: %%~nxi!PLUGIN_FILES[%%i]!
    ) else (
        echo [WARN] 插件文件不存在: !PLUGIN_FILES[%%i]!
    )
)

REM 检查 Python 依赖（使用检测到的 Python）
"%PYTHON_CMD%" -c "import pandas, openpyxl, robotframework" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 依赖验证失败
    goto failed
)

echo [INFO] Python 依赖验证通过
echo.

REM 打印使用说明
echo ==================================
echo   安装完成！
echo ==================================
echo.
echo 插件路径: %PLUGIN_DIR%
echo.
echo 推荐安装方式（marketplace）:
echo   1. 进入插件目录:
echo      cd %PLUGIN_DIR%
echo   2. 在 Claude Code 中执行:
echo      /plugin marketplace add .
echo      /plugin install rf-testing
echo.
echo 可用命令:
echo   /rf-testing:start [tapd-link]  - 完整测试流程
echo.
echo 子工作流:
echo   /rf-testing:requirement-to-rf  - 仅需求转用例
echo   /rf-testing:rf-to-tapd       - 仅 RF 转 TAPD
echo.
echo 环境变量配置:
echo   TAPD_ACCESS_TOKEN=your-tapd-token (必需)
echo   GITLAB_API_URL=https://gitlab.example.com/api/v4 (可选)
echo   GITLAB_PERSONAL_ACCESS_TOKEN=your-gitlab-token (可选)
echo.
echo 使用方式:
echo   1. 配置环境变量
echo   2. 重启 Claude Code
echo   3. 执行: /rf-testing:start
echo.
echo 注意事项:
echo   - 确保 TAPD_ACCESS_TOKEN 已配置
echo   - 首次使用需要提供 TAPD 需求链接
echo   - RF 质量保证 Agent 会自动检查用例质量
echo.

echo [INFO] 安装成功！
exit /b 0

:failed
echo [ERROR] 安装验证失败，请检查上述错误
exit /b 1

REM 检查 Python 环境（更新）
:DetectPythonEnvironment
echo [INFO] 检测 Python 环境...

REM 调用 Python 检测模块
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json > "%TEMP%\env_detection.json" 2>nul

if errorlevel 1 (
    echo [ERROR] Python 环境检测失败
    echo [INFO] 请确保 Python 3.7.16+ 已安装
    exit /b 1
)

REM 显示检测结果
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py"
echo.

REM 获取用户选择
set /p "PYTHON_CHOICE=请选择目标 Python 环境 [默认=1]: "
if "%PYTHON_CHOICE%"=="" set PYTHON_CHOICE=1

REM 解析选择的 Python 路径
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['python_path'] if len(data) >= %PYTHON_CHOICE% else '')"') do set SELECTED_PYTHON=%%p

if "%SELECTED_PYTHON%"=="" (
    echo [ERROR] 无效的选择
    exit /b 1
)

REM 获取版本信息
for /f "tokens=*" %%v in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['version'])"') do set PYTHON_VERSION=%%v

echo [INFO] 已选择: Python %PYTHON_VERSION%
echo [INFO] 路径: %SELECTED_PYTHON%
echo.

REM 设置 Python 和 pip 命令
set PYTHON_CMD=%SELECTED_PYTHON%
for /f "tokens=*" %%i in ('python -c "import os; print(os.path.join(os.path.dirname(r'%SELECTED_PYTHON%'), 'pip'))"') do set PIP_CMD=%%i
if not exist "%PIP_CMD%" set PIP_CMD=pip

goto :eof

REM 安装依赖函数
:InstallDependencies
echo [INFO] 安装 Python 依赖...

REM 检查 pandas
"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas 已安装
)

REM 检查 openpyxl
"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl 已安装
)

REM 检查 robotframework
"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework 已安装
)

echo [INFO] Python 依赖安装完成
echo.
goto :eof

REM 安装 JLTestLibrary 函数
:InstallJLTestLibrary
echo [INFO] 安装 JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip 不存在，跳过安装
    goto :eof
)

REM 检测 site-packages 目录
echo [INFO] 检测 site-packages 目录...
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --format json > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] 无法自动检测 site-packages 目录，跳过安装
    goto :eof
)

REM 显示选项
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages
echo.

set /p "SP_CHOICE=请选择目标目录 [默认=1]: "
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM 解析路径
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\site_packages.json', encoding='utf-8')); print(data['site_packages'][%SP_CHOICE% - 1])"') do set TARGET_DIR=%%p

if "%TARGET_DIR%"=="" (
    echo [WARN] 无效的选择，跳过安装
    goto :eof
)

REM 检查已安装
if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary 已存在，跳过安装
    goto :eof
)

REM 解压
echo [INFO] 解压到: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] 解压失败，请检查权限
    goto :eof
)

REM 验证
"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] 验证失败
) else (
    echo [INFO] JLTestLibrary 安装成功
)

echo.
goto :eof