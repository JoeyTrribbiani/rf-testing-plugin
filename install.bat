@echo off

REM Plugin configuration
set PLUGIN_NAME=rf-testing-plugin
set PLUGIN_DIR=%~dp0

echo [INFO] Start installing %PLUGIN_NAME%...
echo.

REM Check Python
where python >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed
    exit /b 1
)

REM Check git
where git >nul 2>&1
if errorlevel 1 (
    echo [ERROR] git is not installed
    exit /b 1
)

REM Check plugin directory
echo [INFO] Checking plugin directory...

if not exist "%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json" (
    echo [ERROR] Plugin files not found in current directory
    echo [INFO] Please run this script from the plugin root directory
    exit /b 1
)

echo [INFO] Plugin directory verified: %PLUGIN_DIR%
echo.

:detect_python
echo [INFO] Detecting Python environment...

python "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json > "%TEMP%\env_detection.json" 2>nul

if errorlevel 1 (
    echo [ERROR] Python environment detection failed
    echo [INFO] Using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

echo.
python "%PLUGIN_DIR%\03-scripts\python_detector.py"
echo.

set /p PYTHON_CHOICE="Select Python environment (enter number or press Enter for default) "
if "%PYTHON_CHOICE%"=="" set PYTHON_CHOICE=1

REM Use Windows PowerShell to parse JSON safely
powershell -Command "$data = Get-Content '%TEMP%\env_detection.json' | ConvertFrom-Json; $index = %PYTHON_CHOICE% - 1; if ($index -lt $data.Count) { Write-Output $data[$index].python_path }" > "%TEMP%\selected_python.txt"

set /p SELECTED_PYTHON=<"%TEMP%\selected_python.txt"

if "%SELECTED_PYTHON%"=="" (
    echo [ERROR] Invalid selection
    echo [INFO] Using system Python
    set PYTHON_CMD=python
    set PIP_CMD=pip
    goto install_deps
)

REM Parse version
powershell -Command "$data = Get-Content '%TEMP%\env_detection.json' | ConvertFrom-Json; $index = %PYTHON_CHOICE% - 1; if ($index -lt $data.Count) { Write-Output $data[$index].version }" > "%TEMP%\selected_version.txt"

set /p PYTHON_VERSION=<"%TEMP%\selected_version.txt"

echo [INFO] Selected: Python %PYTHON_VERSION%
echo [INFO] Path: %SELECTED_PYTHON%
echo.

set PYTHON_CMD=%SELECTED_PYTHON%

REM Find pip - conda envs have pip in Scripts directory
powershell -Command "$python = '%SELECTED_PYTHON%'; $dir = Split-Path $python -Parent; $pip = Join-Path $dir 'Scripts\pip.exe'; if (Test-Path $pip) { Write-Output $pip } else { Write-Output 'pip' }" > "%TEMP%\pip_path.txt"

set /p PIP_CMD=<"%TEMP%\pip_path.txt"

:install_deps
echo [INFO] Installing Python dependencies with selected Python...

"%PIP_CMD%" show pandas >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing pandas...
    "%PIP_CMD%" install pandas
) else (
    echo [INFO] pandas is already installed
)

"%PIP_CMD%" show openpyxl >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing openpyxl...
    "%PIP_CMD%" install openpyxl
) else (
    echo [INFO] openpyxl is already installed
)

"%PIP_CMD%" show robotframework >nul 2>&1
if errorlevel 1 (
    echo [INFO] Installing robotframework...
    "%PIP_CMD%" install robotframework
) else (
    echo [INFO] robotframework is already installed
)

echo [INFO] Python dependencies installed
echo.

REM Save Python environment configuration
echo [INFO] Saving Python environment configuration...
python "%PLUGIN_DIR%\03-scripts\rf_config.py" --set-python "%PYTHON_CMD%" 2>nul
if errorlevel 1 (
    echo [WARN] Failed to save Python configuration
) else (
    echo [INFO] Python environment saved: %PYTHON_CMD%
)
echo.

:install_jl
echo [INFO] Installing JLTestLibrary...
set JL_LIBRARY=%PLUGIN_DIR%\03-scripts\JLTestLibrary.zip

if not exist "%JL_LIBRARY%" (
    echo [WARN] JLTestLibrary.zip not found, skip installation
    goto configure_mcp
)

echo [INFO] Detecting site-packages directory...
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --format json --site-packages --python-path "%PYTHON_CMD%" > "%TEMP%\site_packages.json" 2>nul

if errorlevel 1 (
    echo [WARN] Cannot detect site-packages directory, skip installation
    goto configure_mcp
)

REM Check if JLTestLibrary is already installed in any site-packages
powershell -Command "$data = Get-Content '%TEMP%\site_packages.json' | ConvertFrom-Json; if ($data.jl_installed -contains $true) { exit 0 } else { exit 1 }" 2>nul

if not errorlevel 1 (
    echo [INFO] JLTestLibrary already installed, skip installation
    goto configure_mcp
)

REM Display site-packages options
echo.
"%PYTHON_CMD%" "%PLUGIN_DIR%\03-scripts\python_detector.py" --site-packages --python-path "%PYTHON_CMD%"
echo.

set /p SP_CHOICE="Select target directory (enter number or press Enter for default) "
if "%SP_CHOICE%"=="" set SP_CHOICE=1

REM Parse site-packages path
powershell -Command "$data = Get-Content '%TEMP%\site_packages.json' | ConvertFrom-Json; $sp = $data.site_packages; $index = %SP_CHOICE% - 1; if ($sp -and $index -ge 0 -and $index -lt $sp.Count) { Write-Output $sp[$index] }" > "%TEMP%\target_dir.txt"

set /p TARGET_DIR=<"%TEMP%\target_dir.txt"

if "%TARGET_DIR%"=="" (
    echo [WARN] Invalid selection, skip installation
    goto configure_mcp
)

if exist "%TARGET_DIR%\JLTestLibrary" (
    echo [WARN] JLTestLibrary already exists, skip installation
    goto configure_mcp
)

echo [INFO] Extracting to: %TARGET_DIR%
powershell -Command "Expand-Archive -Path '%JL_LIBRARY%' -DestinationPath '%TARGET_DIR%' -Force" 2>nul

if errorlevel 1 (
    echo [WARN] Extraction failed, check permissions
    goto configure_mcp
)

"%PYTHON_CMD%" -c "import JLTestLibrary" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Verification failed
) else (
    echo [INFO] JLTestLibrary installed successfully
)

echo.

:configure_mcp
echo [INFO] ====================================
echo [INFO] Plugin installed to local directory
echo [INFO] ====================================
echo.
echo [INFO] To let Claude Code recognize this plugin, run in Claude Code:
echo.
echo [INFO] Command 1: /plugin marketplace add
echo [INFO] Path: %PLUGIN_DIR%
echo.
echo [INFO] Command 2: /plugin install rf-testing
echo.
echo Configure environment variables and MCP servers
echo.
set /p DO_CONFIG="Configure now (y/n, press Enter to skip) "
if /i not "%DO_CONFIG%"=="y" goto verify_install

REM Collect TAPD configuration
echo.
echo Configure TAPD access token
echo Get token at: https://www.tapd.cn/personal_settings/index?tab=personal_token
set /p TAPD_TOKEN="Enter TAPD_ACCESS_TOKEN "

if "%TAPD_TOKEN%"=="" (
    echo [WARN] Token is empty
    set /p SKIP_CONFIG="Skip configuration (y/n) "
    if /i "%SKIP_CONFIG%"=="y" goto verify_install
)

REM Collect GitLab configuration
echo.
echo Configure GitLab. Optional, press Enter to skip
echo Get token at: https://gitlab.jlpay.com/-/user_settings/personal_access_tokens
set /p GITLAB_URL="Enter GITLAB_API_URL (press Enter for default) "
if "%GITLAB_URL%"=="" set GITLAB_URL=https://gitlab.jlpay.com/api/v4

set /p GITLAB_TOKEN="Enter GITLAB_TOKEN (optional, press Enter to skip) "

REM Collect GitHub configuration
echo.
echo Configure GitHub. Optional, press Enter to skip
set /p GITHUB_TOKEN="Enter GITHUB_TOKEN (optional, press Enter to skip) "

REM Collect YAPI configuration
echo.
echo Configure YAPI. Optional, press Enter to skip
set /p YAPI_URL="Enter YAPI_BASE_URL (optional, press Enter to skip) "
if not "%YAPI_URL%"=="" (
    set /p YAPI_TOKEN="Enter YAPI_TOKEN (format projectId token) "
)

REM Write environment variables
echo.
echo Writing system environment variables...
setx TAPD_ACCESS_TOKEN "%TAPD_TOKEN%" >nul
setx GITLAB_API_URL "%GITLAB_URL%" >nul
if not "%GITLAB_TOKEN%"=="" setx GITLAB_PERSONAL_ACCESS_TOKEN "%GITLAB_TOKEN%" >nul
if not "%GITHUB_TOKEN%"=="" setx GITHUB_TOKEN "%GITHUB_TOKEN%" >nul
if not "%YAPI_URL%"=="" (
    setx YAPI_BASE_URL "%YAPI_URL%" >nul
    setx YAPI_TOKEN "%YAPI_TOKEN%" >nul
)
echo [INFO] Environment variables written

REM Create MCP configuration
echo.
echo Configuring Claude MCP servers...
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
echo         "TAPD_BASE_URL": "https://www.tapd.cn">> "%JSON_TEMP%"
echo       }>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
if not "%GITLAB_TOKEN%"=="" (
echo     ,>> "%JSON_TEMP%"
echo     "gitlab": {>> "%JSON_TEMP%"
echo       "command": "npx",>> "%JSON_TEMP%"
echo       "args": ["-y", "@modelcontextprotocol/server-gitlab"],>> "%JSON_TEMP%"
echo       "env": {>> "%JSON_TEMP%"
echo         "GITLAB_API_URL": "%GITLAB_URL%",>> "%JSON_TEMP%"
echo         "GITLAB_PERSONAL_ACCESS_TOKEN": "%GITLAB_TOKEN%">> "%JSON_TEMP%"
echo       }>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
)
if not "%GITHUB_TOKEN%"=="" (
echo     ,>> "%JSON_TEMP%"
echo     "github": {>> "%JSON_TEMP%"
echo       "command": "npx",>> "%JSON_TEMP%"
echo       "args": ["-y", "@modelcontextprotocol/server-github"],>> "%JSON_TEMP%"
echo       "env": {>> "%JSON_TEMP%"
echo         "GITHUB_TOKEN": "%GITHUB_TOKEN%">> "%JSON_TEMP%"
echo       }>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
)
if not "%YAPI_URL%"=="" (
echo     ,>> "%JSON_TEMP%"
echo     "yapi-auto-mcp": {>> "%JSON_TEMP%"
echo       "command": "npx",>> "%JSON_TEMP%"
echo       "args": ["-y", "yapi-auto-mcp", "--stdio"]>> "%JSON_TEMP%"
echo     }>> "%JSON_TEMP%"
)
echo   }>> "%JSON_TEMP%"
echo }>> "%JSON_TEMP%"

move "%JSON_TEMP%" "%MCP_FILE%" >nul
echo [INFO] MCP configuration written

echo.
echo Configuration complete
echo.
echo [INFO] Configured MCP servers:
echo   - tapd (TAPD requirement management)
if not "%GITLAB_TOKEN%"=="" (
    echo   - gitlab (GitLab code management)
) else (
    echo   - gitlab (not configured)
)
if not "%GITHUB_TOKEN%"=="" (
    echo   - github (GitHub code management)
) else (
    echo   - github (not configured)
)
if not "%YAPI_URL%"=="" (
    echo   - yapi-auto-mcp (YAPI API documentation)
) else (
    echo   - yapi-auto-mcp (not configured)
)
echo.
echo [WARN] Restart terminal or Claude to take effect
echo.

:verify_install
echo [INFO] Verifying installation...

if not exist "%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json" (
    echo [ERROR] Plugin files not found in %PLUGIN_DIR%
    goto failed
)

echo [INFO] Checking plugin files...

if exist "%PLUGIN_DIR%\05-plugins\rf-testing\.mcp.json" (
    echo [INFO] File exists: .mcp.json
) else (
    echo [WARN] File not found: .mcp.json
)

if exist "%PLUGIN_DIR%\05-plugins\rf-testing\.claude-plugin\plugin.json" (
    echo [INFO] File exists: plugin.json
) else (
    echo [WARN] File not found: plugin.json
)

if exist "%PLUGIN_DIR%\05-plugins\rf-testing\commands\start.md" (
    echo [INFO] File exists: start.md
) else (
    echo [WARN] File not found: start.md
)

echo [INFO] Verifying Python dependencies with selected Python...
"%PYTHON_CMD%" -c "import pandas, openpyxl, robot" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python dependencies verification failed with selected Python
    echo [INFO] Please install dependencies in the selected Python environment:
    echo   "%PYTHON_CMD%" -m pip install pandas openpyxl robotframework
    goto failed
)

echo [INFO] Python dependencies verification passed
echo.

echo Installation Complete
echo.
echo Plugin path: %PLUGIN_DIR%
echo.
echo Available commands:
echo   /rf-testing:start - Full test workflow
echo.
echo Environment variables:
echo   TAPD_ACCESS_TOKEN - Required
echo   GITLAB_API_URL - Optional
echo   GITLAB_PERSONAL_ACCESS_TOKEN - Optional
echo   YAPI_BASE_URL - Optional
echo   YAPI_TOKEN - Optional
echo.

echo [INFO] Installation successful
exit /b 0

:failed
echo [ERROR] Installation verification failed
exit /b 1