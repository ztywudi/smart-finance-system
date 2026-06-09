"""
==============================================
 ui/pages/general_ledger.py - 总账/凭证管理页面
==============================================
功能凭证管理：列表加载、查询、审核、过账
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QHeaderView, QGroupBox, QDateEdit,
    QMessageBox, QAbstractItemView, QSplitter,
    QTabWidget, QCheckBox, QFrame, QFileDialog
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QColor, QFont


class GeneralLedgerPage(QWidget):
    """总账/凭证管理页面"""

    def __init__(self, db_manager, tab='voucher'):
        super().__init__()
        self.db_manager = db_manager
        self._tab = tab
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border: none; background: #F5F6FA; }
            QTabBar::tab { padding: 10px 20px; font-size: 13px;
                          border: none; border-bottom: 2px solid transparent; }
            QTabBar::tab:selected { color: #1A73E8; border-bottom: 2px solid #1A73E8;
                                   font-weight: bold; }
        """)

        self._tabs.addTab(self._build_voucher_tab(), '📝 凭证管理')
        self._tabs.addTab(self._build_ledger_tab(), '📒 总分类账')
        self._tabs.addTab(self._build_balance_tab(), '⚖️ 科目余额表')

        tab_map = {'voucher': 0, 'ledger': 1, 'balance': 2, 'general': 1, 'detail': 0, 'trial': 2}
        self._tabs.setCurrentIndex(tab_map.get(self._tab, 0))
        layout.addWidget(self._tabs)

    # ──────────────────────────────
    #  凭证管理标签
    # ──────────────────────────────
    def _build_voucher_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 查询条件行
        filter_layout = QHBoxLayout()
        filter_layout.setSpacing(8)

        filter_layout.addWidget(QLabel('期间:'))
        self._v_period = QComboBox()
        for y in range(2024, 2031):
            for m in range(1, 13):
                self._v_period.addItem(f'{y}-{m:02d}')
        now = datetime.now()
        idx = self._v_period.findText(f'{now.year}-{now.month:02d}')
        if idx >= 0: self._v_period.setCurrentIndex(idx)
        self._v_period.setFixedWidth(100)
        filter_layout.addWidget(self._v_period)

        filter_layout.addWidget(QLabel('状态:'))
        self._v_status = QComboBox()
        self._v_status.addItems(['全部', '草稿(draft)', '已审核(approved)', '已过账(posted)'])
        filter_layout.addWidget(self._v_status)

        btn_query = QPushButton('🔍 查询')
        btn_query.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 6px 18px;
                         border-radius: 4px; }
            QPushButton:hover { background: #1557B0; }
        """)
        btn_query.clicked.connect(self._query_vouchers)
        filter_layout.addWidget(btn_query)

        filter_layout.addStretch()

        # 操作按钮
        btn_new = QPushButton('➕ 新增凭证')
        btn_new.setStyleSheet("""
            QPushButton { background: #34A853; color: white; padding: 6px 16px;
                         border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #2E7D32; }
        """)
        btn_new.clicked.connect(self.new_voucher)
        filter_layout.addWidget(btn_new)

        btn_approve = QPushButton('✅ 审核')
        btn_approve.setStyleSheet("""
            QPushButton { background: #FBBC04; color: white; padding: 6px 16px;
                         border-radius: 4px; }
            QPushButton:hover { background: #F9A825; }
        """)
        btn_approve.clicked.connect(self.approve_voucher)
        filter_layout.addWidget(btn_approve)

        btn_post = QPushButton('📌 过账')
        btn_post.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 6px 16px;
                         border-radius: 4px; }
            QPushButton:hover { background: #1557B0; }
        """)
        btn_post.clicked.connect(self.post_voucher)
        filter_layout.addWidget(btn_post)

        btn_export = QPushButton('📤 导出序时账')
        btn_export.setStyleSheet("padding:6px 12px; border-radius:4px;")
        btn_export.clicked.connect(self._export_journal)
        filter_layout.addWidget(btn_export)

        btn_import = QPushButton('📥 导入序时账')
        btn_import.setStyleSheet("background:#9C27B0; color:white; padding:6px 16px; border-radius:4px;")
        btn_import.clicked.connect(self._import_journal)
        filter_layout.addWidget(btn_import)

        layout.addLayout(filter_layout)

        # 凭证列表
        self._v_table = QTableWidget(0, 7)
        self._v_table.setHorizontalHeaderLabels([
            '凭证号', '日期', '凭证字', '摘要', '借方金额', '贷方金额', '状态'
        ])
        self._v_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self._v_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._v_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self._v_table.setAlternatingRowColors(True)
        self._v_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._v_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0;
                          border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none;
                                  border-bottom: 2px solid #E0E0E0; padding: 8px; font-weight: bold; }
        """)
        self._v_table.doubleClicked.connect(self._on_voucher_double_click)
        layout.addWidget(self._v_table, 1)

        # 分页信息
        page_layout = QHBoxLayout()
        self._v_info = QLabel('共 0 条记录')
        self._v_info.setStyleSheet("color: #666;")
        page_layout.addWidget(self._v_info)
        page_layout.addStretch()

        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._query_vouchers)
        page_layout.addWidget(btn_refresh)
        layout.addLayout(page_layout)

        return tab

    def _query_vouchers(self):
        """查询凭证"""
        from core.voucher_service import VoucherService
        vs = VoucherService(self.db_manager)

        period = self._v_period.currentText()
        status_text = self._v_status.currentText()
        status = None
        if 'draft' in status_text: status = 'draft'
        elif 'approved' in status_text: status = 'approved'
        elif 'posted' in status_text: status = 'posted'

        try:
            vouchers, total = vs.query_vouchers(
                period=period if period != '全部' else None,
                status=status)
        except Exception:
            self._v_table.setRowCount(0)
            self._v_info.setText('共 0 条记录（请先选择账套）')
            return

        self._v_table.setRowCount(len(vouchers))
        for i, v in enumerate(vouchers):
            self._v_table.setItem(i, 0, QTableWidgetItem(str(v.get('voucher_no', ''))))
            self._v_table.setItem(i, 1, QTableWidgetItem(v.get('voucher_date', '')))
            self._v_table.setItem(i, 2, QTableWidgetItem(v.get('voucher_type', '记')))
            self._v_table.setItem(i, 3, QTableWidgetItem(v.get('remark', '')))
            self._v_table.setItem(i, 4, QTableWidgetItem(''))
            self._v_table.setItem(i, 5, QTableWidgetItem(''))

            s = v.get('status', '')
            status_map = {'draft': '草稿', 'approved': '已审核', 'posted': '已过账', 'voided': '已作废'}
            item = QTableWidgetItem(status_map.get(s, s))
            if s == 'draft':
                item.setForeground(QColor('#999'))
            elif s == 'approved':
                item.setForeground(QColor('#FBBC04'))
            elif s == 'posted':
                item.setForeground(QColor('#34A853'))
            self._v_table.setItem(i, 6, item)

            # 存voucher_id到第一列
            self._v_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, v.get('voucher_id'))

        self._v_info.setText(f'共 {total} 条记录')

    def _on_voucher_double_click(self, index):
        """双击打开凭证查看"""
        row = index.row()
        item = self._v_table.item(row, 0)
        if item and item.data(Qt.ItemDataRole.UserRole):
            voucher_id = item.data(Qt.ItemDataRole.UserRole)
            from ui.dialogs.voucher_dialog import VoucherDialog
            dlg = VoucherDialog(self.db_manager, self, voucher_id=voucher_id)
            dlg.exec()

    # ──────────────────────────────
    #  总分类账标签
    # ──────────────────────────────
    def _build_ledger_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('科目:'))
        self._l_acct = QLineEdit()
        self._l_acct.setPlaceholderText('输入科目编码或名称')
        self._l_acct.setMinimumWidth(200)
        filter_layout.addWidget(self._l_acct)

        filter_layout.addWidget(QLabel('期间:'))
        self._l_period = QComboBox()
        filter_layout.addWidget(self._l_period)

        btn = QPushButton('🔍 查询')
        btn.clicked.connect(self._query_ledger)
        filter_layout.addWidget(btn)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self._l_table = QTableWidget(0, 6)
        self._l_table.setHorizontalHeaderLabels([
            '科目编码', '科目名称', '期初余额', '本期借方', '本期贷方', '期末余额'
        ])
        self._l_table.horizontalHeader().setStretchLastSection(True)
        self._l_table.setAlternatingRowColors(True)
        layout.addWidget(self._l_table, 1)

        return tab

    def _query_ledger(self):
        """查询总账（从数据库加载科目余额）"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            QMessageBox.warning(self, '提示', '请先选择账套')
            return

        cursor = conn.execute('''
            SELECT acct_code, acct_name FROM accounts
            WHERE enabled = 1 AND is_detail = 1
            ORDER BY acct_code
        ''')
        accounts = cursor.fetchall()
        self._l_table.setRowCount(len(accounts))
        for i, (code, name) in enumerate(accounts):
            self._l_table.setItem(i, 0, QTableWidgetItem(code))
            self._l_table.setItem(i, 1, QTableWidgetItem(name))
            self._l_table.setItem(i, 2, QTableWidgetItem('0.00'))
            self._l_table.setItem(i, 3, QTableWidgetItem('0.00'))
            self._l_table.setItem(i, 4, QTableWidgetItem('0.00'))
            self._l_table.setItem(i, 5, QTableWidgetItem('0.00'))

    # ──────────────────────────────
    #  科目余额表标签
    # ──────────────────────────────
    def _build_balance_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel('期间:'))
        self._b_period = QComboBox()
        filter_layout.addWidget(self._b_period)

        btn = QPushButton('🔍 查询')
        btn.clicked.connect(self._query_balance)
        filter_layout.addWidget(btn)

        btn_trial = QPushButton('🧮 试算平衡')
        btn_trial.clicked.connect(self._calc_trial)
        filter_layout.addWidget(btn_trial)

        self._b_result = QLabel('')
        self._b_result.setStyleSheet("padding: 6px 12px; border-radius: 4px;")
        filter_layout.addWidget(self._b_result)

        filter_layout.addStretch()
        layout.addLayout(filter_layout)

        self._b_table = QTableWidget(0, 6)
        self._b_table.setHorizontalHeaderLabels([
            '科目编码', '科目名称', '期初余额(借)', '期初余额(贷)',
            '期末余额(借)', '期末余额(贷)'
        ])
        self._b_table.horizontalHeader().setStretchLastSection(True)
        self._b_table.setAlternatingRowColors(True)
        layout.addWidget(self._b_table, 1)

        return tab

    def _query_balance(self):
        """查询科目余额表"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        cursor = conn.execute('''
            SELECT a.acct_code, a.acct_name, a.balance_side, a.acct_level,
                   COALESCE(b.begin_debit, 0), COALESCE(b.begin_credit, 0),
                   COALESCE(b.end_debit, 0), COALESCE(b.end_credit, 0)
            FROM accounts a
            LEFT JOIN account_balances b ON a.acct_code = b.acct_code
            WHERE a.enabled = 1
            ORDER BY a.acct_code
        ''')
        rows = cursor.fetchall()
        self._b_table.setRowCount(len(rows))
        for i, (code, name, side, level, bd, bc, ed, ec) in enumerate(rows):
            self._b_table.setItem(i, 0, QTableWidgetItem(code))
            self._b_table.setItem(i, 1, QTableWidgetItem(name))
            self._b_table.setItem(i, 2, QTableWidgetItem(f'{bd:,.2f}' if bd else ''))
            self._b_table.setItem(i, 3, QTableWidgetItem(f'{bc:,.2f}' if bc else ''))
            self._b_table.setItem(i, 4, QTableWidgetItem(f'{ed:,.2f}' if ed else ''))
            self._b_table.setItem(i, 5, QTableWidgetItem(f'{ec:,.2f}' if ec else ''))

    def _calc_trial(self):
        """试算平衡"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        cursor = conn.execute('''
            SELECT SUM(end_debit), SUM(end_credit)
            FROM account_balances
        ''')
        row = cursor.fetchone()
        if row and row[0] == row[1]:
            self._b_result.setText(f'✅ 试算平衡！借方={row[0]:,.2f}  贷方={row[1]:,.2f}')
            self._b_result.setStyleSheet(
                "padding: 6px 12px; background: #E8F5E9; color: #2E7D32; border-radius: 4px;")
        else:
            d = row[0] or 0
            c = row[1] or 0
            self._b_result.setText(f'❌ 不平衡！借方={d:,.2f}  贷方={c:,.2f}  差额={d-c:,.2f}')
            self._b_result.setStyleSheet(
                "padding: 6px 12px; background: #FCE8E6; color: #C62828; border-radius: 4px;")

    # ──────────────────────────────
    #  公共操作
    # ──────────────────────────────
    def new_voucher(self):
        from ui.dialogs.voucher_dialog import VoucherDialog
        dlg = VoucherDialog(self.db_manager, self)
        if dlg.exec():
            self._query_vouchers()

    def approve_voucher(self):
        from core.voucher_service import VoucherService
        vs = VoucherService(self.db_manager)
        selected_rows = set()
        for idx in self._v_table.selectedIndexes():
            selected_rows.add(idx.row())

        if not selected_rows:
            QMessageBox.warning(self, '提示', '请先选择要审核的凭证')
            return

        count = 0
        for row in selected_rows:
            item = self._v_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole):
                try:
                    vs.approve_voucher(item.data(Qt.ItemDataRole.UserRole))
                    count += 1
                except Exception as e:
                    QMessageBox.warning(self, '审核失败', str(e))

        QMessageBox.information(self, '完成', f'已审核 {count} 张凭证')
        self._query_vouchers()

    def post_voucher(self):
        from core.voucher_service import VoucherService
        vs = VoucherService(self.db_manager)
        selected_rows = set()
        for idx in self._v_table.selectedIndexes():
            selected_rows.add(idx.row())

        if not selected_rows:
            QMessageBox.warning(self, '提示', '请先选择要过账的凭证')
            return

        count = 0
        for row in selected_rows:
            item = self._v_table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole):
                try:
                    vs.post_voucher(item.data(Qt.ItemDataRole.UserRole))
                    count += 1
                except Exception as e:
                    QMessageBox.warning(self, '过账失败', str(e))

        QMessageBox.information(self, '完成', f'已过账 {count} 张凭证')
        self._query_vouchers()

    def _export_journal(self):
        """导出序时账（全部凭证按时间排序）"""
        import csv
        path, _ = QFileDialog.getSaveFileName(self, '导出序时账', '序时账.csv', 'CSV(*.csv)')
        if not path: return
        try:
            from core.voucher_service import VoucherService
            vs = VoucherService(self.db_manager)
            period = self._v_period.currentText()
            vouchers, total = vs.query_vouchers(period=period, status='posted')
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['凭证号', '日期', '摘要', '科目编码', '科目名称', '借方金额', '贷方金额', '现金流量项目'])
                for v in vouchers:
                    entries = vs.get_voucher_entries(v['voucher_id'])
                    for e in entries:
                        w.writerow([
                            v.get('voucher_no', ''),
                            v.get('voucher_date', ''),
                            e.get('summary', ''),
                            e.get('acct_code', ''),
                            e.get('acct_name', ''),
                            e.get('debit_amount', 0),
                            e.get('credit_amount', 0),
                            e.get('cf_item_id', 0),
                        ])
            QMessageBox.information(self, '成功', f'已导出 {total} 张凭证到 {path}')
        except Exception as e:
            QMessageBox.critical(self, '导出失败', str(e))

    def _import_journal(self):
        """导入序时账CSV"""
        path, _ = QFileDialog.getOpenFileName(self, '导入序时账', '', 'CSV(*.csv)')
        if not path: return
        try:
            from core.voucher_service import VoucherService
            vs = VoucherService(self.db_manager)
            import csv
            count = 0
            with open(path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                entries = []
                last_no = None
                for row in reader:
                    no = row.get('凭证号', '')
                    if no and no != last_no and entries:
                        # 保存上一张凭证
                        vs.create_voucher(self._v_period.currentText(),
                            row.get('日期', ''), '记', entries, remark='导入凭证')
                        entries = []
                        count += 1
                    entries.append({
                        'summary': row.get('摘要', ''),
                        'acct_code': row.get('科目编码', ''),
                        'debit_amount': float(row.get('借方金额', 0) or 0),
                        'credit_amount': float(row.get('贷方金额', 0) or 0),
                    })
                    last_no = no
                if entries:
                    vs.create_voucher(self._v_period.currentText(),
                        '', '记', entries, remark='导入凭证')
                    count += 1
            QMessageBox.information(self, '成功', f'已导入 {count} 张凭证')
            self._query_vouchers()
        except Exception as e:
            QMessageBox.critical(self, '导入失败', str(e))

    def on_activate(self, book_id):
        self.refresh()

    def refresh(self):
        self._query_vouchers()