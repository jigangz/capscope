"""元数据获取模块"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable

import yfinance as yf

logger = logging.getLogger(__name__)


def fetch_one_metadata(ticker: str) -> dict | None:
    """
    获取单个股票的元数据
    
    Returns:
        {ticker, name, sector, shares} 或 None（无效数据）
    """
    try:
        info = yf.Ticker(ticker).info
        
        shares = info.get("sharesOutstanding")
        if not shares or shares <= 0:
            logger.warning(f"Skipping {ticker}: missing sharesOutstanding")
            return None
        
        return {
            "ticker": ticker,
            "name": info.get("shortName") or info.get("longName") or ticker,
            "sector": info.get("sector") or "Unknown",
            "shares": shares
        }
    except Exception as e:
        logger.error(f"Failed to fetch {ticker}: {e}")
        return None


def fetch_metadata(
    tickers: list[str],
    max_workers: int = 10,
    progress_callback: Callable[[int, int], None] | None = None
) -> list[dict]:
    """
    批量获取元数据
    
    Args:
        tickers: 股票代码列表
        max_workers: 并发线程数
        progress_callback: 进度回调 (completed, total)
    
    Returns:
        有效的元数据列表
    """
    results = []
    total = len(tickers)
    completed = 0
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(fetch_one_metadata, t): t for t in tickers}
        
        for future in as_completed(futures):
            completed += 1
            ticker = futures[future]
            
            try:
                data = future.result()
                if data:
                    results.append(data)
            except Exception as e:
                logger.error(f"Exception for {ticker}: {e}")
            
            if progress_callback:
                progress_callback(completed, total)
    
    logger.info(f"Fetched metadata: {len(results)}/{total} valid")
    return results
