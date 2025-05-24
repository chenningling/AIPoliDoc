# -*- coding: utf-8 -*-
"""
日志工具模块
负责记录应用程序的日志信息，并提供日志显示和管理功能。
"""

import logging
import os
import time
from datetime import datetime
from logging.handlers import RotatingFileHandler

class Logger:
    """日志管理器类。管理日志的创建、格式化和输出。"""
    
    def __init__(self, name="AIPoliDoc", log_dir="logs"):
        """
        初始化日志管理器。
        
        Args:
            name: 日志器名称
            log_dir: 日志文件存放目录
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.log_dir = log_dir
        self.log_file = None
        self.ui_handlers = []
        
        # 创建日志目录
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
            
        # 创建日志文件
        self._setup_file_handler()
        
        # 创建控制台处理器
        self._setup_console_handler()
    
    def _setup_file_handler(self):
        """设置文件日志处理器"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = os.path.join(self.log_dir, f"aipolidoc_{timestamp}.log")
        
        file_handler = RotatingFileHandler(
            self.log_file, 
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
    
    def _setup_console_handler(self):
        """设置控制台日志处理器"""
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)  # 修改为调试级别，以显示更多日志
        
        formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(console_handler)
    
    def add_ui_handler(self, callback):
        """
        添加UI日志处理器，用于将日志信息发送到UI显示。
        
        Args:
            callback: 接收日志信息的回调函数
        """
        class UIHandler(logging.Handler):
            def __init__(self, callback):
                super().__init__()
                self.callback = callback
            
            def emit(self, record):
                log_entry = self.format(record)
                self.callback(log_entry, record.levelname)
        
        handler = UIHandler(callback)
        handler.setLevel(logging.DEBUG)  # 修改为调试级别，以显示更多日志
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        
        self.logger.addHandler(handler)
        self.ui_handlers.append(handler)
    
    def remove_ui_handler(self, callback):
        """移除UI日志处理器"""
        for handler in self.ui_handlers:
            if handler.callback == callback:
                self.logger.removeHandler(handler)
                self.ui_handlers.remove(handler)
                break
    
    def debug(self, message):
        """记录调试级别日志"""
        self.logger.debug(message)
    
    def info(self, message):
        """记录信息级别日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告级别日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误级别日志"""
        self.logger.error(message)
    
    def critical(self, message):
        """记录严重错误级别日志"""
        self.logger.critical(message)

# 创建全局日志实例
app_logger = Logger()
