# -*- coding: utf-8 -*-
"""
模板编辑器对话框模块
负责创建和管理模板编辑器对话框，用于编辑排版模板。
"""

import os
import json
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QLineEdit, QPushButton, QFormLayout, QComboBox,
                           QMessageBox, QGroupBox, QDialogButtonBox, QTextEdit,
                           QTabWidget, QWidget, QTableWidget, QTableWidgetItem,
                           QHeaderView, QSpinBox, QDoubleSpinBox, QCheckBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

from ..utils.logger import app_logger
from ..utils.config_manager import config_manager
from ..utils.font_manager import FontManager
from ..core.format_manager import FormatManager

class FontSelectionDialog(QDialog):
    """
    字体选择对话框，用于选择系统中可用的字体
    """
    def __init__(self, parent=None, current_font="宋体"):
        super().__init__(parent)
        self.setWindowTitle("选择字体")
        self.setMinimumWidth(400)
        self.setMinimumHeight(300)
        self.setModal(True)
        
        self.selected_font = current_font
        self.font_manager = FontManager()
        
        # 初始化UI
        self.init_ui()
        
    def init_ui(self):
        """
        初始化用户界面
        """
        layout = QVBoxLayout(self)
        
        # 创建字体列表
        self.font_list = QComboBox()
        self.font_list.setEditable(True)  # 允许用户输入
        
        # 加载中文字体优先
        chinese_fonts = self.font_manager.get_chinese_fonts()
        all_fonts = self.font_manager.get_all_fonts()
        
        # 添加中文字体（优先显示）
        for font in chinese_fonts:
            self.font_list.addItem(font)
        
        # 添加其他字体
        for font in all_fonts:
            if font not in chinese_fonts:
                self.font_list.addItem(font)
        
        # 设置当前字体
        index = self.font_list.findText(self.selected_font)
        if index >= 0:
            self.font_list.setCurrentIndex(index)
        else:
            self.font_list.setEditText(self.selected_font)
        
        # 字体预览
        self.preview_label = QLabel("字体预览: 中文ABC123")
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setMinimumHeight(100)
        self.update_preview(self.selected_font)
        
        # 连接信号
        self.font_list.currentTextChanged.connect(self.update_preview)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # 添加到布局
        layout.addWidget(QLabel("选择字体:"))
        layout.addWidget(self.font_list)
        layout.addWidget(QLabel("预览:"))
        layout.addWidget(self.preview_label)
        layout.addWidget(button_box)
        
    def update_preview(self, font_name):
        """
        更新字体预览
        """
        try:
            preview_font = QFont(font_name, 14)  # 使用14磅大小便于预览
            self.preview_label.setFont(preview_font)
            self.selected_font = font_name
        except Exception as e:
            app_logger.error(f"设置预览字体失败: {str(e)}")
    
    def get_selected_font(self):
        """
        获取选择的字体
        """
        return self.selected_font


class TemplateEditorDialog(QDialog):
    """模板编辑器对话框，用于编辑排版模板"""
    
    def __init__(self, parent=None, template_name="", template=None):
        """
        初始化模板编辑器对话框
        
        Args:
            parent: 父窗口
            template_name: 模板名称
            template: 模板内容
        """
        super().__init__(parent)
        
        # 设置窗口属性
        self.setWindowTitle("排版模板编辑器")
        self.setMinimumWidth(600)
        self.setMinimumHeight(500)
        self.setModal(True)
        
        # 初始化成员变量
        self.format_manager = FormatManager()
        self.font_manager = FontManager()  # 初始化字体管理器
        self.is_new_template = not template_name or not template
        self.template_name = template_name if not self.is_new_template else ""
        self.template = template if not self.is_new_template else self.format_manager.create_default_template()
        
        # 初始化UI
        self.init_ui()
        
        # 加载模板数据
        self.load_template()
    
    def init_ui(self):
        """
        初始化用户界面
        """
        # 主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 基本信息区域
        info_group = QGroupBox("基本信息")
        info_layout = QFormLayout(info_group)
        
        # 模板名称
        self.name_label = QLabel("模板名称:")
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("请输入模板名称")
        info_layout.addRow(self.name_label, self.name_edit)
        
        # 模板描述
        self.desc_label = QLabel("模板描述:")
        self.desc_edit = QLineEdit()
        self.desc_edit.setPlaceholderText("请输入模板描述")
        info_layout.addRow(self.desc_label, self.desc_edit)
        
        # 添加基本信息组
        main_layout.addWidget(info_group)
        
        # 规则编辑区域
        rules_group = QGroupBox("排版规则")
        rules_layout = QVBoxLayout(rules_group)
        
        # 创建表格
        self.rules_table = QTableWidget()
        self.rules_table.setColumnCount(5)
        self.rules_table.setHorizontalHeaderLabels(["元素类型", "字体", "字号", "粗体", "行间距"])
        self.rules_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.rules_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        
        # 设置表格单元格编辑方式
        self.rules_table.cellDoubleClicked.connect(self.on_cell_double_clicked)
        
        # 添加/删除按钮
        buttons_layout = QHBoxLayout()
        self.add_rule_btn = QPushButton("添加规则")
        self.add_rule_btn.clicked.connect(self.add_rule)
        self.remove_rule_btn = QPushButton("删除规则")
        self.remove_rule_btn.clicked.connect(self.remove_rule)
        buttons_layout.addWidget(self.add_rule_btn)
        buttons_layout.addWidget(self.remove_rule_btn)
        
        rules_layout.addWidget(self.rules_table)
        rules_layout.addLayout(buttons_layout)
        
        # 添加规则编辑组
        main_layout.addWidget(rules_group)
        
        # 预览区域
        preview_group = QGroupBox("预览")
        preview_layout = QVBoxLayout(preview_group)
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        preview_layout.addWidget(self.preview_text)
        
        # 添加预览组
        main_layout.addWidget(preview_group)
        
        # 按钮区域
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Save | 
                                     QDialogButtonBox.StandardButton.Cancel)
        # 将按钮文本改为中文
        save_button = button_box.button(QDialogButtonBox.StandardButton.Save)
        cancel_button = button_box.button(QDialogButtonBox.StandardButton.Cancel)
        if save_button:
            save_button.setText("保存")
            # 设置保存按钮为亮色
            save_button.setStyleSheet("""
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            """)
        if cancel_button:
            cancel_button.setText("取消")
            # 设置取消按钮为灰色
            cancel_button.setStyleSheet("""
                background-color: #9E9E9E;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px 15px;
            """)
            
        button_box.accepted.connect(self.save_template)
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
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox {
                border: 1px solid #BBDEFB;
                border-radius: 3px;
                padding: 5px;
            }
            QTableWidget {
                border: 1px solid #BBDEFB;
                gridline-color: #E3F2FD;
            }
            QHeaderView::section {
                background-color: #E3F2FD;
                padding: 4px;
                border: 1px solid #BBDEFB;
                font-weight: bold;
            }
        """)
    
    def load_template(self):
        """
        加载模板数据到UI
        """
        # 设置基本信息
        self.name_edit.setText(self.template.get("name", ""))
        self.desc_edit.setText(self.template.get("description", ""))
        
        # 加载规则
        rules = self.template.get("rules", {})
        self.rules_table.setRowCount(len(rules))
        
        for i, (element_type, rule) in enumerate(rules.items()):
            # 元素类型
            type_item = QTableWidgetItem(element_type)
            self.rules_table.setItem(i, 0, type_item)
            
            # 字体 - 验证字体是否可用
            font_name = rule.get("font", "宋体")
            available_font = self.font_manager.get_available_font(font_name)
            font_item = QTableWidgetItem(available_font)
            self.rules_table.setItem(i, 1, font_item)
            
            # 字号
            size_item = QTableWidgetItem(rule.get("size", "五号"))
            self.rules_table.setItem(i, 2, size_item)
            
            # 粗体
            bold_item = QTableWidgetItem("是" if rule.get("bold", False) else "否")
            self.rules_table.setItem(i, 3, bold_item)
            
            # 行间距
            spacing_item = QTableWidgetItem(str(rule.get("line_spacing", 1.5)))
            self.rules_table.setItem(i, 4, spacing_item)
        
        # 更新预览
        self.update_preview()
    
    def update_preview(self):
        """
        更新预览内容
        """
        # 构建预览文本
        preview = f"模板名称: {self.name_edit.text()}\n"
        preview += f"模板描述: {self.desc_edit.text()}\n\n"
        preview += "排版规则:\n"
        
        # 添加规则内容并应用字体预览
        self.preview_text.clear()
        self.preview_text.append(f"模板名称: {self.name_edit.text()}")
        self.preview_text.append(f"模板描述: {self.desc_edit.text()}\n")
        self.preview_text.append("排版规则:")
        
        for row in range(self.rules_table.rowCount()):
            element_type = self.rules_table.item(row, 0).text()
            font = self.rules_table.item(row, 1).text()
            size = self.rules_table.item(row, 2).text()
            bold = self.rules_table.item(row, 3).text()
            spacing = self.rules_table.item(row, 4).text()
            
            # 创建带格式的预览文本
            rule_text = f"- {element_type}: {font} {size} {bold} 行距{spacing}"
            
            # 应用字体预览
            cursor = self.preview_text.textCursor()
            format = cursor.charFormat()
            
            # 设置字体
            preview_font = QFont(font)
            
            # 设置粗体
            preview_font.setBold(bold == "是")
            
            # 应用字体
            format.setFont(preview_font)
            self.preview_text.append("")
            self.preview_text.setCurrentCharFormat(format)
            self.preview_text.insertPlainText(rule_text)
    
    def add_rule(self):
        """
        添加新规则
        """
        # 获取当前行数
        row_count = self.rules_table.rowCount()
        self.rules_table.setRowCount(row_count + 1)
        
        # 设置默认值
        self.rules_table.setItem(row_count, 0, QTableWidgetItem(f"新规则{row_count+1}"))
        self.rules_table.setItem(row_count, 1, QTableWidgetItem("宋体"))
        self.rules_table.setItem(row_count, 2, QTableWidgetItem("五号"))
        self.rules_table.setItem(row_count, 3, QTableWidgetItem("否"))
        self.rules_table.setItem(row_count, 4, QTableWidgetItem("1.5"))
        
        # 更新预览
        self.update_preview()
    
    def remove_rule(self):
        """
        删除选中的规则
        """
        # 获取选中的行
        selected_rows = set()
        for item in self.rules_table.selectedItems():
            selected_rows.add(item.row())
        
        # 如果没有选中行，提示用户
        if not selected_rows:
            QMessageBox.warning(self, "未选择", "请先选择要删除的规则！")
            return
        
        # 确认删除
        reply = QMessageBox.question(
            self,
            "确认删除",
            f"确定要删除选中的 {len(selected_rows)} 条规则吗？",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # 从后往前删除，避免索引变化
            for row in sorted(selected_rows, reverse=True):
                self.rules_table.removeRow(row)
            
            # 更新预览
            self.update_preview()
    
    def save_template(self):
        """
        保存模板
        """
        # 获取基本信息
        name = self.name_edit.text().strip()
        description = self.desc_edit.text().strip()
        
        # 验证名称
        if not name:
            QMessageBox.warning(self, "输入错误", "模板名称不能为空！")
            return
        
        # 构建规则字典
        rules = {}
        for row in range(self.rules_table.rowCount()):
            element_type = self.rules_table.item(row, 0).text().strip()
            font = self.rules_table.item(row, 1).text().strip()
            size = self.rules_table.item(row, 2).text().strip()
            bold = self.rules_table.item(row, 3).text().strip() == "是"
            
            # 解析行间距
            try:
                spacing = float(self.rules_table.item(row, 4).text().strip())
            except ValueError:
                spacing = 1.5
                QMessageBox.warning(self, "输入错误", f"规则 '{element_type}' 的行间距格式无效，已设为默认值1.5。")
            
            # 验证字体是否可用
            if not self.font_manager.is_font_available(font):
                available_font = self.font_manager.get_available_font(font)
                reply = QMessageBox.question(
                    self,
                    "字体不可用",
                    f"字体 '{font}' 在系统中不可用，是否使用 '{available_font}' 替代？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    font = available_font
                    # 更新表格中的字体
                    self.rules_table.item(row, 1).setText(font)
            
            # 添加到规则字典
            rules[element_type] = {
                "font": font,
                "size": size,
                "bold": bold,
                "line_spacing": spacing
            }
        
        # 构建模板
        template = {
            "name": name,
            "description": description,
            "rules": rules
        }
        
        # 验证模板
        is_valid, error_msg = self.format_manager.validate_template(template)
        if not is_valid:
            QMessageBox.warning(self, "模板无效", f"模板验证失败: {error_msg}")
            return
        
        # 保存模板
        if self.is_new_template:
            # 检查是否已存在同名模板
            if name in self.format_manager.get_template_names():
                reply = QMessageBox.question(
                    self,
                    "模板已存在",
                    f"已存在名为 '{name}' 的模板，是否覆盖？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.No
                )
                
                if reply != QMessageBox.StandardButton.Yes:
                    return
        
        # 保存模板
        success = self.format_manager.save_template(name, template)
        
        if success:
            app_logger.info(f"模板 '{name}' 已保存")
            QMessageBox.information(self, "保存成功", f"模板 '{name}' 已保存！")
            # 保存当前模板名称，以便主窗口可以获取
            self.template_name = name
            super().accept()
        else:
            app_logger.error(f"保存模板 '{name}' 失败")
            QMessageBox.critical(self, "保存失败", f"模板 '{name}' 保存失败！")
    
    def get_template_name(self):
        """
        获取当前模板名称
        
        Returns:
            str: 模板名称
        """
        return self.template_name
    
    def on_cell_double_clicked(self, row, column):
        """
        单元格双击事件处理
        
        Args:
            row: 行索引
            column: 列索引
        """
        # 根据列类型提供不同的编辑方式
        if column == 1:  # 字体列
            self.edit_font(row, column)
        elif column == 2:  # 字号列
            self.edit_size(row, column)
        elif column == 3:  # 粗体列
            self.edit_bold(row, column)
        elif column == 4:  # 行间距列
            self.edit_spacing(row, column)
    
    def edit_font(self, row, column):
        """
        编辑字体
        
        Args:
            row: 行索引
            column: 列索引
        """
        current_font = self.rules_table.item(row, column).text()
        dialog = FontSelectionDialog(self, current_font)
        
        if dialog.exec():
            selected_font = dialog.get_selected_font()
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_font))
            self.update_preview()
    
    def edit_size(self, row, column):
        """
        编辑字号
        
        Args:
            row: 行索引
            column: 列索引
        """
        current_size = self.rules_table.item(row, column).text()
        
        # 创建字号选择对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("选择字号")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # 创建字号下拉列表
        size_combo = QComboBox()
        size_combo.setEditable(True)
        
        # 添加常用字号
        standard_sizes = ["小二", "三号", "小三", "四号", "小四", "五号", "小五", "六号"]
        for size in standard_sizes:
            size_combo.addItem(size)
        
        # 设置当前字号
        index = size_combo.findText(current_size)
        if index >= 0:
            size_combo.setCurrentIndex(index)
        else:
            size_combo.setEditText(current_size)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # 添加到布局
        layout.addWidget(QLabel("选择字号:"))
        layout.addWidget(size_combo)
        layout.addWidget(button_box)
        
        if dialog.exec():
            selected_size = size_combo.currentText()
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_size))
            self.update_preview()
    
    def edit_bold(self, row, column):
        """
        编辑粗体设置
        
        Args:
            row: 行索引
            column: 列索引
        """
        current_bold = self.rules_table.item(row, column).text()
        new_bold = "否" if current_bold == "是" else "是"
        self.rules_table.setItem(row, column, QTableWidgetItem(new_bold))
        self.update_preview()
    
    def edit_spacing(self, row, column):
        """
        编辑行间距
        
        Args:
            row: 行索引
            column: 列索引
        """
        current_spacing = self.rules_table.item(row, column).text()
        
        # 创建行间距编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("设置行间距")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # 创建行间距输入框
        spacing_spin = QDoubleSpinBox()
        spacing_spin.setRange(0.5, 3.0)
        spacing_spin.setSingleStep(0.1)
        spacing_spin.setDecimals(1)
        
        try:
            spacing_spin.setValue(float(current_spacing))
        except ValueError:
            spacing_spin.setValue(1.5)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # 添加到布局
        layout.addWidget(QLabel("设置行间距:"))
        layout.addWidget(spacing_spin)
        layout.addWidget(button_box)
        
        if dialog.exec():
            selected_spacing = str(spacing_spin.value())
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_spacing))
            self.update_preview()
    
    def closeEvent(self, event):
        """
        窗口关闭事件
        """
        # 询问是否保存更改
        reply = QMessageBox.question(
            self,
            "确认关闭",
            "是否保存更改？",
            QMessageBox.StandardButton.Save | QMessageBox.StandardButton.Discard | QMessageBox.StandardButton.Cancel,
            QMessageBox.StandardButton.Save
        )
        
        if reply == QMessageBox.StandardButton.Save:
            self.save_template()
            event.accept()
        elif reply == QMessageBox.StandardButton.Discard:
            event.accept()
        else:
            event.ignore()
