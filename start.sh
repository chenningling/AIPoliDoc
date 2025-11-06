#!/bin/bash
# -*- coding: utf-8 -*-
# AI Word文档自动排版工具 - 通用启动脚本
# 适用于 macOS、Linux 等 Unix 系统

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# 切换到项目目录
cd "$SCRIPT_DIR"

# 显示启动信息
echo "=========================================="
echo "  AI Word文档自动排版工具"
echo "=========================================="
echo "正在启动应用..."
echo ""

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "错误: 虚拟环境不存在！"
    echo "请先运行: python3 -m venv venv"
    echo "然后安装依赖: source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# 激活虚拟环境
source venv/bin/activate

# 检查依赖是否已安装
python3 -c "import PyQt6; import docx; import requests; import json5" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "警告: 部分依赖可能未安装"
    echo "如果程序无法启动，请运行: pip install -r requirements.txt"
    echo ""
fi

# 运行主程序
python3 main.py

# 检查退出状态
if [ $? -ne 0 ]; then
    echo ""
    echo "程序异常退出，请查看上方错误信息"
    exit 1
fi

