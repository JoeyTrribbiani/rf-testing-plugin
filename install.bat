@echo off
setlocal enabledelayedexpansion

REM 插件配置
set PLUGIN_NAME=rf-testing-plugin
set PLUGIN_REPO=https://github.com/JoeyTrribbiani/rf-testing-plugin.git
set PLUGIN_DIR=%USERPROFILE%\.claude\plugins\%PLUGIN_NAME%

echo [INFO] 开始安装 %PLUGIN_NAME%...
echo.

REM 检查 Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装，请先安装 Python 3.7.16+
    exit /b 1
)

REM 检查 git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git 未安装，请先安装 git
    exit /b 1
)

REM 克隆插件仓库
echo [INFO] 克隆插件仓库...

if exist "%PLUGIN_DIR%" (
    echo [WARN] 插件目录已存在
    set /p REPLY=是否删除并重新克隆？输入 y 或 n:
    if /i "!REPLY!"=="y" (
        rmdir /s /q "%PLUGIN_DIR%"
    ) else (
        echo [INFO] 跳过克隆步骤
        goto detect_python
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

echo [INFO] 插件克隆完成
echo.

:detect_python
REM 检测 Python 环境
echo [INFO] 检测 Python 环境...

python "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json > "%TEMP%\env_detection.json" 2>nul

if errorlevel 1 (
    echo [ERROR] Python 环境检测失败
    echo [INFO] 使用系统 Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py"
echo.

set /p PYTHON_CHOICE=请选择目标 Python 环境，按回车使用默认值 1:
if "%PYTHON_CHOICE%"=="" set PYTHON_CHOICE=1

REM 使用临时 Python 脚本解析 JSON
echo import json > "%TEMP%\parse_env.py"
echo data = json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')) >> "%TEMP%\parse_env.py"
echo index = %PYTHON_CHOICE% - 1 >> "%TEMP%\parse_env.py"
echo if len(data) > index: >> "%TEMP%\parse_env.py"
echo     print(data[index]['python_path']) >> "%TEMP%\parse_env.py"

for /f "tokens=*" %%p in ('python "%TEMP%\parse_env.py"') do set SELECTED_PYTHON=%%p

if "%SELECTED_PYTHON%"=="" (
    echo [ERROR] 无效的选择
    echo [INFO] 使用系统 Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

REM 解析版本
echo import json > "%TEMP%\parse_version.py"
echo data = json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')) >> "%TEMP%\parse_version.py"
echo index = %PYTHON_CHOICE% - 1 >> "%TEMP%\parse_version.py"
echo if len(data) > index: >> "%TEMP%\parse_version.py"
echo     print(data[index]['version']) >> "%TEMP%\parse_version.py"

for /f "tokens=*" %%v in ('python "%TEMP%\parse_version.py"') do set PYTHON_VERSION=%%v

echo [INFO] 已选择: Python %PYTHON_VERSION%
echo [INFO] 路径: %SELECTED_PYTHON%
echo.

set PYTHON_CMD=%SELECTED_PYTHON%

REM 查找 pip
echo import os > "%TEMP%\find_pip.py"
echo python_path = r'%SELECTED_PYTHON%' >> "%TEMP%\find_pip.py"
echo python_dir = os.path.dirname(python_path) >> "%TEMP%\find_pip.py"
echo pip_path = os.path.join(python_dir, 'pip.exe') >> "%TEMP%\find_pip.py"
echo if os.path.exists(pip_path): >> "%TEMP%\find_pip.py"
echo     print(pip_path) >> "%TEMP%\find_pip.py"
echo else: >> "%TEMP%\find_pip.py"
echo     print('pip') >> "%TEMP%\find_pip.py"

for /f "tokens=*" %%i in ('python "%TEMP%\find_pip.py"') do set PIP_CMD=%%i

:install_deps
REM 安装 Python 依赖
echo [INFO] 安装 Python 依赖...

"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas 已安装
)

"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl 已安装
)

"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework 已安装
)

echo [INFO] Python 依赖安装完成
echo.

:install_jl
REM 安装 JLTestLibrary
echo [INFO] 安装 JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip 不存在，跳过安装
    goto configure_mcp
)

echo [INFO] 检测 site-packages 目录...
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --format json > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] 无法自动检测 site-packages 目录，跳过安装
    goto configure_mcp
)

echo.
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages
echo.

set /p SP_CHOICE=请选择目标目录，按回车使用默认值 1:
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM 解析 site-packages 路径
echo import json > "%TEMP%\parse_sp.py"
echo data = json.load(open(r'%TEMP%\site_packages.json', encoding='utf-8')) >> "%TEMP%\parse_sp.py"
echo index = %SP_CHOICE% - 1 >> "%TEMP%\parse_sp.py"
echo if 'site_packages' in data and len(data['site_packages']) > index: >> "%TEMP%\parse_sp.py"
echo     print(data['site_packages'][index]) >> "%TEMP%\parse_sp.py"

for /f "tokens=*" %%p in ('python "%TEMP%\parse_sp.py"') do set TARGET_DIR=%%p

if "%TARGET_DIR%"=="" (
    echo [WARN] 无效的选择，跳过安装
    goto configure_mcp
)

if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary 已存在，跳过安装
    goto configure_mcp
)

echo [INFO] 解压到: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] 解压失败，请检查权限
    goto configure_mcp
)

"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] 验证失败
) else (
    echo [INFO] JLTestLibrary 安装成功
)

echo.

:configure_mcp
echo [INFO] 提示：推荐通过 marketplace 安装插件
echo [INFO] 在 Claude Code 中执行：
echo   /plugin marketplace add .
echo   /plugin install rf-testing
echo.

REM 配置环境变量和 MCP
echo.
echo 配置环境变量和 MCP 服务器
echo.
set /p DO_CONFIG=是否现在配置？输入 y 或 n，按回车跳过:
if /i not "%DO_CONFIG%"=="y" goto verify_install

REM 收集 TAPD 配置
echo.
echo 配置 TAPD 访问令牌
echo 获取令牌: https://www.tapd.cn/personal_settings/index?tab=personal_token
set /p TAPD_TOKEN=请输入 TAPD_ACCESS_TOKEN:

if "%TAPD_TOKEN%"=="" (
    echo [WARN] 令牌不能为空
    set /p SKIP_CONFIG=是否跳过配置？输入 y 或 n:
    if /i "%SKIP_CONFIG%"=="y" goto verify_install
)

REM 收集 GitLab 配置
echo.
echo 配置 GitLab（可选，按回车跳过）
echo 获取令牌: https://gitlab.jlpay.com/-/user_settings/personal_access_tokens
set /p GITLAB_URL=请输入 GITLAB_API_URL，按回车使用默认值:
if "%GITLAB_URL%"=="" set GITLAB_URL=https://gitlab.jlpay.com/api/v4

set /p GITLAB_TOKEN=请输入 GITLAB_TOKEN，可选按回车跳过:

REM 写入环境变量
echo.
echo 写入系统环境变量...
setx TAPD_ACCESS_TOKEN "%TAPD_TOKEN%" >nul
setx GITLAB_API_URL "%GITLAB_URL%" >nul
if not "%GITLAB_TOKEN%"=="" setx GITLAB_PERSONAL_ACCESS_TOKEN "%GITLAB_TOKEN%" >nul
echo [INFO] 环境变量已写入系统

REM 创建 MCP 配置
echo.
echo 配置 Claude MCP 服务器...
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
set MCP_FILE=%CLAUDE_CONFIG_DIR%\mcp.json

if not exist "%CLAUDE_CONFIG_DIR%" mkdir "%CLAUDE_CONFIG_DIR%"

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
echo [INFO] MCP 配置已写入

echo.
echo 配置完成
echo.
echo [WARN] 需要重启终端或 Claude 才能生效
echo.

:verify_install
echo [INFO] 验证安装...

if not exist "%PLUGIN_DIR%" (
    echo [ERROR] 插件目录不存在
    goto failed
)

set PLUGIN_FILES[0]=%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json
set PLUGIN_FILES[1]=%PLUGIN_DIR%\05-plugins\rf-testing\.claude-plugin\plugin.json
set PLUGIN_FILES[2]=%PLUGIN_DIR%\05-plugins\rf-testing\commands\start.md

for /L %%i in (0,1,2) do (
    if exist "!PLUGIN_FILES[%%i]!" (
        echo [INFO] 文件存在: %%~nxi!PLUGIN_FILES[%%i]!
    ) else (
        echo [WARN] 文件不存在: !PLUGIN_FILES[%%i]!
    )
)

"%PYTHON_CMD%" -c "import pandas, openpyxl, robotframework" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 依赖验证失败
    goto failed
)

echo [INFO] Python 依赖验证通过
echo.

echo 安装完成
echo.
echo 插件路径: %PLUGIN_DIR%
echo.
echo 可用命令:
echo   /rf-testing:start - 完整测试流程
echo.
echo 环境变量:
echo   TAPD_ACCESS_TOKEN - 必需
echo   GITLAB_API_URL - 可选
echo   GITLAB_PERSONAL_ACCESS_TOKEN - 可选
echo.

echo [INFO] 安装成功
exit /b 0

:failed
echo [ERROR] 安装验证失败
exit /b 1