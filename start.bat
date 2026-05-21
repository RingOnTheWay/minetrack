@echo off
chcp 65001 >nul
title MineTrack

echo ========================================
echo   MineTrack - Minecraft Server Stats
echo ========================================
echo.

cd /d "%~dp0"

where uv >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] uv not found, please install: https://docs.astral.sh/uv/getting-started/installation/
    pause
    exit /b 1
)

where node >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js not found, please install: https://nodejs.org/
    pause
    exit /b 1
)

echo [1/4] Checking backend dependencies...
uv sync --quiet
if %errorlevel% neq 0 (
    echo [ERROR] Backend dependency sync failed.
    pause
    exit /b 1
)

echo [2/4] Checking frontend dependencies...
cd frontend
if not exist node_modules (
    echo        Installing frontend dependencies...
    npm install --silent
    if %errorlevel% neq 0 (
        echo [ERROR] Frontend npm install failed.
        cd ..
        pause
        exit /b 1
    )
)
cd ..

echo [3/4] Starting backend server (port 5000)...
powershell -Command "Start-Process cmd -ArgumentList '/c uv run python backend/main.py' -WindowStyle Hidden"

echo [4/4] Starting frontend dev server (port 5173)...
cd frontend
powershell -Command "Start-Process cmd -ArgumentList '/c npm run dev' -WindowStyle Hidden"
cd ..

echo.

echo.
echo ========================================
echo   Backend:  http://localhost:5000
echo   Frontend: http://localhost:5173
echo ========================================
echo.
echo   Press any key to STOP all servers
echo ========================================
echo.

pause >nul

echo.
echo Stopping servers...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do taskkill /pid %%a /f >nul 2>&1
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do taskkill /pid %%a /f >nul 2>&1
echo Servers stopped.
timeout /t 2 /nobreak >nul
