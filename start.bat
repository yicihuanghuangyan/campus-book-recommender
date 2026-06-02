@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: ============================================================
::  校园书籍推荐系统 - 一键启动脚本
::  双击运行，自动检查环境、安装依赖、启动服务
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

:: ============================================================
::  第一步：检查 Python 环境
:: ============================================================
echo  -----------------------------------------------------
echo  [1/4] 检查 Python 环境...
echo  -----------------------------------------------------

set PYTHON_EXE=
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

:: 获取 Python 版本（python --version 输出到 stderr，需要重定向）
for /f "tokens=*" %%i in ('python --version 2^>^&1') do set PY_VER=%%i
echo  [通过] %PY_VER%

:: 验证 pip
python -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [警告] pip 不可用，尝试修复...
    python -m ensurepip --upgrade >nul 2>&1
    if %errorlevel% neq 0 (
        echo  [错误] pip 修复失败，请手动修复 Python 安装
        pause
        exit /b 1
    )
)
echo  [通过] pip 可用

echo.

:: ============================================================
::  第二步：安装项目依赖
:: ============================================================
echo  -----------------------------------------------------
echo  [2/4] 安装项目依赖...
echo  -----------------------------------------------------

if not exist "%~dp0requirements.txt" (
    echo  [跳过] requirements.txt 不存在
    goto :skip_deps
)

echo  [执行] pip install -r requirements.txt
echo.
python -m pip install -r "%~dp0requirements.txt" --quiet
if %errorlevel% neq 0 (
    echo.
    echo  [警告] 部分依赖安装失败，尝试不使用缓存重试...
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

:: ============================================================
::  第三步：打印运行信息
:: ============================================================
echo  -----------------------------------------------------
echo  [3/4] 启动信息确认...
echo  -----------------------------------------------------
echo.
echo   项目目录:   %~dp0
echo   启动模块:   backend.main:app
echo   框架:       FastAPI + Uvicorn
echo   后端地址:   http://localhost:8000
echo   API 文档:   http://localhost:8000/docs
echo.

:: ============================================================
::  第四步：检查端口，启动服务
:: ============================================================
echo  -----------------------------------------------------
echo  [4/4] 启动 FastAPI 服务...
echo  -----------------------------------------------------

:: 检查 8000 端口是否被占用（精确匹配 :8000 后跟空格或行尾）
netstat -ano 2>nul | findstr /R ":8000[ ]" >nul
if %errorlevel% equ 0 (
    echo.
    echo  [警告] 端口 8000 已被占用，正在释放...
    for /f "tokens=5" %%a in ('netstat -ano 2^>nul ^| findstr /R ":8000[ ]"') do (
        if not "%%a"=="0" (
            echo  [执行] 终止进程 PID=%%a
            taskkill /F /PID %%a >nul 2>&1
        )
    )
    echo  [提示] 等待 2 秒...
    timeout /t 2 /nobreak >nul
)

cd /d "%~dp0"

echo.
echo  =====================================================
echo    [启动] 正在启动后端服务...
echo.
echo    服务将在一个新窗口中运行。
echo    关闭新窗口即可停止服务。
echo  =====================================================
echo.

:: 在新窗口中启动服务（用户可以看到日志，关闭窗口即停止）
start "BookRecommender Server" cmd /k "cd /d %~dp0 && python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 && pause"

:: 等待服务就绪 - 用 PowerShell 检测（兼容性最好）
echo  [等待] 等待服务就绪...
set RETRY=0
:wait_loop
    timeout /t 2 /nobreak >nul
    set /a RETRY+=1

    :: 用 PowerShell 检测（Win7+ 都内置）
    powershell -Command "try { $r = Invoke-WebRequest -Uri 'http://localhost:8000/api/health' -UseBasicParsing -TimeoutSec 2; exit 0 } catch { exit 1 }" >nul 2>&1
    if %errorlevel% equ 0 goto :ready

    if !RETRY! geq 15 (
        echo.
        echo  [警告] 服务启动超时（已等 30 秒）。
        echo.
        echo  请检查新打开的窗口是否有错误信息。
        echo  常见原因：
        echo    - 依赖未安装完整
        echo    - 端口 8000 被其他程序占用
        echo    - Python 版本过低
        echo.
        echo  手动启动命令：
        echo    python -m uvicorn backend.main:app --reload
        echo.
        pause
        exit /b 1
    )
goto :wait_loop

:ready
echo.
echo  [成功] 服务已就绪！

:: ============================================================
::  第五步：打开浏览器
:: ============================================================
echo  [操作] 打开浏览器访问 API 文档...
start "" http://localhost:8000/docs

echo.
echo  =====================================================
echo.
echo    [OK] 启动成功！
echo.
echo    API 文档:  http://localhost:8000/docs
echo    ReDoc:     http://localhost:8000/redoc
echo    前端页面:  http://localhost:8000/app
echo.
echo    在服务器窗口中按 Ctrl+C 可停止服务
echo.
echo  =====================================================
echo.

pause
endlocal
