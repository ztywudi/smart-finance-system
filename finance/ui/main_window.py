"""
==========================================
 ui/main_window.py - 财务软件主窗口
==========================================
布局：
┌────────────────────────────────────────────────┐
│  菜单栏                                          │
├────────────────────────────────────────────────┤
│  工具栏 [账套选择 ▼] [新建凭证] [保存] [审核] ... │
├──────┬─────────────────────────────────────────┤
│      │  📊 工作台                                │
│  📝  │  📝 凭证管理     ← QStackedWidget         │
│  📒  │  📒 账簿查询     切换页面                  │
│  📑  │  📑 财务报表                              │
│  💰  │  💰 出纳管理                              │
│  🤝  │  🤝 应收应付      ...                     │
│  ...  │                                         │
│      │                                         │
├──────┴─────────────────────────────────────────┤
│  状态栏 | 当前账套: xxx | 会计期间: 2026-05      │
└────────────────────────────────────────────────┘
"""

import sys
import os
from datetime import datetime
from typing import Optional

# 确保项目根在路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTreeWidget, QTreeWidgetItem, QStackedWidget,
    QToolBar, QStatusBar, QComboBox, QPushButton,
    QMenuBar, QMenu, QMessageBox, QLabel, QSplitter,
    QApplication, QHeaderView, QInputDialog, QLineEdit,
    QScrollArea, QFrame
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QAction, QFont, QColor, QPalette

from core.database import DatabaseManager
from core.account_system import AccountingSystemManager
from ui.pages.dashboard import DashboardPage
from ui.pages.general_ledger import GeneralLedgerPage
from ui.pages.cashier import CashierPage
from ui.pages.ar_ap import ArapPage
from ui.pages.fixed_asset import FixedAssetPage
from ui.pages.reports import ReportsPage
from ui.pages.period_end import PeriodEndPage
from ui.pages.settings import SettingsPage
from ui.pages.payroll import PayrollPage
from ui.pages.sync import SyncPage
from ui.pages.opening import OpeningPage


class NavPanel(QTreeWidget):
    """左侧导航面板"""

    PAGE_DASHBOARD = 'dashboard'
    PAGE_VOUCHER = 'voucher'
    PAGE_LEDGER = 'ledger'
    PAGE_REPORT = 'report'
    PAGE_CASHIER = 'cashier'
    PAGE_ARAP = 'arap'
    PAGE_FIXED_ASSET = 'fixed_asset'
    PAGE_PERIOD_END = 'period_end'

    page_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setHeaderHidden(True)
        self.setRootIsDecorated(True)
        self.setIndentation(20)
        self.setMinimumWidth(180)
        self.setMaximumWidth(250)
        self.setAnimated(True)
        self.setStyleSheet("""
            QTreeWidget {
                background-color: #FFFFFF;
                border: none;
                border-right: 1px solid #E0E0E0;
                font-size: 13px;
                padding: 4px;
            }
            QTreeWidget::item {
                padding: 8px 12px;
                border-radius: 4px;
                margin: 1px 0px;
            }
            QTreeWidget::item:hover {
                background-color: #E8F0FE;
            }
            QTreeWidget::item:selected {
                background-color: #1A73E8;
                color: #FFFFFF;
            }
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings {
                border-image: none;
            }
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings {
                border-image: none;
            }
        """)
        self._build_nav()
        self.itemClicked.connect(self._on_item_clicked)

    def _build_nav(self):
        """构建导航树"""
        # 功能图标（使用Unicode字符模拟）
        items = [
            ('📊', '工作台', self.PAGE_DASHBOARD, []),
            ('📝', '凭证管理', self.PAGE_VOUCHER, []),
            ('📒', '账簿查询', self.PAGE_LEDGER, [
                ('总分类账', 'ledger_general'),
                ('明细账', 'ledger_detail'),
                ('科目余额表', 'ledger_balance'),
                ('试算平衡表', 'ledger_trial'),
            ]),
            ('💰', '出纳管理', self.PAGE_CASHIER, [
                ('现金日记账', 'cashier_cash'),
                ('银行日记账', 'cashier_bank'),
                ('银行对账', 'cashier_reconcile'),
            ]),
            ('🤝', '应收应付', self.PAGE_ARAP, [
                ('应收账款', 'arap_ar'),
                ('应付账款', 'arap_ap'),
                ('账龄分析', 'arap_aging'),
            ]),
            ('🏭', '固定资产', self.PAGE_FIXED_ASSET, [
                ('资产卡片', 'fa_card'),
                ('折旧管理', 'fa_depr'),
            ]),
            ('💼', '工资管理', 'payroll', [
                ('员工管理', 'payroll_emp'),
                ('工资计算', 'payroll_calc'),
                ('工资表', 'payroll_result'),
            ]),
            ('📑', '财务报表', self.PAGE_REPORT, [
                ('资产负债表', 'report_balance'),
                ('利润表', 'report_income'),
                ('现金流量表', 'report_cashflow'),
            ]),
            ('📥', '期初管理', 'opening', [
                ('科目期初', 'opening'),
                ('固定资产期初', 'opening'),
            ]),
            ('🔄', '期末处理', self.PAGE_PERIOD_END, [
                ('结转损益', 'period_transfer'),
                ('期末结账', 'period_close'),
            ]),
            ('⚙️', '系统设置', 'settings', [
                ('会计科目', 'settings_accounts'),
                ('辅助核算', 'settings_aux'),
            ]),
            ('💾', 'U盘同步', 'sync', None),
        ]

        for icon, name, page_id, children in items:
            item = QTreeWidgetItem([f'{icon}  {name}'])
            item.setData(0, Qt.ItemDataRole.UserRole, page_id)
            item.setSizeHint(0, QSize(0, 36))
            self.addTopLevelItem(item)

            if children:
                for child_name, child_id in children:
                    child = QTreeWidgetItem([f'    {child_name}'])
                child.setData(0, Qt.ItemDataRole.UserRole, child_id)
                child.setSizeHint(0, QSize(0, 30))
                item.addChild(child)

        # 默认选中第一个
        self.setCurrentItem(self.topLevelItem(0))

    def _on_item_clicked(self, item, column):
        page_id = item.data(0, Qt.ItemDataRole.UserRole)
        if page_id:
            self.page_changed.emit(page_id)


class MainWindow(QMainWindow):
    """财务软件主窗口"""

    def __init__(self, db_manager: DatabaseManager):
        super().__init__()
        self.db_manager = db_manager
        self._current_page = None
        self._current_book_id = None

        self.setWindowTitle('财务软件 - 支持多会计制度·多账套')
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)

        # 加载样式
        self._apply_style()

        # 搭建UI
        self._setup_menu_bar()
        self._setup_toolbar()
        self._setup_central()
        self._setup_status_bar()

        # 检查账套状态
        self._check_account_books()

    def _apply_style(self):
        """应用全局样式"""
        style_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'resources', 'styles', 'main.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())

    def _setup_menu_bar(self):
        """设置菜单栏"""
        menubar = self.menuBar()

        # 文件菜单
        file_menu = menubar.addMenu('文件(&F)')
        file_menu.addAction('新建账套...', self._on_new_book)
        file_menu.addAction('打开账套...', self._on_open_book)
        file_menu.addSeparator()
        file_menu.addAction('备份账套...', self._on_backup)
        file_menu.addAction('恢复账套...', self._on_restore)
        file_menu.addSeparator()
        file_menu.addAction('同步到U盘...', self._on_sync_to_usb)
        file_menu.addAction('从U盘合并...', self._on_sync_from_usb)
        file_menu.addSeparator()
        file_menu.addAction('退出(&X)', self.close)

        # 基础设置菜单
        settings_menu = menubar.addMenu('基础设置(&S)')
        settings_menu.addAction('会计科目', self._on_accounts_settings)
        settings_menu.addAction('辅助核算', self._on_aux_settings)
        settings_menu.addAction('期初余额', self._on_opening_balance)
        settings_menu.addAction('用户管理', self._on_user_management)

        # 凭证菜单
        voucher_menu = menubar.addMenu('凭证(&V)')
        voucher_menu.addAction('录入凭证', self._on_new_voucher)
        voucher_menu.addAction('查询凭证', self._on_query_voucher)
        voucher_menu.addSeparator()
        voucher_menu.addAction('审核凭证', self._on_approve_voucher)
        voucher_menu.addAction('过账', self._on_post_voucher)

        # 账簿菜单
        ledger_menu = menubar.addMenu('账簿(&L)')
        ledger_menu.addAction('总分类账', self._on_ledger_general)
        ledger_menu.addAction('明细账', self._on_ledger_detail)
        ledger_menu.addAction('科目余额表', lambda: self.navigate_to('ledger_balance'))
        ledger_menu.addAction('试算平衡表', lambda: self.navigate_to('ledger_trial'))

        # 报表菜单
        report_menu = menubar.addMenu('报表(&R)')
        report_menu.addAction('资产负债表', lambda: self.navigate_to('report_balance'))
        report_menu.addAction('利润表', lambda: self.navigate_to('report_income'))
        report_menu.addAction('现金流量表', lambda: self.navigate_to('report_cashflow'))

        # 期末菜单
        period_menu = menubar.addMenu('期末(&P)')
        period_menu.addAction('结转损益', lambda: self.navigate_to('period_transfer'))
        period_menu.addAction('期末结账', lambda: self.navigate_to('period_close'))
        period_menu.addAction('反结账', self._on_unclose)

        # 帮助菜单
        help_menu = menubar.addMenu('帮助(&H)')
        help_menu.addAction('关于', self._on_about)

    def _setup_toolbar(self):
        """设置工具栏"""
        toolbar = QToolBar('主工具栏')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(20, 20))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #F8F9FA;
                border-bottom: 1px solid #E0E0E0;
                padding: 4px 8px;
                spacing: 4px;
            }
            QToolButton {
                padding: 6px 12px;
                border-radius: 4px;
                font-size: 12px;
            }
            QToolButton:hover {
                background-color: #E8F0FE;
            }
        """)
        self.addToolBar(toolbar)

        # 账套选择器
        self._book_selector = QComboBox()
        self._book_selector.setMinimumWidth(200)
        self._book_selector.setStyleSheet("""
            QComboBox {
                padding: 4px 8px;
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                background: white;
                font-size: 13px;
            }
        """)
        self._book_selector.currentIndexChanged.connect(self._on_book_selected)
        toolbar.addWidget(QLabel('  账套: '))
        toolbar.addWidget(self._book_selector)

        # 会计期间
        self._period_label = QLabel('  会计期间: ')
        toolbar.addWidget(self._period_label)
        self._period_combo = QComboBox()
        self._period_combo.setStyleSheet("""
            QComboBox { padding: 4px 8px; border: 1px solid #D0D0D0;
                        border-radius: 4px; background: white; }
        """)
        toolbar.addWidget(self._period_combo)

        toolbar.addSeparator()

        # 快捷按钮
        btn_new_voucher = QPushButton('📝 新建凭证')
        btn_new_voucher.clicked.connect(self._on_new_voucher)
        toolbar.addWidget(btn_new_voucher)

        btn_approve = QPushButton('✅ 审核')
        btn_approve.clicked.connect(self._on_approve_voucher)
        toolbar.addWidget(btn_approve)

        btn_post = QPushButton('📌 过账')
        btn_post.clicked.connect(self._on_post_voucher)
        toolbar.addWidget(btn_post)

        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._refresh_current_page)
        toolbar.addWidget(btn_refresh)

    def _setup_central(self):
        """设置中央区域（导航+工作区）"""
        central = QWidget()
        self.setCentralWidget(central)
        layout = QHBoxLayout(central)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # 分割器
        splitter = QSplitter(Qt.Orientation.Horizontal)

        # 左侧导航
        self._nav_panel = NavPanel()
        self._nav_panel.page_changed.connect(self.navigate_to)
        splitter.addWidget(self._nav_panel)

        # 右侧工作区（页面容器）
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; background: #F5F6FA; }")

        self._page_container = QStackedWidget()
        self._pages = {}

        # 注册所有页面
        self._pages['dashboard'] = DashboardPage(self.db_manager)
        self._pages['voucher'] = GeneralLedgerPage(self.db_manager, tab='voucher')
        self._pages['ledger'] = GeneralLedgerPage(self.db_manager, tab='ledger')
        self._pages['ledger_general'] = GeneralLedgerPage(self.db_manager, tab='general')
        self._pages['ledger_detail'] = GeneralLedgerPage(self.db_manager, tab='detail')
        self._pages['ledger_balance'] = GeneralLedgerPage(self.db_manager, tab='balance')
        self._pages['ledger_trial'] = GeneralLedgerPage(self.db_manager, tab='trial')
        self._pages['report'] = ReportsPage(self.db_manager)
        self._pages['report_balance'] = ReportsPage(self.db_manager, report_type='balance')
        self._pages['report_income'] = ReportsPage(self.db_manager, report_type='income')
        self._pages['report_cashflow'] = ReportsPage(self.db_manager, report_type='cashflow')
        self._pages['cashier'] = CashierPage(self.db_manager)
        self._pages['cashier_cash'] = CashierPage(self.db_manager, tab='cash')
        self._pages['cashier_bank'] = CashierPage(self.db_manager, tab='bank')
        self._pages['cashier_reconcile'] = CashierPage(self.db_manager, tab='reconcile')
        self._pages['arap'] = ArapPage(self.db_manager)
        self._pages['arap_ar'] = ArapPage(self.db_manager, tab='ar')
        self._pages['arap_ap'] = ArapPage(self.db_manager, tab='ap')
        self._pages['fixed_asset'] = FixedAssetPage(self.db_manager)
        self._pages['fa_card'] = FixedAssetPage(self.db_manager, tab='card')
        self._pages['fa_depr'] = FixedAssetPage(self.db_manager, tab='depr')
        self._pages['period_end'] = PeriodEndPage(self.db_manager)
        self._pages['period_transfer'] = PeriodEndPage(self.db_manager, tab='transfer')
        self._pages['period_close'] = PeriodEndPage(self.db_manager, tab='close')
        self._pages['settings'] = SettingsPage(self.db_manager)
        self._pages['settings_accounts'] = SettingsPage(self.db_manager)
        self._pages['settings_aux'] = SettingsPage(self.db_manager)
        self._pages['payroll'] = PayrollPage(self.db_manager)
        self._pages['payroll_emp'] = PayrollPage(self.db_manager)
        self._pages['payroll_calc'] = PayrollPage(self.db_manager)
        self._pages['payroll_result'] = PayrollPage(self.db_manager)
        self._pages['sync'] = SyncPage(self.db_manager)
        self._pages['opening'] = OpeningPage(self.db_manager)

        for page in self._pages.values():
            self._page_container.addWidget(page)

        scroll.setWidget(self._page_container)
        splitter.addWidget(scroll)

        # 设置分割比例
        splitter.setSizes([200, 1000])
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        layout.addWidget(splitter)

    def _setup_status_bar(self):
        """设置状态栏"""
        status = QStatusBar()
        status.setStyleSheet("""
            QStatusBar {
                background-color: #FFFFFF;
                border-top: 1px solid #E0E0E0;
                color: #666666;
                font-size: 12px;
                padding: 2px 8px;
            }
            QStatusBar::item { border: none; }
        """)

        self._status_book = QLabel('账套: 未选择')
        self._status_period = QLabel('期间: --')
        self._status_system = QLabel('制度: --')
        self._status_user = QLabel('用户: admin')
        self._status_time = QLabel(datetime.now().strftime('%Y-%m-%d %H:%M'))

        status.addWidget(self._status_book, 1)
        status.addWidget(self._status_period, 1)
        status.addWidget(self._status_system, 1)
        status.addPermanentWidget(self._status_user)
        status.addPermanentWidget(self._status_time)
        self.setStatusBar(status)

    # ──────────────────────────────────────────
    #  账套管理
    # ──────────────────────────────────────────

    def refresh_book_list(self):
        """刷新账套下拉列表"""
        self._book_selector.clear()
        books = self.db_manager.list_account_books()
        if books:
            for b in books:
                sys_info = AccountingSystemManager.get_system(b['accounting_system'])
                sys_name = sys_info.name if sys_info else b['accounting_system']
                label = f"[{b['book_id']}] {b['book_name']} - {sys_name}"
                self._book_selector.addItem(label, b['book_id'])
        else:
            self._book_selector.addItem('-- 暂无账套，请先新建 --', None)

    def _on_book_selected(self, index):
        """选择账套"""
        book_id = self._book_selector.currentData()
        if not book_id:
            return

        try:
            self.db_manager.open_book(book_id)
            book_info = self.db_manager.get_account_book(book_id)
            if book_info:
                sys_info = AccountingSystemManager.get_system(book_info['accounting_system'])
                sys_name = sys_info.name if sys_info else book_info['accounting_system']

                self._status_book.setText(f'账套: {book_info["book_name"]}')
                self._status_system.setText(f'制度: {sys_name}')

                # 刷新会计期间下拉
                self._refresh_periods()

                # 刷新所有页面
                self._refresh_all_pages()
        except Exception as e:
            QMessageBox.warning(self, '错误', f'打开账套失败: {e}')

    def _refresh_periods(self):
        """刷新会计期间"""
        self._period_combo.clear()
        for y in range(2024, 2031):
            for m in range(1, 13):
                self._period_combo.addItem(f'{y}-{m:02d}')

        # 选当前期间
        now = datetime.now()
        idx = self._period_combo.findText(f'{now.year}-{now.month:02d}')
        if idx >= 0:
            self._period_combo.setCurrentIndex(idx)

    def _check_account_books(self):
        """检查账套状态并弹出选择"""
        self.refresh_book_list()
        books = self.db_manager.list_account_books()
        if not books:
            reply = QMessageBox.question(
                self, '欢迎使用',
                '暂未创建账套，是否立即新建一个？',
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if reply == QMessageBox.StandardButton.Yes:
                self._on_new_book()
        else:
            # 默认选择第一个
            self._book_selector.setCurrentIndex(0)

    # ──────────────────────────────────────────
    #  页面导航
    # ──────────────────────────────────────────

    def navigate_to(self, page_id: str):
        """导航到指定页面"""
        if page_id in self._pages:
            self._page_container.setCurrentWidget(self._pages[page_id])
            self._current_page = page_id
            page = self._pages[page_id]
            if hasattr(page, 'on_activate'):
                page.on_activate(self._current_book_id)

    def _refresh_current_page(self):
        """刷新当前页面"""
        if self._current_page and self._current_page in self._pages:
            page = self._pages[self._current_page]
            if hasattr(page, 'refresh'):
                page.refresh()

    def _refresh_all_pages(self):
        """刷新所有页面"""
        for page in self._pages.values():
            if hasattr(page, 'refresh'):
                page.refresh()

    # ──────────────────────────────────────────
    #  菜单/按钮事件
    # ──────────────────────────────────────────

    def _on_new_book(self):
        """新建账套"""
        from ui.dialogs.create_book_dialog import CreateBookDialog
        dlg = CreateBookDialog(self.db_manager, self)
        if dlg.exec():
            self.refresh_book_list()
            self._book_selector.setCurrentIndex(0)
            QMessageBox.information(self, '成功', f'账套 "{dlg.book_name}" 创建成功！')

    def _on_open_book(self):
        """打开账套（切换到选择）"""
        self._book_selector.showPopup()

    def _on_backup(self):
        """备份账套"""
        book_id = self._book_selector.currentData()
        if not book_id:
            QMessageBox.warning(self, '提示', '请先选择账套')
            return
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getSaveFileName(
            self, '备份账套', f'backup_{book_id}_{datetime.now().strftime("%Y%m%d")}.zip',
            'ZIP文件 (*.zip)')
        if path:
            from utils.backup import BackupManager
            bm = BackupManager(self.db_manager.data_dir)
            bm.create_full_backup(path)
            QMessageBox.information(self, '成功', f'备份完成: {path}')

    def _on_restore(self):
        """恢复备份"""
        from PyQt6.QtWidgets import QFileDialog
        path, _ = QFileDialog.getOpenFileName(self, '选择备份文件', '', 'ZIP文件 (*.zip)')
        if path:
            from utils.backup import BackupManager
            bm = BackupManager(self.db_manager.data_dir)
            bm.restore_from_backup(path)
            self.refresh_book_list()
            QMessageBox.information(self, '成功', '恢复完成！')

    def _on_sync_to_usb(self):
        """同步到U盘"""
        from ui.dialogs.sync_dialog import SyncDialog
        dlg = SyncDialog(self.db_manager, self, mode='export')
        dlg.exec()

    def _on_sync_from_usb(self):
        """从U盘合并"""
        from ui.dialogs.sync_dialog import SyncDialog
        dlg = SyncDialog(self.db_manager, self, mode='import')
        dlg.exec()

    def _on_new_voucher(self):
        """新建凭证"""
        self.navigate_to('voucher')
        page = self._pages['voucher']
        if hasattr(page, 'new_voucher'):
            page.new_voucher()

    def _on_approve_voucher(self):
        """审核凭证"""
        if self._current_page and self._current_page in self._pages:
            page = self._pages[self._current_page]
            if hasattr(page, 'approve_voucher'):
                page.approve_voucher()

    def _on_post_voucher(self):
        """过账"""
        if self._current_page and self._current_page in self._pages:
            page = self._pages[self._current_page]
            if hasattr(page, 'post_voucher'):
                page.post_voucher()

    def _on_query_voucher(self):
        """查询凭证"""
        self.navigate_to('voucher')

    def _on_accounts_settings(self):
        """科目设置"""
        self.navigate_to('ledger_balance')

    def _on_aux_settings(self):
        """辅助核算设置"""
        QMessageBox.information(self, '提示', '辅助核算设置功能开发中...')

    def _on_opening_balance(self):
        """期初余额"""
        QMessageBox.information(self, '提示', '期初余额录入功能开发中...')

    def _on_user_management(self):
        """用户管理"""
        QMessageBox.information(self, '提示', '用户管理功能开发中...')

    def _on_ledger_general(self):
        self.navigate_to('ledger_general')

    def _on_ledger_detail(self):
        self.navigate_to('ledger_detail')

    def _on_unclose(self):
        reply = QMessageBox.question(
            self, '确认', '确定要反结账吗？反结账将允许修改已结账期间的凭证。',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, '提示', '反结账功能开发中...')

    def _on_about(self):
        QMessageBox.about(self, '关于',
            '<h3>财务软件 v1.0</h3>'
            '<p>支持多会计制度 · 多账套 · U盘便携同步</p>'
            '<p>已内置11种会计制度：</p>'
            '<ul>'
            '<li>企业会计准则</li>'
            '<li>小企业会计准则</li>'
            '<li>企业会计制度（2001版）</li>'
            '<li>政府会计准则制度</li>'
            '<li>民间非营利组织会计制度</li>'
            '<li>工会会计制度</li>'
            '<li>社会保险基金会计制度</li>'
            '<li>证券投资基金会计核算业务指引</li>'
            '<li>住房公积金会计制度</li>'
            '<li>农村集体经济组织会计制度</li>'
            '<li>农民专业合作社财务会计制度</li>'
            '</ul>')
