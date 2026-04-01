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

REM 检查 Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装，请先安装 Python 3.10+
    exit /b 1
)

REM 检查 Python 版本
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo [INFO] Python 版本: %PYTHON_VERSION%

REM 检查 pip
where pip >nul 2>&1
if errorlevel 1 (
    echo [ERROR] pip 未安装
    exit /b 1
)

REM 检查 git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git 未安装，请先安装 git
    exit /b 1
)

REM 安装 Python 依赖
echo [INFO] 安装 Python 依赖...
pip show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 pandas...
    pip install pandas
) else (
    echo [INFO] pandas 已安装
)

pip show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 openpyxl...
    pip install openpyxl
) else (
    echo [INFO] openpyxl 已安装
)

pip show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] 安装 robotframework...
    pip install robotframework
) else (
    echo [INFO] robotframework 已安装
)

echo [INFO] Python 依赖安装完成
echo.

REM 克隆插件仓库
echo [INFO] 克隆插件仓库...

if exist "%PLUGIN_DIR%" (
    echo [WARN] 插件目录已存在: %PLUGIN_DIR%
    set /p "REPLY=是否删除并重新克隆？(y/n): "
    if /i "!REPLY!"=="y" (
        rmdir /s /q "%PLUGIN_DIR%"
    ) else (
        echo [INFO] 跳过克隆步骤
        goto configure_skills
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

:configure_skills
REM 配置 Claude Skills
echo [INFO] 配置 Claude Skills...

set SETTINGS_FILE=%USERPROFILE%\.claude\settings.json

REM 创建技能配置 JSON
set SKILL_CONFIG={"name": "rf-test", "path": "!PLUGIN_DIR!\01-RF-Skills\skills\test\SKILL.md"}, {"name": "rf-standards-check", "path": "!PLUGIN_DIR!\01-RF-Skills\skills\rf-standards-check\SKILL.md"}, {"name": "rf-tapd-conversion", "path": "!PLUGIN_DIR!\01-RF-Skills\skills\tapd-conversion\SKILL.md"}

if exist "%SETTINGS_FILE%" (
    echo [WARN] settings.json 已存在
    echo [WARN] 请手动添加以下技能配置到 settings.json 的 skills 数组中：
    echo.
    echo   {
    echo     "name": "rf-test",
    echo     "path": "%PLUGIN_DIR%\01-RF-Skills\skills\test\SKILL.md"
    echo   },
    echo   {
    echo     "name": "rf-standards-check",
    echo     "path": "%PLUGIN_DIR%\01-RF-Skills\skills\rf-standards-check\SKILL.md"
    echo   },
    echo   {
    echo     "name": "rf-tapd-conversion",
    echo     "path": "%PLUGIN_DIR%\01-RF-Skills\skills\tapd-conversion\SKILL.md"
    echo   }
    echo.
    echo [WARN] 配置后请重启 Claude Code
) else (
    REM 创建新的 settings.json
    (
        echo {
        echo   "skills": [
        echo     {
        echo       "name": "rf-test",
        echo       "path": "%PLUGIN_DIR%\01-RF-Skills\skills\test\SKILL.md"
        echo     },
        echo     {
        echo       "name": "rf-standards-check",
        echo       "path": "%PLUGIN_DIR%\01-RF-Skills\skills\rf-standards-check\SKILL.md"
        echo     },
        echo     {
        echo       "name": "rf-tapd-conversion",
        echo       "path": "%PLUGIN_DIR%\01-RF-Skills\skills\tapd-conversion\SKILL.md"
        echo     }
        echo   ]
        echo }
    ) > "%SETTINGS_FILE%"

    echo [INFO] settings.json 已创建
)

echo.

REM 验证安装
echo [INFO] 验证安装...

if not exist "%PLUGIN_DIR%" (
    echo [ERROR] 插件目录不存在: %PLUGIN_DIR%
    goto failed
)

REM 检查技能文件
set SKILL_FILES[0]=%PLUGIN_DIR%\01-RF-Skills\skills\test\SKILL.md
set SKILL_FILES[1]=%PLUGIN_DIR%\01-RF-Skills\skills\rf-standards-check\SKILL.md
set SKILL_FILES[2]=%PLUGIN_DIR%\01-RF-Skills\skills\tapd-conversion\SKILL.md

for /L %%i in (0,1,2) do (
    if exist "!SKILL_FILES[%%i]!" (
        echo [INFO] 技能文件存在: %%~nxi!SKILL_FILES[%%i]!
    ) else (
        echo [ERROR] 技能文件不存在: !SKILL_FILES[%%i]!
        goto failed
    )
)

REM 检查 Python 依赖
python -c "import pandas, openpyxl, robotframework" >nul 2>&1
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
echo 可用技能:
echo   /rf-test              - 完整测试流程
echo   /rf-standards-check   - RF 规范检查
echo   /rf-tapd-conversion   - RF 转 TAPD
echo.
echo 使用方式:
echo   1. 重启 Claude Code
echo   2. 在对话框中输入技能命令
echo.
echo 注意事项:
echo   - 确保 TAPD MCP Server 已配置
echo   - 首次使用需要提供 TAPD 需求链接
echo.

echo [INFO] 安装成功！
exit /b 0

:failed
echo [ERROR] 安装验证失败，请检查上述错误
exit /b 1
