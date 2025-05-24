#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
核心功能测试脚本
"""

import os
import sys
import unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.doc_processor import DocProcessor
from src.core.ai_connector import AIConnector
from src.core.format_manager import FormatManager
from src.core.structure_analyzer import StructureAnalyzer
from src.utils.config_manager import config_manager

class TestDocProcessor(unittest.TestCase):
    """测试文档处理器"""
    
    def setUp(self):
        self.doc_processor = DocProcessor()
        # 测试文件路径，需要替换为实际测试文件路径
        self.test_file_path = os.path.join(os.path.dirname(__file__), 'test_files', 'test_document.docx')
        
        # 确保测试文件目录存在
        test_files_dir = os.path.join(os.path.dirname(__file__), 'test_files')
        if not os.path.exists(test_files_dir):
            os.makedirs(test_files_dir)
    
    def test_read_document(self):
        """测试读取文档功能"""
        # 如果测试文件不存在，则跳过测试
        if not os.path.exists(self.test_file_path):
            self.skipTest(f"测试文件不存在: {self.test_file_path}")
            
        result = self.doc_processor.read_document(self.test_file_path)
        self.assertTrue(result, "文档读取失败")
        self.assertIsNotNone(self.doc_processor.document, "文档对象为空")
        self.assertIsNotNone(self.doc_processor.paragraphs_text, "段落文本为空")

class TestAIConnector(unittest.TestCase):
    """测试AI连接器"""
    
    def setUp(self):
        # 从配置文件加载API设置
        api_config = config_manager.load_api_config()
        self.api_url = api_config.get('api_url', '')
        self.api_key = api_config.get('api_key', '')
        self.model = api_config.get('model', '')
        
        # 如果API配置不完整，则创建一个模拟的AI连接器
        if not all([self.api_url, self.api_key, self.model]):
            self.ai_connector = None
        else:
            self.ai_connector = AIConnector(self.api_url, self.api_key, self.model)
    
    def test_generate_prompt(self):
        """测试生成提示"""
        if self.ai_connector is None:
            self.skipTest("API配置不完整，跳过测试")
            
        test_paragraphs = ["标题", "这是一个测试段落。", "这是另一个测试段落。"]
        test_template = {"title": {"font": "Arial", "size": 16, "bold": True}}
        
        prompt = self.ai_connector.generate_prompt(test_paragraphs, test_template)
        self.assertIsNotNone(prompt, "生成的提示为空")
        self.assertIn("标题", prompt, "提示中没有包含文档内容")
        self.assertIn("Arial", prompt, "提示中没有包含模板信息")

class TestFormatManager(unittest.TestCase):
    """测试格式管理器"""
    
    def setUp(self):
        self.format_manager = FormatManager()
        self.test_template_name = "test_template"
        self.test_template_content = {
            "title": {"font": "Arial", "size": 16, "bold": True},
            "subtitle": {"font": "Arial", "size": 14, "bold": True},
            "paragraph": {"font": "Times New Roman", "size": 12, "bold": False}
        }
    
    def test_load_templates(self):
        """测试加载模板"""
        templates = self.format_manager.load_templates()
        self.assertIsNotNone(templates, "模板加载失败")
        self.assertIsInstance(templates, dict, "模板不是字典类型")
    
    def test_save_and_load_template(self):
        """测试保存和加载模板"""
        # 保存测试模板
        self.format_manager.save_template(self.test_template_name, self.test_template_content)
        
        # 重新加载模板
        templates = self.format_manager.load_templates()
        
        # 验证模板是否正确保存和加载
        self.assertIn(self.test_template_name, templates, "测试模板未被保存")
        loaded_template = templates.get(self.test_template_name)
        self.assertEqual(loaded_template, self.test_template_content, "加载的模板内容与保存的不一致")
        
        # 清理测试模板
        template_path = os.path.join(self.format_manager.templates_dir, f"{self.test_template_name}.json")
        if os.path.exists(template_path):
            os.remove(template_path)

class TestStructureAnalyzer(unittest.TestCase):
    """测试结构分析器"""
    
    def setUp(self):
        self.structure_analyzer = StructureAnalyzer()
    
    def test_analyze_document_structure(self):
        """测试文档结构分析"""
        test_paragraphs = [
            "第一章 引言",
            "这是引言的内容。",
            "1.1 研究背景",
            "这是研究背景的内容。",
            "第二章 文献综述",
            "这是文献综述的内容。"
        ]
        
        structure = self.structure_analyzer.analyze_document_structure(test_paragraphs)
        self.assertIsNotNone(structure, "结构分析结果为空")
        self.assertIn("potential_titles", structure, "结构中没有潜在标题")
        self.assertIn("potential_subtitles", structure, "结构中没有潜在子标题")
        
        # 验证标题识别
        self.assertIn("第一章 引言", structure["potential_titles"], "未能识别主标题")
        self.assertIn("第二章 文献综述", structure["potential_titles"], "未能识别主标题")
        
        # 验证子标题识别
        self.assertIn("1.1 研究背景", structure["potential_subtitles"], "未能识别子标题")

if __name__ == "__main__":
    unittest.main()
