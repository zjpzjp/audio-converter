# 音频批量转换工具

一个基于 Python + FFmpeg 的音频批量转换工具，支持自定义转换参数，具有图形化界面。

## 📋 功能特点

### 核心功能
- ✅ **批量转换**：支持一次性处理多个音频文件
- ✅ **自定义参数**：可灵活配置采样率、声道、位深、输出格式
- ✅ **声道处理**：支持混合为单声道、只保留左声道、只保留右声道
- ✅ **文件名控制**：可选择保持原文件名或添加后缀
- ✅ **文件覆盖**：支持覆盖已存在文件或自动添加序号

### 界面特性
- 📜 **滚动界面**：支持鼠标滚轮和滚动条，适应不同屏幕尺寸
- 📊 **进度显示**：实时显示转换进度和状态
- 🎯 **文件管理**：支持添加、移除、清空文件列表
- 🔧 **参数预览**：实时显示当前转换参数

## 🚀 快速开始

### 环境要求
- Windows 7/8/10/11
- FFmpeg（需单独下载）
- Python 3.6+（运行源码时需要）

### 安装步骤

#### 方式一：直接运行 Python 脚本
1. 安装 Python 3.6 或更高版本
2. 下载 FFmpeg 并放在程序同目录
3. 运行 `python app2.py`

#### 方式二：打包成独立 exe
```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包（需要先下载 ffmpeg.exe 放在同目录）
pyinstaller --onefile --windowed --name="音频批量转换工具" --add-data "ffmpeg.exe;." app2.py

#或者 
python -m PyInstaller --onefile --windowed --name="音频批量转换工具" --add-data "ffmpeg.exe;." app2.py