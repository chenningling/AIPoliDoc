@echo off
REM AI Word文档自动排版工具 - Windows 快速启动脚本
REM 双击此文件即可启动应用

REM 设置代码页为 UTF-8，支持中文显示
chcp 65001 >nul

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 显示启动信息
echo ==========================================
echo   AI Word文档自动排版工具
echo ==========================================
echo 正在启动应用...
echo.

REM 检查虚拟环境是否存在
if not exist "venv" (
    echo 错误: 虚拟环境不存在！
    echo 请先运行: python -m venv venv
    echo 然后安装依赖: venv\Scripts\activate ^&^& pip install -r requirements.txt
    pause
    exit /b 1
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 检查依赖是否已安装
python -c "import PyQt6; import docx; import requests; import json5" 2>nul
if errorlevel 1 (
    echo 警告: 部分依赖可能未安装，正在检查...
    echo 如果程序无法启动，请运行: pip install -r requirements.txt
    echo.
)

REM 运行主程序
echo 启动主程序...
python main.py

REM 如果程序异常退出，保持窗口打开以便查看错误信息
if errorlevel 1 (
    echo.
    echo 程序异常退出，请查看上方错误信息
    pause
)

