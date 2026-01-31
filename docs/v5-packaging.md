# CapScope V1 打包发布文档

> Batch 5 产出物 — Windows 绿色版打包流程

---

## 1. 打包工具

- **PyInstaller** — 将 Python 应用打包为独立可执行文件
- 目标：Windows x64 绿色版（解压即用）

---

## 2. 打包命令

### 单文件模式（推荐）

```bash
pyinstaller --onefile --windowed --name CapScope \
    --add-data "data;data" \
    --icon assets/icon.ico \
    run_gui.py
```

### 文件夹模式（启动更快）

```bash
pyinstaller --onedir --windowed --name CapScope \
    --add-data "data;data" \
    --icon assets/icon.ico \
    run_gui.py
```

---

## 3. 参数说明

| 参数 | 说明 |
|------|------|
| `--onefile` | 打包为单个 exe 文件 |
| `--onedir` | 打包为文件夹（启动更快） |
| `--windowed` | 不显示控制台窗口 |
| `--name` | 输出文件名 |
| `--add-data` | 包含数据文件（源路径;目标路径） |
| `--icon` | 应用图标 |

---

## 4. 打包流程

### 4.1 准备环境

```bash
# 创建干净的虚拟环境
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt
pip install pyinstaller
```

### 4.2 创建 spec 文件（可选，用于自定义）

```bash
pyi-makespec --onefile --windowed --name CapScope run_gui.py
```

### 4.3 执行打包

```bash
pyinstaller CapScope.spec
# 或直接用命令行
pyinstaller --onefile --windowed --name CapScope --add-data "data;data" run_gui.py
```

### 4.4 输出

```
dist/
├── CapScope.exe      # 单文件模式
└── CapScope/         # 文件夹模式
    ├── CapScope.exe
    ├── data/
    └── _internal/
```

---

## 5. 运行时依赖

### Windows 用户可能需要

| 依赖 | 说明 | 下载 |
|------|------|------|
| VC++ Runtime | Visual C++ 运行库 | 通常已预装，或从 Microsoft 下载 |

PyInstaller 打包时会自动包含大部分依赖，用户一般不需要额外安装。

---

## 6. 数据文件处理

PyInstaller 打包后，需要修改代码以正确定位数据文件：

```python
# capscope/universe.py 修改
import sys
from pathlib import Path

def get_data_dir():
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后
        return Path(sys._MEIPASS) / "data"
    else:
        # 开发环境
        return Path(__file__).parent.parent / "data"

DATA_DIR = get_data_dir()
```

---

## 7. 发布清单

### 绿色版 zip 包含

```
CapScope-v1.0.0-win64/
├── CapScope.exe
├── README.txt
└── LICENSE.txt
```

### README.txt 内容

```
CapScope v1.0.0 - 美股历史市值查看工具

【使用方法】
1. 双击 CapScope.exe 启动
2. 选择日期，点击「刷新」加载数据
3. 切换行业 Tab 查看不同行业 Top 100
4. 使用搜索框快速查找股票
5. 点击「导出CSV」保存数据

【系统要求】
- Windows 10/11 x64
- 需要联网（获取股票数据）

【常见问题】
Q: 启动很慢？
A: 首次启动需要解压，请耐心等待约 10-30 秒

Q: 加载数据失败？
A: 请检查网络连接，确保可以访问 Yahoo Finance

Q: 某些股票显示 N/A？
A: 该股票在所选日期无交易数据或缺少元数据

【数据来源】
- Yahoo Finance (yfinance)
- 股票池：S&P 500 + Nasdaq 100

【版本信息】
- 版本：1.0.0
- 更新日期：2026-01-30
- 股票池更新：2026-01-30
```

---

## 8. V2 升级点清单

| 功能 | 描述 | 优先级 |
|------|------|--------|
| 精确历史市值 | 接入 Polygon.io 获取历史 sharesOutstanding | 高 |
| 本地缓存 | 缓存元数据，减少重复请求 | 高 |
| 离线模式 | 缓存历史价格数据 | 中 |
| 自动更新股票池 | 从 Wikipedia 抓取最新成分 | 中 |
| 多指数支持 | 支持 Dow Jones、Russell 2000 等 | 低 |
| 图表可视化 | 市值趋势图、行业占比饼图 | 低 |
| 自动更新 | 检查新版本并自动更新 | 低 |

---

*文档版本: v1.0 | 创建日期: 2026-01-30*
