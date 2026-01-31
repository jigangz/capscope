"""市值计算与排名模块"""

import logging

logger = logging.getLogger(__name__)

# 行业中英文映射
SECTOR_CN_MAP = {
    "Technology": "信息技术",
    "Healthcare": "医疗保健",
    "Financials": "金融",
    "Consumer Cyclical": "非必需消费品",
    "Consumer Discretionary": "非必需消费品",
    "Consumer Defensive": "必需消费品",
    "Consumer Staples": "必需消费品",
    "Communication Services": "通信服务",
    "Industrials": "工业",
    "Energy": "能源",
    "Utilities": "公用事业",
    "Real Estate": "房地产",
    "Basic Materials": "原材料",
    "Materials": "原材料",
    "Unknown": "未分类"
}


def compute_market_caps(
    metadata: list[dict],
    prices: dict[str, float]
) -> list[dict]:
    """
    计算市值
    
    Args:
        metadata: [{ticker, name, sector, shares}, ...]
        prices: {ticker: close_price, ...}
    
    Returns:
        [{ticker, name, sector, sector_cn, close, shares, market_cap, market_cap_b}, ...]
    """
    results = []
    
    for stock in metadata:
        ticker = stock["ticker"]
        
        if ticker not in prices:
            logger.debug(f"No price for {ticker}, skipping")
            continue
        
        close = prices[ticker]
        shares = stock["shares"]
        market_cap = close * shares
        
        results.append({
            "ticker": ticker,
            "name": stock["name"],
            "sector": stock["sector"],
            "sector_cn": SECTOR_CN_MAP.get(stock["sector"], "未分类"),
            "close": round(close, 2),
            "shares": shares,
            "market_cap": round(market_cap, 2),
            "market_cap_b": round(market_cap / 1e9, 2)  # 十亿美元
        })
    
    # 按市值降序排序
    results.sort(key=lambda x: x["market_cap"], reverse=True)
    
    logger.info(f"Computed market caps for {len(results)} stocks")
    return results


def rank_by_sector(
    stocks: list[dict],
    top_n: int = 100
) -> dict[str, list[dict]]:
    """
    按行业分组并排名
    
    Args:
        stocks: 已计算市值的股票列表
        top_n: 每行业取前 N 只
    
    Returns:
        {sector: [top N stocks], ...}
    """
    sectors: dict[str, list[dict]] = {}
    
    for stock in stocks:
        sector = stock["sector"]
        if sector not in sectors:
            sectors[sector] = []
        sectors[sector].append(stock)
    
    # 每个行业按市值排序，取 top N
    for sector in sectors:
        sectors[sector].sort(key=lambda x: x["market_cap"], reverse=True)
        sectors[sector] = sectors[sector][:top_n]
    
    return sectors


def get_top_overall(stocks: list[dict], top_n: int = 100) -> list[dict]:
    """获取全市场 Top N"""
    return stocks[:top_n]
