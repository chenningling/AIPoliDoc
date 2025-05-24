#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
启动脚本 - 用于启动AI Word文档自动排版工具
"""

import sys
import os
import subprocess

def main():
    """启动应用程序的主函数"""
    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 设置工作目录为当前脚本所在目录
    os.chdir(current_dir)
    
    # 检查Python版本
    if sys.version_info < (3, 8):
        print("错误: 需要Python 3.8或更高版本")
        sys.exit(1)
    
    # 检查依赖是否已安装
    try:
        import PyQt6
        import docx
        import requests
        import json5
    except ImportError as e:
        print(f"错误: 缺少依赖 {e.name}")
        print("请运行: pip install -r requirements.txt")
        
        # 询问是否自动安装依赖
        choice = input("是否自动安装依赖? (y/n): ")
        if choice.lower() == 'y':
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
                print("依赖安装完成，正在启动应用...")
            except subprocess.CalledProcessError:
                print("依赖安装失败，请手动安装依赖后再启动应用")
                sys.exit(1)
        else:
            sys.exit(1)
    
    # 启动应用程序
    try:
        from main import main as app_main
        app_main()
    except Exception as e:
        print(f"启动失败: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
