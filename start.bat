@echo off
setlocal enabledelayedexpansion

:: ============================================================
::  校园书籍推荐系统 - 一键启动脚本
:: ============================================================

title 校园书籍推荐系统 - 启动中...

echo.
echo  =====================================================
echo    校园书籍推荐系统 - Campus Book Recommender
echo  =====================================================
echo.
echo  [信息] 当前时间: %date% %time%
echo  [信息] 项目目录: %~dp0
echo.

:: ---- 1. 检查 Python ----
echo  [1/4] 检查 Python 环境...
echo.

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo  [错误] 未检测到 Python，请先安装 Python 3.10+
    echo.
    echo  下载地址: https://www.python.org/downloads/
    echo  安装时请勾选 Add Python to PATH
    echo.
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo  [通过] %PY_VER%

python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [警告] pip 不可用，尝试修复...
    python -m ensurepip --upgrade >nul 2>&1
)
echo  [通过] pip 可用
echo.

:: ---- 2. 安装依赖 ----
echo  [2/4] 安装项目依赖...
echo.

if not exist "%~dp0requirements.txt" (
    echo  [跳过] requirements.txt 不存在
    goto :skip_deps
)

echo  [执行] pip install -r requirements.txt
python -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo  [警告] 安装失败，尝试无缓存重试...
    python -m pip install -r "%~dp0requirements.txt" --no-cache-dir --quiet
    if %errorlevel% neq 0 (
        echo  [错误] 依赖安装失败，请检查网络连接
        pause
        exit /b 1
    )
)
echo  [通过] 依赖安装完成

:skip_deps
echo.

:: ---- 3. 启动信息 ----
echo  [3/4] 启动信息确认...
echo.
echo   项目目录:   %~dp0
echo   启动模块:   backend.main:app
echo   API 文档:   http://localhost:8000/docs
echo   前端页面:   http://localhost:8000/app
echo.

:: ---- 4. 启动服务 ----
echo  [4/4] 启动 FastAPI 服务...
echo.

netstat -ano 2>nul | findstr /R ":8000 " >nul
if %errorlevel% equ 0 (
    echo  [警告] 端口 8000 已被占用，正在释放...
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R ":8000 "') do (
        taskkill /F /PID %%a >nul 2>&1
    )
    timeout /t 2 /nobreak >nul
)

cd /d "%~dp0"

start "BookRecommender" cmd /k "title BookRecommender ^&^& cd /d %~dp0 ^&^& python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000"

echo  [等待] 服务启动中（约 5-10 秒）...
timeout /t 6 /nobreak >nul

powershell -Command "try { Invoke-WebRequest -Uri http://localhost:8000/api/health -UseBasicParsing -TimeoutSec 3 | Out-Null; Write-Host '  [OK] 服务健康检查通过' } catch { Write-Host '  [提示] 服务可能仍在启动中，请查看新窗口' }" 2>nul

echo  [操作] 打开浏览器...
start "" http://localhost:8000/docs

echo.
echo  =====================================================
echo    [OK] 启动完成 !
echo.
echo    API 文档:  http://localhost:8000/docs
echo    前端页面:  http://localhost:8000/app
echo.
echo    在服务器窗口中按 Ctrl+C 可停止服务
echo    关闭服务器窗口即停止
echo  =====================================================
echo.

pause
endlocal
