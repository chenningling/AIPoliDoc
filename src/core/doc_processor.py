# -*- coding: utf-8 -*-
"""
文档处理模块
负责读取、解析和写入Word文档，以及应用排版格式。
"""

import os
import docx
from docx import Document
from docx.shared import Pt, RGBColor, Length
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT, WD_LINE_SPACING
from docx.oxml.ns import qn
from ..utils.logger import app_logger
from ..utils.file_utils import generate_output_filename, is_valid_docx, backup_file

class DocProcessor:
    """文档处理器，负责读取、解析和写入Word文档"""
    
    def __init__(self):
        """初始化文档处理器"""
        self.document = None
        self.input_file = None
        self.output_file = None
        self.paragraphs_text = []
        self.font_mapping = {
            "宋体": "SimSun",
            "黑体": "SimHei",
            "楷体": "KaiTi",
            "仿宋": "FangSong",
            "微软雅黑": "Microsoft YaHei",
            "Times New Roman": "Times New Roman"
        }
        self.font_size_mapping = {
            "小二": Pt(18),
            "三号": Pt(16),
            "小三": Pt(15),
            "四号": Pt(14),
            "小四": Pt(12),
            "五号": Pt(10.5),
            "小五": Pt(9),
            "六号": Pt(7.5)
        }
    
    def read_document(self, file_path):
        """
        读取Word文档内容
        
        Args:
            file_path: 文档路径
            
        Returns:
            是否成功读取文档
        """
        if not is_valid_docx(file_path):
            app_logger.error(f"无效的Word文档: {file_path}")
            return False
        
        try:
            self.document = Document(file_path)
            self.input_file = file_path
            self.paragraphs_text = [p.text for p in self.document.paragraphs]
            
            app_logger.info(f"成功读取文档: {file_path}")
            app_logger.debug(f"文档包含 {len(self.document.paragraphs)} 个段落")
            return True
        except Exception as e:
            app_logger.error(f"读取文档失败: {file_path}, 错误: {str(e)}")
            return False
    
    def get_document_text(self):
        """
        获取文档的纯文本内容
        
        Returns:
            文档的段落文本列表
        """
        if not self.document:
            app_logger.warning("尚未加载文档")
            return []
        
        return self.paragraphs_text
    
    def apply_formatting(self, formatting_instructions):
        """
        根据排版指令应用格式
        
        Args:
            formatting_instructions: 排版指令，包含元素类型和格式信息
            
        Returns:
            是否成功应用格式
        """
        if not self.document:
            app_logger.error("尚未加载文档，无法应用格式")
            return False
        
        try:
            # 备份原始文档
            backup_file(self.input_file)
            
            # 创建新文档以应用格式
            new_doc = Document()
            
            # 处理每个元素
            for element in formatting_instructions.get('elements', []):
                self._process_element(new_doc, element)
            
            # 生成输出文件名
            self.output_file = generate_output_filename(self.input_file)
            
            # 保存文档
            new_doc.save(self.output_file)
            
            app_logger.info(f"成功应用排版格式并保存到: {self.output_file}")
            return True
        except Exception as e:
            app_logger.error(f"应用排版格式失败: {str(e)}")
            return False
    
    def _process_element(self, doc, element):
        """
        处理单个排版元素
        
        Args:
            doc: 目标文档对象
            element: 排版元素信息
        """
        content = element.get('content', '')
        element_type = element.get('type', '正文')
        format_info = element.get('format', {})
        
        # 添加段落
        paragraph = doc.add_paragraph()
        run = paragraph.add_run(content)
        
        # 应用字体
        self._apply_font(run, format_info)
        
        # 应用段落格式
        self._apply_paragraph_format(paragraph, format_info, element_type)
        
        app_logger.debug(f"应用格式到元素: {element_type}, 内容: {content[:20]}...")
    
    def _apply_font(self, run, format_info):
        """
        应用字体格式
        
        Args:
            run: 文本运行对象
            format_info: 格式信息
        """
        # 字体名称
        font_name = format_info.get('font', '宋体')
        font_name_en = self.font_mapping.get(font_name, font_name)
        run.font.name = font_name_en
        
        # 设置中文字体
        run._element.rPr.rFonts.set(qn('w:eastAsia'), font_name)
        
        # 字体大小
        font_size = format_info.get('size', '五号')
        if isinstance(font_size, str):
            font_size = self.font_size_mapping.get(font_size, Pt(10.5))  # 默认五号字体
        run.font.size = font_size
        
        # 粗体
        run.bold = format_info.get('bold', False)
        
        # 斜体
        run.italic = format_info.get('italic', False)
        
        # 下划线
        run.underline = format_info.get('underline', False)
    
    def _apply_paragraph_format(self, paragraph, format_info, element_type):
        """
        应用段落格式
        
        Args:
            paragraph: 段落对象
            format_info: 格式信息
            element_type: 元素类型
        """
        # 行间距
        line_spacing = format_info.get('line_spacing', 1.5)
        if isinstance(line_spacing, (int, float)):
            if line_spacing == 1.0:
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.SINGLE
            elif line_spacing == 1.5:
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.ONE_POINT_FIVE
            elif line_spacing == 2.0:
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.DOUBLE
            else:
                # 自定义行间距，如19磅
                paragraph.paragraph_format.line_spacing_rule = WD_LINE_SPACING.EXACTLY
                paragraph.paragraph_format.line_spacing = Pt(line_spacing)
        
        # 对齐方式
        alignment = format_info.get('alignment', 'left')
        if alignment == 'center':
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER
        elif alignment == 'right':
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.RIGHT
        elif alignment == 'justify':
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.JUSTIFY
        else:  # 默认左对齐
            paragraph.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
        
        # 首行缩进
        first_line_indent = format_info.get('first_line_indent', None)
        if first_line_indent is not None:
            paragraph.paragraph_format.first_line_indent = Pt(first_line_indent)
        elif element_type == '正文':  # 正文默认缩进2个字符
            paragraph.paragraph_format.first_line_indent = Pt(21)  # 约2个中文字符
        
        # 段前间距
        before_spacing = format_info.get('before_spacing', None)
        if before_spacing is not None:
            paragraph.paragraph_format.space_before = Pt(before_spacing)
        
        # 段后间距
        after_spacing = format_info.get('after_spacing', None)
        if after_spacing is not None:
            paragraph.paragraph_format.space_after = Pt(after_spacing)
    
    def get_output_file(self):
        """
        获取输出文件路径
        
        Returns:
            输出文件路径
        """
        return self.output_file
