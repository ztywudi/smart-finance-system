"""
==================================================
 ui/dialogs/create_book_dialog.py - 新建账套对话框
==================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLineEdit, QComboBox, QTextEdit, QPushButton,
    QLabel, QDialogButtonBox, QWidget, QGroupBox,
    QMessageBox, QListWidget, QListWidgetItem, QStackedWidget,
    QDateEdit, QSpinBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor

from core.account_system import AccountingSystemManager
from core.database import DatabaseManager
from industry_templates import get_available_templates


class SystemDetailCard(QWidget):
    """会计制度详情卡片"""

    def __init__(self, sys_info):
        super().__init__()
        self.sys_info = sys_info
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # 制度名称
        title = QLabel(f'<h2>{self.sys_info.name}</h2>')
        title.setStyleSheet("color: #1A73E8;")
        layout.addWidget(title)

        # 基本信息
        info = QLabel()
        info.setWordWrap(True)
        info.setText(f"""
        <table style="font-size: 13px;">
        <tr><td width=100><b>适用对象：</b></td><td>{self.sys_info.applicable_to}</td></tr>
        <tr><td><b>分类：</b></td><td>{self.sys_info.category}</td></tr>
        <tr><td><b>科目编码：</b></td><td>{self.sys_info.acct_code_length}位（{' - '.join(str(l) for l in self.sys_info.acct_levels)}）</td></tr>
        <tr><td><b>辅助核算：</b></td><td>{'支持' if self.sys_info.has_auxiliary else '不支持'}</td></tr>
        <tr><td><b>税务方法：</b></td><td>{'正常' if self.sys_info.tax_method == 'normal' else '简化' if self.sys_info.tax_method == 'simplified' else '不适用'}</td></tr>
        <tr><td><b>版本：</b></td><td>{self.sys_info.version}</td></tr>
        <tr><td><b>施行日期：</b></td><td>{self.sys_info.effective_date}</td></tr>
        </table>
        <br><p style="color: #666;">{self.sys_info.description}</p>
        """)
        layout.addWidget(info)

        layout.addStretch()


class CreateBookDialog(QDialog):
    """新建账套对话框"""

    def __init__(self, db_manager: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.book_name = ''
        self.selected_system = None

        self.setWindowTitle('新建账套')
        self.setMinimumSize(800, 600)
        self.resize(900, 650)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 标题
        title = QLabel('<h2>📂 新建账套</h2>')
        layout.addWidget(title)

        # ── 上半：基本信息 ──
        info_group = QGroupBox('基本信息')
        info_layout = QFormLayout(info_group)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText('例如：XX公司2026年度账')
        info_layout.addRow('账套名称：', self._name_edit)

        self._company_edit = QLineEdit()
        self._company_edit.setPlaceholderText('单位全称（可选）')
        info_layout.addRow('单位名称：', self._company_edit)

        self._year_spin = QSpinBox()
        self._year_spin.setRange(2020, 2050)
        self._year_spin.setValue(2026)
        info_layout.addRow('会计年度起始年：', self._year_spin)

        self._month_spin = QSpinBox()
        self._month_spin.setRange(1, 12)
        self._month_spin.setValue(1)
        info_layout.addRow('起始月份：', self._month_spin)

        self._desc_edit = QLineEdit()
        self._desc_edit.setPlaceholderText('备注说明（可选）')
        info_layout.addRow('备注：', self._desc_edit)

        # 行业选择
        self._industry_combo = QComboBox()
        self._industry_combo.addItem('（通用/无特殊行业）', 'none')
        for t in get_available_templates():
            self._industry_combo.addItem(f'{t["name"]}', t['code'])
        info_layout.addRow('行业模板：', self._industry_combo)

        layout.addWidget(info_group)

        # ── 下半：制度选择 ──
        sys_group = QGroupBox('选择会计制度')
        sys_layout = QHBoxLayout(sys_group)

        # 左侧：制度列表
        self._sys_list = QListWidget()
        self._sys_list.setMinimumWidth(200)
        self._sys_list.setMaximumWidth(280)
        self._sys_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #D0D0D0;
                border-radius: 4px;
                font-size: 13px;
            }
            QListWidget::item {
                padding: 10px 12px;
                border-bottom: 1px solid #F0F0F0;
            }
            QListWidget::item:selected {
                background-color: #1A73E8;
                color: white;
            }
        """)
        sys_layout.addWidget(self._sys_list)

        # 右侧：详情面板
        self._detail_stack = QStackedWidget()
        self._detail_stack.setStyleSheet("background: white; border: 1px solid #E0E0E0; border-radius: 4px;")
        sys_layout.addWidget(self._detail_stack, 1)

        layout.addWidget(sys_group, 1)

        # ── 底部按钮 ──
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._btn_create = QPushButton('✅ 创建账套')
        self._btn_create.setStyleSheet("""
            QPushButton {
                background-color: #1A73E8; color: white;
                padding: 10px 30px; font-size: 14px;
                border-radius: 4px; font-weight: bold;
            }
            QPushButton:hover { background-color: #1557B0; }
            QPushButton:disabled { background-color: #CCCCCC; color: #888; }
        """)
        self._btn_create.setEnabled(False)
        self._btn_create.clicked.connect(self._on_create)
        btn_layout.addWidget(self._btn_create)

        btn_cancel = QPushButton('取消')
        btn_cancel.setStyleSheet("""
            QPushButton {
                padding: 10px 20px; font-size: 13px;
                border: 1px solid #D0D0D0; border-radius: 4px;
                background: white;
            }
            QPushButton:hover { background: #F5F5F5; }
        """)
        btn_cancel.clicked.connect(self.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)

        # ── 加载制度数据 ──
        self._load_systems()

        # 连接信号
        self._sys_list.currentRowChanged.connect(self._on_system_changed)
        self._name_edit.textChanged.connect(self._validate)

    def _load_systems(self):
        """加载会计制度列表"""
        categories = AccountingSystemManager.get_categories()

        # 按分类添加标题
        for cat in categories:
            systems = AccountingSystemManager.get_systems_by_category(cat)
            # 分类标题
            icons = {'企业': '🏢', '政府及非营利组织': '🏛️', '基金（资金）': '💰', '农村及合作组织': '🌾'}
            icon = icons.get(cat, '📋')
            title_item = QListWidgetItem(f'{icon}  {cat}')
            title_item.setFlags(Qt.ItemFlag.NoItemFlags)
            title_item.setData(Qt.ItemDataRole.UserRole, None)
            f = title_item.font()
            f.setBold(True)
            f.setPointSize(11)
            title_item.setFont(f)
            title_item.setForeground(QColor(0x5F, 0x63, 0x68))
            self._sys_list.addItem(title_item)

            for sys_info in systems:
                item = QListWidgetItem(f'    {sys_info.name}')
                item.setData(Qt.ItemDataRole.UserRole, sys_info.code)

                # 创建详情卡片
                card = SystemDetailCard(sys_info)
                self._detail_stack.addWidget(card)

                self._sys_list.addItem(item)

    def _on_system_changed(self, row):
        """制度选择变更"""
        item = self._sys_list.item(row)
        if item and item.data(Qt.ItemDataRole.UserRole):
            # 计算对应的详情页索引
            detail_idx = 0
            for i in range(row + 1):
                it = self._sys_list.item(i)
                if it and it.data(Qt.ItemDataRole.UserRole):
                    detail_idx += 1
            self._detail_stack.setCurrentIndex(detail_idx - 1)
            self.selected_system = item.data(Qt.ItemDataRole.UserRole)
        self._validate()

    def _validate(self):
        """校验输入"""
        valid = bool(self._name_edit.text().strip()) and bool(self.selected_system)
        self._btn_create.setEnabled(valid)

    def _on_create(self):
        """确认创建"""
        name = self._name_edit.text().strip()
        company = self._company_edit.text().strip() or name

        try:
            book_id = self.db_manager.create_account_book(
                book_name=name,
                accounting_system=self.selected_system,
                company_name=company,
                fiscal_year_start=self._month_spin.value(),
                description=self._desc_edit.text().strip(),
                industry_code=self._industry_combo.currentData()
            )
            self.book_name = name
            QMessageBox.information(self, '成功',
                f'账套创建成功！\n\n编号：{book_id}\n名称：{name}\n会计制度：{AccountingSystemManager.get_system(self.selected_system).name}')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', f'创建失败：{e}')