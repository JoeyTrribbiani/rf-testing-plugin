@echo off
chcp 65001 >nul
REM RF Testing Plugin one-click installation script (Windows)
REM Purpose: Automatically install and configure rf-testing-plugin

setlocal enabledelayedexpansion

REM Plugin configuration
set PLUGIN_NAME=rf-testing-plugin
set PLUGIN_REPO=https://github.com/JoeyTrribbiani/rf-testing-plugin.git
set PLUGIN_DIR=%USERPROFILE%\.claude\plugins\%PLUGIN_NAME%

echo [INFO] Start installing %PLUGIN_NAME%...
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed, please install Python 3.7.16+ first
    exit /b 1
)

REM Check git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git is not installed, please install git first
    exit /b 1
)

REM Clone plugin repository
echo [INFO] Cloning plugin repository...

if exist "%PLUGIN_DIR%" (
    echo [WARN] Plugin directory already exists: %PLUGIN_DIR%
    set /p "REPLY=Delete and re-clone? (y/n): "
    if /i "!REPLY!"=="y" (
        rmdir /s /q "%PLUGIN_DIR%"
    ) else (
        echo [INFO] Skip cloning step
        goto detect_python
    )
)

if not exist "%USERPROFILE%\.claude\plugins\" (
    mkdir "%USERPROFILE%\.claude\plugins\"
)

git clone "%PLUGIN_REPO%" "%PLUGIN_DIR%"
if errorlevel 1 (
    echo [ERROR] Clone failed, please check network connection and repository URL
    exit /b 1
)

echo [INFO] Plugin cloned: %PLUGIN_DIR%
echo.

:detect_python
REM Detect Python environment
echo [INFO] Detecting Python environment...

REM Call Python detection module
python "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json > "%TEMP%\env_detection.json" 2>nul

if errorlevel 1 (
    echo [ERROR] Python environment detection failed
    echo [INFO] Using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

REM Show detection results
echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py"
echo.

REM Get user choice
set /p "PYTHON_CHOICE=Select target Python environment [default=1]: "
if "%PYTHON_CHOICE%"=="" set PYTHON_CHOICE=1

REM Parse selected Python path
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['python_path'] if len(data) >= %PYTHON_CHOICE% else '')"') do set SELECTED_PYTHON=%%p

if "%SELECTED_PYTHON%"=="" (
    echo [ERROR] Invalid selection
    echo [INFO] Using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

REM Get version info
for /f "tokens=*" %%v in ('python -c "import json; data=json.load(open(r'%TEMP%\env_detection.json', encoding='utf-8')); print(data[%PYTHON_CHOICE% - 1]['version'])"') do set PYTHON_VERSION=%%v

echo [INFO] Selected: Python %PYTHON_VERSION%
echo [INFO] Path: %SELECTED_PYTHON%
echo.

REM Set Python and pip commands
set PYTHON_CMD=%SELECTED_PYTHON%
for /f "tokens=*" %%i in ('python -c "import os; print(os.path.join(os.path.dirname(r'%SELECTED_PYTHON%'), 'pip'))"') do set PIP_CMD=%%i
if not exist "%PIP_CMD%" set PIP_CMD=pip

:install_deps
REM Install Python dependencies
echo [INFO] Installing Python dependencies...

REM Check pandas
"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas is already installed
)

REM Check openpyxl
"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl is already installed
)

REM Check robotframework
"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework is already installed
)

echo [INFO] Python dependencies installed
echo.

:install_jl
REM Install JLTestLibrary
echo [INFO] Installing JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip not found, skip installation
    goto configure_mcp
)

REM Detect site-packages directory
echo [INFO] Detecting site-packages directory...
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --format json > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] Cannot detect site-packages directory automatically, skip installation
    goto configure_mcp
)

REM Show options
echo.
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages
echo.

set /p "SP_CHOICE=Select target directory [default=1]: "
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM Parse path
for /f "tokens=*" %%p in ('python -c "import json; data=json.load(open(r'%TEMP%\site_packages.json', encoding='utf-8')); print(data['site_packages'][%SP_CHOICE% - 1])"') do set TARGET_DIR=%%p

if "%TARGET_DIR%"=="" (
    echo [WARN] Invalid selection, skip installation
    goto configure_mcp
)

REM Check if already installed
if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary already exists, skip installation
    goto configure_mcp
)

REM Extract
echo [INFO] Extracting to: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] Extraction failed, please check permissions
    goto configure_mcp
)

REM Verify
"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Verification failed
) else (
    echo [INFO] JLTestLibrary installed successfully
)

echo.

:configure_mcp
REM Configure Claude Skills (deprecated, use marketplace)
echo [INFO] Note: New version recommends installing via marketplace
echo [INFO] Run in Claude Code:
echo   /plugin marketplace add .
echo   /plugin install rf-testing
echo.

REM Configure environment variables and MCP
echo.
echo ========================================
echo   Configure environment variables and MCP servers
echo ========================================
echo.
set /p DO_CONFIG=Configure environment variables and MCP servers now? (y/n):
if /i not "%DO_CONFIG%"=="y" goto verify_install

REM Collect TAPD configuration
echo.
echo [1/4] Configure TAPD access token
echo ----------------------------------------
set /p TAPD_TOKEN=Please enter TAPD_ACCESS_TOKEN:

if "%TAPD_TOKEN%"=="" (
    echo [WARN] TAPD_ACCESS_TOKEN cannot be empty
    echo [WARN] You can configure manually later, skip this step
    set /p SKIP_CONFIG=Skip configuration? (y/n):
    if /i "%SKIP_CONFIG%"=="y" goto verify_install
)

REM Collect GitLab configuration (optional)
echo.
echo [2/4] Configure GitLab (optional, press Enter to skip)
echo ----------------------------------------
set /p GITLAB_URL=Please enter GITLAB_API_URL (default: https://gitlab.jlpay.com/api/v4):
if "%GITLAB_URL%"=="" set GITLAB_URL=https://gitlab.jlpay.com/api/v4

set /p GITLAB_TOKEN=Please enter GITLAB_PERSONAL_ACCESS_TOKEN (optional):

REM Write environment variables (user level)
echo.
echo [3/4] Write system environment variables...
setx TAPD_ACCESS_TOKEN "%TAPD_TOKEN%" >nul
setx GITLAB_API_URL "%GITLAB_URL%" >nul
if not "%GITLAB_TOKEN%"=="" setx GITLAB_PERSONAL_ACCESS_TOKEN "%GITLAB_TOKEN%" >nul
echo [INFO] Environment variables written to system

REM Create MCP configuration
echo.
echo [4/4] Configure Claude MCP servers...
set CLAUDE_CONFIG_DIR=%USERPROFILE%\.claude
set MCP_FILE=%CLAUDE_CONFIG_DIR%\mcp.json

REM Create directory
if not exist "%CLAUDE_CONFIG_DIR%" mkdir "%CLAUDE_CONFIG_DIR%"

REM Build JSON configuration (using temporary file)
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
echo [INFO] MCP configuration written: %MCP_FILE%

echo.
echo ========================================
echo [Verify] Configuration complete
echo ========================================
echo.
echo [INFO] Environment variables written to system
echo [INFO] MCP configuration written: %MCP_FILE%
echo.
echo [WARN] Need to restart terminal or Claude to take effect
echo.

:verify_install
REM Verify installation
echo [INFO] Verifying installation...

if not exist "%PLUGIN_DIR%" (
    echo [ERROR] Plugin directory does not exist: %PLUGIN_DIR%
    goto failed
)

REM Check plugin files
set PLUGIN_FILES[0]=%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json
set PLUGIN_FILES[1]=%PLUGIN_DIR%\05-plugins\rf-testing\.claude-plugin\plugin.json
set PLUGIN_FILES[2]=%PLUGIN_DIR%\05-plugins\rf-testing\commands\start.md

for /L %%i in (0,1,2) do (
    if exist "!PLUGIN_FILES[%%i]!" (
        echo [INFO] Plugin file exists: %%~nxi!PLUGIN_FILES[%%i]!
    ) else (
        echo [WARN] Plugin file not found: !PLUGIN_FILES[%%i]!
    )
)

REM Check Python dependencies (using detected Python)
"%PYTHON_CMD%" -c "import pandas, openpyxl, robotframework" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python dependencies verification failed
    goto failed
)

echo [INFO] Python dependencies verification passed
echo.

REM Print usage
echo ==================================
echo   Installation Complete!
echo ==================================
echo.
echo Plugin path: %PLUGIN_DIR%
echo.
echo Recommended installation (marketplace):
echo   1. Enter plugin directory:
echo      cd %PLUGIN_DIR%
echo   2. Run in Claude Code:
echo      /plugin marketplace add .
echo      /plugin install rf-testing
echo.
echo Available commands:
echo   /rf-testing:start [tapd-link]  - Full test workflow
echo.
echo Sub-workflows:
echo   /rf-testing:requirement-to-rf  - Requirement to test cases only
echo   /rf-testing:rf-to-tapd       - RF to TAPD only
echo.
echo Environment variables:
echo   TAPD_ACCESS_TOKEN=your-tapd-token (required)
echo   GITLAB_API_URL=https://gitlab.example.com/api/v4 (optional)
echo   GITLAB_PERSONAL_ACCESS_TOKEN=your-gitlab-token (optional)
echo.
echo Usage:
echo   1. Configure environment variables
echo   2. Restart Claude Code
echo   3. Run: /rf-testing:start
echo.
echo Notes:
echo   - Ensure TAPD_ACCESS_TOKEN is configured
echo   - First run requires TAPD requirement link
echo   - RF quality assurance Agent automatically checks case quality
echo.

echo [INFO] Installation successful!
exit /b 0

:failed
echo [ERROR] Installation verification failed, please check above errors
exit /b 1