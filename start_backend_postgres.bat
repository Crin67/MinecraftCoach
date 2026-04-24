@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ==============================
echo   Minecraft Coach Backend
echo ==============================
echo.

if not exist "server\requirements.txt" (
    echo server\requirements.txt not found.
    echo Run this file from the project root folder.
    pause
    exit /b 1
)

set "PY_CMD="
where python >nul 2>nul
if not errorlevel 1 set "PY_CMD=python"
if not defined PY_CMD (
    where py >nul 2>nul
    if not errorlevel 1 set "PY_CMD=py"
)

if not defined PY_CMD (
    echo Python was not found in PATH.
    echo Install Python or run from a terminal where python is available.
    pause
    exit /b 1
)

echo Using: %PY_CMD%
echo Installing/updating backend dependencies...
%PY_CMD% -m pip install -r server\requirements.txt
if errorlevel 1 (
    echo Failed to install backend dependencies.
    pause
    exit /b 1
)

set "UVICORN_ENV_ARGS="
set "CHECK_DB_URL=%MINECRAFT_COACH_DATABASE_URL%"

if exist "server\backend.env" (
    echo Found server\backend.env
    set "UVICORN_ENV_ARGS=--env-file server\backend.env"
    if "%CHECK_DB_URL%"=="" (
        for /f "usebackq tokens=1,* delims==" %%A in (`findstr /B /C:"MINECRAFT_COACH_DATABASE_URL=" "server\backend.env"`) do (
            set "CHECK_DB_URL=%%B"
        )
    )
    echo.
)

if "%CHECK_DB_URL%"=="" (
    echo WARNING: MINECRAFT_COACH_DATABASE_URL is empty.
    echo Backend will fall back to local file-json storage.
    echo.
)

if not "%CHECK_DB_URL%"=="" (
    echo %CHECK_DB_URL% | findstr /C:"://USER:" /C:"@HOST:" /C:"/DBNAME" /C:"password=YOUR_REAL_PASSWORD" /C:"dbname=YOUR_DB_NAME" >nul
    if not errorlevel 1 (
        echo ERROR: MINECRAFT_COACH_DATABASE_URL still contains template placeholders.
        echo Replace USER, PASSWORD, HOST and DBNAME with real PostgreSQL values.
        echo Example:
        echo host=pgsql17.server612364.nazwa.pl port=5432 dbname=real_database user=real_user password=real_password
        echo.
        pause
        exit /b 1
    )
)

echo Starting backend on http://127.0.0.1:8000
echo.
%PY_CMD% -m uvicorn server.app.main:app --host 0.0.0.0 --port 8000 %UVICORN_ENV_ARGS%

echo.
echo Backend stopped.
pause
