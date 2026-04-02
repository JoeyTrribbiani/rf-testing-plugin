@echo off
echo ====================================
echo   Sync local code with remote
echo ====================================
echo.

cd /d "%~dp0"

echo Fetching from remote...
git fetch origin

echo.
echo Checking local changes...
git status

echo.
echo To pull latest changes, run:
echo   git pull origin master
echo.

echo To push local changes, run:
echo   git push origin master
echo.

pause