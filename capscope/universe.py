"""股票池加载模块"""

import json
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"


def get_universe() -> list[str]:
    """
    加载股票池（S&P 500 + Nasdaq 100 去重）
    
    Returns:
        去重后的 ticker 列表
    """
    tickers = set()
    
    for filename in ["sp500.json", "nasdaq100.json"]:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, "r") as f:
                data = json.load(f)
                tickers.update(data.get("tickers", []))
    
    return sorted(list(tickers))


def get_universe_info() -> dict:
    """获取股票池元信息"""
    info = {}
    for filename in ["sp500.json", "nasdaq100.json"]:
        filepath = DATA_DIR / filename
        if filepath.exists():
            with open(filepath, "r") as f:
                data = json.load(f)
                info[data.get("index", filename)] = {
                    "count": data.get("count", 0),
                    "updated": data.get("updated", "unknown")
                }
    return info
