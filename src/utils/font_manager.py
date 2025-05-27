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
        self.display_name_mapping = {}  # 系统字体名称到显示名称的映射
        self.system_to_display_mapping = {}  # 系统字体名称到显示名称的映射
        self.display_to_system_mapping = {}  # 显示名称到系统字体名称的映射
        
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
            
            # 创建直接的字体映射表，将系统字体名称映射到中文显示名称
            self.system_to_display_mapping = {
                # macOS系统字体
                'PingFang SC': '苹方',
                'PingFang TC': '苹方',
                'Songti SC': '宋体',
                'Songti TC': '宋体',
                'Heiti SC': '黑体',
                'Heiti TC': '黑体',
                'Kaiti SC': '楷体',
                'Kaiti TC': '楷体',
                'Yuanti SC': '圆体',
                'Yuanti TC': '圆体',
                'STSong': '华文宋体',
                'STHeiti': '华文黑体',
                'STKaiti': '华文楷体',
                'STFangsong': '华文仿宋',
                'Hiragino Sans GB': '冬青黑体',
                'Lantinghei SC': '兰亭黑',
                'Wawati SC': '娃娃体',
                'Xingkai SC': '行楷',
                'Baoli SC': '报隆体',
                'Libian SC': '隶变体',
                'Weibei SC': '魏碧体',
                'Yuppy SC': '雅痛体',
                'Yuppy TC': '雅痛体',
                
                # Windows系统字体
                'SimSun': '宋体',
                'SimHei': '黑体',
                'KaiTi': '楷体',
                'FangSong': '仿宋',
                'Microsoft YaHei': '微软雅黑',
                'Microsoft YaHei UI': '微软雅黑',
                'YouYuan': '幼圆',
                'LiSu': '隶书',
                'FZYaoTi': '方正姚体',
                'FZShuTi': '方正舒体',
                'DengXian': '等线',
                'DengXian Light': '等线 Light',
                
                # 常用英文字体
                'Arial': 'Arial',
                'Times New Roman': 'Times New Roman',
                'Courier New': 'Courier New',
                'Verdana': 'Verdana',
                'Tahoma': 'Tahoma',
                'Calibri': 'Calibri',
                'Helvetica': 'Helvetica',
                'Helvetica Neue': 'Helvetica Neue'
            }
            
            # 创建反向映射（显示名称 -> 系统名称）
            self.display_to_system_mapping = {}
            for system_name, display_name in self.system_to_display_mapping.items():
                self.display_to_system_mapping[display_name] = system_name
                # 如果是中文字体，添加到中文字体列表
                if any(keyword in display_name for keyword in ['宋', '黑', '楷', '仿', '微', '华', '圆', '苹']):
                    if display_name not in self.chinese_fonts:
                        self.chinese_fonts.append(display_name)
                        app_logger.debug(f"添加中文字体: {display_name}")
            
            # 尝试使用QFontDatabase获取更多字体信息
            try:
                for font_name in self.system_fonts:
                    # 如果字体名称包含中文字符，则可能是中文字体
                    if any(0x4E00 <= ord(char) <= 0x9FFF for char in font_name):
                        if font_name not in self.chinese_fonts:
                            self.chinese_fonts.append(font_name)
                            app_logger.debug(f"添加含中文字符的字体: {font_name}")
                    
                    # 如果字体名称包含常见中文字体关键词
                    if any(keyword in font_name for keyword in ['Song', 'Hei', 'Kai', 'Fang', 'Yuan', 'Ming', 'SimSun', 'SimHei', 'KaiTi', 'FangSong']):
                        # 尝试为其创建一个中文显示名称
                        if font_name not in self.system_to_display_mapping:
                            if 'Song' in font_name:
                                display_name = '宋体'
                            elif 'Hei' in font_name:
                                display_name = '黑体'
                            elif 'Kai' in font_name:
                                display_name = '楷体'
                            elif 'Fang' in font_name:
                                display_name = '仿宋'
                            elif 'Yuan' in font_name:
                                display_name = '圆体'
                            elif 'Ming' in font_name:
                                display_name = '明体'
                            else:
                                continue
                                
                            # 添加到映射
                            self.system_to_display_mapping[font_name] = display_name
                            self.display_to_system_mapping[display_name] = font_name
                            
                            # 添加到中文字体列表
                            if display_name not in self.chinese_fonts:
                                self.chinese_fonts.append(display_name)
                                app_logger.debug(f"添加推断的中文字体: {display_name}")
            except Exception as e:
                app_logger.error(f"分析字体信息失败: {str(e)}")
            
            # 如果从 QFontDatabase 获取的字体列表异常少，尝试其他方法
            if len(self.system_fonts) < 10:
                try:
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
                # 中文常用字体
                "宋体": "SimSun",
                "黑体": "SimHei",
                "楷体": "KaiTi",
                "仿宋": "FangSong",
                "微软雅黑": "Microsoft YaHei",
                "微软雅黑 UI": "Microsoft YaHei UI",
                "华文宋体": "STSong",
                "华文黑体": "STHeiti",
                "华文楷体": "STKaiti",
                "华文仿宋": "STFangsong",
                "幼圆": "YouYuan",
                "隶书": "LiSu",
                "方正姚体": "FZYaoTi",
                "方正舒体": "FZShuTi",
                "思源黑体": "Source Han Sans CN",
                "思源宋体": "Source Han Serif CN",
                "苹方": "PingFang SC",
                "苹方-简": "PingFang SC",
                "冬青黑体": "Hiragino Sans GB",
                "兰亭黑": "Lantinghei SC",
                "翩翩体": "Pianpian",
                "娃娃体": "Wawati SC",
                "行楷": "Xingkai SC",
                "圆体": "Yuanti SC",
                "华文细黑": "STXihei",
                "华文中宋": "STZhongsong",
                "等线": "DengXian",
                "等线 Light": "DengXian Light",
                
                # 英文常用字体
                "Arial": "Arial",
                "Arial Black": "Arial Black",
                "Arial Narrow": "Arial Narrow",
                "Times New Roman": "Times New Roman",
                "Courier New": "Courier New",
                "Verdana": "Verdana",
                "Georgia": "Georgia",
                "Tahoma": "Tahoma",
                "Calibri": "Calibri",
                "Cambria": "Cambria",
                "Consolas": "Consolas",
                "Segoe UI": "Segoe UI",
                "Helvetica": "Helvetica",
                "Helvetica Neue": "Helvetica Neue",
                "Lucida Grande": "Lucida Grande",
                "Monaco": "Monaco",
                "Menlo": "Menlo",
                "Andale Mono": "Andale Mono",
                "Comic Sans MS": "Comic Sans MS",
                "Impact": "Impact",
                "Trebuchet MS": "Trebuchet MS",
                "Palatino": "Palatino",
                "Book Antiqua": "Book Antiqua",
                "Garamond": "Garamond",
                "Century Gothic": "Century Gothic",
                "Baskerville": "Baskerville",
                "Futura": "Futura",
                "Gill Sans": "Gill Sans",
                "Optima": "Optima",
                "Avenir": "Avenir",
                "Avenir Next": "Avenir Next",
                "San Francisco": "San Francisco",
                "SF Pro": "SF Pro",
                "SF Pro Text": "SF Pro Text",
                "SF Pro Display": "SF Pro Display",
                
                # 简化名称映射
                "英文": "Arial"
            }
            
            # 创建英文到中文的映射
            self.en_to_cn_mapping = {}
            for cn_name, en_name in common_fonts.items():
                # 如果一个英文名称对应多个中文名称，优先使用最短的、最常见的中文名称
                if en_name in self.en_to_cn_mapping:
                    # 如果当前中文名称比已存在的短，或者是常见字体名称，则替换
                    if len(cn_name) < len(self.en_to_cn_mapping[en_name]) or cn_name in ["宋体", "黑体", "楷体", "仿宋", "微软雅黑"]:
                        self.en_to_cn_mapping[en_name] = cn_name
                else:
                    self.en_to_cn_mapping[en_name] = cn_name
                    
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
    
    def load_font_mapping(self):
        """加载字体映射配置"""
        # 扩展的字体映射表（中文名称到英文名称）
        self.font_mapping = {
            # 基本中文字体
            "宋体": "SimSun",
            "黑体": "SimHei",
            "楷体": "KaiTi",
            "仿宋": "FangSong",
            "微软雅黑": "Microsoft YaHei",
            "微软雅黑 UI": "Microsoft YaHei UI",
            "等线": "DengXian",
            "等线 Light": "DengXian Light",
            "幼圆": "YouYuan",
            "隶书": "LiSu",
            "华文宋体": "STSong",
            "华文黑体": "STHeiti",
            "华文楷体": "STKaiti",
            "华文仿宋": "STFangsong",
            
            # macOS中文字体
            "苹方": "PingFang SC",
            "苹方-简": "PingFang SC",
            "苹方-繁": "PingFang TC",
            "宋体-简": "Songti SC",
            "宋体-繁": "Songti TC",
            "黑体-简": "Heiti SC",
            "黑体-繁": "Heiti TC",
            "楷体-简": "Kaiti SC",
            "楷体-繁": "Kaiti TC",
            "冬青黑体": "Hiragino Sans GB",
            "兰亭黑": "Lantinghei SC",
            "华文细黑": "STXihei",
            
            # 常用英文字体
            "Times New Roman": "Times New Roman",
            "Arial": "Arial",
            "Calibri": "Calibri",
            "Cambria": "Cambria",
            "Courier New": "Courier New",
            "Tahoma": "Tahoma",
            "Verdana": "Verdana",
            "Georgia": "Georgia",
            
            # 其他常用字体
            "思源黑体": "Source Han Sans CN",
            "思源宋体": "Source Han Serif CN",
            "方正书宋": "FZShuSong",
            "方正黑体": "FZHei",
            "方正楷体": "FZKai",
            "方正仿宋": "FZFangSong",
            "阿里巴巴普惠体": "Alibaba PuHuiTi",
            "阿里巴巴方圆体": "Alimama FangYuanTi VF"
        }
        
        # 创建反向映射（英文名称到中文名称）
        self.reverse_mapping = {v: k for k, v in self.font_mapping.items()}
        
        # 创建英文到中文的映射
        self.en_to_cn_mapping = {k: k for k in self.font_mapping.values()}
        for cn, en in self.font_mapping.items():
            if cn not in self.en_to_cn_mapping:
                self.en_to_cn_mapping[en] = cn
        
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
    
    def get_font_for_document(self, font_name):
        """
        获取用于文档的字体名称，完全尊重用户选择的字体名称
        
        Args:
            font_name: 用户指定的字体名称
        
        Returns:
            str: 用于Word文档的字体名称
        """
        # 首先检查字体是否直接可用
        if self.is_font_available(font_name):
            app_logger.debug(f"字体 '{font_name}' 直接可用")
            return font_name
            
        # 如果字体不直接可用，检查是否在映射表中
        if font_name in self.font_mapping:
            mapped_font = self.font_mapping[font_name]
            # 检查映射后的字体是否可用
            if self.is_font_available(mapped_font):
                app_logger.debug(f"字体 '{font_name}' 映射为 '{mapped_font}'")
                return mapped_font
        
        # 如果不在映射表中或映射后的字体不可用，直接返回原始字体名称
        # 这将完全尊重用户的选择，即使字体不可用
        app_logger.info(f"尊重用户选择，保留原始字体名称: '{font_name}'")
        return font_name
    
    def is_font_available(self, font_name):
        """
        检查字体是否可用，采用更宽松的检测机制
        
        Args:
            font_name: 要检查的字体名称
        
        Returns:
            bool: 字体是否可用
        """
        # 1. 直接检查系统字体列表
        if font_name in self.system_fonts:
            return True
        
        # 2. 通过映射检查
        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and mapped_font in self.system_fonts:
            return True
        
        # 3. 检查字体名称的小写版本（不区分大小写）
        for system_font in self.system_fonts:
            if font_name.lower() == system_font.lower():
                return True
        
        # 4. 检查字体名称是否包含在系统字体中（部分匹配）
        # 这对于处理带有额外后缀或前缀的字体名称很有用
        for system_font in self.system_fonts:
            if font_name in system_font or system_font in font_name:
                return True
        
        # 5. 特殊处理常用中文字体（Word兼容性）
        common_fonts = {
            '宋体': ['Songti', 'SimSun', 'Song'],
            '黑体': ['Heiti', 'SimHei'],
            '楷体': ['Kaiti', 'KaiTi'],
            '仿宋': ['Fangsong', 'FangSong'],
            '微软雅黑': ['Microsoft YaHei', 'MYingHei', 'YaHei']
        }
        
        # 检查是否是常用中文字体
        for common_font, aliases in common_fonts.items():
            if font_name == common_font:
                # 检查别名是否在系统字体中
                for alias in aliases:
                    for system_font in self.system_fonts:
                        if alias in system_font:
                            app_logger.info(f"字体 '{font_name}' 使用别名 '{system_font}' 可用")
                            return True
        
        # 6. 创建一个测试字体对象，看是否能成功创建
        try:
            test_font = QFont(font_name)
            actual_family = test_font.family()
            
            # 如果实际字体族不是我们请求的，并且不是默认字体，那么可能是找到了替代字体
            if actual_family != font_name and actual_family != "Arial" and actual_family != "System" and actual_family != ".AppleSystemUIFont":
                app_logger.info(f"字体 '{font_name}' 被Qt映射到系统字体 '{actual_family}'，视为可用")
                return True
        except Exception as e:
            app_logger.debug(f"测试字体 '{font_name}' 时出错: {str(e)}")
        
        return False
    
    def get_available_font(self, font_name, fallback="SimSun"):
        """
        获取可用字体，如果指定字体不可用则返回后备字体
        
        Args:
            font_name: 字体名称（可能是中文或英文）
            fallback: 后备字体名称
            
        Returns:
            str: 可用的字体名称
        """
        # 1. 直接尝试使用原始字体名称（可能是中文名称）
        if self.is_font_available(font_name):
            app_logger.debug(f"字体 '{font_name}' 直接可用")
            return font_name
        
        # 2. 如果是常用中文字体，尝试使用别名
        common_fonts = {
            '宋体': ['Songti SC', 'Songti TC', 'SimSun', 'STSong'],
            '黑体': ['Heiti SC', 'Heiti TC', 'SimHei', 'STHeiti'],
            '楷体': ['Kaiti SC', 'Kaiti TC', 'KaiTi', 'STKaiti'],
            '仿宋': ['Fangsong', 'STFangsong', 'FangSong'],
            '微软雅黑': ['Microsoft YaHei', 'Microsoft YaHei UI', 'PingFang SC', '苹方-简']
        }
        
        # 检查是否是常用中文字体
        for common_font, aliases in common_fonts.items():
            if font_name == common_font:
                # 尝试所有别名
                for alias in aliases:
                    if self.is_font_available(alias):
                        app_logger.info(f"字体 '{font_name}' 使用别名 '{alias}' 替代")
                        return alias
        
        # 3. 如果原始字体不可用，尝试查找反向映射（英文到中文）
        if font_name in self.en_to_cn_mapping:
            cn_name = self.en_to_cn_mapping[font_name]
            if self.is_font_available(cn_name):
                app_logger.debug(f"使用中文字体名称 '{cn_name}' 替代英文名称 '{font_name}'")
                return cn_name
        
        # 4. 尝试使用中文到英文的映射
        mapped_font = self.font_mapping.get(font_name)
        if mapped_font and self.is_font_available(mapped_font):
            app_logger.debug(f"使用映射的英文字体名称 '{mapped_font}' 替代中文名称 '{font_name}'")
            return mapped_font
        
        # 5. 尝试创建QFont对象，获取实际使用的字体
        try:
            test_font = QFont(font_name)
            actual_family = test_font.family()
            
            # 如果实际字体族不是默认字体，那么可能是找到了替代字体
            if actual_family != "Arial" and actual_family != "System" and actual_family != ".AppleSystemUIFont":
                app_logger.info(f"字体 '{font_name}' 被Qt映射到系统字体 '{actual_family}'")
                return actual_family
        except Exception as e:
            app_logger.debug(f"测试字体 '{font_name}' 时出错: {str(e)}")
        
        # 6. 确保后备字体可用
        if self.is_font_available(fallback):
            app_logger.warning(f"字体 '{font_name}' 不可用，使用后备字体 '{fallback}'")
            return fallback
        
        # 7. 如果后备字体也不可用，使用系统第一个可用字体
        app_logger.warning(f"字体 '{font_name}' 和后备字体 '{fallback}' 均不可用，使用系统默认字体")
        return self.system_fonts[0] if self.system_fonts else "Arial"
    
    def get_font_display_name(self, font_name):
        """
        获取字体的显示名称（优先返回本地化显示名称）
        
        Args:
            font_name: 字体名称（可能是系统名称或显示名称）
            
        Returns:
            str: 字体的显示名称，与系统字体册显示一致
        """
        # 1. 检查是否在系统显示名称映射中
        if font_name in self.system_to_display_mapping:
            return self.system_to_display_mapping[font_name]
        
        # 2. 检查是否有系统字体的本地化显示名称
        for system_name, display_name in self.system_to_display_mapping.items():
            if font_name.lower() == system_name.lower():
                return display_name
        
        # 3. 如果已经是中文名称，直接返回
        for cn_name in self.font_mapping.keys():
            if font_name == cn_name:
                return font_name
        
        # 4. 如果是英文名称，尝试从英文到中文的映射中查找
        if font_name in self.en_to_cn_mapping:
            return self.en_to_cn_mapping[font_name]
        
        # 5. 如果在反向映射中找到，返回中文名称
        if font_name in self.reverse_mapping:
            return self.reverse_mapping[font_name]
        
        # 6. 如果没有对应的本地化名称，返回原始名称
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
    
    def add_font_mapping(self, display_name, system_name):
        """
        添加新的字体映射
        
        Args:
            display_name: 显示名称（可以是用户自定义的名称）
            system_name: 系统字体名称
        
        Returns:
            bool: 是否成功添加映射
        """
        # 检查系统字体是否可用
        if not self.is_font_available(system_name):
            app_logger.warning(f"添加字体映射失败: 系统字体 {system_name} 不可用")
            # 尝试查找替代字体
            alternative_font = self.get_available_font(system_name)
            if alternative_font != system_name:
                system_name = alternative_font
                app_logger.info(f"使用替代字体: {alternative_font}")
            else:
                return False
        
        # 添加到映射中
        self.font_mapping[display_name] = system_name
        self.reverse_mapping[system_name] = display_name
        
        # 同时添加到系统显示名称映射
        self.system_to_display_mapping[system_name] = display_name
        
        # 保存到配置文件
        try:
            # 确保配置目录存在
            os.makedirs("config", exist_ok=True)
            
            mapping_file = os.path.join("config", "font_mapping.json")
            
            # 读取现有映射文件（如果存在）
            existing_mapping = {}
            if os.path.exists(mapping_file):
                try:
                    with open(mapping_file, 'r', encoding='utf-8') as f:
                        existing_mapping = json.load(f)
                except Exception as e:
                    app_logger.warning(f"读取现有字体映射文件失败: {str(e)}")
            
            # 只添加或更新一个映射，而不是覆盖整个文件
            existing_mapping[display_name] = system_name
            
            # 保存更新后的映射
            with open(mapping_file, 'w', encoding='utf-8') as f:
                json.dump(existing_mapping, f, ensure_ascii=False, indent=4)
            
            app_logger.info(f"添加字体映射: {display_name} -> {system_name}")
            return True
        except Exception as e:
            app_logger.error(f"保存字体映射失败: {str(e)}")
            return False
