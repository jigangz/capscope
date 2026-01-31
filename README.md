# CapScope 🔭

美股历史市值查看工具 — 按 GICS 行业分类，支持任意日期 Top 100

## 功能

- 📊 查看美股历史市值（日线）
- 🏢 按 GICS 行业分类浏览
- 📅 选择任意日期查看该日市值排名
- 🔝 每行业 Top 100 展示
- 💾 导出 CSV

## 股票池

- S&P 500 + Nasdaq 100（约 550 只）

## 计算方式

```
市值 ≈ 当前流通股数 × 历史收盘价
```

> ⚠️ V1 使用近似算法，历史市值存在因拆股/增发导致的误差

## 技术栈

- Python 3.10+
- yfinance（数据）
- PyQt6（GUI）
- PyInstaller（打包）

## 开发进度

- [x] Batch 1: 数据契约定稿
- [ ] Batch 2: 股票池方案
- [ ] Batch 3: 核心计算
- [ ] Batch 4: GUI
- [ ] Batch 5: 打包发布

## License

MIT
