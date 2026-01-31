"""后台工作线程"""

from PyQt6.QtCore import QThread, pyqtSignal


class DataLoaderWorker(QThread):
    """数据加载工作线程"""
    
    progress = pyqtSignal(int, int)  # (completed, total)
    finished = pyqtSignal(list, str)  # (stocks, actual_date)
    error = pyqtSignal(str)
    
    def __init__(self, date: str):
        super().__init__()
        self.date = date
    
    def run(self):
        try:
            from ..universe import get_universe
            from ..metadata import fetch_metadata
            from ..prices import fetch_prices
            from ..compute import compute_market_caps
            
            # 1. 加载股票池
            tickers = get_universe()
            
            # 2. 获取元数据
            def on_progress(done, total):
                self.progress.emit(done, total)
            
            metadata = fetch_metadata(tickers, progress_callback=on_progress)
            
            # 3. 获取价格
            valid_tickers = [m["ticker"] for m in metadata]
            prices, actual_date = fetch_prices(valid_tickers, self.date)
            
            # 4. 计算市值
            stocks = compute_market_caps(metadata, prices)
            
            self.finished.emit(stocks, actual_date)
            
        except Exception as e:
            self.error.emit(str(e))
