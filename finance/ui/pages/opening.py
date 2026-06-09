"""
==============================================
 ui/pages/opening.py - 期初余额管理页面
==============================================
包含：科目期初、固定资产期初、应收应付期初、导入导出
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QHeaderView, QMessageBox,
    QAbstractItemView, QGroupBox, QTabWidget, QFileDialog, QFormLayout,
    QDoubleSpinBox, QDialog, QDialogButtonBox, QLineEdit, QSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor

from core.opening_service import OpeningService


class OpeningPage(QWidget):
    """期初余额管理页面"""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.service = OpeningService(db_manager)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        title = QLabel('<b>📥 期初余额导入</b>  <span style="color:#999;font-weight:normal;">使用本系统前已有数据，在此导入期初余额</span>')
        layout.addWidget(title)

        self._tabs = QTabWidget()
        self._tabs.addTab(self._build_balance_tab(), '📊 科目期初')
        self._tabs.addTab(self._build_asset_tab(), '🏭 固定资产期初')
        layout.addWidget(self._tabs, 1)

        # 底部上线按钮
        btn_post = QPushButton('✅ 期初上线（生成期初凭证）')
        btn_post.setStyleSheet("""
            QPushButton { background: #FF9800; color: white; padding: 12px 32px;
                         border-radius: 6px; font-size: 14px; font-weight: bold; }
        """)
        btn_post.clicked.connect(self._post_opening)
        layout.addWidget(btn_post)

    # ── 科目期初 ──
    def _build_balance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>科目期初余额</b>'))
        tool.addStretch()
        btn_tpl = QPushButton('📄 下载模板')
        btn_tpl.clicked.connect(self._export_bal_template)
        tool.addWidget(btn_tpl)
        btn_imp = QPushButton('📥 导入CSV')
        btn_imp.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;")
        btn_imp.clicked.connect(self._import_balances)
        tool.addWidget(btn_imp)
        btn_ref = QPushButton('🔄 刷新')
        btn_ref.clicked.connect(self._refresh_balances)
        tool.addWidget(btn_ref)
        layout.addLayout(tool)

        self._bal_table = QTableWidget(0, 4)
        self._bal_table.setHorizontalHeaderLabels(['科目编码', '科目名称', '借方余额', '贷方余额'])
        self._bal_table.horizontalHeader().setStretchLastSection(True)
        self._bal_table.setAlternatingRowColors(True)
        self._bal_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self._bal_table, 1)
        return tab

    def _refresh_balances(self):
        try:
            rows = self.service.get_balances()
            self._bal_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._bal_table.setItem(i, 0, QTableWidgetItem(r.get('acct_code', '')))
                self._bal_table.setItem(i, 1, QTableWidgetItem(r.get('sys_acct_name', r.get('acct_name', ''))))
                item_d = QTableWidgetItem(f"¥{r.get('debit_bal', 0):,.2f}" if r.get('debit_bal', 0) else '')
                if r.get('debit_bal', 0) > 0: item_d.setForeground(QColor('#1A73E8'))
                self._bal_table.setItem(i, 2, item_d)
                item_c = QTableWidgetItem(f"¥{r.get('credit_bal', 0):,.2f}" if r.get('credit_bal', 0) else '')
                if r.get('credit_bal', 0) > 0: item_c.setForeground(QColor('#EA4335'))
                self._bal_table.setItem(i, 3, item_c)
        except: pass

    def _import_balances(self):
        path, _ = QFileDialog.getOpenFileName(self, '导入科目期初', '', 'CSV(*.csv)')
        if path:
            ok, fail = self.service.import_balances_csv(path)
            QMessageBox.information(self, '导入结果', f'成功 {ok} 条，失败 {fail} 条')
            self._refresh_balances()

    def _export_bal_template(self):
        path, _ = QFileDialog.getSaveFileName(self, '导出模板', '科目期初模板.csv', 'CSV(*.csv)')
        if path:
            self.service.export_balances_template(path)
            QMessageBox.information(self, '成功', f'模板已导出至 {path}')

    # ── 固定资产期初 ──
    def _build_asset_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>固定资产期初卡片</b>'))
        tool.addStretch()
        btn_tpl = QPushButton('📄 下载模板')
        btn_tpl.clicked.connect(lambda: self.service.export_assets_template(
            QFileDialog.getSaveFileName(self, '导出模板', '资产期初模板.csv', 'CSV(*.csv)')[0] or ''))
        tool.addWidget(btn_tpl)
        btn_imp = QPushButton('📥 导入CSV')
        btn_imp.setStyleSheet("background:#9C27B0;color:white;padding:6px 16px;border-radius:4px;")
        btn_imp.clicked.connect(self._import_assets)
        tool.addWidget(btn_imp)
        btn_ref = QPushButton('🔄 刷新')
        btn_ref.clicked.connect(self._refresh_assets)
        tool.addWidget(btn_ref)
        layout.addLayout(tool)

        self._asset_table = QTableWidget(0, 6)
        self._asset_table.setHorizontalHeaderLabels(['资产编码', '资产名称', '类别', '原值', '累计折旧', '净值'])
        self._asset_table.horizontalHeader().setStretchLastSection(True)
        self._asset_table.setAlternatingRowColors(True)
        layout.addWidget(self._asset_table, 1)
        return tab

    def _refresh_assets(self):
        try:
            rows = self.service.get_opening_assets()
            self._asset_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._asset_table.setItem(i, 0, QTableWidgetItem(r.get('asset_code', '')))
                self._asset_table.setItem(i, 1, QTableWidgetItem(r.get('asset_name', '')))
                self._asset_table.setItem(i, 2, QTableWidgetItem(r.get('category', '')))
                self._asset_table.setItem(i, 3, QTableWidgetItem(f"¥{r.get('original_value',0):,.2f}"))
                self._asset_table.setItem(i, 4, QTableWidgetItem(f"¥{r.get('accumulated_depr',0):,.2f}"))
                self._asset_table.setItem(i, 5, QTableWidgetItem(f"¥{r.get('original_value',0)-r.get('accumulated_depr',0):,.2f}"))
        except: pass

    def _import_assets(self):
        path, _ = QFileDialog.getOpenFileName(self, '导入固定资产期初', '', 'CSV(*.csv)')
        if path:
            ok, fail = self.service.import_assets_csv(path)
            QMessageBox.information(self, '导入结果', f'成功 {ok} 条，失败 {fail} 条')
            self._refresh_assets()

    # ── 期初上线 ──
    def _post_opening(self):
        reply = QMessageBox.question(self, '确认上线',
            '期初上线将生成一张"期初建账"凭证，将所有期初余额过入账簿。\n'
            '建议：确认科目期初借贷平衡后再操作。\n\n确定上线吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes: return
        try:
            result = self.service.post_opening()
            if result['success']:
                QMessageBox.information(self, '成功', result['message'])
            else:
                QMessageBox.warning(self, '无法上线', result['message'])
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def on_activate(self, book_id):
        self.refresh()

    def refresh(self):
        self._refresh_balances()
        self._refresh_assets()