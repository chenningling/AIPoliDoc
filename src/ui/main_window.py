# -*- coding: utf-8 -*-
"""
主窗口模块
负责创建和管理应用程序的主窗口界面。
"""

import os
import sys
import time
import subprocess
from PyQt6.QtWidgets import (QMainWindow, QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                           QLabel, QPushButton, QFileDialog, QProgressBar, QTextEdit,
                           QComboBox, QGroupBox, QGridLayout, QMessageBox, QSplitter,
                           QDialog, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QColor, QPalette

from ..core.doc_processor import DocProcessor
from ..core.ai_connector import AIConnector
from ..core.format_manager import FormatManager
from ..core.structure_analyzer import StructureAnalyzer
from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..utils.file_utils import is_valid_docx

from .api_config_dialog import ApiConfigDialog
from .template_editor import TemplateEditorDialog


class FormattingCompleteDialog(QDialog):
    """
    排版完成对话框，显示成功消息并提供打开文档按钮
    """
    def __init__(self, parent=None, message=""):
        super().__init__(parent)
        self.message = message
        self.setWindowTitle("排版完成")
        self.setup_ui()
        
    def setup_ui(self):
        # 创建布局
        layout = QVBoxLayout(self)
        
        # 添加消息标签
        message_label = QLabel(f"文档排版已完成！\n文件已保存为: {self.message}")
        message_label.setWordWrap(True)
        layout.addWidget(message_label)
        
        # 创建按钮盒子
        button_box = QDialogButtonBox()
        
        # 添加标准按钮（确定）
        self.ok_button = button_box.addButton(QDialogButtonBox.StandardButton.Ok)
        
        # 添加自定义按钮（打开文档）
        self.open_doc_button = QPushButton("打开文档")
        button_box.addButton(self.open_doc_button, QDialogButtonBox.ButtonRole.ActionRole)
        
        # 连接信号和槽
        button_box.accepted.connect(self.accept)
        self.open_doc_button.clicked.connect(self.open_document)
        
        layout.addWidget(button_box)
        self.setLayout(layout)
        
    def open_document(self):
        """打开已排版的文档"""
        try:
            # 根据操作系统选择打开方式
            if sys.platform == "win32":
                os.startfile(self.message)
            elif sys.platform == "darwin":  # macOS
                subprocess.run(["open", self.message])
            else:  # Linux
                subprocess.run(["xdg-open", self.message])
                
            app_logger.info(f"已打开文档: {self.message}")
        except Exception as e:
            app_logger.error(f"打开文档失败: {str(e)}")
            QMessageBox.warning(self.parent(), "打开失败", f"无法打开文档！\n错误: {str(e)}")


class FormattingWorker(QThread):
    """排版工作线程，用于后台执行排版任务"""
    
    # 信号定义
    progress_updated = pyqtSignal(int)  # 进度更新信号
    log_message = pyqtSignal(str)  # 日志消息信号
    task_completed = pyqtSignal(bool, str)  # 任务完成信号，参数为是否成功和消息
    
    def __init__(self, doc_processor, ai_connector, format_manager, structure_analyzer, doc_path, template_name, save_path=None):
        super().__init__()
        self.doc_processor = doc_processor
        self.ai_connector = ai_connector
        self.format_manager = format_manager
        self.structure_analyzer = structure_analyzer
        self.doc_path = doc_path
        self.template_name = template_name
        self.save_path = save_path
        self.is_running = False
    
    def run(self):
        """执行排版任务"""
        self.is_running = True
        success = False
        output_file = ""
        
        try:
            # 更新进度和日志
            self.progress_updated.emit(5)
            self.log_message.emit("开始读取文档...")
            
            # 读取文档
            if not self.doc_processor.read_document(self.doc_path):
                self.log_message.emit("读取文档失败！")
                self.task_completed.emit(False, "读取文档失败")
                return
            
            # 获取文档内容
            self.progress_updated.emit(15)
            self.log_message.emit("文档读取成功，开始分析文档结构...")
            doc_content = self.doc_processor.get_document_text()
            
            # 分析文档结构
            features = self.structure_analyzer.analyze_text_features(doc_content)
            structure_hints = self.structure_analyzer.generate_structure_hints(features)
            
            self.progress_updated.emit(25)
            self.log_message.emit(f"文档结构分析完成，发现 {len(features.get('potential_titles', []))} 个潜在标题")
            
            # 获取排版模板
            template = self.format_manager.get_template(self.template_name)
            if not template:
                self.log_message.emit(f"模板 '{self.template_name}' 不存在，使用默认模板")
                template = self.format_manager.create_default_template()
            
            # 构建AI提示词
            self.progress_updated.emit(35)
            self.log_message.emit("正在生成AI提示词...")
            prompt = self.ai_connector.generate_prompt(doc_content, template.get('rules', {}))
            
            # 发送请求到AI API
            self.progress_updated.emit(45)
            self.log_message.emit("正在发送请求到AI API...")
            success, response = self.ai_connector.send_request(prompt)
            
            if not success:
                self.log_message.emit(f"AI API请求失败: {response}")
                self.task_completed.emit(False, "AI API请求失败")
                return
            
            # 解析AI响应
            self.progress_updated.emit(65)
            self.log_message.emit("AI响应成功，正在解析响应...")
            success, formatting_instructions = self.ai_connector.parse_response(response)
            
            if not success:
                self.log_message.emit(f"解析AI响应失败: {formatting_instructions}")
                self.task_completed.emit(False, "解析AI响应失败")
                return
            
            # 验证结构
            self.progress_updated.emit(75)
            self.log_message.emit("正在验证文档结构...")
            valid, formatting_instructions = self.structure_analyzer.validate_structure(formatting_instructions)
            
            if not valid:
                self.log_message.emit("文档结构验证失败，将使用部分识别结果")
            
            # 应用排版
            self.progress_updated.emit(85)
            self.log_message.emit("正在应用排版格式...")
            
            # 使用自定义保存路径
            if self.save_path:
                self.log_message.emit(f"将使用自定义保存路径: {self.save_path}")
                if not self.doc_processor.apply_formatting(formatting_instructions, self.save_path):
                    self.log_message.emit("应用排版格式失败！")
                    self.task_completed.emit(False, "应用排版格式失败")
                    return
            else:
                self.log_message.emit("未指定保存路径，将保存到原文件目录")
                if not self.doc_processor.apply_formatting(formatting_instructions):
                    self.log_message.emit("应用排版格式失败！")
                    self.task_completed.emit(False, "应用排版格式失败")
                    return
            
            # 获取输出文件路径
            output_file = self.doc_processor.get_output_file()
            
            # 完成
            self.progress_updated.emit(100)
            self.log_message.emit(f"排版完成！文件已保存为: {output_file}")
            success = True
            
        except Exception as e:
            self.log_message.emit(f"排版过程发生错误: {str(e)}")
            success = False
        
        self.is_running = False
        self.task_completed.emit(success, output_file)
    
    def stop(self):
        """停止排版任务"""
        if self.is_running:
            self.log_message.emit("正在停止排版任务...")
            self.terminate()
            self.is_running = False

class MainWindow(QMainWindow):
    """应用程序主窗口"""
    
    def __init__(self):
        super().__init__()
        
        # 初始化核心组件
        self.doc_processor = DocProcessor()
        self.format_manager = FormatManager()
        self.structure_analyzer = StructureAnalyzer()
        
        # 加载API配置
        api_config = config_manager.get_api_config()
        self.ai_connector = AIConnector(api_config)
        
        # 加载应用配置
        self.app_config = config_manager.get_app_config()
        
        # 初始化UI
        self.init_ui()
        
        # 初始化工作线程
        self.formatting_worker = None
        
        # 添加日志处理器
        app_logger.add_ui_handler(self.update_log)
        
        # 加载模板列表
        self.load_templates()
        
        # 设置窗口标题和图标
        self.setWindowTitle("AI Word文档自动排版工具")
        
        # 日志
        app_logger.info("应用程序启动完成")
    
    def init_ui(self):
        """初始化用户界面"""
        # 设置窗口大小
        self.resize(900, 700)
        
        # 创建中央窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)
        
        # 顶部功能区
        top_section = self.create_top_section()
        main_layout.addLayout(top_section)
        
        # 中间日志区
        mid_section = self.create_mid_section()
        main_layout.addLayout(mid_section, 1)  # 1表示拉伸因子
        
        # 底部按钮区
        bottom_section = self.create_bottom_section()
        main_layout.addLayout(bottom_section)
        
        # 设置样式
        self.set_style()
    
    def create_top_section(self):
        """创建顶部功能区"""
        top_layout = QVBoxLayout()
        
        # 文档选择区
        doc_group = QGroupBox("文档选择")
        doc_layout = QGridLayout()
        
        self.doc_path_label = QLabel("请选择Word文档:")
        self.doc_path_value = QLabel("未选择文件")
        self.doc_path_value.setStyleSheet("color: gray;")
        self.select_doc_btn = QPushButton("浏览...")
        self.select_doc_btn.clicked.connect(self.select_document)
        
        doc_layout.addWidget(self.doc_path_label, 0, 0)
        doc_layout.addWidget(self.doc_path_value, 0, 1)
        doc_layout.addWidget(self.select_doc_btn, 0, 2)
        
        doc_group.setLayout(doc_layout)
        top_layout.addWidget(doc_group)
        
        # 排版规则区
        format_group = QGroupBox("排版规则")
        format_layout = QGridLayout()
        
        self.template_label = QLabel("选择排版模板:")
        self.template_combo = QComboBox()
        self.template_combo.currentIndexChanged.connect(self.on_template_changed)
        
        self.edit_template_btn = QPushButton("编辑模板")
        self.edit_template_btn.clicked.connect(self.edit_template)
        
        self.template_content = QTextEdit()
        self.template_content.setReadOnly(True)
        self.template_content.setMaximumHeight(100)
        
        format_layout.addWidget(self.template_label, 0, 0)
        format_layout.addWidget(self.template_combo, 0, 1)
        format_layout.addWidget(self.edit_template_btn, 0, 2)
        format_layout.addWidget(self.template_content, 1, 0, 1, 3)
        
        format_group.setLayout(format_layout)
        top_layout.addWidget(format_group)
        
        # 保存位置区
        save_group = QGroupBox("保存位置")
        save_layout = QGridLayout()
        
        self.save_path_label = QLabel("保存文件位置:")
        self.save_path_value = QLabel(self.app_config.get("save_path", "与源文件相同目录"))
        self.save_path_value.setStyleSheet("color: gray;")
        self.select_save_btn = QPushButton("浏览...")
        self.select_save_btn.clicked.connect(self.select_save_location)
        
        save_layout.addWidget(self.save_path_label, 0, 0)
        save_layout.addWidget(self.save_path_value, 0, 1)
        save_layout.addWidget(self.select_save_btn, 0, 2)
        
        save_group.setLayout(save_layout)
        top_layout.addWidget(save_group)
        
        # API配置按钮（放在右上角）
        api_layout = QHBoxLayout()
        api_layout.addStretch(1)
        
        self.api_config_btn = QPushButton("API配置")
        self.api_config_btn.clicked.connect(self.open_api_config)
        api_layout.addWidget(self.api_config_btn)
        
        top_layout.addLayout(api_layout)
        
        return top_layout
    
    def create_mid_section(self):
        """创建中间日志区"""
        mid_layout = QVBoxLayout()
        
        # 日志标签
        log_label = QLabel("处理日志")
        log_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        mid_layout.addWidget(log_label)
        
        # 日志文本框
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        mid_layout.addWidget(self.log_text)
        
        # 进度条
        progress_layout = QHBoxLayout()
        progress_label = QLabel("进度:")
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(progress_label)
        progress_layout.addWidget(self.progress_bar)
        
        mid_layout.addLayout(progress_layout)
        
        return mid_layout
    
    def create_bottom_section(self):
        """创建底部按钮区"""
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch(1)
        
        # 开始排版按钮
        self.start_btn = QPushButton("开始排版")
        self.start_btn.setEnabled(False)  # 初始禁用
        self.start_btn.clicked.connect(self.start_formatting)
        self.start_btn.setMinimumWidth(120)
        self.start_btn.setMinimumHeight(40)
        
        # 停止排版按钮
        self.stop_btn = QPushButton("停止排版")
        self.stop_btn.setEnabled(False)  # 初始禁用
        self.stop_btn.clicked.connect(self.stop_formatting)
        self.stop_btn.setMinimumWidth(120)
        self.stop_btn.setMinimumHeight(40)
        
        bottom_layout.addWidget(self.start_btn)
        bottom_layout.addWidget(self.stop_btn)
        
        return bottom_layout
    
    def set_style(self):
        """设置界面样式"""
        # 设置字体
        app = QApplication.instance()
        font = QFont("Microsoft YaHei", 10)
        app.setFont(font)
        
        # 设置按钮样式
        button_style = """
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #0D8AEE;
            }
            QPushButton:pressed {
                background-color: #0A6EBD;
            }
            QPushButton:disabled {
                background-color: #B3E5FC;
                color: #E1F5FE;
            }
        """
        
        self.start_btn.setStyleSheet(button_style)
        self.stop_btn.setStyleSheet(button_style)
        self.select_doc_btn.setStyleSheet(button_style)
        self.select_save_btn.setStyleSheet(button_style)
        self.edit_template_btn.setStyleSheet(button_style)
        self.api_config_btn.setStyleSheet(button_style)
        
        # 设置分组框样式
        group_style = """
            QGroupBox {
                border: 1px solid #BBDEFB;
                border-radius: 5px;
                margin-top: 1ex;
                font-weight: bold;
                color: #1976D2;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 5px;
            }
        """
        
        # 设置文本框样式
        text_style = """
            QTextEdit {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                background-color: #FFFFFF;
            }
        """
        
        self.log_text.setStyleSheet(text_style)
        self.template_content.setStyleSheet(text_style)
    
    def load_templates(self):
        """加载排版模板列表"""
        self.template_combo.clear()
        
        template_names = self.format_manager.get_template_names()
        for name in template_names:
            self.template_combo.addItem(name)
        
        # 设置默认模板
        default_template = self.app_config.get("last_template", "默认模板")
        index = self.template_combo.findText(default_template)
        if index >= 0:
            self.template_combo.setCurrentIndex(index)
        elif self.template_combo.count() > 0:
            self.template_combo.setCurrentIndex(0)
    
    def on_template_changed(self, index):
        """模板选择变更事件"""
        if index < 0:
            return
        
        template_name = self.template_combo.currentText()
        template_text = self.format_manager.get_template_as_text(template_name)
        self.template_content.setText(template_text)
        
        # 保存最后使用的模板
        self.app_config["last_template"] = template_name
        config_manager.save_app_config(self.app_config)
    
    def select_document(self):
        """选择Word文档"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "选择Word文档",
            "",
            "Word文档 (*.docx)"
        )
        
        if file_path:
            # 验证文档有效性
            if not is_valid_docx(file_path):
                QMessageBox.warning(self, "无效文档", "所选文件不是有效的Word文档！")
                return
            
            self.doc_path_value.setText(file_path)
            self.doc_path_value.setStyleSheet("color: black;")
            app_logger.info(f"已选择文档: {file_path}")
            
            # 启用开始按钮
            self.start_btn.setEnabled(True)
    
    def select_save_location(self):
        """选择保存位置"""
        file_dialog = QFileDialog()
        save_dir = file_dialog.getExistingDirectory(
            self,
            "选择保存位置",
            self.app_config.get("save_path", "")
        )
        
        if save_dir:
            self.save_path_value.setText(save_dir)
            self.save_path_value.setStyleSheet("color: black;")
            app_logger.info(f"已设置保存位置: {save_dir}")
            
            # 更新配置
            self.app_config["save_path"] = save_dir
            config_manager.save_app_config(self.app_config)
    
    def open_api_config(self):
        """打开API配置对话框"""
        dialog = ApiConfigDialog(self)
        if dialog.exec():
            # 更新AI连接器
            api_config = config_manager.get_api_config()
            self.ai_connector = AIConnector(api_config)
            app_logger.info("API配置已更新")
    
    def edit_template(self):
        """编辑排版模板"""
        template_name = self.template_combo.currentText()
        template = self.format_manager.get_template(template_name)
        
        dialog = TemplateEditorDialog(self, template_name, template)
        if dialog.exec():
            # 重新加载所有模板
            self.format_manager.load_templates()  # 先重新从文件系统加载模板
            self.load_templates()  # 然后更新UI显示
            
            # 获取新的模板名称（可能已更改）
            new_template_name = dialog.get_template_name()
            if new_template_name != template_name:
                app_logger.info(f"模板名称已从 '{template_name}' 更改为 '{new_template_name}'")
                # 选中新的模板
                index = self.template_combo.findText(new_template_name)
                if index >= 0:
                    self.template_combo.setCurrentIndex(index)
            else:
                app_logger.info(f"模板 '{template_name}' 已更新")
    
    def update_log(self, message, level="INFO"):
        """更新日志显示"""
        # 根据日志级别设置颜色
        color = "black"
        if level == "ERROR":
            color = "red"
        elif level == "WARNING":
            color = "orange"
        elif level == "INFO":
            color = "blue"
        
        # 添加时间戳
        timestamp = time.strftime("%H:%M:%S", time.localtime())
        formatted_message = f"<span style='color:{color};'>[{timestamp}] {message}</span>"
        
        # 添加到日志文本框
        self.log_text.append(formatted_message)
        
        # 滚动到底部
        scrollbar = self.log_text.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_formatting(self):
        """开始排版"""
        # 检查文档是否已选择
        doc_path = self.doc_path_value.text()
        if doc_path == "未选择文件" or not os.path.exists(doc_path):
            QMessageBox.warning(self, "错误", "请先选择有效的Word文档！")
            return
        
        # 检查API配置
        valid, error_msg = self.ai_connector.validate_config()
        if not valid:
            QMessageBox.warning(self, "API配置错误", f"API配置无效，请先配置API信息！\n错误: {error_msg}")
            self.open_api_config()
            return
        
        # 获取当前模板
        template_name = self.template_combo.currentText()
        if not template_name:
            QMessageBox.warning(self, "错误", "请先选择排版模板！")
            return
        
        # 获取保存路径
        save_path = self.save_path_value.text()
        if save_path == "与源文件相同目录":
            save_path = None
        
        # 创建工作线程
        self.formatting_worker = FormattingWorker(
            self.doc_processor,
            self.ai_connector,
            self.format_manager,
            self.structure_analyzer,
            doc_path,
            template_name,
            save_path
        )
        
        # 更新应用配置
        if save_path and save_path != self.app_config.get("save_path", ""):
            self.app_config["save_path"] = save_path
            config_manager.save_app_config(self.app_config)
            app_logger.debug(f"已更新保存路径配置: {save_path}")
        
        # 连接信号
        self.formatting_worker.progress_updated.connect(self.update_progress)
        self.formatting_worker.log_message.connect(lambda msg: self.update_log(msg, "INFO"))
        self.formatting_worker.task_completed.connect(self.on_formatting_completed)
        
        # 更新UI状态
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.progress_bar.setValue(0)
        
        # 启动线程
        self.formatting_worker.start()
        app_logger.info("开始排版任务")
    
    def stop_formatting(self):
        """停止排版"""
        if self.formatting_worker and self.formatting_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认停止",
                "确定要停止当前排版任务吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.formatting_worker.stop()
                app_logger.warning("排版任务已手动停止")
                
                # 更新UI状态
                self.start_btn.setEnabled(True)
                self.stop_btn.setEnabled(False)
    
    def update_progress(self, value):
        """更新进度条"""
        self.progress_bar.setValue(value)
    
    def on_formatting_completed(self, success, message):
        """排版完成回调"""
        # 更新UI状态
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        
        if success:
            # 使用自定义对话框，提供“打开文档”按钮
            dialog = FormattingCompleteDialog(self, message)
            dialog.exec()
            app_logger.info(f"排版任务成功完成，输出文件: {message}")
        else:
            QMessageBox.critical(self, "排版失败", f"文档排版失败！\n错误: {message}")
            app_logger.error(f"排版任务失败: {message}")
    
    def closeEvent(self, event):
        """窗口关闭事件"""
        # 停止所有正在运行的任务
        if self.formatting_worker and self.formatting_worker.isRunning():
            reply = QMessageBox.question(
                self,
                "确认退出",
                "排版任务正在进行中，确定要退出吗？",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.formatting_worker.stop()
                app_logger.info("应用程序正在关闭，排版任务已停止")
            else:
                event.ignore()
                return
        
        # 保存配置
        config_manager.save_app_config(self.app_config)
        
        # 移除日志处理器
        app_logger.remove_ui_handler(self.update_log)
        
        app_logger.info("应用程序正常关闭")
        event.accept()
