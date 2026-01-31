@echo off
REM CapScope Windows 打包脚本

echo ========================================
echo CapScope Windows Build Script
echo ========================================

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python not found
    exit /b 1
)

REM 创建虚拟环境（如果不存在）
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

REM 激活虚拟环境
call venv\Scripts\activate.bat

REM 安装依赖
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM 清理旧构建
echo Cleaning old build...
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul

REM 执行打包
echo Building CapScope...
pyinstaller CapScope.spec

REM 检查结果
if exist "dist\CapScope.exe" (
    echo ========================================
    echo Build successful!
    echo Output: dist\CapScope.exe
    echo ========================================
) else (
    echo ========================================
    echo Build failed!
    echo ========================================
    exit /b 1
)

REM 创建发布包
echo Creating release package...
mkdir "dist\CapScope-v1.0.0-win64" 2>nul
copy "dist\CapScope.exe" "dist\CapScope-v1.0.0-win64\"
copy "README.txt" "dist\CapScope-v1.0.0-win64\" 2>nul
copy "LICENSE" "dist\CapScope-v1.0.0-win64\" 2>nul

echo Done!
pause
