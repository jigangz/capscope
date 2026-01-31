# CapScope V1 股票池与元数据获取方案

> Batch 2 产出物 — 确定 ticker 获取方式与元数据处理规则

---

## 1. 股票池获取方案

### 方案对比

| 方案 | 优点 | 缺点 |
|------|------|------|
| A: 内置静态列表 | 离线可用、稳定、不依赖网络 | 成分变化后需手动更新 |
| B: 运行时抓取 Wikipedia | 自动获取最新成分 | 依赖网络、Wikipedia 格式可能变化 |

### ✅ V1 选择: 方案 A — 内置静态列表

**理由:**
1. 绿色版要求稳定，减少外部依赖
2. S&P 500 / Nasdaq 100 成分变化不频繁（每季度调整）
3. 避免 Wikipedia 页面结构变化导致解析失败
4. 启动更快，无需等待网络请求

**维护策略:**
- 发布时内置最新列表（JSON 文件）
- README 注明列表更新日期
- 后续版本可提供「更新股票池」功能（V2）

---

## 2. 股票池数据文件

### 文件位置

```
data/
├── sp500.json      # S&P 500 成分股
├── nasdaq100.json  # Nasdaq 100 成分股
└── universe.json   # 合并去重后的完整列表（启动时生成或预生成）
```

### 数据结构

```json
// sp500.json / nasdaq100.json
{
  "index": "S&P 500",
  "updated": "2026-01-30",
  "count": 503,
  "tickers": ["AAPL", "MSFT", "GOOGL", ...]
}
```

### 初始数据来源

1. Wikipedia: [List of S&P 500 companies](https://en.wikipedia.org/wiki/List_of_S%26P_500_companies)
2. Wikipedia: [Nasdaq-100](https://en.wikipedia.org/wiki/Nasdaq-100)

> Batch 3 实现时会写一个一次性脚本抓取并生成 JSON，之后内置

---

## 3. 元数据字段清单

### 从 yfinance 获取的字段

| 字段 | yfinance 属性 | 用途 | 必需 |
|------|--------------|------|------|
| 股票代码 | (ticker 本身) | 标识 | ✅ |
| 公司名称 | `shortName` 或 `longName` | 展示 | ❌ |
| 行业 | `sector` | 分类 | ❌ |
| 流通股数 | `sharesOutstanding` | 计算市值 | ✅ |

### 价格数据（单独请求）

| 字段 | 来源 | 用途 |
|------|------|------|
| 收盘价 | `yf.download(ticker, start, end)` | 计算市值 |

---

## 4. 元数据获取流程

```
┌─────────────────────────────────────────────────────────┐
│  1. 加载股票池 (data/universe.json)                      │
│     → tickers: ["AAPL", "MSFT", ...]                    │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  2. 批量获取元数据                                        │
│     for ticker in tickers:                              │
│         info = yf.Ticker(ticker).info                   │
│         extract: shortName, sector, sharesOutstanding   │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  3. 过滤无效数据                                          │
│     - 跳过 sharesOutstanding 为空/0 的                   │
│     - 记录跳过原因（可选日志）                             │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│  4. 输出有效元数据列表                                     │
│     → metadata: [{ticker, name, sector, shares}, ...]   │
└─────────────────────────────────────────────────────────┘
```

---

## 5. 缺失数据处理规则

### 规则表

| 字段 | 缺失情况 | 处理方式 | 日志 |
|------|----------|----------|------|
| `shortName` | None / 空 | 使用 `ticker` 作为名称 | INFO |
| `longName` | None / 空 | 回退到 `shortName`，再回退到 `ticker` | — |
| `sector` | None / 空 | 归类为 `"Unknown"` | INFO |
| `sharesOutstanding` | None / 0 / 负数 | **跳过该股票** | WARN |
| yfinance 请求失败 | 网络错误/超时 | **跳过该股票**，记录错误 | ERROR |

### 处理代码示例

```python
def process_metadata(ticker: str, info: dict) -> dict | None:
    shares = info.get("sharesOutstanding")
    
    # 必需字段校验
    if not shares or shares <= 0:
        logger.warning(f"Skipping {ticker}: missing sharesOutstanding")
        return None
    
    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName") or ticker,
        "sector": info.get("sector") or "Unknown",
        "shares": shares
    }
```

---

## 6. 并发与性能考虑

### 问题

- yfinance 单个 `Ticker.info` 调用约 0.5-1 秒
- 550 只股票顺序请求 = 5-10 分钟（太慢）

### V1 策略

| 方案 | 说明 |
|------|------|
| 多线程 | `ThreadPoolExecutor(max_workers=10)`，约 1-2 分钟 |
| 进度反馈 | 每完成 50 只更新进度条 |
| 错误隔离 | 单个股票失败不影响整体 |

### 代码框架

```python
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_all_metadata(tickers: list[str], max_workers: int = 10):
    results = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one, t): t for t in tickers}
        for future in as_completed(futures):
            ticker = futures[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                logger.error(f"Failed to fetch {ticker}: {e}")
    return results
```

---

## 7. 确认清单

- [x] 股票池方案: 内置静态 JSON 列表
- [x] 数据文件: `data/sp500.json`, `data/nasdaq100.json`
- [x] 元数据字段: ticker, shortName, sector, sharesOutstanding
- [x] 缺失处理: 缺 shares 跳过，缺 sector 归 Unknown
- [x] 并发策略: ThreadPoolExecutor, 10 workers

---

*文档版本: v1.0 | 创建日期: 2026-01-30*
