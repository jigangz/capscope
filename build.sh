#!/bin/bash
# CapScope macOS/Linux 打包脚本

set -e

echo "========================================"
echo "CapScope Build Script"
echo "========================================"

# 检查 Python
if ! command -v python3 &> /dev/null; then
    echo "Error: Python3 not found"
    exit 1
fi

# 创建虚拟环境
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

# 清理旧构建
echo "Cleaning old build..."
rm -rf build dist

# 执行打包
echo "Building CapScope..."
pyinstaller CapScope.spec

# 检查结果
if [ -f "dist/CapScope" ] || [ -f "dist/CapScope.exe" ]; then
    echo "========================================"
    echo "Build successful!"
    echo "Output: dist/"
    echo "========================================"
else
    echo "========================================"
    echo "Build failed!"
    echo "========================================"
    exit 1
fi

echo "Done!"
