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
        self.setMinimumHeight(350)  # 增加高度以容纳新的控件
        self.setModal(True)
        
        self.selected_font = current_font
        self.font_manager = FontManager()
        self.user_input_name = ""  # 用户自定义输入的字体名称
        
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
        
        # 获取字体列表及其显示名称
        all_fonts = self.font_manager.get_all_fonts()
        
        # 创建显示名称到系统名称的映射（用于选择时转换回系统名称）
        self.display_to_system_mapping = {}
        
        # 获取所有字体的显示名称
        display_fonts = []
        for font in all_fonts:
            display_name = self.font_manager.get_font_display_name(font)
            if display_name not in display_fonts:
                display_fonts.append(display_name)
                self.display_to_system_mapping[display_name] = font
        
        # 将字体分为中文字体和非中文字体
        chinese_fonts = []
        other_fonts = []
        
        # 判断是否为中文字体名称
        for font in display_fonts:
            # 判断字体名称是否包含中文字符
            if any('一' <= char <= '鿿' for char in font):
                chinese_fonts.append(font)
            else:
                other_fonts.append(font)
        
        # 分别排序
        chinese_fonts.sort()
        other_fonts.sort()
        
        # 合并列表，中文字体在前
        sorted_fonts = chinese_fonts + other_fonts
        
        # 添加到下拉列表
        for font in sorted_fonts:
            self.font_list.addItem(font)
        
        # 设置当前字体的显示名称
        display_font = self.font_manager.get_font_display_name(self.selected_font)
        index = self.font_list.findText(display_font)
        if index >= 0:
            self.font_list.setCurrentIndex(index)
        else:
            # 如果找不到显示名称，尝试原始字体名称
            index = self.font_list.findText(self.selected_font)
            if index >= 0:
                self.font_list.setCurrentIndex(index)
            else:
                self.font_list.setEditText(self.selected_font)
        
        # 添加自定义字体名称输入框
        custom_group = QGroupBox("自定义字体名称")
        custom_layout = QVBoxLayout()
        
        # 添加说明文字
        custom_layout.addWidget(QLabel("如果需要使用特定字体名称（如微软雅黑），可在下方输入"))
        
        # 自定义名称输入框
        self.custom_name_input = QLineEdit()
        self.custom_name_input.setPlaceholderText("输入自定义字体名称（可选）")
        custom_layout.addWidget(self.custom_name_input)
        
        custom_group.setLayout(custom_layout)
        
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
        layout.addWidget(custom_group)  # 添加自定义字体组
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
    
    def accept(self):
        """
        对话框接受时的处理
        """
        # 保存当前选择的字体
        self.selected_font = self.font_list.currentText()
        
        # 保存用户输入的自定义字体名称
        self.user_input_name = self.custom_name_input.text().strip()
        
        # 调用父类的accept方法
        super().accept()
    
    def get_user_input(self):
        """
        获取用户输入的自定义字体名称
        
        Returns:
            str: 用户输入的自定义字体名称，如果没有输入则返回空字符串
        """
        return self.user_input_name
        
    def get_selected_font(self):
        """
        获取选择的字体
        
        Returns:
            str: 系统可用的字体名称
        """
        # 获取用户选择的显示名称
        display_name = self.selected_font
        
        # 如果显示名称在映射中，返回对应的系统名称
        if display_name in self.display_to_system_mapping:
            system_name = self.display_to_system_mapping[display_name]
            if self.font_manager.is_font_available(system_name):
                return system_name
        
        # 如果显示名称可用，直接返回
        if self.font_manager.is_font_available(display_name):
            return display_name
        
        # 如果都不可用，返回后备字体
        return self.font_manager.get_available_font(display_name)


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
        self.rules_table.setColumnCount(6)
        self.rules_table.setHorizontalHeaderLabels(["元素类型", "字体", "字号", "粗体", "行间距", "对齐方式"])
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
            
            # 检查是否有保存的显示名称
            if "font_display_name" in rule:
                display_name = rule["font_display_name"]
            else:
                # 获取字体的显示名称（优先使用中文名称）
                display_name = self.font_manager.get_font_display_name(available_font)
            
            font_item = QTableWidgetItem(display_name)
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
            
            # 对齐方式
            alignment = rule.get("alignment", "left")
            alignment_display = {
                "left": "左对齐",
                "center": "居中",
                "right": "右对齐",
                "justify": "两端对齐"
            }.get(alignment, "左对齐")
            alignment_item = QTableWidgetItem(alignment_display)
            self.rules_table.setItem(i, 5, alignment_item)
        
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
        
        # 创建字体管理器实例
        font_manager = FontManager()
        
        for row in range(self.rules_table.rowCount()):
            element_type = self.rules_table.item(row, 0).text()
            font_display_name = self.rules_table.item(row, 1).text()  # 这已经是显示名称
            size = self.rules_table.item(row, 2).text()
            bold = self.rules_table.item(row, 3).text()
            spacing = self.rules_table.item(row, 4).text()
            alignment = self.rules_table.item(row, 5).text()
            
            # 创建带格式的预览文本
            rule_text = f"- {element_type}: {font_display_name} {size} {bold} 行距{spacing} {alignment}"
            
            # 应用字体预览
            cursor = self.preview_text.textCursor()
            format = cursor.charFormat()
            
            # 获取系统字体名称（用于实际应用）
            system_font_name = font_display_name
            
            # 如果在映射中有对应的系统字体名称，使用系统字体名称
            if font_display_name in font_manager.font_mapping:
                system_font_name = font_manager.font_mapping[font_display_name]
            
            # 确保字体可用
            if not font_manager.is_font_available(system_font_name):
                system_font_name = font_manager.get_available_font(system_font_name)
            
            # 设置字体
            preview_font = QFont(system_font_name)
            
            # 设置粗体
            preview_font.setBold(bold == "是")
            
            # 应用字体
            format.setFont(preview_font)
            self.preview_text.append("")
            self.preview_text.setCurrentCharFormat(format)
            self.preview_text.insertPlainText(rule_text)
            
            # 设置对齐方式（仅用于预览效果）
            block_format = self.preview_text.textCursor().blockFormat()
            if alignment == "左对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignLeft)
            elif alignment == "居中":
                block_format.setAlignment(Qt.AlignmentFlag.AlignCenter)
            elif alignment == "右对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignRight)
            elif alignment == "两端对齐":
                block_format.setAlignment(Qt.AlignmentFlag.AlignJustify)
            
            # 应用对齐方式到当前段落
            cursor = self.preview_text.textCursor()
            cursor.movePosition(cursor.MoveOperation.End)
            cursor.setBlockFormat(block_format)
    
    def add_rule(self):
        """
        添加新规则
        """
        # 获取当前行数
        row_count = self.rules_table.rowCount()
        self.rules_table.setRowCount(row_count + 1)
        
        # 设置默认值
        self.rules_table.setItem(row_count, 0, QTableWidgetItem("自定义"))
        self.rules_table.setItem(row_count, 1, QTableWidgetItem("宋体"))
        self.rules_table.setItem(row_count, 2, QTableWidgetItem("五号"))
        self.rules_table.setItem(row_count, 3, QTableWidgetItem("否"))
        self.rules_table.setItem(row_count, 4, QTableWidgetItem("1.5"))
        self.rules_table.setItem(row_count, 5, QTableWidgetItem("左对齐"))
        
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
            
            # 获取对齐方式
            alignment_display = self.rules_table.item(row, 5).text().strip()
            alignment_map = {
                "左对齐": "left",
                "居中": "center",
                "右对齐": "right",
                "两端对齐": "justify"
            }
            alignment = alignment_map.get(alignment_display, "left")
            
            # 使用用户选择的字体名称，不进行自动映射
            system_font = font
            
            # 验证字体是否可用
            if not self.font_manager.is_font_available(system_font):
                available_font = self.font_manager.get_available_font(system_font)
                reply = QMessageBox.question(
                    self,
                    "字体不可用",
                    f"字体 '{font}' 在系统中不可用，是否使用 '{self.font_manager.get_font_display_name(available_font)}' 替代？",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    system_font = available_font
                    # 更新表格中的字体（显示名称）
                    display_name = self.font_manager.get_font_display_name(available_font)
                    self.rules_table.item(row, 1).setText(display_name)
            
            # 添加到规则字典
            rules[element_type] = {
                "font": system_font,  # 使用系统字体名称而不是显示名称
                "size": size,
                "bold": bold,
                "line_spacing": spacing,
                "alignment": alignment,
                "font_display_name": font  # 保存显示名称，便于后续显示
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
        elif column == 5:  # 对齐方式列
            self.edit_alignment(row, column)
    
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
            # 获取系统可用的字体名称
            system_font = dialog.get_selected_font()
            
            # 获取字体的显示名称（中文名称）
            font_manager = FontManager()
            display_name = font_manager.get_font_display_name(system_font)
            
            # 如果用户输入了自定义名称，使用用户输入的名称
            user_input = dialog.get_user_input()
            if user_input:
                display_name = user_input
                
                # 不再自动创建字体映射，直接使用用户输入的名称
                # font_manager.add_font_mapping(display_name, system_font)
            
            # 在表格中显示字体名称
            self.rules_table.setItem(row, column, QTableWidgetItem(display_name))
            
            # 更新预览
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
            
    def edit_alignment(self, row, column):
        """
        编辑对齐方式
        
        Args:
            row: 行索引
            column: 列索引
        """
        current_alignment = self.rules_table.item(row, column).text()
        
        # 创建对齐方式编辑对话框
        dialog = QDialog(self)
        dialog.setWindowTitle("设置对齐方式")
        dialog.setMinimumWidth(250)
        
        layout = QVBoxLayout(dialog)
        
        # 创建对齐方式下拉框
        alignment_combo = QComboBox()
        alignment_options = ["左对齐", "居中", "右对齐", "两端对齐"]
        for option in alignment_options:
            alignment_combo.addItem(option)
        
        # 设置当前对齐方式
        index = alignment_combo.findText(current_alignment)
        if index >= 0:
            alignment_combo.setCurrentIndex(index)
        
        # 按钮
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        
        # 添加到布局
        layout.addWidget(QLabel("选择对齐方式:"))
        layout.addWidget(alignment_combo)
        layout.addWidget(button_box)
        
        if dialog.exec():
            selected_alignment = alignment_combo.currentText()
            self.rules_table.setItem(row, column, QTableWidgetItem(selected_alignment))
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
