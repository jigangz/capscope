"""主窗口"""

import csv
from datetime import datetime, date
from pathlib import Path

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QDateEdit, QLineEdit, QLabel,
    QTableView, QTabWidget, QProgressDialog,
    QFileDialog, QMessageBox, QStatusBar, QHeaderView
)
from PyQt6.QtCore import Qt, QDate, QTimer
from PyQt6.QtGui import QIcon

from .model import StockTableModel
from .worker import DataLoaderWorker
from ..compute import rank_by_sector, get_top_overall


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CapScope - 美股市值查看工具")
        self.setMinimumSize(900, 600)
        
        # 数据
        self._all_stocks: list[dict] = []
        self._by_sector: dict[str, list[dict]] = {}
        self._actual_date = ""
        self._load_time = 0.0
        
        # 工作线程
        self._worker: DataLoaderWorker | None = None
        self._progress_dialog: QProgressDialog | None = None
        self._start_time = 0.0
        
        self._setup_ui()
    
    def _setup_ui(self):
        """设置 UI"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # 顶部工具栏
        toolbar = QHBoxLayout()
        
        toolbar.addWidget(QLabel("📅 日期:"))
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDisplayFormat("yyyy-MM-dd")
        toolbar.addWidget(self.date_edit)
        
        self.refresh_btn = QPushButton("🔄 刷新")
        self.refresh_btn.clicked.connect(self._on_refresh)
        toolbar.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("💾 导出CSV")
        self.export_btn.clicked.connect(self._on_export)
        self.export_btn.setEnabled(False)
        toolbar.addWidget(self.export_btn)
        
        toolbar.addStretch()
        
        toolbar.addWidget(QLabel("🔍 搜索:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("输入 Ticker 或公司名...")
        self.search_edit.setFixedWidth(200)
        self.search_edit.textChanged.connect(self._on_search)
        toolbar.addWidget(self.search_edit)
        
        layout.addLayout(toolbar)
        
        # 行业 Tab
        self.tab_widget = QTabWidget()
        self.tab_widget.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self.tab_widget)
        
        # 创建初始 Tab
        self._create_tabs([])
        
        # 状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self._update_status("请点击「刷新」加载数据")
    
    def _create_tabs(self, sectors: list[str]):
        """创建行业 Tab"""
        self.tab_widget.clear()
        self._tab_models: dict[str, StockTableModel] = {}
        
        # 全部 Tab
        all_model = StockTableModel()
        all_table = self._create_table(all_model)
        self.tab_widget.addTab(all_table, "全部")
        self._tab_models["__all__"] = all_model
        
        # 各行业 Tab
        for sector in sorted(sectors):
            model = StockTableModel()
            table = self._create_table(model)
            
            # 中文行业名
            from ..compute import SECTOR_CN_MAP
            sector_cn = SECTOR_CN_MAP.get(sector, sector)
            
            self.tab_widget.addTab(table, sector_cn)
            self._tab_models[sector] = model
    
    def _create_table(self, model: StockTableModel) -> QTableView:
        """创建表格"""
        table = QTableView()
        table.setModel(model)
        table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        table.setAlternatingRowColors(True)
        table.setSortingEnabled(False)
        
        # 列宽
        header = table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.Fixed)
        
        table.setColumnWidth(0, 50)
        table.setColumnWidth(1, 80)
        table.setColumnWidth(3, 100)
        table.setColumnWidth(4, 90)
        table.setColumnWidth(5, 100)
        
        return table
    
    def _on_refresh(self):
        """刷新数据"""
        if self._worker and self._worker.isRunning():
            return
        
        date_str = self.date_edit.date().toString("yyyy-MM-dd")
        
        # 显示进度对话框
        self._progress_dialog = QProgressDialog("正在加载数据...", "取消", 0, 100, self)
        self._progress_dialog.setWindowTitle("加载中")
        self._progress_dialog.setWindowModality(Qt.WindowModality.WindowModal)
        self._progress_dialog.setMinimumDuration(0)
        self._progress_dialog.setValue(0)
        self._progress_dialog.show()
        
        self.refresh_btn.setEnabled(False)
        self._start_time = datetime.now().timestamp()
        
        # 启动工作线程
        self._worker = DataLoaderWorker(date_str)
        self._worker.progress.connect(self._on_progress)
        self._worker.finished.connect(self._on_load_finished)
        self._worker.error.connect(self._on_load_error)
        self._worker.start()
    
    def _on_progress(self, done: int, total: int):
        """更新进度"""
        if self._progress_dialog:
            pct = done * 100 // total if total > 0 else 0
            self._progress_dialog.setValue(pct)
            self._progress_dialog.setLabelText(f"正在获取元数据... {done}/{total}")
    
    def _on_load_finished(self, stocks: list[dict], actual_date: str):
        """加载完成"""
        self._load_time = datetime.now().timestamp() - self._start_time
        self._all_stocks = stocks
        self._actual_date = actual_date
        self._by_sector = rank_by_sector(stocks, top_n=100)
        
        # 更新 Tab
        self._create_tabs(list(self._by_sector.keys()))
        
        # 填充数据
        self._tab_models["__all__"].set_data(get_top_overall(stocks, 100))
        for sector, sector_stocks in self._by_sector.items():
            if sector in self._tab_models:
                self._tab_models[sector].set_data(sector_stocks)
        
        # 更新状态
        self._update_status(
            f"数据日期: {actual_date} │ "
            f"共 {len(stocks)} 只 │ "
            f"加载耗时: {self._load_time:.1f}s"
        )
        
        self.refresh_btn.setEnabled(True)
        self.export_btn.setEnabled(True)
        
        if self._progress_dialog:
            self._progress_dialog.close()
    
    def _on_load_error(self, error: str):
        """加载失败"""
        self.refresh_btn.setEnabled(True)
        
        if self._progress_dialog:
            self._progress_dialog.close()
        
        QMessageBox.critical(self, "加载失败", f"数据加载失败:\n{error}")
        self._update_status("加载失败")
    
    def _on_search(self, text: str):
        """搜索过滤"""
        for model in self._tab_models.values():
            model.set_filter(text)
    
    def _on_tab_changed(self, index: int):
        """Tab 切换"""
        # 搜索过滤保持
        text = self.search_edit.text()
        if text:
            self._on_search(text)
    
    def _on_export(self):
        """导出 CSV"""
        # 获取当前 Tab 的数据
        current_index = self.tab_widget.currentIndex()
        if current_index == 0:
            model = self._tab_models.get("__all__")
        else:
            tab_text = self.tab_widget.tabText(current_index)
            # 找到对应的英文 sector
            from ..compute import SECTOR_CN_MAP
            sector = None
            for en, cn in SECTOR_CN_MAP.items():
                if cn == tab_text:
                    sector = en
                    break
            model = self._tab_models.get(sector) if sector else None
        
        if not model:
            return
        
        data = model.get_filtered_data()
        if not data:
            QMessageBox.information(self, "导出", "没有数据可导出")
            return
        
        # 选择保存路径
        default_name = f"capscope_{self._actual_date}.csv"
        path, _ = QFileDialog.getSaveFileName(
            self, "导出 CSV", default_name, "CSV Files (*.csv)"
        )
        
        if not path:
            return
        
        # 写入 CSV
        try:
            with open(path, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=[
                    "ticker", "name", "sector", "sector_cn",
                    "close", "shares", "market_cap", "market_cap_b"
                ])
                writer.writeheader()
                writer.writerows(data)
            
            QMessageBox.information(self, "导出成功", f"已导出到:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "导出失败", str(e))
    
    def _update_status(self, text: str):
        """更新状态栏"""
        self.status_bar.showMessage(text)
