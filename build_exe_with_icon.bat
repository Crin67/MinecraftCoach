@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================
echo   Minecraft Coach EXE Build
echo ==============================
echo.

where py >nul 2>nul
if errorlevel 1 (
    echo Python launcher ^(py^) not found.
    echo Install Python from python.org and enable "Add Python to PATH".
    pause
    exit /b 1
)

echo Checking PyInstaller...
py -m pip show pyinstaller >nul 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    py -m pip install --upgrade pip
    py -m pip install pyinstaller
    if errorlevel 1 (
        echo Failed to install PyInstaller.
        pause
        exit /b 1
    )
)

if not exist "app.ico" (
    echo app.ico not found in this folder.
    pause
    exit /b 1
)

if not exist "minecraft_homework_overlay_v23.py" (
    echo minecraft_homework_overlay_v23.py not found in this folder.
    pause
    exit /b 1
)

echo Cleaning old build...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

echo Building EXE...
py -m PyInstaller ^
  --noconfirm ^
  --onefile ^
  --name MinecraftCoach_debug ^
  --icon=app.ico ^
  --add-data "app.ico;." ^
  --add-data "coach_seed_v22.db;." ^
  --add-data "Electryk;Electryk" ^
  --add-data "modules;modules" ^
  --add-data "module_templates;module_templates" ^
  minecraft_homework_overlay_v23.py

if errorlevel 1 (
    echo Build failed.
    pause
    exit /b 1
)

echo Copying external content into dist...
if exist "coach_seed_v22.db" copy /y "coach_seed_v22.db" "dist\\coach_seed_v22.db" >nul
if exist "Electryk" xcopy "Electryk" "dist\\Electryk" /e /i /y >nul
if exist "modules" xcopy "modules" "dist\modules" /e /i /y >nul
if exist "module_templates" xcopy "module_templates" "dist\module_templates" /e /i /y >nul

echo.
echo Done.
echo EXE file: dist\MinecraftCoach_debug.exe
pause
