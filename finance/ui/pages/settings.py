"""
==============================================
 ui/pages/settings.py - 系统设置页面
==============================================
包含：科目管理、辅助核算设置、用户管理、系统参数
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QHeaderView, QGroupBox, QTabWidget,
    QMessageBox, QAbstractItemView, QFormLayout,
    QTreeWidget, QTreeWidgetItem, QSplitter,
    QDialog, QDialogButtonBox, QCheckBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QColor, QFont


class AccountManagePage(QWidget):
    """科目管理页面"""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 工具栏
        tool_layout = QHBoxLayout()
        tool_layout.addWidget(QLabel('<h3>📋 会计科目管理</h3>'))
        tool_layout.addStretch()

        self._search = QLineEdit()
        self._search.setPlaceholderText('搜索科目...')
        self._search.setFixedWidth(200)
        self._search.textChanged.connect(self._filter)
        tool_layout.addWidget(self._search)

        btn_add = QPushButton('➕ 新增科目')
        btn_add.setStyleSheet("""
            QPushButton { background: #34A853; color: white; padding: 6px 16px;
                         border-radius: 4px; }
            QPushButton:hover { background: #2E7D32; }
        """)
        btn_add.clicked.connect(self._add_account)
        tool_layout.addWidget(btn_add)

        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 6px 16px;
                         border-radius: 4px; }
        """)
        btn_refresh.clicked.connect(self.refresh)
        tool_layout.addWidget(btn_refresh)

        layout.addLayout(tool_layout)

        # 科目树表格
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(['科目编码', '科目名称', '科目类型', '余额方向', '末级', '状态'])
        self._tree.setColumnWidth(0, 100)
        self._tree.setColumnWidth(1, 200)
        self._tree.setColumnWidth(2, 80)
        self._tree.setColumnWidth(3, 80)
        self._tree.setColumnWidth(4, 50)
        self._tree.setAlternatingRowColors(True)
        self._tree.setStyleSheet("""
            QTreeWidget { background: white; border: 1px solid #E0E0E0;
                         border-radius: 4px; }
            QTreeWidget::item { padding: 4px 0; }
            QHeaderView::section { background: #F8F9FA; border: none;
                                  border-bottom: 2px solid #E0E0E0; padding: 8px; font-weight: bold; }
        """)
        layout.addWidget(self._tree, 1)

    def refresh(self):
        self._tree.clear()
        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        cursor = conn.execute('''
            SELECT acct_code, acct_name, acct_type, balance_side,
                   is_detail, enabled, parent_code
            FROM accounts WHERE enabled = 1 ORDER BY acct_code
        ''')
        all_accts = cursor.fetchall()

        acct_map = {}
        for code, name, atype, side, detail, enabled, parent in all_accts:
            type_names = {'asset': '资产', 'liability': '负债', 'equity': '权益',
                          'cost': '成本', 'pl': '损益', 'income': '收入',
                          'expense': '费用', 'net_asset': '净资产',
                          'budget_income': '预算收入', 'budget_expense': '预算支出',
                          'budget_balance': '预算结余', 'fund': '基金',
                          'expenditure': '支出', 'common': '共同'}
            side_names = {'debit': '借方', 'credit': '贷方'}

            item = QTreeWidgetItem([
                code, name,
                type_names.get(atype, atype),
                side_names.get(side, side),
                '是' if detail else '否',
                '启用' if enabled else '停用'
            ])
            item.setData(0, Qt.ItemDataRole.UserRole, code)
            acct_map[code] = item

        for code, name, atype, side, detail, enabled, parent in all_accts:
            if parent and parent in acct_map:
                acct_map[parent].addChild(acct_map[code])
            else:
                self._tree.addTopLevelItem(acct_map[code])

        # 展开前两级
        for i in range(min(3, self._tree.topLevelItemCount())):
            item = self._tree.topLevelItem(i)
            item.setExpanded(True)

    def _filter(self, text):
        """搜索过滤"""
        if not text:
            self.refresh()
            return
        self._tree.clear()
        conn = self.db_manager.get_current_conn()
        if not conn:
            return
        cursor = conn.execute('''
            SELECT acct_code, acct_name, acct_type, balance_side,
                   is_detail, enabled
            FROM accounts WHERE enabled = 1
            AND (acct_code LIKE ? OR acct_name LIKE ?)
            ORDER BY acct_code
        ''', (f'%{text}%', f'%{text}%'))
        for code, name, atype, side, detail, enabled in cursor.fetchall():
            item = QTreeWidgetItem([code, name, atype, side, '是' if detail else '否', '启用'])
            self._tree.addTopLevelItem(item)

    def _add_account(self):
        """新增科目"""
        code, ok = QInputDialog.getText(self, '新增科目', '科目编码:')
        if not ok or not code:
            return
        name, ok = QInputDialog.getText(self, '新增科目', '科目名称:')
        if not ok or not name:
            return

        conn = self.db_manager.get_current_conn()
        if conn:
            from datetime import datetime
            now = datetime.now().isoformat()
            try:
                conn.execute('''
                    INSERT INTO accounts
                    (acct_code, acct_name, acct_level, is_detail,
                     acct_type, balance_side, enabled, created_at, modified_at)
                    VALUES (?, ?, 1, 1, 'asset', 'debit', 1, ?, ?)
                ''', (code, name, now, now))
                conn.commit()
                self.refresh()
            except Exception as e:
                QMessageBox.warning(self, '错误', str(e))


class SettingsPage(QWidget):
    """系统设置页面"""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
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

        # 科目管理
        self._acct_page = AccountManagePage(self.db_manager)
        self._tabs.addTab(self._acct_page, '📋 会计科目')

        # 辅助核算
        aux_label = QLabel('辅助核算设置（功能开发中）\n\n支持：客户/供应商/部门/职员/项目/存货等多维度核算')
        aux_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
        aux_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._tabs.addTab(aux_label, '#️⃣ 辅助核算')

        # 系统参数
        params_label = QLabel('系统参数（功能开发中）\n\n包括：会计期间、凭证设置、打印设置等')
        params_label.setStyleSheet("color: #999; font-size: 14px; padding: 40px;")
        params_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._tabs.addTab(params_label, '⚙️ 系统参数')

        layout.addWidget(self._tabs)

    def refresh(self):
        self._acct_page.refresh()

    def on_activate(self, book_id):
        self.refresh()