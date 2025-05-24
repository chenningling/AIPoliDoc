# -*- coding: utf-8 -*-
"""
AI接口连接器模块
负责与AI API通信，发送请求和处理响应。
"""

import json
import requests
from ..utils.logger import app_logger

class AIConnector:
    """AI接口连接器，负责与AI API通信"""
    
    def __init__(self, api_config):
        """
        初始化连接器
        
        Args:
            api_config: API配置信息，包含api_url, api_key, model等
        """
        self.api_url = api_config.get("api_url", "")
        self.api_key = api_config.get("api_key", "")
        self.model = api_config.get("model", "deepseek-chat")
        
        app_logger.info(f"AI连接器初始化完成，使用模型: {self.model}")
    
    def validate_config(self):
        """
        验证API配置是否有效
        
        Returns:
            (bool, str): 是否有效及错误信息
        """
        if not self.api_url:
            return False, "API URL不能为空"
        
        if not self.api_key:
            return False, "API Key不能为空"
        
        if not self.model:
            return False, "模型名称不能为空"
        
        # 尝试发送测试请求
        try:
            response = self._send_test_request()
            if response.status_code == 200:
                app_logger.info("API配置验证成功")
                return True, "API配置验证成功"
            else:
                error_msg = f"API请求失败，状态码: {response.status_code}, 响应: {response.text}"
                app_logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"API请求异常: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def _send_test_request(self):
        """
        发送测试请求以验证API配置
        
        Returns:
            requests.Response: 响应对象
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello!"}
            ],
            "stream": False
        }
        
        return requests.post(self.api_url, headers=headers, json=data, timeout=10)
    
    def generate_prompt(self, document_content, formatting_rules):
        """
        生成AI提示词
        
        Args:
            document_content: 文档内容列表，每个元素为一个段落
            formatting_rules: 排版规则
            
        Returns:
            str: 生成的提示词
        """
        # 将文档内容列表转换为文本
        doc_text = "\n\n".join(document_content)
        
        # 将排版规则转换为文本
        rules_text = json.dumps(formatting_rules, ensure_ascii=False, indent=2)
        
        # 构建提示词
        prompt = f"""
你是一个专业的文档排版助手。请分析以下未经排版的文档内容（全部使用默认正文格式），通过语义理解识别其中的结构元素（如标题、正文、列表等），并根据提供的排版规则，返回详细的排版指令。

文档内容：
{doc_text}

排版规则：
{rules_text}

请特别注意：
1. 文档没有任何预先排版，所有内容都使用相同的默认格式
2. 需要通过内容语义来判断每段文字的结构角色（如标题、小标题、正文等）
3. 标题通常简短、概括性强，且可能没有标点符号
4. 请识别出文档的层级结构，包括标题、小标题、正文等

请以JSON格式返回排版指令，格式如下：
{{
  "elements": [
    {{
      "type": "标题",
      "content": "文本内容",
      "format": {{
        "font": "黑体",
        "size": "小二",
        "line_spacing": 1.0
      }}
    }},
    ...
  ]
}}

请确保返回的JSON格式正确，可以被解析。只返回JSON内容，不要有其他说明文字。
"""
        
        app_logger.debug("生成AI提示词完成")
        return prompt
    
    def send_request(self, prompt):
        """
        发送请求到AI API
        
        Args:
            prompt: 提示词
            
        Returns:
            (bool, dict/str): 是否成功及响应内容/错误信息
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            "stream": False
        }
        
        app_logger.info(f"发送请求到AI API: {self.api_url}")
        
        try:
            response = requests.post(self.api_url, headers=headers, json=data, timeout=60)
            
            if response.status_code == 200:
                app_logger.info("AI API请求成功")
                return True, response.json()
            else:
                error_msg = f"AI API请求失败，状态码: {response.status_code}, 响应: {response.text}"
                app_logger.error(error_msg)
                return False, error_msg
        except Exception as e:
            error_msg = f"AI API请求异常: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
    
    def parse_response(self, response):
        """
        解析AI响应
        
        Args:
            response: AI API的响应内容
            
        Returns:
            (bool, dict/str): 是否成功及解析结果/错误信息
        """
        try:
            # 从响应中提取content内容
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            
            if not content:
                error_msg = "AI响应内容为空"
                app_logger.error(error_msg)
                return False, error_msg
            
            # 尝试解析JSON内容
            # 有时AI可能会在JSON前后添加额外文本，需要提取JSON部分
            json_start = content.find('{')
            json_end = content.rfind('}')
            
            app_logger.debug(f"JSON内容起始位置: {json_start}, 结束位置: {json_end}")
            
            if json_start >= 0 and json_end >= 0:
                json_content = content[json_start:json_end+1]
                app_logger.debug(f"提取的JSON内容长度: {len(json_content)}")
                app_logger.debug(f"JSON内容前50个字符: {json_content[:50]}...")
                
                try:
                    formatting_instructions = json.loads(json_content)
                    app_logger.info("成功解析AI响应")
                    
                    # 记录解析后的结构信息
                    elements = formatting_instructions.get('elements', [])
                    app_logger.info(f"结构验证完成，共{len(elements)}个元素")
                    
                    # 检查elements是否为列表
                    if not isinstance(elements, list):
                        app_logger.error(f"elements不是列表类型: {type(elements)}")
                        return False, "响应格式错误: elements不是列表类型"
                    
                    # 检查每个元素的结构
                    for i, elem in enumerate(elements):
                        if not isinstance(elem, dict):
                            app_logger.error(f"元素 {i} 不是字典类型: {type(elem)}")
                            return False, f"响应格式错误: 元素 {i} 不是字典类型"
                        
                        # 检查必要字段
                        if 'content' not in elem:
                            app_logger.error(f"元素 {i} 缺少content字段")
                            return False, f"响应格式错误: 元素 {i} 缺少content字段"
                        
                        if 'format' not in elem:
                            app_logger.error(f"元素 {i} 缺少format字段")
                            return False, f"响应格式错误: 元素 {i} 缺少format字段"
                    
                    return True, formatting_instructions
                except json.JSONDecodeError as e:
                    error_msg = f"JSON解析错误: {str(e)}\n提取的JSON内容: {json_content[:100]}..."
                    app_logger.error(error_msg)
                    return False, error_msg
            else:
                error_msg = "无法在AI响应中找到有效的JSON内容"
                app_logger.error(error_msg)
                return False, error_msg
        except json.JSONDecodeError as e:
            error_msg = f"JSON解析错误: {str(e)}\n响应内容: {content}"
            app_logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"解析AI响应异常: {str(e)}"
            app_logger.error(error_msg)
            return False, error_msg
