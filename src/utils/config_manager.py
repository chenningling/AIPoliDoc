# -*- coding: utf-8 -*-
"""
配置管理模块
负责管理应用程序的配置信息，包括API配置、应用配置和排版模板。
"""

import os
import json
import json5
from datetime import datetime
from .logger import app_logger

class ConfigManager:
    """配置管理器类，负责加载、保存和管理应用配置"""
    
    def __init__(self, config_dir="config"):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置文件目录
        """
        self.config_dir = config_dir
        self.templates_dir = os.path.join(config_dir, "templates")
        self.api_config_file = os.path.join(config_dir, "api_config.json")
        self.app_config_file = os.path.join(config_dir, "app_config.json")
        
        # 确保配置目录存在
        self._ensure_dirs_exist()
        
        # 加载配置
        self.api_config = self._load_config(self.api_config_file)
        self.app_config = self._load_config(self.app_config_file)
        self.templates = self._load_templates()
        
        app_logger.info("配置管理器初始化完成")
    
    def _ensure_dirs_exist(self):
        """确保配置目录存在"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
            app_logger.info(f"创建配置目录: {self.config_dir}")
        
        if not os.path.exists(self.templates_dir):
            os.makedirs(self.templates_dir)
            app_logger.info(f"创建模板目录: {self.templates_dir}")
    
    def _load_config(self, config_file):
        """加载配置文件"""
        if not os.path.exists(config_file):
            app_logger.warning(f"配置文件不存在: {config_file}，将创建默认配置")
            return {}
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json5.loads(f.read())
                app_logger.debug(f"加载配置文件: {config_file}")
                return config
        except Exception as e:
            app_logger.error(f"加载配置文件失败: {config_file}, 错误: {str(e)}")
            return {}
    
    def _save_config(self, config, config_file):
        """保存配置到文件"""
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=4)
                app_logger.debug(f"保存配置文件: {config_file}")
                return True
        except Exception as e:
            app_logger.error(f"保存配置文件失败: {config_file}, 错误: {str(e)}")
            return False
    
    def _load_templates(self):
        """加载所有排版模板"""
        templates = {}
        
        if not os.path.exists(self.templates_dir):
            app_logger.warning(f"模板目录不存在: {self.templates_dir}")
            return templates
        
        for filename in os.listdir(self.templates_dir):
            if filename.endswith('.json'):
                template_path = os.path.join(self.templates_dir, filename)
                try:
                    with open(template_path, 'r', encoding='utf-8') as f:
                        template = json5.loads(f.read())
                        template_name = template.get('name', os.path.splitext(filename)[0])
                        templates[template_name] = template
                        app_logger.debug(f"加载模板: {template_name}")
                except Exception as e:
                    app_logger.error(f"加载模板失败: {template_path}, 错误: {str(e)}")
        
        return templates
    
    def get_api_config(self):
        """获取API配置"""
        return self.api_config
    
    def save_api_config(self, api_config):
        """保存API配置"""
        api_config['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.api_config = api_config
        return self._save_config(api_config, self.api_config_file)
    
    def get_app_config(self):
        """获取应用配置"""
        return self.app_config
    
    def save_app_config(self, app_config):
        """保存应用配置"""
        self.app_config = app_config
        return self._save_config(app_config, self.app_config_file)
    
    def get_templates(self):
        """获取所有排版模板"""
        return self.templates
    
    def get_template(self, template_name):
        """获取指定名称的排版模板"""
        return self.templates.get(template_name)
    
    def save_template(self, template_name, template_content):
        """保存排版模板"""
        # 确保模板有name字段
        if 'name' not in template_content:
            template_content['name'] = template_name
        
        # 更新内存中的模板
        self.templates[template_name] = template_content
        
        # 保存到文件
        template_file = os.path.join(self.templates_dir, f"{template_name}.json")
        try:
            with open(template_file, 'w', encoding='utf-8') as f:
                json.dump(template_content, f, ensure_ascii=False, indent=4)
                app_logger.info(f"保存模板: {template_name}")
                return True
        except Exception as e:
            app_logger.error(f"保存模板失败: {template_name}, 错误: {str(e)}")
            return False
    
    def delete_template(self, template_name):
        """删除排版模板"""
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

# 创建全局配置管理器实例
config_manager = ConfigManager()
