# CapScope V1 核心计算与数据管线设计

> Batch 3 产出物 — 核心逻辑设计与 CLI 方案

---

## 1. 模块架构

```
capscope/
├── __init__.py
├── universe.py      # 股票池加载
├── metadata.py      # 元数据获取
├── prices.py        # 价格获取
├── compute.py       # 市值计算与排名
├── export.py        # 导出 CSV/JSON
└── cli.py           # 命令行入口
```

---

## 2. 核心函数设计

### 2.1 universe.py — 股票池加载

```python
def get_universe() -> list[str]:
    """
    加载股票池（S&P 500 + Nasdaq 100 去重）
    
    Returns:
        tickers: ["AAPL", "MSFT", ...]
    """
```

### 2.2 metadata.py — 元数据获取

```python
def fetch_metadata(tickers: list[str], max_workers: int = 10) -> list[dict]:
    """
    批量获取元数据（公司名、行业、流通股数）
    
    Args:
        tickers: 股票代码列表
        max_workers: 并发线程数
    
    Returns:
        metadata: [{ticker, name, sector, shares}, ...]
        (跳过 shares 无效的股票)
    """
```

### 2.3 prices.py — 价格获取

```python
def fetch_prices(tickers: list[str], date: str) -> dict[str, float]:
    """
    获取指定日期的收盘价
    
    Args:
        tickers: 股票代码列表
        date: 目标日期 "YYYY-MM-DD"
    
    Returns:
        prices: {"AAPL": 185.92, "MSFT": 402.56, ...}
        actual_date: 实际使用的交易日
    """
```

### 2.4 compute.py — 市值计算与排名

```python
def compute_market_caps(
    metadata: list[dict], 
    prices: dict[str, float]
) -> list[dict]:
    """
    计算市值
    
    Returns:
        stocks: [{ticker, name, sector, close, shares, market_cap}, ...]
    """

def rank_by_sector(
    stocks: list[dict], 
    top_n: int = 100
) -> dict[str, list[dict]]:
    """
    按行业分组并排名
    
    Returns:
        {
            "Technology": [top 100 stocks...],
            "Healthcare": [top 100 stocks...],
            ...
        }
    """
```

### 2.5 export.py — 导出

```python
def export_csv(stocks: list[dict], path: str) -> None:
    """导出为 CSV"""

def export_json(data: dict, path: str) -> None:
    """导出为 JSON"""
```

---

## 3. 数据流

```
┌──────────────┐
│ get_universe │ → tickers (550)
└──────┬───────┘
       ↓
┌────────────────┐
│ fetch_metadata │ → metadata [{ticker, name, sector, shares}]
└──────┬─────────┘
       ↓
┌──────────────┐
│ fetch_prices │ → prices {ticker: close}
└──────┬───────┘
       ↓
┌────────────────────┐
│ compute_market_caps│ → stocks [{..., market_cap}]
└──────┬─────────────┘
       ↓
┌────────────────┐
│ rank_by_sector │ → {sector: [top 100]}
└──────┬─────────┘
       ↓
┌────────────┐
│ export_csv │ → output.csv
└────────────┘
```

---

## 4. CLI 方案

### 命令格式

```bash
python -m capscope --date 2024-01-15 --out result.csv --format csv
```

### 参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--date` | 查询日期 (YYYY-MM-DD) | 今天 |
| `--out` | 输出文件路径 | stdout |
| `--format` | 输出格式 (csv/json) | csv |
| `--sector` | 只看某个行业 | 全部 |
| `--top` | 每行业取 Top N | 100 |

### 输出示例

```
$ python -m capscope --date 2024-01-15 --format csv

ticker,name,sector,close,shares,market_cap
AAPL,Apple Inc.,Technology,185.92,15460000000,2875027200000
MSFT,Microsoft Corporation,Technology,402.56,7430000000,2991020800000
...
```

---

## 5. 并发与性能策略

### 5.1 元数据获取

- **方式**: ThreadPoolExecutor, 10 workers
- **耗时**: ~1-2 分钟 (550 只)
- **重试**: 单股失败不重试，跳过

### 5.2 价格获取

- **方式**: yfinance `download()` 批量接口
- **优化**: 一次请求所有 ticker
- **耗时**: ~10-30 秒

```python
import yfinance as yf

# 批量获取，比逐个快很多
data = yf.download(
    tickers=tickers,      # 传入列表
    start=date,
    end=next_day,
    progress=False
)
prices = data["Close"].iloc[0].to_dict()
```

### 5.3 进度反馈

```python
from tqdm import tqdm

for ticker in tqdm(tickers, desc="Fetching metadata"):
    ...
```

---

## 6. 错误处理

| 场景 | 处理 |
|------|------|
| 网络超时 | 跳过该股票，记录 warning |
| 无效日期 | 报错退出，提示格式 |
| 非交易日 | 自动回退，输出实际日期 |
| 无数据返回 | 跳过，记录 warning |

---

## 7. 确认清单

- [x] 5 个核心模块: universe, metadata, prices, compute, export
- [x] CLI 支持: --date, --out, --format, --sector, --top
- [x] 元数据并发: 10 workers
- [x] 价格批量获取: yf.download()
- [x] 进度条: tqdm

---

*文档版本: v1.0 | 创建日期: 2026-01-30*
