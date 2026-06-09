"""
==============================================
 ui/pages/fixed_asset.py - 固定资产管理页面
==============================================
功能：
  - 资产卡片列表（分页、搜索、筛选）
  - 新增/编辑/删除资产
  - 折旧计提（直线法/双倍余额/年数总和法）
  - 折旧明细查询
  - 资产汇总统计
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QLineEdit,
    QComboBox, QHeaderView, QGroupBox, QTabWidget,
    QMessageBox, QAbstractItemView, QFormLayout,
    QDialog, QDialogButtonBox, QDoubleSpinBox,
    QDateEdit, QSpinBox, QTextEdit, QGridLayout,
    QFrame, QSplitter, QProgressBar
)
from PyQt6.QtCore import Qt, QDate, QSize
from PyQt6.QtGui import QColor, QFont

from core.fixed_asset_service import FixedAssetService


# ────────────────────────────────────────
#  新增/编辑资产对话框
# ────────────────────────────────────────
class AssetDialog(QDialog):
    """资产卡片对话框"""

    def __init__(self, service: FixedAssetService, parent=None, asset_id=None):
        super().__init__(parent)
        self.service = service
        self.asset_id = asset_id
        self.setWindowTitle('新增资产' if not asset_id else '编辑资产')
        self.setMinimumWidth(550)
        self.setModal(True)
        self._setup()
        if asset_id:
            self._load(asset_id)

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        form = QFormLayout()
        form.setSpacing(8)

        self._code = QLineEdit()
        self._code.setPlaceholderText('例如：ZC-2026-001')
        form.addRow('资产编号*:', self._code)

        self._name = QLineEdit()
        self._name.setPlaceholderText('例如：办公电脑')
        form.addRow('资产名称*:', self._name)

        self._category = QComboBox()
        self._category.addItems(['', '房屋建筑物', '机器设备', '运输设备',
                                  '电子设备', '办公家具', '其他'])
        self._category.setEditable(True)
        form.addRow('类别:', self._category)

        self._spec = QLineEdit()
        self._spec.setPlaceholderText('规格型号')
        form.addRow('规格型号:', self._spec)

        self._dept = QLineEdit()
        self._dept.setPlaceholderText('使用部门')
        form.addRow('使用部门:', self._dept)

        self._location = QLineEdit()
        form.addRow('存放地点:', self._location)

        # 金额
        self._original = QDoubleSpinBox()
        self._original.setRange(0, 999999999)
        self._original.setDecimals(2)
        self._original.setSingleStep(1000)
        self._original.setPrefix('¥ ')
        form.addRow('原值*:', self._original)

        self._residual_rate = QDoubleSpinBox()
        self._residual_rate.setRange(0, 1)
        self._residual_rate.setDecimals(2)
        self._residual_rate.setSingleStep(0.01)
        self._residual_rate.setValue(0.05)
        self._residual_rate.setSuffix(' (5%)')
        form.addRow('残值率:', self._residual_rate)

        # 折旧方法
        self._depr_method = QComboBox()
        self._depr_method.addItem('直线法（平均年限法）', 'straight')
        self._depr_method.addItem('双倍余额递减法', 'double')
        self._depr_method.addItem('年数总和法', 'sum_years')
        form.addRow('折旧方法:', self._depr_method)

        self._total_months = QSpinBox()
        self._total_months.setRange(1, 600)
        self._total_months.setValue(60)
        self._total_months.setSuffix(' 个月')
        form.addRow('折旧期限:', self._total_months)

        # 日期
        self._purchase_date = QDateEdit()
        self._purchase_date.setCalendarPopup(True)
        self._purchase_date.setDate(QDate.currentDate())
        form.addRow('购入日期:', self._purchase_date)

        self._use_date = QDateEdit()
        self._use_date.setCalendarPopup(True)
        self._use_date.setDate(QDate.currentDate())
        form.addRow('开始使用日期:', self._use_date)

        self._remark = QTextEdit()
        self._remark.setMaximumHeight(60)
        form.addRow('备注:', self._remark)

        layout.addLayout(form)

        # 按钮
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self._save)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _save(self):
        if not self._code.text().strip():
            QMessageBox.warning(self, '提示', '请输入资产编号')
            return
        if not self._name.text().strip():
            QMessageBox.warning(self, '提示', '请输入资产名称')
            return
        if self._original.value() <= 0:
            QMessageBox.warning(self, '提示', '原值必须大于0')
            return

        try:
            data = {
                'asset_code': self._code.text().strip(),
                'asset_name': self._name.text().strip(),
                'category': self._category.currentText(),
                'specification': self._spec.text().strip(),
                'department': self._dept.text().strip(),
                'location': self._location.text().strip(),
                'original_value': self._original.value(),
                'residual_rate': self._residual_rate.value(),
                'depr_method': self._depr_method.currentData(),
                'total_months': self._total_months.value(),
                'purchase_date': self._purchase_date.date().toString('yyyy-MM-dd'),
                'start_use_date': self._use_date.date().toString('yyyy-MM-dd'),
                'remark': self._remark.toPlainText().strip(),
            }

            if self.asset_id:
                self.service.update_asset(self.asset_id, **data)
                QMessageBox.information(self, '成功', '资产已更新！')
            else:
                self.service.create_asset(**data)
                QMessageBox.information(self, '成功', '资产已新增！')

            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def _load(self, asset_id: int):
        """加载资产数据到表单"""
        asset = self.service.get_asset(asset_id)
        if not asset:
            return
        self._code.setText(asset.get('asset_code', ''))
        self._name.setText(asset.get('asset_name', ''))
        idx = self._category.findText(asset.get('category', ''))
        if idx >= 0:
            self._category.setCurrentIndex(idx)
        self._spec.setText(asset.get('specification', ''))
        self._dept.setText(asset.get('department', ''))
        self._location.setText(asset.get('location', ''))
        self._original.setValue(asset.get('original_value', 0))
        self._residual_rate.setValue(asset.get('residual_rate', 0.05))

        method = asset.get('depr_method', 'straight')
        midx = self._depr_method.findData(method)
        if midx >= 0:
            self._depr_method.setCurrentIndex(midx)

        self._total_months.setValue(asset.get('total_months', 60))

        pd = asset.get('purchase_date', '')
        if pd:
            self._purchase_date.setDate(QDate.fromString(pd, 'yyyy-MM-dd'))
        ud = asset.get('start_use_date', '')
        if ud:
            self._use_date.setDate(QDate.fromString(ud, 'yyyy-MM-dd'))
        self._remark.setText(asset.get('remark', ''))


# ────────────────────────────────────────
#  主页面
# ────────────────────────────────────────
class FixedAssetPage(QWidget):
    """固定资产管理页面"""

    def __init__(self, db_manager, tab='card'):
        super().__init__()
        self.db_manager = db_manager
        self.service = FixedAssetService(db_manager)
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

        self._tabs.addTab(self._build_card_tab(), '📋 资产卡片')
        self._tabs.addTab(self._build_depr_tab(), '💰 折旧管理')
        self._tabs.addTab(self._build_summary_tab(), '📊 汇总统计')
        self._tabs.addTab(self._build_change_tab(), '📜 变动历史')

        tab_map = {'card': 0, 'depr': 1, 'default': 0}
        self._tabs.setCurrentIndex(tab_map.get(self._tab, 0))
        layout.addWidget(self._tabs)

    # ── 资产卡片标签 ──
    def _build_card_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        # 工具栏
        tool = QHBoxLayout()
        tool.setSpacing(8)

        tool.addWidget(QLabel('搜索:'))
        self._card_search = QLineEdit()
        self._card_search.setPlaceholderText('编号/名称/部门...')
        self._card_search.setFixedWidth(200)
        self._card_search.returnPressed.connect(self._query_cards)
        tool.addWidget(self._card_search)

        self._card_status = QComboBox()
        self._card_status.addItems(['全部状态', '使用中(in_use)', '已报废(deprecated)', '已清理(scrapped)'])
        tool.addWidget(self._card_status)

        tool.addWidget(QLabel('类别:'))
        self._card_category = QComboBox()
        self._card_category.addItems(['全部', '房屋建筑物', '机器设备', '运输设备', '电子设备', '办公家具', '其他'])
        tool.addWidget(self._card_category)

        btn_query = QPushButton('🔍 查询')
        btn_query.clicked.connect(self._query_cards)
        tool.addWidget(btn_query)

        tool.addStretch()

        btn_add = QPushButton('➕ 新增资产')
        btn_add.setStyleSheet("background: #34A853; color: white; padding: 6px 16px; border-radius: 4px; font-weight: bold;")
        btn_add.clicked.connect(self._add_asset)
        tool.addWidget(btn_add)

        btn_edit = QPushButton('✏️ 编辑')
        btn_edit.clicked.connect(self._edit_asset)
        tool.addWidget(btn_edit)

        btn_del = QPushButton('🗑️ 删除')
        btn_del.setStyleSheet("color: #EA4335; padding: 6px 12px; border: 1px solid #EA4335; border-radius: 4px;")
        btn_del.clicked.connect(self._delete_asset)
        tool.addWidget(btn_del)

        sep = QLabel('│')
        sep.setStyleSheet("color: #E0E0E0; padding: 0 4px;")
        tool.addWidget(sep)

        btn_value = QPushButton('✏️ 信息变更')
        btn_value.setStyleSheet("background: #FF9800; color: white; padding: 6px 12px; border-radius: 4px;")
        btn_value.clicked.connect(self._modify_asset)
        tool.addWidget(btn_value)

        btn_split = QPushButton('✂️ 拆分')
        btn_split.setStyleSheet("background: #9C27B0; color: white; padding: 6px 12px; border-radius: 4px;")
        btn_split.clicked.connect(self._split_asset)
        tool.addWidget(btn_split)

        btn_merge = QPushButton('🔗 合并')
        btn_merge.setStyleSheet("background: #1A73E8; color: white; padding: 6px 12px; border-radius: 4px;")
        btn_merge.clicked.connect(self._merge_assets)
        tool.addWidget(btn_merge)

        layout.addLayout(tool)

        # 卡片表格
        self._card_table = QTableWidget(0, 11)
        self._card_table.setHorizontalHeaderLabels([
            '资产编号', '资产名称', '类别', '部门', '原值',
            '累计折旧', '净值', '残值率', '折旧方法', '状态', '使用日期'
        ])
        self._card_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self._card_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self._card_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._card_table.setAlternatingRowColors(True)
        self._card_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._card_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none;
                                  border-bottom: 2px solid #E0E0E0; padding: 6px; font-weight: bold; }
        """)
        self._card_table.doubleClicked.connect(self._edit_asset)
        layout.addWidget(self._card_table, 1)

        # 分页信息
        page_layout = QHBoxLayout()
        self._card_info = QLabel('共 0 条记录')
        self._card_info.setStyleSheet("color: #666;")
        page_layout.addWidget(self._card_info)
        page_layout.addStretch()

        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._query_cards)
        page_layout.addWidget(btn_refresh)
        layout.addLayout(page_layout)

        return tab

    def _query_cards(self):
        """查询资产卡片"""
        keyword = self._card_search.text().strip()
        status_text = self._card_status.currentText()
        status = None
        for s in ['in_use', 'deprecated', 'scrapped']:
            if s in status_text:
                status = s
                break

        cat = self._card_category.currentText()
        if cat == '全部':
            cat = None

        try:
            assets, total = self.service.list_assets(
                status=status, category=cat, keyword=keyword)
        except Exception:
            self._card_table.setRowCount(0)
            self._card_info.setText('请先选择账套')
            return

        method_names = {'straight': '直线法', 'double': '双倍余额', 'sum_years': '年数总和'}
        status_names = {'in_use': '使用中', 'deprecated': '已报废', 'scrapped': '已清理'}

        self._card_table.setRowCount(len(assets))
        for i, a in enumerate(assets):
            net = a['original_value'] - a['accumulated_depr']
            self._card_table.setItem(i, 0, QTableWidgetItem(a.get('asset_code', '')))
            self._card_table.setItem(i, 1, QTableWidgetItem(a.get('asset_name', '')))
            self._card_table.setItem(i, 2, QTableWidgetItem(a.get('category', '')))
            self._card_table.setItem(i, 3, QTableWidgetItem(a.get('department', '')))
            self._card_table.setItem(i, 4, QTableWidgetItem(f"{a.get('original_value', 0):,.2f}"))
            self._card_table.setItem(i, 5, QTableWidgetItem(f"{a.get('accumulated_depr', 0):,.2f}"))

            item_net = QTableWidgetItem(f"{net:,.2f}")
            if net <= 0:
                item_net.setForeground(QColor('#999'))
            self._card_table.setItem(i, 6, item_net)

            self._card_table.setItem(i, 7, QTableWidgetItem(f"{a.get('residual_rate', 0)*100:.0f}%"))
            self._card_table.setItem(i, 8, QTableWidgetItem(method_names.get(a.get('depr_method', ''), a.get('depr_method', ''))))
            self._card_table.setItem(i, 9, QTableWidgetItem(status_names.get(a.get('status', ''), a.get('status', ''))))
            self._card_table.setItem(i, 10, QTableWidgetItem(a.get('start_use_date', '')))

            # 存asset_id
            self._card_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, a.get('asset_id'))

        self._card_info.setText(f'共 {total} 条记录')

    def _add_asset(self):
        dlg = AssetDialog(self.service, self)
        if dlg.exec():
            self._query_cards()

    def _edit_asset(self):
        row = self._card_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, '提示', '请先选择要编辑的资产')
            return
        item = self._card_table.item(row, 0)
        if item and item.data(Qt.ItemDataRole.UserRole):
            dlg = AssetDialog(self.service, self, asset_id=item.data(Qt.ItemDataRole.UserRole))
            if dlg.exec():
                self._query_cards()

    def _delete_asset(self):
        row = self._card_table.currentRow()
        if row < 0:
            return
        item = self._card_table.item(row, 0)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return

        reply = QMessageBox.question(self, '确认删除',
            f'确定要删除资产 "{item.text()}" 吗？\n此操作不可撤销！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.service.delete_asset(item.data(Qt.ItemDataRole.UserRole))
            self._query_cards()

    # ── 折旧管理标签 ──
    def _build_depr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 操作区
        op_layout = QHBoxLayout()
        op_layout.setSpacing(12)

        op_layout.addWidget(QLabel('<b>折旧计提</b>'))
        op_layout.addWidget(QLabel('期间:'))

        self._depr_period = QComboBox()
        for y in range(2024, 2031):
            for m in range(1, 13):
                self._depr_period.addItem(f'{y}-{m:02d}')
        now = datetime.now()
        idx = self._depr_period.findText(f'{now.year}-{now.month:02d}')
        if idx >= 0:
            self._depr_period.setCurrentIndex(idx)
        op_layout.addWidget(self._depr_period)

        btn_calc = QPushButton('🧮 计算并计提')
        btn_calc.setStyleSheet("background: #1A73E8; color: white; padding: 8px 20px; border-radius: 4px; font-weight: bold;")
        btn_calc.clicked.connect(self._do_depr)
        op_layout.addWidget(btn_calc)

        btn_voucher = QPushButton('📝 生成凭证')
        btn_voucher.setStyleSheet("background: #34A853; color: white; padding: 8px 20px; border-radius: 4px;")
        btn_voucher.clicked.connect(self._gen_depr_voucher)
        op_layout.addWidget(btn_voucher)

        op_layout.addStretch()
        layout.addLayout(op_layout)

        # 折旧结果提示
        self._depr_result = QLabel('')
        self._depr_result.setStyleSheet("padding: 8px 12px; background: #F5F6FA; border-radius: 4px;")
        layout.addWidget(self._depr_result)

        # 折旧明细表格
        self._depr_table = QTableWidget(0, 8)
        self._depr_table.setHorizontalHeaderLabels([
            '期间', '资产编号', '资产名称', '部门', '原值',
            '累计折旧', '本期折旧', '折旧后净值'
        ])
        self._depr_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._depr_table.setAlternatingRowColors(True)
        self._depr_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._depr_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none;
                                  border-bottom: 2px solid #E0E0E0; padding: 6px; font-weight: bold; }
        """)
        layout.addWidget(self._depr_table, 1)

        # 刷新
        btn_refresh_depr = QPushButton('🔄 刷新折旧明细')
        btn_refresh_depr.clicked.connect(self._refresh_depr)
        layout.addWidget(btn_refresh_depr)

        return tab

    def _do_depr(self):
        """执行折旧计提"""
        period = self._depr_period.currentText()
        try:
            result = self.service.calc_and_record_depr(period)
            if result['asset_count'] == 0:
                self._depr_result.setText(f'ℹ️ 期间 {period} 所有资产已计提折旧，无需重复操作')
                self._depr_result.setStyleSheet("padding: 8px 12px; background: #FFF8E1; border-radius: 4px;")
            else:
                self._depr_result.setText(
                    f'✅ 计提完成！{result["asset_count"]} 项资产，'
                    f'共提折旧 ¥{result["total_amount"]:,.2f}')
                self._depr_result.setStyleSheet("padding: 8px 12px; background: #E8F5E9; border-radius: 4px;")
            self._refresh_depr()
        except Exception as e:
            QMessageBox.critical(self, '折旧失败', str(e))

    def _gen_depr_voucher(self):
        """生成折旧凭证"""
        period = self._depr_period.currentText()
        try:
            vid = self.service.generate_depr_voucher(period)
            QMessageBox.information(self, '成功', f'折旧凭证已生成！凭证ID: {vid}\n请到凭证管理查看并审核过账。')
        except ValueError as e:
            QMessageBox.warning(self, '提示', str(e))
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def _refresh_depr(self):
        """刷新折旧明细"""
        period = self._depr_period.currentText()
        try:
            records, total = self.service.get_depr_detail(period=period)
        except Exception:
            self._depr_table.setRowCount(0)
            return

        self._depr_table.setRowCount(len(records))
        for i, r in enumerate(records):
            self._depr_table.setItem(i, 0, QTableWidgetItem(r.get('period', '')))
            self._depr_table.setItem(i, 1, QTableWidgetItem(r.get('asset_code', '')))
            self._depr_table.setItem(i, 2, QTableWidgetItem(r.get('asset_name', '')))
            self._depr_table.setItem(i, 3, QTableWidgetItem(r.get('department', '')))
            self._depr_table.setItem(i, 4, QTableWidgetItem(f"{r.get('original_value', 0):,.2f}"))
            self._depr_table.setItem(i, 5, QTableWidgetItem(f"{r.get('accumulated_depr', 0):,.2f}"))
            self._depr_table.setItem(i, 6, QTableWidgetItem(f"{r.get('depr_amount', 0):,.2f}"))
            net = (r.get('original_value', 0) or 0) - (r.get('accumulated_depr', 0) or 0)
            self._depr_table.setItem(i, 7, QTableWidgetItem(f"{net:,.2f}"))

    # ── 汇总统计标签 ──
    def _build_summary_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(12)

        # 总览卡片
        summary_group = QGroupBox('资产总览')
        summary_group.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px;
                       background: white; border: 1px solid #E0E0E0; border-radius: 8px; }
        """)
        summary_layout = QGridLayout(summary_group)
        summary_layout.setSpacing(16)

        self._summary_labels = {}
        stats = [
            ('total_count', '资产总数', '--', 0, 0),
            ('in_use_count', '使用中', '--', 0, 1),
            ('total_original', '原值合计', '--', 1, 0),
            ('total_depr', '累计折旧', '--', 1, 1),
            ('total_net', '净值合计', '--', 2, 0),
        ]

        for key, label, default, row, col in stats:
            card = QFrame()
            card.setStyleSheet("""
                QFrame { background: #F8F9FA; border-radius: 8px; padding: 12px; }
            """)
            cl = QVBoxLayout(card)
            cl.addWidget(QLabel(f'<span style="color:#666;font-size:12px;">{label}</span>'))
            val = QLabel(f'<span style="font-size:22px;font-weight:bold;">{default}</span>')
            val.setStyleSheet("color: #1A73E8;")
            self._summary_labels[key] = val
            cl.addWidget(val)
            summary_layout.addWidget(card, row, col)

        layout.addWidget(summary_group)

        # 按类别汇总表
        layout.addWidget(QLabel('<b>按类别汇总</b>'))
        self._cat_table = QTableWidget(0, 5)
        self._cat_table.setHorizontalHeaderLabels([
            '类别', '数量', '原值合计', '累计折旧', '净值合计'
        ])
        self._cat_table.horizontalHeader().setStretchLastSection(True)
        self._cat_table.setAlternatingRowColors(True)
        self._cat_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._cat_table, 1)

        btn_refresh = QPushButton('🔄 刷新统计')
        btn_refresh.clicked.connect(self._refresh_summary)
        layout.addWidget(btn_refresh)

        return tab

    def _refresh_summary(self):
        """刷新汇总统计"""
        try:
            summary = self.service.get_asset_summary()
            if summary:
                self._summary_labels['total_count'].setText(
                    f'<span style="font-size:22px;font-weight:bold;">{summary.get("total_count", 0)}</span>')
                self._summary_labels['in_use_count'].setText(
                    f'<span style="font-size:22px;font-weight:bold;">{summary.get("in_use_count", 0)}</span>')
                self._summary_labels['total_original'].setText(
                    f'<span style="font-size:22px;font-weight:bold;">¥{summary.get("total_original", 0):,.2f}</span>')
                self._summary_labels['total_depr'].setText(
                    f'<span style="font-size:22px;font-weight:bold;">¥{summary.get("total_depr", 0):,.2f}</span>')
                self._summary_labels['total_net'].setText(
                    f'<span style="font-size:22px;font-weight:bold;">¥{summary.get("total_net", 0):,.2f}</span>')
        except Exception:
            pass

        try:
            cats = self.service.get_category_summary()
            self._cat_table.setRowCount(len(cats))
            for i, c in enumerate(cats):
                self._cat_table.setItem(i, 0, QTableWidgetItem(c.get('category', '')))
                self._cat_table.setItem(i, 1, QTableWidgetItem(str(c.get('count', 0))))
                self._cat_table.setItem(i, 2, QTableWidgetItem(f"¥{c.get('original_total', 0):,.2f}"))
                self._cat_table.setItem(i, 3, QTableWidgetItem(f"¥{c.get('depr_total', 0):,.2f}"))
                self._cat_table.setItem(i, 4, QTableWidgetItem(f"¥{c.get('net_total', 0):,.2f}"))
        except Exception:
            pass

    # ── 变动历史标签 ──
    def _build_change_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>资产变动记录</b>'))

        self._ch_search = QLineEdit()
        self._ch_search.setPlaceholderText('搜索资产名称...')
        self._ch_search.setFixedWidth(200)
        tool.addWidget(self._ch_search)

        btn = QPushButton('🔍 查询')
        btn.clicked.connect(self._query_changes)
        tool.addWidget(btn)

        tool.addStretch()
        btn_refresh = QPushButton('🔄 刷新')
        btn_refresh.clicked.connect(self._query_changes)
        tool.addWidget(btn_refresh)
        layout.addLayout(tool)

        self._ch_table = QTableWidget(0, 8)
        self._ch_table.setHorizontalHeaderLabels([
            '日期', '资产编码', '资产名称', '变动类型', '变动金额',
            '变动前原值', '变动后原值', '原因'
        ])
        self._ch_table.horizontalHeader().setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)
        self._ch_table.setAlternatingRowColors(True)
        self._ch_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._ch_table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none; font-weight: bold; padding: 6px; }
        """)
        layout.addWidget(self._ch_table, 1)

        self._ch_info = QLabel('共 0 条记录')
        self._ch_info.setStyleSheet("color: #666;")
        layout.addWidget(self._ch_info)

        return tab

    def _query_changes(self):
        """查询变动历史"""
        records, total = self.service.get_change_history()
        type_names = {'value_up': '💰增值', 'value_down': '📉减值',
                      'split': '✂️拆分', 'merge': '🔗合并', 'modify': '✏️信息变更'}
        self._ch_table.setRowCount(len(records))
        for i, r in enumerate(records):
            self._ch_table.setItem(i, 0, QTableWidgetItem(r.get('change_date', '')))
            self._ch_table.setItem(i, 1, QTableWidgetItem(r.get('asset_code', '')))
            self._ch_table.setItem(i, 2, QTableWidgetItem(r.get('asset_name', '')))
            ct = r.get('change_type', '')
            self._ch_table.setItem(i, 3, QTableWidgetItem(type_names.get(ct, ct)))
            amt_item = QTableWidgetItem(f"¥{r.get('change_amount', 0):+,.2f}")
            if r.get('change_amount', 0) > 0:
                amt_item.setForeground(QColor('#34A853'))
            elif r.get('change_amount', 0) < 0:
                amt_item.setForeground(QColor('#EA4335'))
            self._ch_table.setItem(i, 4, amt_item)
            self._ch_table.setItem(i, 5, QTableWidgetItem(f"¥{r.get('old_value', 0):,.2f}"))
            self._ch_table.setItem(i, 6, QTableWidgetItem(f"¥{r.get('new_value', 0):,.2f}"))

            # 显示变更明细摘要
            details = r.get('change_details', '')
            reason = r.get('reason', '')
            if details and details.startswith('{'):
                try:
                    import json
                    det = json.loads(details)
                    parts = []
                    if ct == 'modify':
                        for field, vals in det.items():
                            parts.append(f'{field}: {vals.get("old","")}→{vals.get("new","")}')
                        reason = reason or '; '.join(parts[:3])
                    elif ct == 'split':
                        parts = [p.get('name','') for p in det.get('parts',[])]
                        reason = reason or f'拆分为: {", ".join(parts)}'
                    elif ct == 'merge':
                        merged = det.get('merged_assets', [])
                        reason = reason or f'合并: {", ".join(merged)}'
                except Exception:
                    pass
            self._ch_table.setItem(i, 7, QTableWidgetItem(reason))
        self._ch_info.setText(f'共 {total} 条记录')

    # ── 资产变动操作方法 ──
    def _get_selected_asset(self):
        """获取当前选中的资产"""
        row = self._card_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, '提示', '请先选择一个资产')
            return None
        item = self._card_table.item(row, 0)
        if not item or not item.data(Qt.ItemDataRole.UserRole):
            return None
        return self.service.get_asset(item.data(Qt.ItemDataRole.UserRole))

    def _modify_asset(self):
        """信息变更（原值/折旧期限/折旧方法/残值率等）"""
        asset = self._get_selected_asset()
        if not asset:
            return
        from ui.dialogs.asset_change_dialogs import ModifyAssetDialog
        dlg = ModifyAssetDialog(self.service, asset, self)
        if dlg.exec():
            self._query_cards()

    def _split_asset(self):
        """拆分资产"""
        asset = self._get_selected_asset()
        if not asset:
            return
        from ui.dialogs.asset_change_dialogs import SplitDialog
        dlg = SplitDialog(self.service, asset, self)
        if dlg.exec():
            self._query_cards()

    def _merge_assets(self):
        """合并资产"""
        # 获取所有状态为in_use的资产
        assets, _ = self.service.list_assets(status='in_use')
        if len(assets) < 2:
            QMessageBox.warning(self, '提示', '至少需要两个使用中的资产才能合并')
            return
        from ui.dialogs.asset_change_dialogs import MergeDialog
        dlg = MergeDialog(self.service, assets, self)
        if dlg.exec():
            self._query_cards()

    # ── 公共 ──
    def on_activate(self, book_id):
        self.refresh()

    def refresh(self):
        self._query_cards()
        self._refresh_depr()
        self._refresh_summary()
        self._query_changes()
        self._refresh_summary()