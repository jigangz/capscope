"""价格获取模块"""

import logging
from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_prices(
    tickers: list[str],
    date: str
) -> tuple[dict[str, float], str]:
    """
    获取指定日期的收盘价
    
    Args:
        tickers: 股票代码列表
        date: 目标日期 "YYYY-MM-DD"
    
    Returns:
        (prices_dict, actual_date)
        prices_dict: {"AAPL": 185.92, ...}
        actual_date: 实际使用的交易日
    """
    target_date = datetime.strptime(date, "%Y-%m-%d")
    
    # 往前多取几天，确保能拿到交易日数据
    start_date = target_date - timedelta(days=10)
    end_date = target_date + timedelta(days=1)
    
    logger.info(f"Fetching prices for {len(tickers)} tickers, target date: {date}")
    
    # yfinance 批量下载
    data = yf.download(
        tickers=tickers,
        start=start_date.strftime("%Y-%m-%d"),
        end=end_date.strftime("%Y-%m-%d"),
        progress=False,
        threads=True
    )
    
    if data.empty:
        logger.error("No price data returned")
        return {}, date
    
    # 获取 Close 价格
    close_data = data["Close"] if "Close" in data.columns else data[("Close",)]
    
    # 找到最接近目标日期的交易日（不超过目标日期）
    available_dates = close_data.index[close_data.index <= pd.Timestamp(target_date)]
    
    if len(available_dates) == 0:
        logger.error(f"No trading day found before {date}")
        return {}, date
    
    actual_date = available_dates[-1]
    actual_date_str = actual_date.strftime("%Y-%m-%d")
    
    if actual_date_str != date:
        logger.info(f"Using nearest trading day: {actual_date_str} (requested: {date})")
    
    # 提取该日价格
    if isinstance(close_data, pd.DataFrame):
        prices_row = close_data.loc[actual_date]
        prices = {ticker: price for ticker, price in prices_row.items() if pd.notna(price)}
    else:
        # 单个 ticker 的情况
        price = close_data.loc[actual_date]
        prices = {tickers[0]: price} if pd.notna(price) else {}
    
    logger.info(f"Got prices for {len(prices)} tickers on {actual_date_str}")
    return prices, actual_date_str
