# -*- coding: utf-8 -*-
"""
文件工具模块
负责文件操作相关的工具函数，如文件选择、路径处理等。
"""

import os
import time
import shutil
from datetime import datetime
from .logger import app_logger

def generate_output_filename(input_file, custom_save_path=None):
    """
    生成输出文件名
    
    Args:
        input_file: 输入文件路径
        custom_save_path: 自定义保存路径，如果指定则使用该路径
        
    Returns:
        输出文件路径
    """
    # 获取文件名和扩展名
    filename, ext = os.path.splitext(os.path.basename(input_file))
    
    # 初始输出文件名
    output_filename = f"{filename}_已排版{ext}"
    
    # 如果指定了自定义保存路径，则使用该路径
    if custom_save_path and os.path.isdir(custom_save_path):
        app_logger.debug(f"使用自定义保存路径: {custom_save_path}")
        output_dir = custom_save_path
    else:
        # 否则使用原文件所在目录
        output_dir = os.path.dirname(input_file)
        app_logger.debug(f"使用原文件目录作为保存路径: {output_dir}")
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
            app_logger.debug(f"创建输出目录: {output_dir}")
        except Exception as e:
            app_logger.error(f"创建输出目录失败: {output_dir}, 错误: {str(e)}")
            # 如果创建目录失败，则使用原文件目录
            output_dir = os.path.dirname(input_file)
    
    output_path = os.path.join(output_dir, output_filename)
    
    # 如果文件已存在，添加时间戳
    if os.path.exists(output_path):
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_filename = f"{filename}_已排版_{timestamp}{ext}"
        output_path = os.path.join(output_dir, output_filename)
    
    app_logger.debug(f"生成输出文件路径: {output_path}")
    return output_path

def ensure_dir_exists(dir_path):
    """
    确保目录存在，如不存在则创建
    
    Args:
        dir_path: 目录路径
        
    Returns:
        是否成功创建或目录已存在
    """
    if not os.path.exists(dir_path):
        try:
            os.makedirs(dir_path)
            app_logger.debug(f"创建目录: {dir_path}")
            return True
        except Exception as e:
            app_logger.error(f"创建目录失败: {dir_path}, 错误: {str(e)}")
            return False
    return True

def is_valid_docx(file_path):
    """
    检查是否是有效的Word文档
    
    Args:
        file_path: 文件路径
        
    Returns:
        是否是有效的Word文档
    """
    if not os.path.exists(file_path):
        app_logger.warning(f"文件不存在: {file_path}")
        return False
    
    # 检查扩展名
    _, ext = os.path.splitext(file_path)
    if ext.lower() != '.docx':
        app_logger.warning(f"非Word文档格式: {file_path}")
        return False
    
    # 检查文件大小
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            app_logger.warning(f"空文件: {file_path}")
            return False
    except Exception as e:
        app_logger.error(f"检查文件大小失败: {file_path}, 错误: {str(e)}")
        return False
    
    return True

def backup_file(file_path):
    """
    备份文件
    
    Args:
        file_path: 要备份的文件路径
        
    Returns:
        备份文件路径或None(如果备份失败)
    """
    if not os.path.exists(file_path):
        app_logger.warning(f"要备份的文件不存在: {file_path}")
        return None
    
    try:
        # 生成备份文件名
        dir_path = os.path.dirname(file_path)
        filename, ext = os.path.splitext(os.path.basename(file_path))
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        backup_filename = f"{filename}_backup_{timestamp}{ext}"
        backup_path = os.path.join(dir_path, backup_filename)
        
        # 复制文件
        shutil.copy2(file_path, backup_path)
        app_logger.info(f"文件备份成功: {file_path} -> {backup_path}")
        return backup_path
    except Exception as e:
        app_logger.error(f"文件备份失败: {file_path}, 错误: {str(e)}")
        return None
