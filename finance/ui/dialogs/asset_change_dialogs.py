"""
==================================================
 ui/dialogs/asset_change_dialogs.py - 资产变动对话框
==================================================
包含：原值变动、拆分、合并 三个对话框
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGroupBox,
    QLineEdit, QDoubleSpinBox, QPushButton, QLabel, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox, QDateEdit,
    QTextEdit, QDialogButtonBox, QComboBox, QAbstractItemView,
    QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor


# ─────────────────────────────────────────────
#  通用资产信息变更对话框
# ─────────────────────────────────────────────
class ModifyAssetDialog(QDialog):
    """通用资产信息变更对话框——支持修改所有字段"""

    # 可修改字段配置
    FIELD_CONFIG = [
        ('asset_name', '资产名称', 'text'),
        ('category', '类别', 'combo', ['', '房屋建筑物', '机器设备', '运输设备',
                                         '电子设备', '办公家具', '其他']),
        ('specification', '规格型号', 'text'),
        ('department', '使用部门', 'text'),
        ('location', '存放地点', 'text'),
        ('original_value', '原值', 'money'),
        ('accumulated_depr', '累计折旧', 'money'),
        ('residual_rate', '残值率', 'percent'),
        ('depr_method', '折旧方法', 'combo',
         [('直线法（平均年限法）', 'straight'),
          ('双倍余额递减法', 'double'),
          ('年数总和法', 'sum_years')]),
        ('total_months', '折旧期限(月)', 'int', 1, 600),
        ('status', '状态', 'combo',
         [('使用中', 'in_use'), ('已报废', 'deprecated'), ('已清理', 'scrapped')]),
    ]

    def __init__(self, service, asset, parent=None):
        super().__init__(parent)
        self.service = service
        self.asset = asset
        self.setWindowTitle(f'信息变更 - {asset["asset_name"]} ({asset["asset_code"]})')
        self.setMinimumSize(550, 500)
        self.setModal(True)
        self._changes = {}
        self._widgets = {}
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)

        # 当前资产信息
        info = QLabel(
            f'<b>资产：</b>{self.asset["asset_name"]} ({self.asset["asset_code"]})<br>'
            f'<b>当前原值：</b>¥{self.asset["original_value"]:,.2f} | '
            f'<b>累计折旧：</b>¥{self.asset["accumulated_depr"]:,.2f} | '
            f'<b>净值：</b>¥{self.asset["original_value"] - self.asset["accumulated_depr"]:,.2f}'
        )
        info.setStyleSheet("padding: 8px; background: #F5F6FA; border-radius: 4px; font-size: 13px;")
        layout.addWidget(info)

        # 变动日期和原因
        top_form = QHBoxLayout()
        top_form.addWidget(QLabel('变动日期:'))
        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())
        top_form.addWidget(self._date)
        top_form.addWidget(QLabel('  原因:'))
        self._reason = QLineEdit()
        self._reason.setPlaceholderText('变更原因说明')
        top_form.addWidget(self._reason, 1)
        layout.addLayout(top_form)

        # 可编辑字段表单
        scroll = QGroupBox('修改字段（留空=不修改）')
        scroll.setStyleSheet("""
            QGroupBox { font-weight: bold; padding-top: 16px; }
        """)
        form = QFormLayout(scroll)
        form.setSpacing(6)

        # 折旧方法名称映射
        method_map = {'straight': '直线法（平均年限法）', 'double': '双倍余额递减法',
                      'sum_years': '年数总和法'}

        for cfg in self.FIELD_CONFIG:
            field = cfg[0]
            label = cfg[1]
            ftype = cfg[2]
            old_val = self.asset.get(field, '')

            if field == 'depr_method':
                old_val = method_map.get(old_val, old_val)
            elif field == 'residual_rate':
                old_val = f'{float(old_val)*100:.0f}%'
            elif field == 'original_value' or field == 'accumulated_depr':
                old_val = f'¥{float(old_val):,.2f}'
            elif field == 'total_months':
                old_val = f'{old_val}个月'

            # 旧值显示
            old_label = QLabel(f'<span style="color:#999;">当前: {old_val}</span>')
            old_label.setStyleSheet("font-size: 12px;")

            if ftype == 'text':
                w = QLineEdit()
                w.setPlaceholderText(f'输入新{label}')
                widget_box = QVBoxLayout()
                widget_box.addWidget(w)
                widget_box.addWidget(old_label)
                form.addRow(f'{label}:', widget_box)
                self._widgets[field] = ('text', w)

            elif ftype == 'money':
                w = QDoubleSpinBox()
                w.setRange(0, 999999999)
                w.setDecimals(2)
                w.setPrefix('¥ ')
                w.setSpecialValueText('(不变)')
                w.setValue(0)
                widget_box = QVBoxLayout()
                widget_box.addWidget(w)
                widget_box.addWidget(old_label)
                form.addRow(f'{label}:', widget_box)
                self._widgets[field] = ('money', w)

            elif ftype == 'percent':
                w = QDoubleSpinBox()
                w.setRange(0, 1)
                w.setDecimals(2)
                w.setSingleStep(0.01)
                w.setSuffix(' (0-100%)')
                w.setSpecialValueText('(不变)')
                w.setValue(0)
                widget_box = QVBoxLayout()
                widget_box.addWidget(w)
                widget_box.addWidget(old_label)
                form.addRow(f'{label}:', widget_box)
                self._widgets[field] = ('percent', w)

            elif ftype == 'combo':
                items = cfg[3] if len(cfg) > 3 else []
                w = QComboBox()
                w.addItem('(不变)', None)
                for item in items:
                    if isinstance(item, tuple):
                        w.addItem(item[0], item[1])
                    else:
                        w.addItem(item, item)
                widget_box = QVBoxLayout()
                widget_box.addWidget(w)
                widget_box.addWidget(old_label)
                form.addRow(f'{label}:', widget_box)
                self._widgets[field] = ('combo', w)

            elif ftype == 'int':
                min_v = cfg[3] if len(cfg) > 3 else 1
                max_v = cfg[4] if len(cfg) > 4 else 600
                w = QDoubleSpinBox()
                w.setRange(min_v, max_v)
                w.setDecimals(0)
                w.setSpecialValueText('(不变)')
                w.setValue(0)
                widget_box = QVBoxLayout()
                widget_box.addWidget(w)
                widget_box.addWidget(old_label)
                form.addRow(f'{label}:', widget_box)
                self._widgets[field] = ('int', w)

        layout.addWidget(scroll, 1)

        # 预览变更
        self._preview = QLabel('')
        self._preview.setStyleSheet("padding: 8px; background: #FFF8E1; border-radius: 4px;")
        self._preview.setWordWrap(True)
        layout.addWidget(self._preview)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        btn_preview = QPushButton('👁️ 预览变更')
        btn_preview.clicked.connect(self._preview_changes)
        btn_layout.addWidget(btn_preview)

        self._btn_ok = QPushButton('✅ 确认变更')
        self._btn_ok.setStyleSheet("""
            QPushButton { background: #FF9800; color: white; padding: 8px 24px;
                         border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #F57C00; }
        """)
        self._btn_ok.clicked.connect(self._confirm)
        btn_layout.addWidget(self._btn_ok)
        btn_layout.addWidget(QPushButton('取消', clicked=self.reject))
        layout.addLayout(btn_layout)

    def _collect_changes(self) -> dict:
        """收集用户修改的字段"""
        changes = {}
        method_rev_map = {'直线法（平均年限法）': 'straight', '双倍余额递减法': 'double',
                          '年数总和法': 'sum_years'}

        for field, (ftype, widget) in self._widgets.items():
            if ftype == 'text':
                val = widget.text().strip()
                if val:
                    changes[field] = val
            elif ftype == 'money':
                val = widget.value()
                if val > 0:
                    changes[field] = val
            elif ftype == 'percent':
                val = widget.value()
                if val > 0:
                    changes[field] = val
            elif ftype == 'combo':
                data = widget.currentData()
                if data is not None:
                    changes[field] = data
            elif ftype == 'int':
                val = int(widget.value())
                if val > 0:
                    changes[field] = val

        return changes

    def _preview_changes(self):
        """预览所有变更"""
        changes = self._collect_changes()
        if not changes:
            self._preview.setText('⚠️ 未检测到任何变更')
            return

        lines = ['<b>将变更以下字段：</b>']
        field_names = {c[0]: c[1] for c in self.FIELD_CONFIG}
        for field, new_val in changes.items():
            old_val = self.asset.get(field, '')
            name = field_names.get(field, field)
            # 格式化显示
            if field == 'residual_rate':
                lines.append(f'  • {name}: <span style="color:#999;">{float(old_val)*100:.0f}%</span> → '
                             f'<span style="color:#FF9800;font-weight:bold;">{float(new_val)*100:.0f}%</span>')
            elif field in ('original_value', 'accumulated_depr'):
                lines.append(f'  • {name}: <span style="color:#999;">¥{float(old_val):,.2f}</span> → '
                             f'<span style="color:#FF9800;font-weight:bold;">¥{float(new_val):,.2f}</span>')
            else:
                lines.append(f'  • {name}: <span style="color:#999;">{old_val}</span> → '
                             f'<span style="color:#FF9800;font-weight:bold;">{new_val}</span>')

        self._preview.setText('<br>'.join(lines))

    def _confirm(self):
        """确认变更"""
        changes = self._collect_changes()
        if not changes:
            QMessageBox.warning(self, '提示', '请至少修改一个字段')
            return

        try:
            result = self.service.modify_asset(
                self.asset['asset_id'], changes,
                self._date.date().toString('yyyy-MM-dd'),
                self._reason.text().strip()
            )
            QMessageBox.information(self, '成功',
                f'资产信息已更新！\n'
                f'原值：¥{result["original_value"]:,.2f} | '
                f'折旧：¥{result["accumulated_depr"]:,.2f} | '
                f'期限：{result["total_months"]}个月')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '变更失败', str(e))


# ─────────────────────────────────────────────
#  原值变动对话框
# ─────────────────────────────────────────────
class ValueChangeDialog(QDialog):
    """资产原值变动对话框（增值/减值）"""

    def __init__(self, service, asset, parent=None):
        super().__init__(parent)
        self.service = service
        self.asset = asset
        self.setWindowTitle(f'原值变动 - {asset["asset_name"]} ({asset["asset_code"]})')
        self.setMinimumWidth(450)
        self.setModal(True)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)

        # 当前资产信息
        info = QLabel(
            f'<b>资产：</b>{self.asset["asset_name"]} ({self.asset["asset_code"]})<br>'
            f'<b>当前原值：</b>¥{self.asset["original_value"]:,.2f}<br>'
            f'<b>累计折旧：</b>¥{self.asset["accumulated_depr"]:,.2f}<br>'
            f'<b>当前净值：</b>¥{self.asset["original_value"] - self.asset["accumulated_depr"]:,.2f}'
        )
        info.setStyleSheet("padding: 10px; background: #F5F6FA; border-radius: 4px;")
        layout.addWidget(info)

        form = QFormLayout()
        form.setSpacing(8)

        self._amount = QDoubleSpinBox()
        self._amount.setRange(-999999999, 999999999)
        self._amount.setDecimals(2)
        self._amount.setSingleStep(1000)
        self._amount.setPrefix('¥ ')
        self._amount.valueChanged.connect(self._preview)
        form.addRow('变动金额:', self._amount)
        form.addRow('', QLabel('<span style="color:#999;font-size:12px;">正值=增值，负值=减值</span>'))

        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())
        form.addRow('变动日期:', self._date)

        self._reason = QTextEdit()
        self._reason.setPlaceholderText('变动原因（如：设备升级改造、部分拆除等）')
        self._reason.setMaximumHeight(60)
        form.addRow('变动原因:', self._reason)

        layout.addLayout(form)

        # 变动后预览
        self._preview_label = QLabel('变动后原值：¥---,--  变动后净值：¥---,--')
        self._preview_label.setStyleSheet("padding: 8px; background: #FFF8E1; border-radius: 4px;")
        layout.addWidget(self._preview_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn_ok = QPushButton('✅ 确认变动')
        self._btn_ok.setStyleSheet("""
            QPushButton { background: #FF9800; color: white; padding: 8px 24px;
                         border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #F57C00; }
        """)
        self._btn_ok.clicked.connect(self._confirm)
        btn_layout.addWidget(self._btn_ok)
        btn_layout.addWidget(QPushButton('取消', clicked=self.reject))
        layout.addLayout(btn_layout)

    def _preview(self):
        amount = self._amount.value()
        new_value = self.asset['original_value'] + amount
        old_rate = self.asset['accumulated_depr'] / self.asset['original_value'] if self.asset['original_value'] > 0 else 0
        new_depr = round(new_value * old_rate, 2)
        new_net = new_value - new_depr
        color = '#34A853' if amount >= 0 else '#EA4335'
        self._preview_label.setText(
            f'变动后原值：<span style="color:{color};font-weight:bold;">¥{new_value:,.2f}</span>  '
            f'变动后净值：¥{new_net:,.2f}  '
            f'累计折旧：¥{new_depr:,.2f}'
        )

    def _confirm(self):
        amount = self._amount.value()
        if amount == 0:
            QMessageBox.warning(self, '提示', '变动金额不能为0')
            return
        new_value = self.asset['original_value'] + amount
        if new_value <= 0:
            QMessageBox.warning(self, '提示', '变动后原值不能小于等于0')
            return

        try:
            result = self.service.value_change(
                self.asset['asset_id'], amount,
                self._date.date().toString('yyyy-MM-dd'),
                self._reason.toPlainText().strip())
            QMessageBox.information(self, '成功',
                f'原值变动完成！\n变动后原值：¥{result["original_value"]:,.2f}\n'
                f'累计折旧：¥{result["accumulated_depr"]:,.2f}')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))


# ─────────────────────────────────────────────
#  拆分对话框
# ─────────────────────────────────────────────
class SplitDialog(QDialog):
    """资产拆分对话框"""

    def __init__(self, service, asset, parent=None):
        super().__init__(parent)
        self.service = service
        self.asset = asset
        self.setWindowTitle(f'拆分资产 - {asset["asset_name"]}')
        self.setMinimumSize(550, 450)
        self.setModal(True)
        self._parts = []
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        info = QLabel(
            f'<b>资产：</b>{self.asset["asset_name"]} ({self.asset["asset_code"]})<br>'
            f'<b>原值：</b>¥{self.asset["original_value"]:,.2f} '
            f'<b>累计折旧：</b>¥{self.asset["accumulated_depr"]:,.2f}'
        )
        layout.addWidget(info)

        layout.addWidget(QLabel('<b>拆分后资产明细（金额合计需等于原值）</b>'))

        self._table = QTableWidget(2, 4)
        self._table.setHorizontalHeaderLabels(['资产名称', '拆分金额', '部门', '类别'])
        self._table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; }
            QHeaderView::section { background: #F8F9FA; border: none; font-weight: bold; }
        """)
        self._fill_row(0, f'{self.asset["asset_name"]}(一)')
        self._fill_row(1, f'{self.asset["asset_name"]}(二)')
        layout.addWidget(self._table)

        btn_add = QPushButton('➕ 添加拆分项')
        btn_add.clicked.connect(self._add_row)
        layout.addWidget(btn_add)

        # 校验提示
        self._balance_label = QLabel(f'已分配：¥0.00 / ¥{self.asset["original_value"]:,.2f}')
        self._balance_label.setStyleSheet("padding: 6px; background: #F5F6FA; border-radius: 4px;")
        layout.addWidget(self._balance_label)

        # 原因
        form = QFormLayout()
        self._reason = QTextEdit()
        self._reason.setPlaceholderText('拆分原因')
        self._reason.setMaximumHeight(50)
        form.addRow('拆分原因:', self._reason)
        layout.addLayout(form)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn_ok = QPushButton('✅ 确认拆分')
        self._btn_ok.setStyleSheet("""
            QPushButton { background: #9C27B0; color: white; padding: 8px 24px;
                         border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background: #7B1FA2; }
        """)
        self._btn_ok.clicked.connect(self._confirm)
        btn_layout.addWidget(self._btn_ok)
        btn_layout.addWidget(QPushButton('取消', clicked=self.reject))
        layout.addLayout(btn_layout)

        self._table.itemChanged.connect(self._update_balance)

    def _fill_row(self, row, name):
        self._table.setItem(row, 0, QTableWidgetItem(name))
        amt = QTableWidgetItem(f'{self.asset["original_value"] / 2:,.2f}' if row == 0 else '')
        self._table.setItem(row, 1, amt)
        self._table.setItem(row, 2, QTableWidgetItem(self.asset.get('department', '')))
        self._table.setItem(row, 3, QTableWidgetItem(self.asset.get('category', '')))

    def _add_row(self):
        row = self._table.rowCount()
        self._table.insertRow(row)
        self._table.setItem(row, 0, QTableWidgetItem(f'{self.asset["asset_name"]}({row+1})'))
        self._table.setItem(row, 1, QTableWidgetItem(''))
        self._table.setItem(row, 2, QTableWidgetItem(self.asset.get('department', '')))
        self._table.setItem(row, 3, QTableWidgetItem(self.asset.get('category', '')))

    def _update_balance(self):
        total = 0.0
        for r in range(self._table.rowCount()):
            try:
                total += float(self._table.item(r, 1).text().replace(',', '') or '0')
            except (ValueError, AttributeError):
                pass
        diff = self.asset['original_value'] - total
        color = '#34A853' if abs(diff) < 0.01 else '#EA4335'
        self._balance_label.setText(
            f'已分配：¥{total:,.2f} / ¥{self.asset["original_value"]:,.2f}  '
            f'<span style="color:{color};">差额：¥{diff:,.2f}</span>'
        )

    def _confirm(self):
        total = 0.0
        parts = []
        for r in range(self._table.rowCount()):
            name_item = self._table.item(r, 0)
            amt_item = self._table.item(r, 1)
            if not name_item or not name_item.text().strip():
                continue
            try:
                amt = float(amt_item.text().replace(',', '') or '0')
            except (ValueError, AttributeError):
                continue
            if amt <= 0:
                continue
            total += amt
            dept_item = self._table.item(r, 2)
            cat_item = self._table.item(r, 3)
            parts.append({
                'asset_name': name_item.text().strip(),
                'original_value': amt,
                'department': dept_item.text().strip() if dept_item else '',
                'category': cat_item.text().strip() if cat_item else '',
            })

        if len(parts) < 2:
            QMessageBox.warning(self, '提示', '至少需要两个有效的拆分项')
            return
        if abs(total - self.asset['original_value']) > 0.01:
            QMessageBox.warning(self, '提示',
                f'拆分金额合计 ¥{total:,.2f} ≠ 原值 ¥{self.asset["original_value"]:,.2f}')
            return

        try:
            results = self.service.split_asset(
                self.asset['asset_id'], parts,
                QDate.currentDate().toString('yyyy-MM-dd'),
                self._reason.toPlainText().strip())
            names = [r['asset_name'] for r in results]
            QMessageBox.information(self, '成功',
                f'拆分完成！已创建 {len(results)} 项新资产：\n' + '\n'.join(f'  • {n}' for n in names))
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '拆分失败', str(e))


# ─────────────────────────────────────────────
#  合并对话框
# ─────────────────────────────────────────────
class MergeDialog(QDialog):
    """资产合并对话框"""

    def __init__(self, service, source_assets, parent=None):
        super().__init__(parent)
        self.service = service
        self.source_assets = source_assets  # 列表中选中的资产
        self.setWindowTitle('合并资产')
        self.setMinimumSize(550, 400)
        self.setModal(True)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)

        layout.addWidget(QLabel('<b>选择目标资产（合并到哪个资产）</b>'))

        self._target_combo = QComboBox()
        for a in self.source_assets:
            self._target_combo.addItem(
                f'{a["asset_code"]} {a["asset_name"]} ¥{a["original_value"]:,.2f}',
                a['asset_id'])
        layout.addWidget(self._target_combo)

        # 被合并资产列表
        layout.addWidget(QLabel('<b>被合并的资产（将合并到目标资产中）：</b>'))
        self._source_list = QListWidget()
        for a in self.source_assets:
            item = QListWidgetItem(f'{a["asset_code"]} {a["asset_name"]} ¥{a["original_value"]:,.2f}')
            item.setData(Qt.ItemDataRole.UserRole, a['asset_id'])
            item.setCheckState(Qt.CheckState.Checked)
            self._source_list.addItem(item)
        self._source_list.setStyleSheet("""
            QListWidget { border: 1px solid #E0E0E0; border-radius: 4px; }
            QListWidget::item { padding: 6px; }
        """)
        layout.addWidget(self._source_list, 1)

        # 预览
        self._preview = QLabel('')
        self._preview.setStyleSheet("padding: 8px; background: #F5F6FA; border-radius: 4px;")
        layout.addWidget(self._preview)
        self._target_combo.currentIndexChanged.connect(self._update_preview)

        # 原因
        self._reason = QTextEdit()
        self._reason.setPlaceholderText('合并原因')
        self._reason.setMaximumHeight(50)
        layout.addWidget(self._reason)

        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn_ok = QPushButton('✅ 确认合并')
        self._btn_ok.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 8px 24px;
                         border-radius: 4px; font-weight: bold; }
        """)
        self._btn_ok.clicked.connect(self._confirm)
        btn_layout.addWidget(self._btn_ok)
        btn_layout.addWidget(QPushButton('取消', clicked=self.reject))
        layout.addLayout(btn_layout)

        self._update_preview()

    def _update_preview(self):
        target_id = self._target_combo.currentData()
        target = next((a for a in self.source_assets if a['asset_id'] == target_id), None)
        if not target:
            return

        total_add = 0
        for i in range(self._source_list.count()):
            item = self._source_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                aid = item.data(Qt.ItemDataRole.UserRole)
                if aid != target_id:
                    a = next((x for x in self.source_assets if x['asset_id'] == aid), None)
                    if a:
                        total_add += a['original_value']

        new_value = target['original_value'] + total_add
        self._preview.setText(
            f'目标资产：{target["asset_name"]} 原值 ¥{target["original_value"]:,.2f}\n'
            f'合并增加：¥{total_add:,.2f}\n'
            f'合并后原值：<b>¥{new_value:,.2f}</b>'
        )

    def _confirm(self):
        target_id = self._target_combo.currentData()
        source_ids = []
        for i in range(self._source_list.count()):
            item = self._source_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                aid = item.data(Qt.ItemDataRole.UserRole)
                if aid != target_id:
                    source_ids.append(aid)

        if not source_ids:
            QMessageBox.warning(self, '提示', '请至少勾选一个被合并的资产')
            return

        try:
            result = self.service.merge_assets(
                source_ids + [target_id], target_id,
                QDate.currentDate().toString('yyyy-MM-dd'),
                self._reason.toPlainText().strip())
            QMessageBox.information(self, '成功',
                f'合并完成！\n{result["asset_name"]} 原值变为 ¥{result["original_value"]:,.2f}')
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, '合并失败', str(e))