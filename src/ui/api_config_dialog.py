# -*- coding: utf-8 -*-
"""
API配置对话框模块
负责创建和管理API配置对话框，用于设置AI API的相关参数。
"""

import os
from datetime import datetime
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFormLayout, QComboBox,
                           QMessageBox, QGroupBox, QDialogButtonBox)
from PyQt6.QtCore import Qt

from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..core.ai_connector import AIConnector

class ApiConfigDialog(QDialog):
    """API配置对话框，用于设置AI API的相关参数"""
    
    def __init__(self, parent=None):
        """
        初始化API配置对话框
        
        Args:
            parent: 父窗口
        """
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("模型配置")
        self.setMinimumWidth(500)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        # 加载当前配置
        self.api_config = config_manager.get_api_config()
        
        # 初始化UI
        self.init_ui()
        
        # 加载配置到UI
        self.load_config()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # API配置组
        api_group = QGroupBox("API配置")
        form_layout = QFormLayout(api_group)
        
        # API URL
        self.api_url_label = QLabel("API URL:")
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("例如: https://api.deepseek.com/chat/completions")
        form_layout.addRow(self.api_url_label, self.api_url_edit)
        
        # API Key
        self.api_key_label = QLabel("API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setPlaceholderText("输入您的API密钥")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)  # 密码模式
        form_layout.addRow(self.api_key_label, self.api_key_edit)
        
        # 模型选择
        self.model_label = QLabel("模型:")
        self.model_combo = QComboBox()
        self.model_combo.addItems(["deepseek-chat", "deepseek-coder", "gpt-3.5-turbo", "gpt-4", "custom"])
        self.model_combo.setEditable(True)  # 允许自定义输入
        form_layout.addRow(self.model_label, self.model_combo)
        
        # 最后更新时间
        self.last_updated_label = QLabel("最后更新:")
        self.last_updated_value = QLabel("未设置")
        form_layout.addRow(self.last_updated_label, self.last_updated_value)
        
        # 添加API配置组
        main_layout.addWidget(api_group)
        
        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.clicked.connect(self.test_connection)
        main_layout.addWidget(self.test_btn)
        
        # 按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # 设置样式
        self.set_style()
    
    def set_style(self):
        """
        设置对话框样式
        """
        self.setStyleSheet("""
            QGroupBox {
                font-weight: bold;
                border: 1px solid #BBDEFB;
                border-radius: 5px;
                margin-top: 1ex;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
                color: #1976D2;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            }
            QPushButton:hover {
                background-color: #0D8AEE;
            }
            QPushButton:pressed {
                background-color: #0A6EBD;
            }
            QLineEdit, QComboBox {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
        """)
    
    def load_config(self):
        """
        从配置中加载数据到UI
        """
        # 设置API URL
        self.api_url_edit.setText(self.api_config.get("api_url", ""))
        
        # 设置API Key
        self.api_key_edit.setText(self.api_config.get("api_key", ""))
        
        # 设置模型
        model = self.api_config.get("model", "deepseek-chat")
        index = self.model_combo.findText(model)
        if index >= 0:
            self.model_combo.setCurrentIndex(index)
        else:
            self.model_combo.setEditText(model)
        
        # 设置最后更新时间
        last_updated = self.api_config.get("last_updated", "")
        if last_updated:
            self.last_updated_value.setText(last_updated)
    
    def accept(self):
        """
        保存配置并关闭对话框
        """
        # 获取输入值
        api_url = self.api_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        model = self.model_combo.currentText().strip()
        
        # 验证输入
        if not api_url:
            QMessageBox.warning(self, "输入错误", "API URL不能为空！")
            return
        
        if not api_key:
            QMessageBox.warning(self, "输入错误", "API Key不能为空！")
            return
        
        if not model:
            QMessageBox.warning(self, "输入错误", "模型名称不能为空！")
            return
        
        # 更新配置
        self.api_config["api_url"] = api_url
        self.api_config["api_key"] = api_key
        self.api_config["model"] = model
        self.api_config["last_updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # 保存配置
        config_manager.save_api_config(self.api_config)
        app_logger.info("API配置已更新")
        
        # 关闭对话框
        super().accept()
    
    def test_connection(self):
        """
        测试API连接
        """
        # 获取当前输入的配置
        api_url = self.api_url_edit.text().strip()
        api_key = self.api_key_edit.text().strip()
        model = self.model_combo.currentText().strip()
        
        # 验证输入
        if not api_url or not api_key or not model:
            QMessageBox.warning(self, "输入错误", "请填写所有API配置信息！")
            return
        
        # 创建临时配置
        temp_config = {
            "api_url": api_url,
            "api_key": api_key,
            "model": model
        }
        
        # 创建AI连接器并测试
        ai_connector = AIConnector(temp_config)
        
        # 显示等待消息
        self.test_btn.setEnabled(False)
        self.test_btn.setText("测试中...")
        app_logger.info("正在测试API连接...")
        
        # 验证配置
        is_valid, message = ai_connector.validate_config()
        
        # 恢复按钮状态
        self.test_btn.setEnabled(True)
        self.test_btn.setText("测试连接")
        
        # 显示结果
        if is_valid:
            QMessageBox.information(self, "连接成功", "API连接测试成功！")
            app_logger.info("API连接测试成功")
        else:
            QMessageBox.critical(self, "连接失败", f"API连接测试失败！\n错误: {message}")
            app_logger.error(f"API连接测试失败: {message}")
