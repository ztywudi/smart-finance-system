"""
==============================================
 ui/pages/cashier.py - 出纳管理页面
==============================================
包含：现金日记账、银行日记账、银行对账+余额调节表
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QHeaderView,
    QTabWidget, QMessageBox, QAbstractItemView, QDialog, QFormLayout,
    QDateEdit, QDoubleSpinBox, QTextEdit, QGroupBox, QGridLayout,
    QFrame, QDialogButtonBox
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QColor

from core.cashier_service import CashierService


# ── 日记账登记对话框 ──
class JournalEntryDialog(QDialog):
    """出纳日记账登记对话框"""

    def __init__(self, service, journal_type='cash', parent=None):
        super().__init__(parent)
        self.service = service
        self.journal_type = journal_type
        self.setWindowTitle(f'登记{"现金" if journal_type=="cash" else "银行"}日记账')
        self.setMinimumWidth(450)
        self.setModal(True)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        form = QFormLayout()
        form.setSpacing(8)

        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())
        form.addRow('日期:', self._date)

        if self.journal_type == 'bank':
            self._bank_acct = QComboBox()
            self._bank_acct.setEditable(True)
            self._bank_acct.addItems(['工行存款', '建行存款', '农行存款', '招行存款'])
            form.addRow('银行账户:', self._bank_acct)

        self._summary = QTextEdit()
        self._summary.setPlaceholderText('业务摘要')
        self._summary.setMaximumHeight(50)
        form.addRow('摘要:', self._summary)

        self._income = QDoubleSpinBox()
        self._income.setRange(0, 999999999)
        self._income.setDecimals(2)
        self._income.setPrefix('¥ ')
        self._income.setValue(0)
        form.addRow('收入金额:', self._income)

        self._expense = QDoubleSpinBox()
        self._expense.setRange(0, 999999999)
        self._expense.setDecimals(2)
        self._expense.setPrefix('¥ ')
        self._expense.setValue(0)
        form.addRow('支出金额:', self._expense)

        self._acct_code = QLineEdit()
        self._acct_code.setPlaceholderText('对方科目编码（可选）')
        form.addRow('对方科目:', self._acct_code)

        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn = QPushButton('✅ 保存')
        self._btn.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 8px 24px;
                         border-radius: 4px; font-weight: bold; }
        """)
        self._btn.clicked.connect(self._save)
        btn_layout.addWidget(self._btn)
        btn_layout.addWidget(QPushButton('取消', clicked=self.reject))
        layout.addLayout(btn_layout)

    def _save(self):
        income = self._income.value()
        expense = self._expense.value()
        if income == 0 and expense == 0:
            QMessageBox.warning(self, '提示', '收入和支出不能同时为0')
            return
        if income > 0 and expense > 0:
            QMessageBox.warning(self, '提示', '收入和支出不能同时有值')
            return

        date = self._date.date().toString('yyyy-MM-dd')
        summary = self._summary.toPlainText().strip()
        acct_code = self._acct_code.text().strip()

        try:
            if self.journal_type == 'cash':
                self.service.cash_entry(date, summary, income, expense, acct_code)
            else:
                bank_acct = self._bank_acct.currentText() if hasattr(self, '_bank_acct') else ''
                self.service.bank_entry(date, summary, income, expense, bank_acct, acct_code)
            QMessageBox.information(self, '成功', '登记完成')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))


# ── 主页面 ──
class CashierPage(QWidget):
    """出纳管理页面"""

    def __init__(self, db_manager, tab='cash'):
        super().__init__()
        self.db_manager = db_manager
        self.service = CashierService(db_manager)
        self._setup()

        tab_map = {'cash': 0, 'bank': 1, 'reconcile': 2}
        self._tabs.setCurrentIndex(tab_map.get(tab, 0))

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #F5F6FA; }
            QTabBar::tab { padding: 10px 20px; font-size: 13px;
                          border: none; border-bottom: 2px solid transparent; }
            QTabBar::tab:selected { color: #1A73E8; border-bottom: 2px solid #1A73E8; font-weight: bold; }
        """)

        self._tabs.addTab(self._build_cash_tab(), '💰 现金日记账')
        self._tabs.addTab(self._build_bank_tab(), '🏦 银行日记账')
        self._tabs.addTab(self._build_reconcile_tab(), '📊 银行对账')
        layout.addWidget(self._tabs)

    # ── 现金日记账 ──
    def _build_cash_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>💰 现金日记账</b>'))
        tool.addStretch()

        self._cash_balance = QLabel('余额: ¥0.00')
        self._cash_balance.setStyleSheet("""
            padding: 6px 12px; background: #E8F5E9; border-radius: 4px;
            font-weight: bold; font-size: 14px; color: #2E7D32;
        """)
        tool.addWidget(self._cash_balance)
        tool.addWidget(QLabel('  '))

        btn_add = QPushButton('➕ 登记')
        btn_add.setStyleSheet("background: #34A853; color: white; padding: 6px 16px; border-radius: 4px; font-weight: bold;")
        btn_add.clicked.connect(lambda: self._add_entry('cash'))
        tool.addWidget(btn_add)

        btn_sync = QPushButton('🔄 从凭证同步')
        btn_sync.clicked.connect(lambda: self._sync_from_voucher('cash'))
        tool.addWidget(btn_sync)

        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._refresh_cash)
        tool.addWidget(btn_refresh)
        layout.addLayout(tool)

        # 查询条件
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('从:'))
        self._cash_from = QDateEdit()
        self._cash_from.setCalendarPopup(True)
        self._cash_from.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self._cash_from)
        filter_layout.addWidget(QLabel('至:'))
        self._cash_to = QDateEdit()
        self._cash_to.setCalendarPopup(True)
        self._cash_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self._cash_to)
        btn_q = QPushButton('🔍 查询')
        btn_q.clicked.connect(self._refresh_cash)
        filter_layout.addWidget(btn_q)
        filter_layout.addStretch()

        self._cash_info = QLabel('')
        self._cash_info.setStyleSheet("color: #666;")
        filter_layout.addWidget(self._cash_info)
        layout.addLayout(filter_layout)

        self._cash_table = QTableWidget(0, 6)
        self._cash_table.setHorizontalHeaderLabels(['日期', '摘要', '对方科目', '收入', '支出', '余额'])
        self._cash_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._cash_table.setAlternatingRowColors(True)
        self._cash_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._cash_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none; border-bottom: 2px solid #E0E0E0;
                                  padding: 6px; font-weight: bold; }
        """)
        layout.addWidget(self._cash_table, 1)

        return tab

    def _refresh_cash(self):
        date_from = self._cash_from.date().toString('yyyy-MM-dd')
        date_to = self._cash_to.date().toString('yyyy-MM-dd')
        try:
            rows, total = self.service.query_cash(date_from, date_to)
            self._cash_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._cash_table.setItem(i, 0, QTableWidgetItem(r.get('date', '')))
                self._cash_table.setItem(i, 1, QTableWidgetItem(r.get('summary', '')))
                self._cash_table.setItem(i, 2, QTableWidgetItem(r.get('acct_code', '')))
                income_item = QTableWidgetItem(f"¥{r.get('income', 0):,.2f}")
                if r.get('income', 0) > 0:
                    income_item.setForeground(QColor('#34A853'))
                self._cash_table.setItem(i, 3, income_item)
                expense_item = QTableWidgetItem(f"¥{r.get('expense', 0):,.2f}")
                if r.get('expense', 0) > 0:
                    expense_item.setForeground(QColor('#EA4335'))
                self._cash_table.setItem(i, 4, expense_item)
                self._cash_table.setItem(i, 5, QTableWidgetItem(f"¥{r.get('balance', 0):,.2f}"))
            balance = self.service.get_cash_balance()
            self._cash_balance.setText(f'余额: ¥{balance:,.2f}')
            self._cash_info.setText(f'共 {total} 条记录')
        except Exception:
            pass

    # ── 银行日记账 ──
    def _build_bank_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>🏦 银行日记账</b>'))
        tool.addStretch()

        self._bank_balance = QLabel('余额: ¥0.00')
        self._bank_balance.setStyleSheet("""
            padding: 6px 12px; background: #E3F2FD; border-radius: 4px;
            font-weight: bold; font-size: 14px; color: #1565C0;
        """)
        tool.addWidget(self._bank_balance)
        tool.addWidget(QLabel('  '))

        btn_add = QPushButton('➕ 登记')
        btn_add.setStyleSheet("background: #34A853; color: white; padding: 6px 16px; border-radius: 4px; font-weight: bold;")
        btn_add.clicked.connect(lambda: self._add_entry('bank'))
        tool.addWidget(btn_add)
        btn_sync = QPushButton('🔄 从凭证同步')
        btn_sync.clicked.connect(lambda: self._sync_from_voucher('bank'))
        tool.addWidget(btn_sync)
        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._refresh_bank)
        tool.addWidget(btn_refresh)
        layout.addLayout(tool)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('账户:'))
        self._bank_acct_filter = QComboBox()
        self._bank_acct_filter.setEditable(True)
        self._bank_acct_filter.addItems(['全部', '工行存款', '建行存款', '农行存款', '招行存款'])
        filter_layout.addWidget(self._bank_acct_filter)
        filter_layout.addWidget(QLabel('从:'))
        self._bank_from = QDateEdit()
        self._bank_from.setCalendarPopup(True)
        self._bank_from.setDate(QDate.currentDate().addMonths(-1))
        filter_layout.addWidget(self._bank_from)
        filter_layout.addWidget(QLabel('至:'))
        self._bank_to = QDateEdit()
        self._bank_to.setCalendarPopup(True)
        self._bank_to.setDate(QDate.currentDate())
        filter_layout.addWidget(self._bank_to)
        btn_q = QPushButton('🔍 查询')
        btn_q.clicked.connect(self._refresh_bank)
        filter_layout.addWidget(btn_q)
        filter_layout.addStretch()
        self._bank_info = QLabel('')
        self._bank_info.setStyleSheet("color: #666;")
        filter_layout.addWidget(self._bank_info)
        layout.addLayout(filter_layout)

        self._bank_table = QTableWidget(0, 7)
        self._bank_table.setHorizontalHeaderLabels(['日期', '银行账户', '摘要', '对方科目', '收入', '支出', '余额'])
        self._bank_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._bank_table.setAlternatingRowColors(True)
        self._bank_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._bank_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none; border-bottom: 2px solid #E0E0E0;
                                  padding: 6px; font-weight: bold; }
        """)
        layout.addWidget(self._bank_table, 1)

        return tab

    def _refresh_bank(self):
        acct = self._bank_acct_filter.currentText()
        if acct == '全部': acct = ''
        date_from = self._bank_from.date().toString('yyyy-MM-dd')
        date_to = self._bank_to.date().toString('yyyy-MM-dd')
        try:
            rows, total = self.service.query_bank(acct, date_from, date_to)
            self._bank_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._bank_table.setItem(i, 0, QTableWidgetItem(r.get('date', '')))
                self._bank_table.setItem(i, 1, QTableWidgetItem(r.get('bank_acct', '')))
                self._bank_table.setItem(i, 2, QTableWidgetItem(r.get('summary', '')))
                self._bank_table.setItem(i, 3, QTableWidgetItem(r.get('acct_code', '')))
                inc = QTableWidgetItem(f"¥{r.get('income',0):,.2f}")
                if r.get('income',0)>0: inc.setForeground(QColor('#34A853'))
                self._bank_table.setItem(i, 4, inc)
                exp = QTableWidgetItem(f"¥{r.get('expense',0):,.2f}")
                if r.get('expense',0)>0: exp.setForeground(QColor('#EA4335'))
                self._bank_table.setItem(i, 5, exp)
                self._bank_table.setItem(i, 6, QTableWidgetItem(f"¥{r.get('balance',0):,.2f}"))
            balance = self.service.get_bank_balance()
            self._bank_balance.setText(f'余额: ¥{balance:,.2f}')
            self._bank_info.setText(f'共 {total} 条记录')
        except Exception:
            pass

    # ── 银行对账 ──
    def _build_reconcile_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 操作区
        op_group = QGroupBox('余额调节表')
        op_group.setStyleSheet("QGroupBox { font-weight: bold; padding-top: 16px; }")
        op_layout = QGridLayout(op_group)
        op_layout.setSpacing(8)

        op_layout.addWidget(QLabel('期间:'), 0, 0)
        self._rec_period = QComboBox()
        for y in range(2024, 2031):
            for m in range(1, 13):
                self._rec_period.addItem(f'{y}-{m:02d}')
        now = datetime.now()
        idx = self._rec_period.findText(f'{now.year}-{now.month:02d}')
        if idx >= 0: self._rec_period.setCurrentIndex(idx)
        op_layout.addWidget(self._rec_period, 0, 1)

        op_layout.addWidget(QLabel('银行账户:'), 0, 2)
        self._rec_acct = QComboBox()
        self._rec_acct.setEditable(True)
        self._rec_acct.addItems(['工行存款', '建行存款'])
        op_layout.addWidget(self._rec_acct, 0, 3)

        op_layout.addWidget(QLabel('账面余额:'), 1, 0)
        self._rec_book = QDoubleSpinBox()
        self._rec_book.setRange(0, 999999999)
        self._rec_book.setDecimals(2)
        self._rec_book.setPrefix('¥ ')
        op_layout.addWidget(self._rec_book, 1, 1)

        op_layout.addWidget(QLabel('银行对账单余额:'), 1, 2)
        self._rec_bank = QDoubleSpinBox()
        self._rec_bank.setRange(0, 999999999)
        self._rec_bank.setDecimals(2)
        self._rec_bank.setPrefix('¥ ')
        op_layout.addWidget(self._rec_bank, 1, 3)

        op_layout.addWidget(QLabel('企业已收银行未收:'), 2, 0)
        self._rec_bu = QDoubleSpinBox()
        self._rec_bu.setRange(0, 999999999); self._rec_bu.setDecimals(2); self._rec_bu.setPrefix('¥ ')
        op_layout.addWidget(self._rec_bu, 2, 1)

        op_layout.addWidget(QLabel('企业已付银行未付:'), 2, 2)
        self._rec_bp = QDoubleSpinBox()
        self._rec_bp.setRange(0, 999999999); self._rec_bp.setDecimals(2); self._rec_bp.setPrefix('¥ ')
        op_layout.addWidget(self._rec_bp, 2, 3)

        op_layout.addWidget(QLabel('银行已收企业未收:'), 3, 0)
        self._rec_ub = QDoubleSpinBox()
        self._rec_ub.setRange(0, 999999999); self._rec_ub.setDecimals(2); self._rec_ub.setPrefix('¥ ')
        op_layout.addWidget(self._rec_ub, 3, 1)

        op_layout.addWidget(QLabel('银行已付企业未付:'), 3, 2)
        self._rec_up = QDoubleSpinBox()
        self._rec_up.setRange(0, 999999999); self._rec_up.setDecimals(2); self._rec_up.setPrefix('¥ ')
        op_layout.addWidget(self._rec_up, 3, 3)

        # 计算按钮
        btn_calc = QPushButton('🧮 计算调节表')
        btn_calc.setStyleSheet("background: #1A73E8; color: white; padding: 8px 24px; border-radius: 4px; font-weight: bold;")
        btn_calc.clicked.connect(self._do_reconcile)
        op_layout.addWidget(btn_calc, 4, 0, 1, 2)

        self._rec_result = QLabel('')
        op_layout.addWidget(self._rec_result, 4, 2, 1, 2)
        layout.addWidget(op_group)

        # 历史记录
        layout.addWidget(QLabel('<b>历史调节表</b>'))
        self._rec_table = QTableWidget(0, 5)
        self._rec_table.setHorizontalHeaderLabels(['期间', '银行账户', '账面余额', '银行余额', '是否平衡'])
        self._rec_table.horizontalHeader().setStretchLastSection(True)
        self._rec_table.setAlternatingRowColors(True)
        self._rec_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._rec_table, 1)

        btn_refresh = QPushButton('🔄 刷新历史')
        btn_refresh.clicked.connect(self._refresh_rec)
        layout.addWidget(btn_refresh)

        return tab

    def _do_reconcile(self):
        period = self._rec_period.currentText()
        acct = self._rec_acct.currentText()
        book = self._rec_book.value()
        bank = self._rec_bank.value()
        try:
            result = self.service.reconcile(
                period, acct, book, bank,
                self._rec_bu.value(), self._rec_bp.value(),
                self._rec_ub.value(), self._rec_up.value())
            if result['matched']:
                self._rec_result.setText(
                    f'✅ 平衡！调整后余额: ¥{result["adjusted_book"]:,.2f}')
                self._rec_result.setStyleSheet(
                    "padding: 8px; background: #E8F5E9; border-radius: 4px; color: #2E7D32; font-weight: bold;")
            else:
                self._rec_result.setText(
                    f'❌ 不平衡！企业调整: ¥{result["adjusted_book"]:,.2f} | '
                    f'银行调整: ¥{result["adjusted_bank"]:,.2f} | '
                    f'差额: ¥{result["adjusted_book"] - result["adjusted_bank"]:,.2f}')
                self._rec_result.setStyleSheet(
                    "padding: 8px; background: #FCE8E6; border-radius: 4px; color: #C62828; font-weight: bold;")
            self._refresh_rec()
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def _refresh_rec(self):
        try:
            rows, total = self.service.get_reconciliation_history()
            self._rec_table.setRowCount(len(rows))
            for i, r in enumerate(rows):
                self._rec_table.setItem(i, 0, QTableWidgetItem(r.get('period', '')))
                self._rec_table.setItem(i, 1, QTableWidgetItem(r.get('bank_acct', '')))
                self._rec_table.setItem(i, 2, QTableWidgetItem(f"¥{r.get('book_balance',0):,.2f}"))
                self._rec_table.setItem(i, 3, QTableWidgetItem(f"¥{r.get('bank_balance',0):,.2f}"))
                item = QTableWidgetItem('✅ 平衡' if r.get('matched') else '❌ 不平衡')
                item.setForeground(QColor('#34A853') if r.get('matched') else QColor('#EA4335'))
                self._rec_table.setItem(i, 4, item)
        except Exception:
            pass

    # ── 公共 ──
    def _add_entry(self, jtype):
        dlg = JournalEntryDialog(self.service, jtype, self)
        if dlg.exec():
            self._refresh_cash() if jtype == 'cash' else self._refresh_bank()

    def _sync_from_voucher(self, jtype):
        period = f'{datetime.now().year}-{datetime.now().month:02d}'
        try:
            self.service.synch_from_vouchers(period)
            QMessageBox.information(self, '成功', '从凭证同步完成')
            self._refresh_cash() if jtype == 'cash' else self._refresh_bank()
        except Exception as e:
            QMessageBox.information(self, '提示', f'同步完成（{e}）')
            self._refresh_cash() if jtype == 'cash' else self._refresh_bank()

    def on_activate(self, book_id):
        self.refresh()

    def refresh(self):
        self._refresh_cash()
        self._refresh_bank()
        self._refresh_rec()