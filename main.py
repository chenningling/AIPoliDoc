#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AI Word文档自动排版工具主程序入口
"""

import os
import sys
import traceback
from PyQt6.QtWidgets import QApplication, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from src.ui.main_window import MainWindow
from src.utils.logger import app_logger

def exception_hook(exc_type, exc_value, exc_traceback):
    """全局异常处理函数"""
    # 记录异常到日志
    error_msg = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    app_logger.critical(f"未捕获异常: {error_msg}")
    
    # 显示错误对话框
    error_box = QMessageBox()
    error_box.setIcon(QMessageBox.Icon.Critical)
    error_box.setWindowTitle("程序错误")
    error_box.setText("程序发生错误，请查看日志了解详情。")
    error_box.setDetailedText(error_msg)
    error_box.exec()

def create_required_dirs():
    """创建必要的目录"""
    dirs = [
        "config",
        "config/templates",
        "logs"
    ]
    
    for dir_path in dirs:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
                app_logger.info(f"创建目录: {dir_path}")
            except Exception as e:
                app_logger.error(f"创建目录失败: {dir_path}, 错误: {str(e)}")

def main():
    """主函数"""
    # 创建必要的目录
    create_required_dirs()
    
    # 创建QApplication实例
    app = QApplication(sys.argv)
    app.setApplicationName("AI Word文档自动排版工具")
    
    # 设置默认字体
    default_font = QFont("Microsoft YaHei UI", 10)
    app.setFont(default_font)
    
    # 设置全局异常处理
    sys.excepthook = exception_hook
    
    # 创建主窗口
    window = MainWindow()
    window.show()
    
    # 记录启动信息
    app_logger.info("AI Word文档自动排版工具启动成功")
    
    # 运行应用程序
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
