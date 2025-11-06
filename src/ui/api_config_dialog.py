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
        self.setWindowTitle("API配置")
        self.setMinimumWidth(500)  # 恢复原来的宽度
        self.setMinimumHeight(350)
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
        self.api_url_edit.setMinimumWidth(600)  # 设置最小宽度
        self.api_url_edit.setText("https://api.deepseek.com/chat/completions")  # 设置默认值
        self.api_url_edit.setPlaceholderText("请输入 API URL，例如：https://api.deepseek.com/chat/completions")
        form_layout.addRow(self.api_url_label, self.api_url_edit)
        
        # API Key
        self.api_key_label = QLabel("API Key:")
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setMinimumWidth(600)  # 设置最小宽度
        self.api_key_edit.setPlaceholderText("请输入您的 API Key")
        self.api_key_edit.setEchoMode(QLineEdit.EchoMode.Password)  # 密码模式
        form_layout.addRow(self.api_key_label, self.api_key_edit)
        
        # 模型选择
        self.model_label = QLabel("模型名称:")
        self.model_edit = QLineEdit()
        self.model_edit.setMinimumWidth(600)  # 设置最小宽度
        self.model_edit.setText("deepseek-chat")  # 设置默认值
        self.model_edit.setPlaceholderText("请输入模型名称，例如：deepseek-chat")
        form_layout.addRow(self.model_label, self.model_edit)
        
        # 添加说明文本
        info_text = "推荐使用DeepSeek模型，也可更换其他AI模型。"
        link_text = "点击获取DeepSeek API key"
        info_label = QLabel(f"{info_text} 👉 <a href='https://platform.deepseek.com/api_keys'>{link_text}</a>")
        info_label.setOpenExternalLinks(True)  # 允许打开外部链接
        info_label.setStyleSheet("color: #666; margin-top: 5px;")
        form_layout.addRow("", info_label)
        
        # 最后更新时间
        self.last_updated_label = QLabel("最后更新:")
        self.last_updated_value = QLabel("未设置")
        form_layout.addRow(self.last_updated_label, self.last_updated_value)
        
        # 添加API配置组
        main_layout.addWidget(api_group)
        
        # 按钮布局
        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        
        # 测试连接按钮
        self.test_btn = QPushButton("测试连接")
        self.test_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #45a049; }
            QPushButton:pressed { background-color: #3d8b40; }
        """)
        self.test_btn.clicked.connect(self.test_connection)
        
        # 确定按钮
        ok_btn = QPushButton("确定")
        ok_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #1976D2; }
            QPushButton:pressed { background-color: #1565C0; }
        """)
        ok_btn.clicked.connect(self.accept)
        
        # 取消按钮
        cancel_btn = QPushButton("取消")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
                min-width: 100px;
            }
            QPushButton:hover { background-color: #757575; }
            QPushButton:pressed { background-color: #616161; }
        """)
        cancel_btn.clicked.connect(self.reject)
        
        # 添加按钮到布局
        button_layout.addStretch()
        button_layout.addWidget(self.test_btn)
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
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
            QLineEdit, QComboBox {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
                min-width: 350px;
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
        self.model_edit.setText(model)
        
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
        model = self.model_edit.text().strip()
        
        # 验证输入
        if not api_url:
            QMessageBox.warning(self, "输入错误", "API URL 不能为空！")
            self.api_url_edit.setFocus()
            return
        
        if not api_key:
            QMessageBox.warning(self, "输入错误", "API Key 不能为空！")
            self.api_key_edit.setFocus()
            return
        
        if not model:
            QMessageBox.warning(self, "输入错误", "模型名称不能为空！")
            self.model_edit.setFocus()
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
        model = self.model_edit.text().strip()
        
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
