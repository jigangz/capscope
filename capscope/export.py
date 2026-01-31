"""导出模块"""

import csv
import json
from datetime import datetime
from pathlib import Path


def export_csv(stocks: list[dict], path: str) -> None:
    """
    导出为 CSV
    
    Args:
        stocks: 股票数据列表
        path: 输出文件路径
    """
    if not stocks:
        return
    
    fieldnames = ["ticker", "name", "sector", "sector_cn", "close", "shares", "market_cap", "market_cap_b"]
    
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(stocks)


def export_json(
    stocks: list[dict],
    query_date: str,
    actual_date: str,
    path: str
) -> None:
    """
    导出为 JSON
    
    Args:
        stocks: 股票数据列表
        query_date: 用户请求日期
        actual_date: 实际使用的交易日
        path: 输出文件路径
    """
    data = {
        "query_date": query_date,
        "actual_date": actual_date,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_stocks": len(stocks),
        "stocks": stocks
    }
    
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def print_csv(stocks: list[dict]) -> None:
    """输出到 stdout"""
    if not stocks:
        print("No data")
        return
    
    fieldnames = ["ticker", "name", "sector", "close", "shares", "market_cap_b"]
    print(",".join(fieldnames))
    
    for stock in stocks:
        row = [str(stock.get(f, "")) for f in fieldnames]
        print(",".join(row))
