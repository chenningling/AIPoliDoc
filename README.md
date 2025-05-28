# AI Word文档自动排版工具（AIPoliDoc）

## 项目简介

AIPoliDoc 是一款结合 AI 能力的文档排版助手，能够自动分析未排版的 Word 文档结构，并根据用户配置的排版规则进行智能排版。本工具特别适合用于学术论文、报告等需要规范格式的文档处理。

## 主要功能

- **文档结构智能分析**：利用 AI 能力分析未排版文档的结构，自动识别标题、摘要、关键词、正文等内容
- **排版规则管理**：
  - 支持预设模板和自定义排版规则
  - 提供多个预设模板（论文格式、研究报告等）
  - 可自定义字体、段落、间距等详细排版参数
- **自动排版**：根据识别的结构和排版规则自动排版文档
- **多种 AI API 支持**：
  - 支持配置多种 AI API 接口
  - 默认支持 DeepSeek API
  - 可扩展支持其他 AI 服务
- **用户友好界面**：
  - 直观的图形界面操作
  - 实时预览排版效果
  - 支持模板编辑和管理
- **详细日志**：提供详细的处理日志和进度显示

## 系统要求

- **操作系统**：
  - Windows 10/11
  - macOS 10.15+
- **Python 环境**：
  - Python 3.8 或更高版本
- **依赖包**：
  - python-docx >= 0.8.11 (Word文档处理)
  - PyQt6 >= 6.4.0 (GUI界面)
  - requests >= 2.28.1 (HTTP请求)
  - pillow >= 9.3.0 (图像处理)
  - chardet >= 5.0.0 (字符编码检测)
  - json5 >= 0.9.10 (JSON处理)

## 项目结构

```
AIPoliDoc/
├── config/                # 配置文件目录
│   ├── api_config.json   # AI API配置
│   ├── app_config.json   # 应用配置
│   ├── font_mapping.json # 字体映射配置
│   └── templates/        # 排版模板目录
├── src/                  # 源代码目录
│   ├── core/            # 核心功能模块
│   │   ├── ai_connector.py     # AI服务连接器
│   │   ├── doc_processor.py    # 文档处理器
│   │   ├── format_manager.py   # 格式管理器
│   │   └── structure_analyzer.py# 结构分析器
│   ├── ui/              # 用户界面模块
│   │   ├── main_window.py      # 主窗口
│   │   ├── template_editor.py  # 模板编辑器
│   │   └── api_config_dialog.py# API配置对话框
│   └── utils/           # 工具类模块
├── main.py              # 主程序入口
└── requirements.txt     # 依赖包列表
```

## 安装方法

1. 克隆项目代码：
   ```bash
   git clone https://github.com/chenningling/AIPoliDoc.git
   cd AIPoliDoc
   ```

2. 安装 Python 环境（如果尚未安装）

3. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 配置说明

1. 首次使用需要配置 AI API：
   - 复制 `config/api_config.example.json` 为 `config/api_config.json`
   - 在 `api_config.json` 中填入你的 API 配置信息：
     ```json
     {
         "api_url": "https://your-api-endpoint.com/v1/chat/completions",
         "api_key": "your-api-key-here",
         "model": "deepseek-chat"
     }
     ```

2. 应用配置：
   - `config/app_config.json` 中可以配置保存路径、窗口大小等
   - `config/font_mapping.json` 中可以配置字体映射关系

## 使用说明

1. 启动程序：
   ```bash
   python main.py
   ```

2. 基本使用流程：
   - 选择需要排版的 Word 文档
   - 选择或自定义排版模板
   - 点击"开始排版"按钮
   - 等待排版完成，查看结果

3. 模板管理：
   - 在模板编辑器中可以创建、编辑、删除模板
   - 每个模板可以设置不同层级标题、正文等的格式
   - 支持导入导出模板配置

4. 注意事项：
   - 首次使用需要配置 AI API 信息
   - 建议在正式排版前先备份原文档
   - 如遇到问题，可查看日志文件了解详情

## 常见问题

1. API 配置问题：
   - 确保 API 密钥正确
   - 检查网络连接是否正常
   - 确认 API 服务是否可用

2. 字体问题：
   - 确保系统安装了模板中使用的字体
   - 可以在 `font_mapping.json` 中配置字体替代方案

3. 排版效果问题：
   - 检查文档结构是否规范
   - 调整模板中的排版参数
   - 查看日志了解 AI 识别结果

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加了必要的注释和文档
3. 通过了所有测试用例

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
