# CapScope V1 数据契约 / 计算说明

> Batch 1 产出物 — 定义 V1 的计算口径、股票池、输出结构

---

## 1. 市值计算公式（近似）

```
市值 (Market Cap) = 当前流通股数 (sharesOutstanding) × 历史收盘价 (Close)
```

### 已知误差说明

| 场景 | 影响 | V1 处理方式 |
|------|------|-------------|
| 拆股 (Stock Split) | 历史价格已调整，但流通股数用当前值，导致历史市值偏高 | **接受误差**，文档说明 |
| 增发 (Secondary Offering) | 历史实际流通股少于当前，导致历史市值偏高 | **接受误差**，文档说明 |
| 回购 (Buyback) | 历史实际流通股多于当前，导致历史市值偏低 | **接受误差**，文档说明 |
| 停牌/退市 | 无当日价格 | 返回 null，UI 显示 "N/A" |

### V2 升级路径

- 接入付费 API（如 Polygon.io）获取历史 sharesOutstanding
- 使用调整后股数计算精确历史市值

---

## 2. 日期定义

### 交易日处理

- **输入**: 用户选择任意日期 (YYYY-MM-DD)
- **逻辑**:
  - 如果是交易日 → 使用该日收盘价
  - 如果是非交易日（周末/节假日）→ **自动回退到最近的前一个交易日**
- **反馈**: UI 显示实际使用的交易日（如 "数据日期: 2024-01-15 (Mon)"）

### 时区

- 以 **美东时间 (ET)** 为准，与美股交易时间一致
- yfinance 返回的日期已按此处理

---

## 3. 股票池定义

### V1 股票池 = Pool B

| 指数 | 成分数量 | 来源 |
|------|---------|------|
| S&P 500 | ~503 | Wikipedia / 静态列表 |
| Nasdaq 100 | ~101 | Wikipedia / 静态列表 |

- **去重后约 550 只**（两个指数有重叠）
- 不含 ADR、OTC、粉单市场

### 股票池获取方式（Batch 2 细化）

- 方案 A: 内置静态列表（发布时固定）
- 方案 B: 运行时从 Wikipedia 抓取（更新更及时）

---

## 4. 行业字段映射

### yfinance sector → GICS 行业名

yfinance 返回的 `sector` 字段基本对应 GICS 一级行业：

| yfinance sector | 展示名称 |
|-----------------|---------|
| Technology | 信息技术 (Information Technology) |
| Healthcare | 医疗保健 (Health Care) |
| Financials | 金融 (Financials) |
| Consumer Cyclical | 非必需消费品 (Consumer Discretionary) |
| Consumer Defensive | 必需消费品 (Consumer Staples) |
| Communication Services | 通信服务 (Communication Services) |
| Industrials | 工业 (Industrials) |
| Energy | 能源 (Energy) |
| Utilities | 公用事业 (Utilities) |
| Real Estate | 房地产 (Real Estate) |
| Basic Materials | 原材料 (Materials) |

### 缺失处理

- 如果 `sector` 为空或 None → 归类为 **"未分类 (Unknown)"**
- UI 中单独显示 Unknown 分类

---

## 5. 输出数据结构

### 单条记录

```python
{
    "ticker": "AAPL",           # 股票代码
    "name": "Apple Inc.",       # 公司名称 (shortName)
    "sector": "Technology",     # 行业 (yfinance 原始值)
    "sector_cn": "信息技术",     # 行业中文名
    "close": 185.92,            # 收盘价 (USD)
    "shares": 15460000000,      # 流通股数
    "market_cap": 2875027200000,# 市值 (USD)
    "market_cap_b": 2875.03     # 市值 (十亿 USD，便于展示)
}
```

### 完整输出

```python
{
    "query_date": "2024-01-15",      # 用户请求日期
    "actual_date": "2024-01-12",     # 实际使用的交易日
    "generated_at": "2024-01-16T10:30:00Z",  # 生成时间
    "total_stocks": 548,              # 总股票数
    "stocks": [...]                   # 记录列表
}
```

---

## 6. Top 100 规则

### 排序与筛选

1. 按 `market_cap` **降序**排序
2. 每个行业取 **市值最高的 100 只**
3. 如果某行业不足 100 只，全部显示

### 展示方式

- 默认按行业分 Tab/列表
- 支持「全部」视图（跨行业 Top 100）
- 支持按 ticker 搜索

---

## 7. 性能目标

| 指标 | 目标值 | 说明 |
|------|--------|------|
| 首次加载（冷启动） | < 3 分钟 | 550 只股票，yfinance 批量请求 |
| 切换日期（热切换） | < 2 分钟 | 复用元数据，只拉价格 |
| 内存占用 | < 500 MB | GUI + 数据 |

### 并发策略（Batch 3 细化）

- yfinance 支持批量 ticker 查询
- 考虑分批请求（如每批 50 只）+ 进度条
- 不做本地缓存（V1 简化，每次联网查询）

---

## 8. 缺失数据处理汇总

| 字段 | 缺失情况 | 处理方式 |
|------|----------|----------|
| `sector` | None/空 | 归类 "Unknown" |
| `sharesOutstanding` | None/0 | **跳过该股票**，不计算市值 |
| `close` (指定日期) | 无数据 | **跳过该股票**，UI 显示 "N/A" |
| `shortName` | None | 使用 ticker 作为名称 |

---

## 9. 确认清单

- [x] 市值 = 当前流通股 × 历史收盘价（近似）
- [x] 非交易日自动回退到最近交易日
- [x] 股票池 = S&P 500 + Nasdaq 100（去重约 550 只）
- [x] 行业用 yfinance sector 映射到 GICS
- [x] Top 100 按市值降序，每行业最多 100
- [x] 缺 sharesOutstanding 或 close 的股票跳过

---

*文档版本: v1.0 | 创建日期: 2026-01-30*
