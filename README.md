# CapScope 🔭

美股历史市值查看工具 — 按 GICS 行业分类，支持任意日期 Top 100

## 功能

- 📊 查看美股历史市值（日线）
- 🏢 按 GICS 行业分类浏览
- 📅 选择任意日期查看该日市值排名
- 🔝 每行业 Top 100 展示
- 🔍 实时搜索过滤
- 💾 导出 CSV

## 截图

*(待添加)*

## 下载

### Windows 绿色版

从 [Releases](https://github.com/jigangz/capscope/releases) 下载最新版本，解压后双击 `CapScope.exe` 即可运行。

### 从源码运行

```bash
# 克隆仓库
git clone https://github.com/jigangz/capscope.git
cd capscope

# 安装依赖
pip install -r requirements.txt

# 启动 GUI
python run_gui.py
```

## 使用方式

### GUI（推荐）

```bash
python run_gui.py
```

1. 选择日期，点击「刷新」加载数据
2. 切换行业 Tab 查看不同行业 Top 100
3. 使用搜索框快速查找股票
4. 点击「导出CSV」保存数据

### CLI

```bash
# 查询今天的市值
python -m capscope

# 查询指定日期
python -m capscope --date 2024-01-15

# 导出 CSV
python -m capscope --date 2024-01-15 --out result.csv

# 导出 JSON
python -m capscope --date 2024-01-15 --out result.json --format json

# 只看某个行业
python -m capscope --sector Technology --top 50
```

## 股票池

- S&P 500 (~503 只)
- Nasdaq 100 (~101 只)
- 去重后约 550 只

## 计算方式

```
市值 ≈ 当前流通股数 × 历史收盘价
```

> ⚠️ **V1 使用近似算法**
> 
> 由于使用当前流通股数计算历史市值，存在以下误差：
> - 拆股：历史价格已调整，但流通股用当前值 → 历史市值偏高
> - 增发：历史实际流通股少于当前 → 历史市值偏高
> - 回购：历史实际流通股多于当前 → 历史市值偏低
>
> 精确历史市值需接入付费 API（计划 V2 支持）

## 打包

### Windows

```bash
# 安装 PyInstaller
pip install pyinstaller

# 方法 1: 使用 spec 文件
pyinstaller CapScope.spec

# 方法 2: 使用脚本
build.bat
```

输出: `dist/CapScope.exe`

### macOS/Linux

```bash
chmod +x build.sh
./build.sh
```

## 技术栈

- Python 3.10+
- yfinance（数据）
- PyQt6（GUI）
- PyInstaller（打包）

## 开发进度

- [x] Batch 1: 数据契约定稿
- [x] Batch 2: 股票池方案
- [x] Batch 3: 核心计算
- [x] Batch 4: GUI
- [x] Batch 5: 打包发布

## V2 计划

- [ ] 精确历史市值（接入 Polygon.io）
- [ ] 本地缓存（减少重复请求）
- [ ] 离线模式
- [ ] 自动更新股票池
- [ ] 图表可视化

## 常见问题

**Q: 启动很慢？**  
A: 首次启动需解压临时文件，约 10-30 秒。

**Q: 加载数据失败？**  
A: 检查网络连接，确保可访问 Yahoo Finance。

**Q: 某些股票显示 N/A？**  
A: 该股票在所选日期无交易数据或缺少元数据。

**Q: 非交易日怎么办？**  
A: 自动回退到最近的前一个交易日。

## License

MIT
