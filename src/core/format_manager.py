# -*- coding: utf-8 -*-
"""
排版规则管理模块
负责管理和应用排版规则，包括加载预设模板、保存自定义模板等。
"""

import os
import json
import json5
from docx.shared import Pt
from ..utils.logger import app_logger

class FormatManager:
    """排版规则管理器，负责管理和应用排版规则"""
    
    def __init__(self, templates_dir="config/templates"):
        """
        初始化排版规则管理器
        
        Args:
            templates_dir: 模板目录路径
        """
        self.templates_dir = templates_dir
        self.templates = {}
        self.current_template = None
        self.current_template_name = ""
        
        # 字体大小映射表
        self.font_size_mapping = {
            "初号": Pt(42),
            "小初": Pt(36),
            "一号": Pt(26),
            "小一": Pt(24),
            "二号": Pt(22),
            "小二": Pt(18),
            "三号": Pt(16),
            "小三": Pt(15),
            "四号": Pt(14),
            "小四": Pt(12),
            "五号": Pt(10.5),
            "小五": Pt(9),
            "六号": Pt(7.5),
            "小六": Pt(6.5),
            "七号": Pt(5.5),
            "八号": Pt(5)
        }
        
        # 加载模板
        self.load_templates()
        
        app_logger.info(f"排版规则管理器初始化完成，加载了 {len(self.templates)} 个模板")
    
    def load_templates(self):
        """
        加载所有预设模板
        
        Returns:
            dict: 模板字典，键为模板名称，值为模板内容
        """
        self.templates = {}
        
        if not os.path.exists(self.templates_dir):
            app_logger.warning(f"模板目录不存在: {self.templates_dir}")
            return self.templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = json5.loads(f.read())
                        template_name = template.get('name', os.path.splitext(filename)[0])
                        self.templates[template_name] = template
                        app_logger.debug(f"加载模板: {template_name}")
                except Exception as e:
                    app_logger.error(f"加载模板失败: {template_path}, 错误: {str(e)}")
        
        return self.templates
    
    def get_templates(self):
        """
        获取所有模板
        
        Returns:
            dict: 模板字典
        """
        return self.templates
    
    def get_template_names(self):
        """
        获取所有模板名称
        
        Returns:
            list: 模板名称列表
        """
        return list(self.templates.keys())
    
    def get_template(self, template_name):
        """
        获取指定名称的模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            dict: 模板内容，如果模板不存在则返回None
        """
        return self.templates.get(template_name)
    
    def set_current_template(self, template_name):
        """
        设置当前使用的模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 是否成功设置
        """
        if template_name not in self.templates:
            app_logger.warning(f"模板不存在: {template_name}")
            return False
        
        self.current_template = self.templates[template_name]
        self.current_template_name = template_name
        app_logger.info(f"设置当前模板: {template_name}")
        return True
    
    def get_current_template(self):
        """
        获取当前模板
        
        Returns:
            dict: 当前模板内容
        """
        return self.current_template
    
    def save_template(self, template_name, template_content):
        """
        保存模板
        
        Args:
            template_name: 模板名称
            template_content: 模板内容
            
        Returns:
            bool: 是否成功保存
        """
        # 确保模板有name字段
        if 'name' not in template_content:
            template_content['name'] = template_name
        
        # 更新内存中的模板
        self.templates[template_name] = template_content
        
        # 保存到文件
        # 记录保存路径信息，方便调试
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        app_logger.debug(f"模板保存路径: {template_file}")
        
        try:
            # 确保模板目录存在
            if not os.path.exists(self.templates_dir):
                os.makedirs(self.templates_dir)
                app_logger.debug(f"创建模板目录: {self.templates_dir}")
            
            # 先删除同名模板文件（如果存在）
            if os.path.exists(template_file):
                os.remove(template_file)
                app_logger.debug(f"删除原模板文件: {template_file}")
            
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_content, f, ensure_ascii=False, indent=4)
                app_logger.info(f"保存模板: {template_name}")
                
                # 验证文件是否写入成功
                if os.path.exists(template_file):
                    app_logger.debug(f"模板文件写入成功: {template_file}")
                else:
                    app_logger.error(f"模板文件写入失败: {template_file}")
                    
                return True
        except Exception as e:
            app_logger.error(f"保存模板失败: {template_name}, 错误: {str(e)}")
            return False
    
    def delete_template(self, template_name):
        """
        删除模板
        
        Args:
            template_name: 模板名称
            
        Returns:
            bool: 是否成功删除
        """
        if template_name not in self.templates:
            app_logger.warning(f"模板不存在: {template_name}")
            return False
        
        # 从内存中删除
        del self.templates[template_name]
        
        # 从文件系统中删除
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        if os.path.exists(template_file):
            try:
                os.remove(template_file)
                app_logger.info(f"删除模板: {template_name}")
                return True
            except Exception as e:
                app_logger.error(f"删除模板文件失败: {template_name}, 错误: {str(e)}")
                return False
        return True
    
    def create_default_template(self):
        """
        创建默认模板
        
        Returns:
            dict: 默认模板内容
        """
        default_template = {
            "name": "默认模板",
            "description": "基本排版模板，适用于一般文档",
            "rules": {
                "标题": {
                    "font": "黑体",
                    "size": "小二",
                    "bold": True,
                    "line_spacing": 1.0
                },
                "一级标题": {
                    "font": "黑体",
                    "size": "五号",
                    "bold": True,
                    "line_spacing": 1.5
                },
                "二级标题": {
                    "font": "宋体",
                    "size": "五号",
                    "bold": True,
                    "line_spacing": 1.5
                },
                "正文": {
                    "font": "宋体",
                    "size": "五号",
                    "bold": False,
                    "line_spacing": 19
                }
            }
        }
        return default_template
    
    def format_to_docx_params(self, format_instruction):
        """
        将格式指令转换为docx参数
        
        Args:
            format_instruction: 格式指令
            
        Returns:
            dict: docx参数
        """
        docx_params = {}
        
        # 字体名称
        if 'font' in format_instruction:
            docx_params['font_name'] = format_instruction['font']
        
        # 字体大小
        if 'size' in format_instruction:
            size = format_instruction['size']
            if isinstance(size, str):
                docx_params['font_size'] = self.font_size_mapping.get(size, Pt(10.5))  # 默认五号字体
            else:
                docx_params['font_size'] = Pt(size)
        
        # 粗体
        if 'bold' in format_instruction:
            docx_params['bold'] = format_instruction['bold']
        
        # 斜体
        if 'italic' in format_instruction:
            docx_params['italic'] = format_instruction['italic']
        
        # 下划线
        if 'underline' in format_instruction:
            docx_params['underline'] = format_instruction['underline']
        
        # 行间距
        if 'line_spacing' in format_instruction:
            docx_params['line_spacing'] = format_instruction['line_spacing']
        
        # 对齐方式
        if 'alignment' in format_instruction:
            docx_params['alignment'] = format_instruction['alignment']
        
        # 首行缩进
        if 'first_line_indent' in format_instruction:
            docx_params['first_line_indent'] = format_instruction['first_line_indent']
        
        return docx_params
    
    def validate_template(self, template):
        """
        验证模板格式是否正确
        
        Args:
            template: 模板内容
            
        Returns:
            (bool, str): 是否有效及错误信息
        """
        # 检查必要字段
        if 'name' not in template:
            return False, "模板缺少name字段"
        
        if 'rules' not in template:
            return False, "模板缺少rules字段"
        
        rules = template['rules']
        if not isinstance(rules, dict):
            return False, "rules字段必须是字典类型"
        
        # 检查每个规则
        for element_type, format_rule in rules.items():
            if not isinstance(format_rule, dict):
                return False, f"规则 '{element_type}' 必须是字典类型"
            
            # 检查必要的格式字段
            if 'font' not in format_rule:
                return False, f"规则 '{element_type}' 缺少font字段"
            
            if 'size' not in format_rule:
                return False, f"规则 '{element_type}' 缺少size字段"
        
        return True, ""
    
    def get_template_as_text(self, template_name):
        """
        获取模板的文本表示，用于显示
        
        Args:
            template_name: 模板名称
            
        Returns:
            str: 模板的文本表示
        """
        template = self.get_template(template_name)
        if not template:
            return ""
        
        text = f"{template.get('name', template_name)}\n"
        if 'description' in template:
            text += f"{template['description']}\n"
        
        text += "\n格式规则:\n"
        
        for element_type, format_rule in template.get('rules', {}).items():
            text += f"{element_type}: "
            format_parts = []
            
            if 'font' in format_rule:
                format_parts.append(f"{format_rule['font']}")
            
            if 'size' in format_rule:
                format_parts.append(f"{format_rule['size']}")
            
            if format_rule.get('bold', False):
                format_parts.append("粗体")
            
            if 'line_spacing' in format_rule:
                format_parts.append(f"行距 {format_rule['line_spacing']}")
            
            # 添加对齐方式显示
            if 'alignment' in format_rule:
                alignment = format_rule['alignment']
                alignment_display = {
                    "left": "左对齐",
                    "center": "居中",
                    "right": "右对齐",
                    "justify": "两端对齐"
                }.get(alignment, "左对齐")
                format_parts.append(f"{alignment_display}")
            
            text += ", ".join(format_parts) + "\n"
        
        return text
