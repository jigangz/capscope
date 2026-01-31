"""命令行入口"""

import argparse
import logging
import sys
from datetime import datetime

from .universe import get_universe
from .metadata import fetch_metadata
from .prices import fetch_prices
from .compute import compute_market_caps, rank_by_sector, get_top_overall
from .export import export_csv, export_json, print_csv


def setup_logging(verbose: bool = False):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        datefmt="%H:%M:%S"
    )


def main():
    parser = argparse.ArgumentParser(
        description="CapScope - 美股历史市值查看工具"
    )
    parser.add_argument(
        "--date", "-d",
        default=datetime.now().strftime("%Y-%m-%d"),
        help="查询日期 (YYYY-MM-DD)，默认今天"
    )
    parser.add_argument(
        "--out", "-o",
        help="输出文件路径，不指定则输出到 stdout"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["csv", "json"],
        default="csv",
        help="输出格式 (csv/json)，默认 csv"
    )
    parser.add_argument(
        "--sector", "-s",
        help="只看某个行业"
    )
    parser.add_argument(
        "--top", "-t",
        type=int,
        default=100,
        help="每行业取 Top N，默认 100"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="详细日志"
    )
    
    args = parser.parse_args()
    setup_logging(args.verbose)
    logger = logging.getLogger(__name__)
    
    # 1. 加载股票池
    logger.info("Loading universe...")
    tickers = get_universe()
    logger.info(f"Loaded {len(tickers)} tickers")
    
    # 2. 获取元数据
    logger.info("Fetching metadata...")
    
    def progress(done, total):
        pct = done * 100 // total
        print(f"\rFetching metadata: {done}/{total} ({pct}%)", end="", flush=True)
    
    metadata = fetch_metadata(tickers, progress_callback=progress)
    print()  # 换行
    
    # 3. 获取价格
    logger.info(f"Fetching prices for {args.date}...")
    valid_tickers = [m["ticker"] for m in metadata]
    prices, actual_date = fetch_prices(valid_tickers, args.date)
    
    if actual_date != args.date:
        logger.info(f"Note: Using trading day {actual_date} (requested {args.date})")
    
    # 4. 计算市值
    logger.info("Computing market caps...")
    stocks = compute_market_caps(metadata, prices)
    
    # 5. 过滤/排名
    if args.sector:
        by_sector = rank_by_sector(stocks, args.top)
        if args.sector in by_sector:
            output_stocks = by_sector[args.sector]
        else:
            logger.error(f"Sector '{args.sector}' not found")
            logger.info(f"Available sectors: {list(by_sector.keys())}")
            sys.exit(1)
    else:
        output_stocks = get_top_overall(stocks, args.top)
    
    # 6. 输出
    if args.out:
        if args.format == "json":
            export_json(output_stocks, args.date, actual_date, args.out)
        else:
            export_csv(output_stocks, args.out)
        logger.info(f"Exported to {args.out}")
    else:
        print_csv(output_stocks)
    
    logger.info("Done!")


if __name__ == "__main__":
    main()
