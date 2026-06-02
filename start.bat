@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

:: ============================================================
::  校园书籍推荐系统 — 一键启动脚本
::  双击运行，自动检查环境、安装依赖、启动服务
:: ============================================================

title 校园书籍推荐系统 - 启动中...

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║     校园书籍推荐系统 — Campus Book Recommender    ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  [信息] 当前时间: %date% %time%
echo  [信息] 项目目录: %~dp0
echo.

:: ============================================================
::  第一步：检查 Python 环境
:: ============================================================
echo  ──────────────────────────────────────────────
echo  [1/4] 检查 Python 环境...
echo  ──────────────────────────────────────────────

where python >nul 2>&1
if %errorlevel% neq 0 (
    echo.
    echo  [错误] 未检测到 Python，请先安装 Python 3.10+
    echo.
    echo  下载地址: https://www.python.org/downloads/
    echo  安装时请勾选 "Add Python to PATH"
    echo.
    pause
    exit /b 1
)

:: 打印 Python 版本信息
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo  [通过] %PY_VER%

:: 检查 pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [警告] pip 不可用，尝试修复...
    python -m ensurepip --upgrade 2>nul
)
echo  [通过] pip 可用

echo.

:: ============================================================
::  第二步：安装项目依赖
:: ============================================================
echo  ──────────────────────────────────────────────
echo  [2/4] 安装项目依赖...
echo  ──────────────────────────────────────────────

if exist "%~dp0requirements.txt" (
    echo  [执行] pip install -r requirements.txt
    echo.
    python -m pip install -r "%~dp0requirements.txt" --quiet
    if %errorlevel% neq 0 (
        echo.
        echo  [警告] 部分依赖安装失败，尝试不使用缓存重新安装...
        python -m pip install -r "%~dp0requirements.txt" --no-cache-dir
        if %errorlevel% neq 0 (
            echo  [错误] 依赖安装失败，请检查网络连接或 requirements.txt
            pause
            exit /b 1
        )
    )
    echo  [通过] 依赖安装完成
) else (
    echo  [跳过] requirements.txt 不存在，跳过依赖安装
    echo        后续可通过 pip install -r requirements.txt 手动安装
)

echo.

:: ============================================================
::  第三步：打印运行信息
:: ============================================================
echo  ──────────────────────────────────────────────
echo  [3/4] 启动信息确认...
echo  ──────────────────────────────────────────────
echo  项目目录:   %~dp0
echo  启动文件:   backend/main.py
echo  框架:       FastAPI + Uvicorn
echo  访问地址:   http://localhost:8000
echo  API 文档:   http://localhost:8000/docs
echo  备选文档:   http://localhost:8000/redoc
echo.

:: ============================================================
::  第四步：检查端口，启动服务
:: ============================================================
echo  ──────────────────────────────────────────────
echo  [4/4] 启动 FastAPI 服务...
echo  ──────────────────────────────────────────────

:: 检查 8000 端口是否被占用
netstat -ano 2>nul | findstr ":8000.*LISTENING" >nul
if %errorlevel% equ 0 (
    echo.
    echo  [警告] 端口 8000 已被占用，正在尝试释放...
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr ":8000.*LISTENING"') do (
        echo  [执行] 终止进程 PID=%%a
        taskkill /F /PID %%a 2>nul
    )
    echo  [提示] 已尝试释放端口，等待 2 秒...
    timeout /t 2 /nobreak >nul
)

:: 切换到项目目录
cd /d "%~dp0"

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║  服务启动中，请稍候...                            ║
echo  ║  启动后将自动打开浏览器访问 API 文档              ║
echo  ╚══════════════════════════════════════════════════╝
echo.
echo  ┌─ 服务日志 ─────────────────────────────────────┐
echo.

:: 后台启动 FastAPI
start "" /B python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 >nul 2>&1

:: 等待服务就绪（轮询检测）
echo  [等待] 服务启动中...
set RETRY=0
:wait_loop
    timeout /t 1 /nobreak >nul
    set /a RETRY+=1

    :: 用 curl 检测服务是否就绪
    curl -s http://localhost:8000/api/health >nul 2>&1
    if %errorlevel% equ 0 goto :ready

    if !RETRY! geq 15 (
        echo.
        echo  [警告] 服务启动超时，请手动检查。
        echo         运行: python -m uvicorn backend.main:app --reload
        echo         访问: http://localhost:8000/docs
        echo.
        pause
        exit /b 1
    )
goto :wait_loop

:ready
echo.
echo  └────────────────────────────────────────────────┘
echo.
echo  [成功] 服务已就绪 ✓

:: ============================================================
::  第五步：打开浏览器
:: ============================================================
echo  [操作] 打开浏览器访问 API 文档...
start "" http://localhost:8000/docs

echo.
echo  ╔══════════════════════════════════════════════════╗
echo  ║                                                  ║
echo  ║    🎉 启动成功！                                  ║
echo  ║                                                  ║
echo  ║    API 文档:  http://localhost:8000/docs           ║
echo  ║    ReDoc:     http://localhost:8000/redoc          ║
echo  ║    前端页面:  http://localhost:8000/app            ║
echo  ║                                                  ║
echo  ║    按 Ctrl+C 可停止服务                           ║
echo  ║                                                  ║
echo  ╚══════════════════════════════════════════════════╝
echo.

pause
endlocal
