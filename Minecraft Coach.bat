@echo off
chcp 65001 >nul
cd /d "%~dp0"

if exist "dist\MinecraftCoach.exe" (
    start "" "dist\MinecraftCoach.exe"
    exit /b 0
)

where py >nul 2>nul
if not errorlevel 1 (
    py "minecraft_homework_overlay_v23.py"
    exit /b %errorlevel%
)

where python >nul 2>nul
if not errorlevel 1 (
    python "minecraft_homework_overlay_v23.py"
    exit /b %errorlevel%
)

echo Python launcher not found and dist\MinecraftCoach.exe is missing.
echo Build the EXE first or install Python from python.org.
pause
