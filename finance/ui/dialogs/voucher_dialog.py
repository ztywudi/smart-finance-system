"""
==================================================
 ui/dialogs/voucher_dialog.py - 凭证录入对话框
==================================================
功能完整的凭证录入界面，支持：
  - 科目模糊搜索 + 科目树选择
  - 借贷金额实时平衡校验
  - 辅助核算选择
  - F6保存 / F7保存并新增
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QFormLayout,
    QLineEdit, QComboBox, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit,
    QSpinBox, QWidget, QFrame, QAbstractItemView,
    QTreeWidget, QTreeWidgetItem, QDialogButtonBox,
    QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QSize
from PyQt6.QtGui import QColor, QFont, QKeySequence, QShortcut, QDoubleValidator

from core.voucher_service import VoucherService
from core.database import DatabaseManager
from core.cashflow_service import CashFlowService


class AccountSelector(QWidget):
    """科目选择器（搜索框+科目树弹窗）"""
    account_selected = pyqtSignal(str, str)  # code, name

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._setup()

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self._search = QLineEdit()
        self._search.setPlaceholderText('输入科目编码或名称搜索...')
        self._search.textChanged.connect(self._on_search)
        layout.addWidget(self._search)

        self._btn_tree = QPushButton('📂')
        self._btn_tree.setFixedWidth(32)
        self._btn_tree.setToolTip('选择科目')
        self._btn_tree.clicked.connect(self._show_tree)
        layout.addWidget(self._btn_tree)

        # 匹配结果下拉
        self._result_list = QTreeWidget()
        self._result_list.setHeaderHidden(True)
        self._result_list.setWindowFlags(Qt.WindowType.Popup)
        self._result_list.setMinimumWidth(300)
        self._result_list.setMaximumHeight(300)
        self._result_list.itemClicked.connect(self._on_select)
        self._result_list.setStyleSheet("""
            QTreeWidget { background: white; border: 1px solid #CCC; }
            QTreeWidget::item { padding: 4px 8px; }
            QTreeWidget::item:hover { background: #E8F0FE; }
            QTreeWidget::item:selected { background: #1A73E8; color: white; }
        """)

        self._selected_code = ''
        self._selected_name = ''

    def _on_search(self, text):
        """搜索科目"""
        if not text:
            self._result_list.hide()
            return

        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        cursor = conn.execute('''
            SELECT acct_code, acct_name FROM accounts
            WHERE (acct_code LIKE ? OR acct_name LIKE ?)
            AND enabled = 1
            LIMIT 20
        ''', (f'%{text}%', f'%{text}%'))

        results = cursor.fetchall()
        if not results:
            self._result_list.hide()
            return

        self._result_list.clear()
        for code, name in results:
            item = QTreeWidgetItem([f'{code}  {name}'])
            item.setData(0, Qt.ItemDataRole.UserRole, {'code': code, 'name': name})
            self._result_list.addTopLevelItem(item)

        # 显示在搜索框下方
        pos = self._search.mapToGlobal(self._search.rect().bottomLeft())
        self._result_list.setGeometry(pos.x(), pos.y(), 350, min(250, len(results) * 28))
        self._result_list.show()

    def _show_tree(self):
        """展开科目树"""
        self._result_list.clear()
        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        cursor = conn.execute('''
            SELECT acct_code, acct_name, parent_code, acct_level
            FROM accounts WHERE enabled = 1 ORDER BY acct_code
        ''')
        all_accounts = cursor.fetchall()

        # 构建树
        acct_map = {}
        for code, name, parent, level in all_accounts:
            item = QTreeWidgetItem([f'{code}  {name}'])
            item.setData(0, Qt.ItemDataRole.UserRole, {'code': code, 'name': name})
            acct_map[code] = item

        for code, name, parent, level in all_accounts:
            if parent and parent in acct_map:
                acct_map[parent].addChild(acct_map[code])
            else:
                self._result_list.addTopLevelItem(acct_map[code])

        # 展开前两级
        for i in range(self._result_list.topLevelItemCount()):
            item = self._result_list.topLevelItem(i)
            item.setExpanded(True)
            for j in range(item.childCount()):
                item.child(j).setExpanded(True)

        pos = self._search.mapToGlobal(self._search.rect().bottomLeft())
        self._result_list.setGeometry(pos.x(), pos.y(), 400, 400)
        self._result_list.show()

    def _on_select(self, item):
        data = item.data(0, Qt.ItemDataRole.UserRole)
        if data:
            self._selected_code = data['code']
            self._selected_name = data['name']
            self._search.setText(f'{data["code"]}  {data["name"]}')
            self.account_selected.emit(data['code'], data['name'])
        self._result_list.hide()

    def get_code(self):
        return self._selected_code

    def set_code(self, code, name=''):
        self._selected_code = code
        self._selected_name = name
        self._search.setText(f'{code}  {name}' if name else code)

    def clear(self):
        self._selected_code = ''
        self._selected_name = ''
        self._search.clear()


class VoucherEntryRow(QWidget):
    """单行凭证分录"""
    remove_requested = pyqtSignal(object)

    def __init__(self, db_manager, row_num=1):
        super().__init__()
        self.db_manager = db_manager
        self.row_num = row_num
        self._setup()

    def _setup(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(2, 2, 2, 2)
        layout.setSpacing(6)

        # 行号
        self._lbl_num = QLabel(str(self.row_num))
        self._lbl_num.setFixedWidth(30)
        self._lbl_num.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self._lbl_num)

        # 摘要
        self._summary = QLineEdit()
        self._summary.setPlaceholderText('输入摘要...')
        self._summary.setMinimumWidth(150)
        layout.addWidget(self._summary)

        # 科目选择器
        self._account = AccountSelector(self.db_manager)
        self._account.setMinimumWidth(200)
        layout.addWidget(self._account)

        # 借方金额
        self._debit = QLineEdit()
        self._debit.setPlaceholderText('0.00')
        self._debit.setFixedWidth(120)
        self._debit.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self._debit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._debit.textChanged.connect(self._on_amount_changed)
        layout.addWidget(self._debit)

        # 贷方金额
        self._credit = QLineEdit()
        self._credit.setPlaceholderText('0.00')
        self._credit.setFixedWidth(120)
        self._credit.setValidator(QDoubleValidator(0.0, 999999999.99, 2))
        self._credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        self._credit.textChanged.connect(self._on_amount_changed)
        layout.addWidget(self._credit)

        # 现金流量项目（仅现金/银行科目时显示）
        self._cf_combo = QComboBox()
        self._cf_combo.setMinimumWidth(160)
        self._cf_combo.setPlaceholderText('现金流量')
        self._cf_combo.addItem('(选择现金流量项目)', 0)
        self._cf_combo.setVisible(False)
        layout.addWidget(self._cf_combo)

        self._cf_service = CashFlowService(db_manager)
        self._load_cf_items()

        # 科目变化时切换现金流量显示
        self._account.account_selected.connect(self._on_account_changed)

        # 辅助核算
        self._btn_aux = QPushButton('#')
        self._btn_aux.setFixedWidth(32)
        self._btn_aux.setToolTip('辅助核算')
        layout.addWidget(self._btn_aux)

        # 删除按钮
        self._btn_remove = QPushButton('✕')
        self._btn_remove.setFixedWidth(32)
        self._btn_remove.setStyleSheet("""
            QPushButton { color: #EA4335; font-weight: bold; border: none; }
            QPushButton:hover { background: #FCE8E6; border-radius: 4px; }
        """)
        self._btn_remove.clicked.connect(lambda: self.remove_requested.emit(self))
        layout.addWidget(self._btn_remove)

    def _on_amount_changed(self, text):
        """借贷金额互相清零"""
        sender = self.sender()
        if sender == self._debit and text:
            self._credit.clear()
        elif sender == self._credit and text:
            self._debit.clear()

    def _load_cf_items(self):
        """加载现金流量项目"""
        items = self._cf_service.get_items()
        for it in items:
            self._cf_combo.addItem(f'[{it["cf_code"]}] {it["cf_name"]}', it['cf_id'])

    def _on_account_changed(self, code, name):
        """科目变化时切换现金流量项目"""
        is_cash = self._cf_service.is_cash_acct(code)
        self._cf_combo.setVisible(is_cash)
        if is_cash:
            cf_id = self._cf_service.auto_assign_cf_item(code)
            idx = self._cf_combo.findData(cf_id)
            if idx >= 0:
                self._cf_combo.setCurrentIndex(idx)

    def get_data(self) -> dict:
        return {
            'summary': self._summary.text(),
            'acct_code': self._account.get_code(),
            'debit_amount': float(self._debit.text() or '0'),
            'credit_amount': float(self._credit.text() or '0'),
            'cf_item_id': self._cf_combo.currentData() or 0,
        }

    def is_valid(self) -> bool:
        if not self._account.get_code():
            return False
        debit = float(self._debit.text() or '0')
        credit = float(self._credit.text() or '0')
        return debit > 0 or credit > 0


class VoucherDialog(QDialog):
    """凭证录入对话框"""

    def __init__(self, db_manager: DatabaseManager, parent=None, voucher_id=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.voucher_service = VoucherService(db_manager)
        self._voucher_id = voucher_id  # None=新增, int=编辑
        self._entry_rows = []
        self.setWindowTitle('录入凭证' if not voucher_id else '编辑凭证')
        self.setMinimumSize(850, 500)
        self.resize(950, 600)
        self._setup()
        self._setup_shortcuts()

        if voucher_id:
            self._load_voucher(voucher_id)

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        # ── 凭证头 ──
        header = QGroupBox()
        header.setStyleSheet("QGroupBox { border: none; }")
        header_layout = QHBoxLayout(header)

        header_layout.addWidget(QLabel('凭证字:'))
        self._type_combo = QComboBox()
        self._type_combo.addItems(['记', '收', '付', '转'])
        self._type_combo.setFixedWidth(60)
        header_layout.addWidget(self._type_combo)

        header_layout.addWidget(QLabel('  凭证号:'))
        self._lbl_voucher_no = QLabel('自动')
        self._lbl_voucher_no.setStyleSheet("font-weight: bold; color: #1A73E8;")
        header_layout.addWidget(self._lbl_voucher_no)

        header_layout.addWidget(QLabel('  日期:'))
        self._date_edit = QDateEdit()
        self._date_edit.setCalendarPopup(True)
        self._date_edit.setDate(QDate.currentDate())
        self._date_edit.setFixedWidth(120)
        header_layout.addWidget(self._date_edit)

        header_layout.addWidget(QLabel('  附件:'))
        self._attach_spin = QSpinBox()
        self._attach_spin.setRange(0, 999)
        self._attach_spin.setFixedWidth(60)
        header_layout.addWidget(self._attach_spin)
        header_layout.addWidget(QLabel('张'))

        header_layout.addStretch()

        layout.addWidget(header)

        # ── 分录表格 ──
        entries_label = QLabel('<b>凭证分录</b>')
        layout.addWidget(entries_label)

        self._entries_container = QVBoxLayout()
        self._entries_container.setSpacing(4)
        layout.addLayout(self._entries_container)

        # 添加第一行
        self._add_entry_row()

        # 添加行按钮
        btn_add = QPushButton('➕ 添加分录行')
        btn_add.setStyleSheet("""
            QPushButton { background: #F5F6FA; border: 1px dashed #D0D0D0;
                         border-radius: 4px; padding: 8px; color: #666; }
            QPushButton:hover { background: #E8F0FE; border-color: #1A73E8; color: #1A73E8; }
        """)
        btn_add.clicked.connect(lambda: self._add_entry_row())
        layout.addWidget(btn_add)

        # ── 合计行 ──
        total_layout = QHBoxLayout()
        total_layout.addStretch()
        total_layout.addWidget(QLabel('<b>借方合计:</b>'))
        self._total_debit = QLabel('0.00')
        self._total_debit.setStyleSheet("font-weight: bold; font-size: 14px; color: #1A73E8;")
        self._total_debit.setFixedWidth(120)
        self._total_debit.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self._total_debit)

        total_layout.addWidget(QLabel('  <b>贷方合计:</b>'))
        self._total_credit = QLabel('0.00')
        self._total_credit.setStyleSheet("font-weight: bold; font-size: 14px; color: #EA4335;")
        self._total_credit.setFixedWidth(120)
        self._total_credit.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self._total_credit)

        # 差额
        total_layout.addWidget(QLabel('  <b>差额:</b>'))
        self._diff = QLabel('0.00')
        self._diff.setStyleSheet("font-weight: bold; font-size: 14px;")
        self._diff.setFixedWidth(100)
        self._diff.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_layout.addWidget(self._diff)

        total_layout.addStretch()
        layout.addLayout(total_layout)

        # ── 备注 ──
        remark_layout = QHBoxLayout()
        remark_layout.addWidget(QLabel('备注:'))
        self._remark = QLineEdit()
        self._remark.setPlaceholderText('备注信息（可选）')
        remark_layout.addWidget(self._remark)
        layout.addLayout(remark_layout)

        # ── 按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._btn_save = QPushButton('💾 保存 (F6)')
        self._btn_save.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 10px 28px;
                         border-radius: 4px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background: #1557B0; }
        """)
        self._btn_save.clicked.connect(self._save)
        btn_layout.addWidget(self._btn_save)

        self._btn_save_new = QPushButton('💾 保存并新增 (F7)')
        self._btn_save_new.setStyleSheet("""
            QPushButton { background: #34A853; color: white; padding: 10px 28px;
                         border-radius: 4px; font-size: 14px; }
            QPushButton:hover { background: #2E7D32; }
        """)
        self._btn_save_new.clicked.connect(lambda: self._save(and_new=True))
        btn_layout.addWidget(self._btn_save_new)

        btn_cancel = QPushButton('取消 (Esc)')
        btn_cancel.setStyleSheet("""
            QPushButton { padding: 10px 20px; border: 1px solid #D0D0D0;
                         border-radius: 4px; background: white; }
            QPushButton:hover { background: #F5F5F5; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

    def _setup_shortcuts(self):
        """设置快捷键"""
        QShortcut(QKeySequence('F6'), self).activated.connect(self._save)
        QShortcut(QKeySequence('F7'), self).activated.connect(
            lambda: self._save(and_new=True))
        QShortcut(QKeySequence('Escape'), self).activated.connect(self.reject)

    def _add_entry_row(self, row_data: dict = None):
        """添加一行分录"""
        row = VoucherEntryRow(self.db_manager, len(self._entry_rows) + 1)
        row.remove_requested.connect(self._remove_entry_row)

        if row_data:
            row._summary.setText(row_data.get('summary', ''))
            row._account.set_code(
                row_data.get('acct_code', ''),
                row_data.get('acct_name', ''))
            if row_data.get('debit_amount', 0) > 0:
                row._debit.setText(str(row_data['debit_amount']))
            if row_data.get('credit_amount', 0) > 0:
                row._credit.setText(str(row_data['credit_amount']))

        self._entry_rows.append(row)
        self._entries_container.addWidget(row)
        self._update_total()

    def _remove_entry_row(self, row):
        """删除一行分录"""
        if len(self._entry_rows) <= 1:
            QMessageBox.warning(self, '提示', '至少保留一条分录')
            return
        self._entry_rows.remove(row)
        self._entries_container.removeWidget(row)
        row.deleteLater()
        # 重新编号
        for i, r in enumerate(self._entry_rows, 1):
            r._lbl_num.setText(str(i))
            r.row_num = i
        self._update_total()

    def _update_total(self):
        """更新合计行"""
        total_debit = sum(float(r._debit.text() or '0') for r in self._entry_rows)
        total_credit = sum(float(r._credit.text() or '0') for r in self._entry_rows)
        diff = total_debit - total_credit

        self._total_debit.setText(f'{total_debit:,.2f}')
        self._total_credit.setText(f'{total_credit:,.2f}')
        self._diff.setText(f'{diff:,.2f}')

        if abs(diff) < 0.01:
            self._diff.setStyleSheet("font-weight: bold; font-size: 14px; color: #34A853;")
        else:
            self._diff.setStyleSheet("font-weight: bold; font-size: 14px; color: #EA4335;")

    def _validate(self) -> list:
        """校验凭证数据，返回错误列表"""
        errors = []

        # 至少两行分录
        if len(self._entry_rows) < 2:
            errors.append('凭证至少需要两行分录（一借一贷）')

        # 每行数据有效性
        valid_rows = [r for r in self._entry_rows if r.is_valid()]
        if len(valid_rows) < 2:
            errors.append('至少需要两行有效的分录')

        # 借贷平衡
        total_debit = sum(float(r._debit.text() or '0') for r in self._entry_rows)
        total_credit = sum(float(r._credit.text() or '0') for r in self._entry_rows)
        if abs(total_debit - total_credit) >= 0.01:
            errors.append(f'借贷不平衡：借方 {total_debit:.2f} ≠ 贷方 {total_credit:.2f}')

        # 科目是否都选
        for r in self._entry_rows:
            if r.is_valid() and not r._account.get_code():
                errors.append(f'第{r.row_num}行未选择会计科目')

        return errors

    def _save(self, and_new=False):
        """保存凭证"""
        # 校验
        errors = self._validate()
        if errors:
            QMessageBox.warning(self, '数据校验未通过', '\n'.join(f'• {e}' for e in errors))
            return

        # 收集数据
        period = f"{self._date_edit.date().year():04d}-{self._date_edit.date().month():02d}"
        entries = [r.get_data() for r in self._entry_rows if r.is_valid()]

        try:
            if self._voucher_id:
                self.voucher_service.update_voucher(
                    self._voucher_id, entries,
                    attachment_count=self._attach_spin.value(),
                    remark=self._remark.text())
                QMessageBox.information(self, '成功', '凭证已更新！')
                self.accept()
            else:
                vid = self.voucher_service.create_voucher(
                    period=period,
                    voucher_date=self._date_edit.date().toString('yyyy-MM-dd'),
                    voucher_type=self._type_combo.currentText(),
                    entries=entries,
                    attachment_count=self._attach_spin.value(),
                    remark=self._remark.text())
                QMessageBox.information(self, '成功', f'凭证已保存！凭证号: {vid}')

                if and_new:
                    self._reset()
                else:
                    self.accept()

        except Exception as e:
            QMessageBox.critical(self, '保存失败', str(e))

    def _reset(self):
        """重置表单（用于"保存并新增"）"""
        self._voucher_id = None
        self._date_edit.setDate(QDate.currentDate())
        self._attach_spin.setValue(0)
        self._remark.clear()

        # 清空分录行
        for r in self._entry_rows[:]:
            self._entry_rows.remove(r)
            self._entries_container.removeWidget(r)
            r.deleteLater()

        self._add_entry_row()
        self._add_entry_row()

    def _load_voucher(self, voucher_id: int):
        """加载已有凭证进行编辑"""
        voucher = self.voucher_service.get_voucher(voucher_id)
        if not voucher:
            QMessageBox.warning(self, '错误', f'凭证 {voucher_id} 不存在')
            self.reject()
            return

        self._type_combo.setCurrentText(voucher['voucher_type'])
        self._lbl_voucher_no.setText(str(voucher['voucher_no']))
        self._date_edit.setDate(QDate.fromString(voucher['voucher_date'], 'yyyy-MM-dd'))
        self._attach_spin.setValue(voucher['attachment_count'])
        self._remark.setText(voucher.get('remark', ''))

        # 清除默认行
        self._entry_rows.clear()
        while self._entries_container.count():
            w = self._entries_container.takeAt(0).widget()
            if w:
                w.deleteLater()

        # 加载分录
        for entry in voucher['entries']:
            self._add_entry_row(entry)