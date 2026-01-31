"""表格数据模型"""

from PyQt6.QtCore import Qt, QAbstractTableModel, QModelIndex
from typing import Any


class StockTableModel(QAbstractTableModel):
    """股票数据表格模型"""
    
    HEADERS = ["#", "Ticker", "公司名称", "行业", "收盘价", "市值(B)"]
    
    def __init__(self):
        super().__init__()
        self._data: list[dict] = []
        self._filtered_data: list[dict] = []
        self._filter_text = ""
    
    def set_data(self, stocks: list[dict]):
        """设置数据"""
        self.beginResetModel()
        self._data = stocks
        self._apply_filter()
        self.endResetModel()
    
    def set_filter(self, text: str):
        """设置过滤文本"""
        self.beginResetModel()
        self._filter_text = text.lower()
        self._apply_filter()
        self.endResetModel()
    
    def _apply_filter(self):
        """应用过滤"""
        if not self._filter_text:
            self._filtered_data = self._data
        else:
            self._filtered_data = [
                s for s in self._data
                if self._filter_text in s["ticker"].lower()
                or self._filter_text in s["name"].lower()
            ]
    
    def get_filtered_data(self) -> list[dict]:
        """获取过滤后的数据"""
        return self._filtered_data
    
    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._filtered_data)
    
    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.HEADERS)
    
    def data(self, index: QModelIndex, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if not index.isValid():
            return None
        
        if role == Qt.ItemDataRole.DisplayRole:
            row = index.row()
            col = index.column()
            stock = self._filtered_data[row]
            
            if col == 0:
                return row + 1
            elif col == 1:
                return stock["ticker"]
            elif col == 2:
                return stock["name"]
            elif col == 3:
                return stock["sector_cn"]
            elif col == 4:
                return f"${stock['close']:,.2f}"
            elif col == 5:
                return f"{stock['market_cap_b']:,.2f}"
        
        elif role == Qt.ItemDataRole.TextAlignmentRole:
            col = index.column()
            if col in [0]:
                return Qt.AlignmentFlag.AlignCenter
            elif col in [4, 5]:
                return Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter
            return Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        
        return None
    
    def headerData(self, section: int, orientation: Qt.Orientation, role: int = Qt.ItemDataRole.DisplayRole) -> Any:
        if orientation == Qt.Orientation.Horizontal and role == Qt.ItemDataRole.DisplayRole:
            return self.HEADERS[section]
        return None
