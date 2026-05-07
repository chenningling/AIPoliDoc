# -*- coding: utf-8 -*-
"""
文档结构分析器模块
负责分析未排版文档的结构，并生成结构提示。
"""

import re
from ..utils.logger import app_logger

class StructureAnalyzer:
    """文档结构分析器，负责分析未排版文档的结构"""
    
    def __init__(self):
        """初始化文档结构分析器"""
        # 标题关键词列表
        self.title_keywords = [
            "标题", "题目", "标题：", "题目：", "title", "subject"
        ]
        
        # 摘要关键词列表
        self.abstract_keywords = [
            "摘要", "摘 要", "摘要：", "abstract", "summary"
        ]
        
        # 关键词关键词列表
        self.keywords_keywords = [
            "关键词", "关键词：", "关 键 词", "keywords", "key words"
        ]
        
        # 参考文献关键词列表
        self.references_keywords = [
            "参考文献", "参考文献：", "引用文献", "references", "bibliography"
        ]
        
        # 数字标题模式
        self.numeric_title_patterns = [
            r'^\d+\.\s+.+',  # 1. 标题
            r'^\d+\.\d+\.\s+.+',  # 1.1. 标题
            r'^\d+\.\d+\.\d+\.\s+.+',  # 1.1.1. 标题
            r'^[\u4e00-\u9fa5]+\s*[\u3001\uff0c\uff1a]\s*.+',  # 一、标题
            r'^\(\d+\)\s+.+',  # (1) 标题
            r'^[A-Z]\.\s+.+',  # A. 标题
            r'^[a-z]\.\s+.+'   # a. 标题
        ]
    
    def analyze_text_features(self, paragraphs):
        """
        分析文本特征
        
        Args:
            paragraphs: 段落列表
            
        Returns:
            dict: 文本特征信息
        """
        if not paragraphs:
            app_logger.warning("没有段落内容可分析")
            return {}
        
        features = {
            'paragraph_lengths': [],  # 段落长度列表
            'potential_titles': [],   # 潜在的标题段落索引
            'potential_subtitles': [], # 潜在的小标题段落索引
            'special_sections': {},   # 特殊部分，如摘要、关键词等
            'avg_length': 0,          # 平均段落长度
            'max_length': 0,          # 最大段落长度
            'min_length': float('inf')  # 最小段落长度
        }
        
        # 计算段落长度统计信息
        total_length = 0
        for i, para in enumerate(paragraphs):
            if not para.strip():  # 跳过空段落
                continue
                
            length = len(para)
            features['paragraph_lengths'].append(length)
            total_length += length
            
            features['max_length'] = max(features['max_length'], length)
            features['min_length'] = min(features['min_length'], length)
            
            # 检测潜在的标题
            if self._is_potential_title(para, i, len(paragraphs)):
                features['potential_titles'].append(i)
            
            # 检测潜在的小标题
            elif self._is_potential_subtitle(para, i, len(paragraphs)):
                features['potential_subtitles'].append(i)
            
            # 检测特殊部分
            self._detect_special_sections(para, i, features)
        
        # 计算平均长度
        if features['paragraph_lengths']:
            features['avg_length'] = total_length / len(features['paragraph_lengths'])
        
        app_logger.debug(f"完成文本特征分析，发现 {len(features['potential_titles'])} 个潜在标题")
        return features
    
    def _is_potential_title(self, paragraph, index, total_paragraphs):
        """
        判断段落是否可能是标题
        
        Args:
            paragraph: 段落文本
            index: 段落索引
            total_paragraphs: 总段落数
            
        Returns:
            bool: 是否可能是标题
        """
        # 段落过长不太可能是标题
        if len(paragraph) > 50:
            return False
        
        # 第一段通常是标题的可能性很大
        if index == 0 and len(paragraph) < 30:
            return True
        
        # 包含标题关键词
        for keyword in self.title_keywords:
            if keyword in paragraph.lower():
                return True
        
        # 没有标点符号的短段落可能是标题
        if len(paragraph) < 20 and not any(p in paragraph for p in '.!?;,uff0cuff01uff1fuff1bu3002'):
            return True
        
        return False
    
    def _is_potential_subtitle(self, paragraph, index, total_paragraphs):
        """
        判断段落是否可能是小标题
        
        Args:
            paragraph: 段落文本
            index: 段落索引
            total_paragraphs: 总段落数
            
        Returns:
            bool: 是否可能是小标题
        """
        # 检查是否符合数字标题模式
        for pattern in self.numeric_title_patterns:
            if re.match(pattern, paragraph):
                return True
        
        # 短段落且下一段不为空
        if len(paragraph) < 30 and index < total_paragraphs - 1:
            # 没有标点符号的短段落可能是小标题
            if not any(p in paragraph for p in '.!?;,uff0cuff01uff1fuff1bu3002'):
                return True
        
        return False
    
    def _detect_special_sections(self, paragraph, index, features):
        """
        检测特殊部分，如摘要、关键词等
        
        Args:
            paragraph: 段落文本
            index: 段落索引
            features: 特征字典，将被修改
        """
        para_lower = paragraph.lower()
        
        # 检测摘要
        for keyword in self.abstract_keywords:
            if keyword in para_lower:
                features['special_sections']['abstract'] = index
                return
        
        # 检测关键词
        for keyword in self.keywords_keywords:
            if keyword in para_lower:
                features['special_sections']['keywords'] = index
                return
        
        # 检测参考文献
        for keyword in self.references_keywords:
            if keyword in para_lower:
                features['special_sections']['references'] = index
                return
    
    def generate_structure_hints(self, features):
        """
        生成结构提示
        
        Args:
            features: 文本特征信息
            
        Returns:
            dict: 结构提示信息
        """
        hints = {
            'title_index': None,
            'abstract_range': None,
            'keywords_index': None,
            'references_range': None,
            'section_titles': [],
            'subsection_titles': []
        }
        
        # 设置标题索引
        if features.get('potential_titles'):
            hints['title_index'] = features['potential_titles'][0]
        
        # 设置特殊部分范围
        if 'abstract' in features.get('special_sections', {}):
            abstract_start = features['special_sections']['abstract']
            abstract_end = abstract_start
            
            # 尝试确定摘要结束位置
            for i in range(abstract_start + 1, len(features.get('paragraph_lengths', []))):
                if i in features.get('potential_titles', []) or i in features.get('potential_subtitles', []):
                    abstract_end = i - 1
                    break
                if 'keywords' in features.get('special_sections', {}) and i == features['special_sections']['keywords']:
                    abstract_end = i - 1
                    break
            
            hints['abstract_range'] = (abstract_start, abstract_end)
        
        # 设置关键词索引
        if 'keywords' in features.get('special_sections', {}):
            hints['keywords_index'] = features['special_sections']['keywords']
        
        # 设置参考文献范围
        if 'references' in features.get('special_sections', {}):
            references_start = features['special_sections']['references']
            hints['references_range'] = (references_start, len(features.get('paragraph_lengths', [])) - 1)
        
        # 设置段落标题
        hints['section_titles'] = features.get('potential_titles', [])[1:] if features.get('potential_titles') else []
        hints['subsection_titles'] = features.get('potential_subtitles', [])
        
        app_logger.debug(f"生成结构提示完成")
        return hints
    
    def validate_structure(self, structure):
        """
        验证结构合理性
        
        Args:
            structure: AI返回的文档结构
            
        Returns:
            (bool, dict): 是否有效及修正后的结构
        """
        if not structure or 'elements' not in structure:
            app_logger.error("结构无效，缺少elements字段")
            return False, structure
        
        elements = structure['elements']
        if not elements:
            app_logger.error("结构无效，elements为空")
            return False, structure
        
        # 检查必要字段
        for i, element in enumerate(elements):
            if 'type' not in element:
                app_logger.warning(f"第{i+1}个元素缺少type字段，添加默认值'正文'")
                element['type'] = '正文'
            
            if 'content' not in element:
                app_logger.warning(f"第{i+1}个元素缺少content字段，添加空字符串")
                element['content'] = ''
            
            if 'format' not in element:
                app_logger.warning(f"第{i+1}个元素缺少format字段，添加默认格式")
                element['format'] = {
                    'font': '宋体',
                    'size': '五号',
                    'line_spacing': 1.5
                }
        
        app_logger.info(f"结构验证完成，共{len(elements)}个元素")
        return True, structure
