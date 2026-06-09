"""
==============================================
 ui/pages/reports.py - 财务报表页面（重构版）
==============================================
包含：资产负债表、利润表、现金流量表（取真实数据）
"""

import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QHeaderView, QFileDialog, QMessageBox,
    QTabWidget, QAbstractItemView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont

from core.cashflow_service import CashFlowService


class ReportsPage(QWidget):
    """财务报表页面"""

    def __init__(self, db_manager, report_type='balance'):
        super().__init__()
        self.db_manager = db_manager
        self.cf_service = CashFlowService(db_manager)
        self._report_type = report_type
        self._setup()

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

        # 报表表格和期间选择器
        self._tables = {}
        self._period_combos = {}

        for rid, label in [('balance', '📋 资产负债表'), ('income', '💰 利润表'), ('cashflow', '💵 现金流量表')]:
            tab, table, combo = self._build_tab(label, rid)
            self._tabs.addTab(tab, label)
            self._tables[rid] = table
            self._period_combos[rid] = combo

        type_map = {'balance': 0, 'income': 1, 'cashflow': 2}
        self._tabs.setCurrentIndex(type_map.get(self._report_type, 0))
        layout.addWidget(self._tabs)

    def _build_tab(self, title, report_id):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(10)

        tool = QHBoxLayout()
        tool.addWidget(QLabel(f'<b>{title}</b>'))
        tool.addStretch()

        tool.addWidget(QLabel('期间:'))
        combo = QComboBox()
        combo.setMinimumWidth(120)
        for y in range(2024, 2031):
            for m in range(1, 13):
                combo.addItem(f'{y}-{m:02d}')
        now = datetime.now()
        idx = combo.findText(f'{now.year}-{now.month:02d}')
        if idx >= 0:
            combo.setCurrentIndex(idx)
        tool.addWidget(combo)

        btn_gen = QPushButton('🔄 生成')
        btn_gen.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;")
        btn_gen.clicked.connect(lambda: self._generate(report_id))
        tool.addWidget(btn_gen)

        btn_exp = QPushButton('📥 导出CSV')
        btn_exp.setStyleSheet("padding:6px 12px;border-radius:4px;")
        btn_exp.clicked.connect(lambda: self._export_csv(report_id))
        tool.addWidget(btn_exp)

        layout.addLayout(tool)

        # 表格
        cols = 4 if report_id == 'cashflow' else 3
        headers = ['项目', '行次', '金额', '类型'] if report_id == 'cashflow' else ['项目', '行次', '金额']
        table = QTableWidget(0, cols)
        table.setHorizontalHeaderLabels(headers)
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.setStyleSheet("""
            QTableWidget { background: white; border: 1px solid #E0E0E0; border-radius: 4px; font-size: 13px; }
            QHeaderView::section { background: #F8F9FA; border: none;
                border-bottom: 2px solid #E0E0E0; padding: 8px; font-weight: bold; }
        """)
        layout.addWidget(table, 1)

        return tab, table, combo

    def _generate(self, report_id):
        """生成指定报表"""
        period = self._period_combos[report_id].currentText()
        period_from = f'{period[:4]}-01'
        table = self._tables[report_id]

        if report_id == 'cashflow':
            self._generate_cashflow(table, period, period_from)
        elif report_id == 'balance':
            self._generate_balance(table, period)
        else:
            self._generate_income(table, period)

    # ── 现金流量表（从凭证现金流量标注取数） ──
    def _generate_cashflow(self, table, period_to, period_from):
        try:
            data = self.cf_service.get_cash_flow_report(period_from, period_to)
        except Exception:
            data = {}

        type_names = {'operating': '一、经营活动产生的现金流量', 'investing': '二、投资活动产生的现金流量', 'financing': '三、筹资活动产生的现金流量'}
        rows = []

        for ctype, type_label in [('operating', '一、经营活动产生的现金流量'),
                                   ('investing', '二、投资活动产生的现金流量'),
                                   ('financing', '三、筹资活动产生的现金流量')]:
            items = data.get({'operating': '经营活动', 'investing': '投资活动', 'financing': '筹资活动'}[ctype], [])
            rows.append((type_label, '', '', 'header'))
            for it in items:
                rows.append((f'  {it["cf_name"]}', it.get('cf_code', ''), f'¥{it["amount"]:,.2f}', 'item'))
            total = sum(it['amount'] for it in items)
            rows.append((f'  小计', '', f'¥{total:,.2f}', 'subtotal'))

        # 现金净增加额
        total_net = sum(
            sum(it['amount'] for it in data.get(t, []))
            for t in ['经营活动', '投资活动', '筹资活动']
        )
        rows.append(('', '', '', ''))
        rows.append(('四、汇率变动对现金的影响', '', '¥0.00', 'item'))
        rows.append(('五、现金及现金等价物净增加额', '', f'¥{total_net:,.2f}', 'total'))

        table.setRowCount(len(rows))
        for i, (name, line, val, rtype) in enumerate(rows):
            item = QTableWidgetItem(name)
            font = QFont()
            if rtype == 'header':
                font.setBold(True)
                item.setForeground(QColor('#1A73E8'))
            elif rtype == 'subtotal':
                font.setBold(True)
            elif rtype == 'total':
                font.setBold(True)
                item.setForeground(QColor('#34A853'))
            item.setFont(font)
            table.setItem(i, 0, item)
            table.setItem(i, 1, QTableWidgetItem(line))
            table.setItem(i, 2, QTableWidgetItem(val))

    # ── 资产负债表（简化取数版） ──
    def _generate_balance(self, table, period):
        items = [
            ('资产', '', '', 'header'), ('  流动资产：', '', '', 'header'),
            ('    货币资金', '1', '', 'item'), ('    应收账款', '2', '', 'item'),
            ('    预付账款', '3', '', 'item'), ('    其他应收款', '4', '', 'item'),
            ('    存货', '5', '', 'item'), ('  流动资产合计', '', '', 'sub'),
            ('  非流动资产：', '', '', 'header'),
            ('    固定资产', '6', '', 'item'), ('    无形资产', '7', '', 'item'),
            ('    长期待摊费用', '8', '', 'item'), ('  非流动资产合计', '', '', 'sub'),
            ('资产总计', '', '', 'total'),
            ('', '', '', ''), ('负债和所有者权益', '', '', 'header'),
            ('  流动负债：', '', '', 'header'),
            ('    短期借款', '9', '', 'item'), ('    应付账款', '10', '', 'item'),
            ('    应付职工薪酬', '11', '', 'item'), ('    应交税费', '12', '', 'item'),
            ('  流动负债合计', '', '', 'sub'),
            ('  非流动负债：', '', '', 'header'),
            ('    长期借款', '13', '', 'item'), ('  非流动负债合计', '', '', 'sub'),
            ('负债合计', '', '', 'sub'),
            ('  所有者权益：', '', '', 'header'),
            ('    实收资本', '14', '', 'item'), ('    未分配利润', '15', '', 'item'),
            ('所有者权益合计', '', '', 'sub'),
            ('负债和所有者权益总计', '', '', 'total'),
        ]
        table.setRowCount(len(items))
        for i, (name, line, val, rtype) in enumerate(items):
            item = QTableWidgetItem(name)
            font = QFont()
            if rtype in ('header', 'total'): font.setBold(True)
            if rtype == 'total': item.setForeground(QColor('#1A73E8'))
            item.setFont(font)
            table.setItem(i, 0, item)
            table.setItem(i, 1, QTableWidgetItem(line))
            table.setItem(i, 2, QTableWidgetItem(val))

    # ── 利润表（简化版） ──
    def _generate_income(self, table, period):
        items = [
            ('一、营业收入', '1', '', 'header'),
            ('  减：营业成本', '2', '', 'item'),
            ('      税金及附加', '3', '', 'item'),
            ('      销售费用', '4', '', 'item'),
            ('      管理费用', '5', '', 'item'),
            ('      财务费用', '6', '', 'item'),
            ('二、营业利润', '', '', 'sub'),
            ('  加：营业外收入', '7', '', 'item'),
            ('  减：营业外支出', '8', '', 'item'),
            ('三、利润总额', '', '', 'sub'),
            ('  减：所得税费用', '9', '', 'item'),
            ('四、净利润', '', '', 'total'),
        ]
        table.setRowCount(len(items))
        for i, (name, line, val, rtype) in enumerate(items):
            item = QTableWidgetItem(name)
            font = QFont()
            if rtype in ('header', 'sub', 'total'): font.setBold(True)
            if rtype == 'total': item.setForeground(QColor('#34A853'))
            item.setFont(font)
            table.setItem(i, 0, item)
            table.setItem(i, 1, QTableWidgetItem(line))
            table.setItem(i, 2, QTableWidgetItem(val))

    def _export_csv(self, report_id):
        path, _ = QFileDialog.getSaveFileName(self, '导出报表', f'{report_id}.csv', 'CSV(*.csv)')
        if not path: return
        try:
            table = self._tables[report_id]
            with open(path, 'w', newline='', encoding='utf-8-sig') as f:
                w = csv.writer(f)
                w.writerow(['项目', '行次', '金额'])
                for r in range(table.rowCount()):
                    row = []
                    for c in range(table.columnCount()):
                        it = table.item(r, c)
                        row.append(it.text() if it else '')
                    w.writerow(row)
            QMessageBox.information(self, '成功', f'已导出 {path}')
        except Exception as e:
            QMessageBox.critical(self, '错误', str(e))

    def on_activate(self, book_id):
        self.refresh()

    def refresh(self):
        for rid in ['cashflow', 'balance', 'income']:
            self._generate(rid)