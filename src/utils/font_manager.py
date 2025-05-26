# -*- coding: utf-8 -*-
"""
字体管理模块
负责获取系统字体、验证字体可用性和提供字体映射功能。
"""

import os
import json
import platform
from PyQt6.QtGui import QFontDatabase, QFont
from ..utils.logger import app_logger

class FontManager:
    """字体管理器，负责获取和验证系统字体"""
    
    _instance = None
    
    def __new__(cls):
        """单例模式实现"""
        if cls._instance is None:
            cls._instance = super(FontManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """初始化字体管理器"""
        if self._initialized:
            return
            
        self._initialized = True
        self.system_fonts = []
        self.chinese_fonts = []
        self.font_mapping = {}
        self.reverse_mapping = {}
        
        # 加载字体信息
        self.load_system_fonts()
        self.load_font_mapping()
        
        app_logger.info(f"字体管理器初始化完成，共加载 {len(self.system_fonts)} 个系统字体")
    
    def load_system_fonts(self):
        """加载系统所有可用字体"""
        try:
            # 使用PyQt6静态方法获取字体列表
            all_families = QFontDatabase.families()
            app_logger.debug(f"QFontDatabase原始字体列表长度: {len(all_families)}")
            if len(all_families) < 5:  # 如果字体数量异常少，记录所有字体
                app_logger.debug(f"所有原始字体: {all_families}")
            
            # 过滤掉以@开头的字体（这些通常是垂直方向的字体变体）
            self.system_fonts = [font for font in all_families if not font.startswith('@')]
            app_logger.debug(f"过滤后的字体列表长度: {len(self.system_fonts)}")
            
            # 如果从 QFontDatabase 获取的字体列表异常少，尝试其他方法
            if len(self.system_fonts) < 10:
                try:
                    import platform
                    system = platform.system()
                    app_logger.debug(f"当前操作系统: {system}")
                    
                    # 在macOS上尝试使用fc-list命令获取字体
                    if system == "Darwin":  # macOS
                        import subprocess
                        try:
                            # 使用fc-list命令获取字体列表
                            result = subprocess.run(['fc-list', ':', 'family'], capture_output=True, text=True, timeout=5)
                            output = result.stdout
                            app_logger.debug(f"fc-list命令执行状态: {result.returncode}")
                            
                            # 解析输出提取字体名称
                            fonts_from_system = []
                            for line in output.split('\n'):
                                if line.strip():
                                    # fc-list返回的字体名称可能包含多个逗号分隔的名称
                                    for font in line.split(','):
                                        font = font.strip()
                                        if font and font not in fonts_from_system:
                                            fonts_from_system.append(font)
                            
                            app_logger.debug(f"通过fc-list获取的字体数量: {len(fonts_from_system)}")
                            if len(fonts_from_system) > len(self.system_fonts):
                                app_logger.debug(f"使用fc-list获取的字体列表替代QFontDatabase")
                                self.system_fonts = fonts_from_system
                        except Exception as e:
                            app_logger.error(f"使用fc-list获取字体失败: {str(e)}")
                            
                        # 如果上面的方法失败，尝试使用system_profiler
                        if len(self.system_fonts) < 10:
                            try:
                                # 使用system_profiler获取字体列表
                                result = subprocess.run(['system_profiler', 'SPFontsDataType'], capture_output=True, text=True, timeout=5)
                                output = result.stdout
                                app_logger.debug(f"system_profiler命令执行状态: {result.returncode}")
                                
                                # 解析输出提取字体名称
                                fonts_from_system = []
                                for line in output.split('\n'):
                                    if 'Full Name:' in line:
                                        font_name = line.split('Full Name:')[1].strip()
                                        fonts_from_system.append(font_name)
                                
                                app_logger.debug(f"通过system_profiler获取的字体数量: {len(fonts_from_system)}")
                                if len(fonts_from_system) > len(self.system_fonts):
                                    app_logger.debug(f"使用system_profiler获取的字体列表替代先前的列表")
                                    self.system_fonts = fonts_from_system
                            except Exception as e:
                                app_logger.error(f"使用system_profiler获取字体失败: {str(e)}")
                except Exception as e:
                    app_logger.error(f"尝试替代方法获取字体失败: {str(e)}")
            
            # 增加常见字体的中文名称和英文名称映射
            common_fonts = {
                "宋体": "SimSun",
                "黑体": "SimHei",
                "楷体": "KaiTi",
                "仿宋": "FangSong",
                "微软雅黑": "Microsoft YaHei",
                "华文宋体": "STSong",
                "华文黑体": "STHeiti",
                "华文楷体": "STKaiti",
                "华文仿宋": "STFangsong",
                "英文": "Arial",
                "新罗马": "Times New Roman",
                "等宽": "Courier New"
            }
            
            # 将中文字体名称添加到字体列表中
            for cn_name, en_name in common_fonts.items():
                if cn_name not in self.system_fonts and en_name in self.system_fonts:
                    self.system_fonts.append(cn_name)
                    app_logger.debug(f"添加中文字体名称: {cn_name}")
                elif en_name not in self.system_fonts and cn_name in self.system_fonts:
                    self.system_fonts.append(en_name)
                    app_logger.debug(f"添加英文字体名称: {en_name}")
            
            # 识别中文字体（简单方法：包含常见中文字体关键词的字体）
            chinese_keywords = ['宋', '黑', '楷', '仿', '微软', '华文', 'SimSun', 'SimHei', 'KaiTi', 'FangSong', 'Microsoft YaHei']
            self.chinese_fonts = [font for font in self.system_fonts 
                                if any(keyword in font for keyword in chinese_keywords)]
            
            # 记录详细信息
            app_logger.debug(f"加载系统字体成功，共 {len(self.system_fonts)} 个字体")
            app_logger.debug(f"识别中文字体 {len(self.chinese_fonts)} 个")
            
            # 如果字体数量仍然异常少，记录所有字体并添加基本字体
            if len(self.system_fonts) < 10:
                app_logger.debug(f"系统字体列表内容: {self.system_fonts}")
                app_logger.debug(f"中文字体列表内容: {self.chinese_fonts}")
                
                # 添加一些基本字体确保程序可用
                basic_fonts = ["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei", "Microsoft YaHei", "宋体", "黑体", "微软雅黑"]
                for font in basic_fonts:
                    if font not in self.system_fonts:
                        self.system_fonts.append(font)
                        app_logger.debug(f"添加基本字体: {font}")
                        
                # 更新中文字体列表
                self.chinese_fonts = [font for font in self.system_fonts 
                                    if any(keyword in font for keyword in chinese_keywords)]
            
            return self.system_fonts
        except Exception as e:
            app_logger.error(f"加载系统字体失败: {str(e)}")
            import traceback
            app_logger.error(f"异常详情: {traceback.format_exc()}")
            # 返回基本字体列表作为后备
            self.system_fonts = ["Arial", "Times New Roman", "Courier New", "SimSun", "SimHei", "Microsoft YaHei", "宋体", "黑体", "微软雅黑"]
            app_logger.debug(f"使用后备字体列表: {self.system_fonts}")
            return self.system_fonts
    
    def load_font_mapping(self):
        """加载字体映射配置"""
        # 基本映射（中文名称到英文名称）
        self.font_mapping = {
            "宋体": "SimSun",
            "黑体": "SimHei",
            "楷体": "KaiTi",
            "仿宋": "FangSong",
            "微软雅黑": "Microsoft YaHei UI",
            "微软雅黑 UI": "Microsoft YaHei UI",
            "华文宋体": "STSong",
            "华文黑体": "STHeiti",
            "华文楷体": "STKaiti",
            "华文仿宋": "STFangsong",
            "Times New Roman": "Times New Roman",
            "Arial": "Arial",
            "Calibri": "Calibri"
        }
        
        # 创建反向映射（英文名称到中文名称）
        self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
        
        # 尝试从配置文件加载额外映射
        try:
            mapping_file = os.path.join("config", "font_mapping.json")
            if os.path.exists(mapping_file):
                with open(mapping_file, 'r', encoding='utf-8') as f:
                    additional_mapping = json.load(f)
                    self.font_mapping.update(additional_mapping)
                    # 更新反向映射
                    self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
                app_logger.info(f"从配置文件加载了额外的字体映射")
        except Exception as e:
            app_logger.error(f"加载字体映射配置失败: {str(e)}")
    
    def is_font_available(self, font_name):
        """检查字体是否可用"""
        # 直接检查
        if font_name in self.system_fonts:
            return True
        
        # 通过映射检查
        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and mapped_font in self.system_fonts:
            return True
        
        return False
    
    def get_available_font(self, font_name, fallback="SimSun"):
        """获取可用字体，如果指定字体不可用则返回后备字体"""
        if self.is_font_available(font_name):
            # 如果字体直接可用，返回原始名称
            return font_name
        
        # 尝试映射
        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and mapped_font in self.system_fonts:
            return mapped_font
        
        # 确保后备字体可用
        if fallback in self.system_fonts:
            app_logger.warning(f"字体 '{font_name}' 不可用，使用后备字体 '{fallback}'")
            return fallback
        
        # 如果后备字体也不可用，使用系统第一个可用字体
        app_logger.warning(f"字体 '{font_name}' 和后备字体 '{fallback}' 均不可用，使用系统默认字体")
        return self.system_fonts[0] if self.system_fonts else "Arial"
    
    def get_font_display_name(self, font_name):
        """获取字体的显示名称（优先返回中文名称）"""
        # 检查反向映射
        if font_name in self.reverse_mapping:
            return self.reverse_mapping[font_name]
        return font_name
    
    def get_all_fonts(self):
        """获取所有系统字体"""
        return self.system_fonts
    
    def get_chinese_fonts(self):
        """获取所有中文字体"""
        return self.chinese_fonts
    
    def get_font_mapping(self):
        """获取字体映射表"""
        return self.font_mapping
    
    def add_font_mapping(self, chinese_name, english_name):
        """添加新的字体映射"""
        self.font_mapping[chinese_name] = english_name
        self.reverse_mapping[english_name] = chinese_name
        
        # 保存到配置文件
        try:
            mapping_file = os.path.join("config", "font_mapping.json")
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(self.font_mapping, f, ensure_ascii=False, indent=4)
            app_logger.info(f"添加字体映射: {chinese_name} -> {english_name}")
            return True
        except Exception as e:
            app_logger.error(f"保存字体映射失败: {str(e)}")
            return False
