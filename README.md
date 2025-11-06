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
├── config/                    # 配置文件目录
│   ├── api_config.example.json # API配置示例文件
│   ├── api_config.json        # AI API配置（需用户创建，不提交到Git）
│   ├── app_config.json        # 应用配置（自动创建）
│   ├── font_mapping.json      # 字体映射配置
│   └── templates/             # 排版模板目录
│       ├── 默认模板.json
│       ├── 论文格式.json
│       └── ...
├── src/                       # 源代码目录
│   ├── core/                  # 核心功能模块
│   │   ├── ai_connector.py    # AI服务连接器
│   │   ├── doc_processor.py   # 文档处理器
│   │   ├── format_manager.py  # 格式管理器
│   │   └── structure_analyzer.py # 结构分析器
│   ├── ui/                    # 用户界面模块
│   │   ├── main_window.py     # 主窗口
│   │   ├── template_editor.py # 模板编辑器
│   │   └── api_config_dialog.py # API配置对话框
│   └── utils/                 # 工具类模块
│       ├── config_manager.py  # 配置管理
│       ├── file_utils.py      # 文件工具
│       ├── font_manager.py    # 字体管理
│       └── logger.py           # 日志管理
├── tests/                     # 测试文件目录
│   └── test_core_functions.py # 核心功能测试
├── logs/                      # 日志目录（不提交到Git）
├── main.py                    # 主程序入口
├── start.py                   # Python启动脚本（跨平台）
├── start.sh                   # Shell启动脚本（Linux/macOS）
├── mac启动应用.command           # macOS快速启动脚本
├── win启动应用.bat                # Windows快速启动脚本
└── requirements.txt           # 依赖包列表
```

## 安装方法

1. 克隆项目代码：
   ```bash
   git clone https://github.com/chenningling/AIPoliDoc.git
   cd AIPoliDoc
   ```

2. 安装 Python 环境（如果尚未安装）
   - 需要 Python 3.8 或更高版本

3. 创建虚拟环境（推荐）：
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # macOS/Linux
   # 或
   venv\Scripts\activate  # Windows
   ```

4. 安装依赖包：
   ```bash
   pip install -r requirements.txt
   ```

## 配置说明

1. 首次使用需要配置 AI API：
   - **重要**：项目中的 `config/api_config.json` 不会被提交到 Git（包含敏感信息）
   - 复制 `config/api_config.example.json` 为 `config/api_config.json`
   - 在 `api_config.json` 中填入你的 API 配置信息：
     ```json
     {
         "api_url": "https://api.deepseek.com/chat/completions",
         "api_key": "your-api-key-here",
         "model": "deepseek-chat"
     }
     ```
   - **推荐使用 DeepSeek API**：访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys) 获取 API Key

2. 应用配置：
   - `config/app_config.json` 会自动创建（首次运行时），可以配置保存路径、窗口大小等
   - `config/font_mapping.json` 中可以配置字体映射关系

## 使用说明

### 启动方式

**方式一：快速启动（推荐）**
- **macOS**：双击 `启动应用.command` 文件即可启动
- **Windows**：双击 `启动应用.bat` 文件即可启动

**方式二：使用启动脚本**
```bash
# macOS/Linux
./start.sh

# 或使用 Python 启动脚本（跨平台）
python start.py
```

**方式三：直接运行主程序**
```bash
# 确保虚拟环境已激活
source venv/bin/activate  # macOS/Linux
# 或
venv\Scripts\activate  # Windows

python main.py
```

### 基本使用流程

1. **选择文档**：点击"浏览..."选择需要排版的 Word 文档（.docx 格式）
2. **选择模板**：从下拉框选择排版模板，或点击"编辑模板"/"新增模板"自定义
3. **配置 API**（首次使用）：点击右上角"API配置"按钮，填写 API 信息
4. **开始排版**：点击"开始排版"按钮，等待处理完成
5. **查看结果**：排版完成后，文件会保存为 `原文件名_已排版.docx`

### 模板管理

- 在模板编辑器中可以创建、编辑、删除模板
- 每个模板可以设置不同层级标题、正文等的格式
- 支持字体、字号、行距、对齐方式等详细参数配置
- 模板会自动保存到 `config/templates/` 目录

### 注意事项

- ⚠️ **首次使用必须配置 AI API 信息**，否则无法使用排版功能
- ⚠️ **建议在正式排版前先备份原文档**
- 📝 如遇到问题，可查看 `logs/` 目录下的日志文件了解详情
- 💡 程序会自动备份原文档，备份文件名为 `原文件名_备份.docx`

## 常见问题

### 1. API 配置问题

**问题**：提示 API 配置无效或连接失败

**解决方案**：
- 确保 API 密钥正确（检查是否复制完整）
- 检查网络连接是否正常
- 确认 API 服务是否可用（可点击"测试连接"按钮验证）
- 推荐使用 DeepSeek API，访问 [DeepSeek Platform](https://platform.deepseek.com/api_keys) 获取

### 2. 字体问题

**问题**：排版后字体显示不正确

**解决方案**：
- 确保系统安装了模板中使用的字体
- 可以在 `config/font_mapping.json` 中配置字体替代方案
- 程序会自动使用系统可用字体进行映射

### 3. 排版效果问题

**问题**：排版结果不符合预期

**解决方案**：
- 检查文档结构是否规范（标题、正文等是否清晰）
- 调整模板中的排版参数（字体、字号、行距等）
- 查看 `logs/` 目录下的日志文件，了解 AI 识别结果
- 尝试使用不同的排版模板

### 4. 启动问题

**问题**：程序无法启动

**解决方案**：
- 确保已安装所有依赖：`pip install -r requirements.txt`
- 检查 Python 版本是否符合要求（Python 3.8+）
- 确保虚拟环境已激活（如果使用虚拟环境）
- 查看终端错误信息，检查是否有缺失的模块

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进项目。在提交代码前，请确保：

1. 代码符合项目的编码规范
2. 添加了必要的注释和文档
3. 通过了所有测试用例
4. **重要**：不要提交包含真实 API Key 的配置文件
5. 使用 `api_config.example.json` 作为配置模板

### 开发环境设置

1. Fork 本项目
2. 克隆你的 Fork：
   ```bash
   git clone https://github.com/your-username/AIPoliDoc.git
   ```
3. 创建开发分支：
   ```bash
   git checkout -b feature/your-feature-name
   ```
4. 进行开发并提交更改
5. 推送到你的 Fork 并创建 Pull Request

## 安全说明

- ⚠️ **重要**：`config/api_config.json` 包含敏感信息，已被 `.gitignore` 忽略，不会提交到仓库
- ✅ 请使用 `config/api_config.example.json` 作为配置模板
- ✅ 如果之前误提交了包含真实 API Key 的文件，请立即在 API 提供商处撤销该 Key

## 许可证

本项目采用 MIT 许可证，详见 LICENSE 文件。
