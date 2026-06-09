"""
==============================================
 ui/pages/ar_ap.py - 应收应付管理页面
==============================================
4个标签页：往来单位 | 应收账款 | 应付账款 | 账龄分析
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QHeaderView,
    QTabWidget, QMessageBox, QAbstractItemView, QDialog, QFormLayout,
    QDateEdit, QDoubleSpinBox, QGroupBox, QDialogButtonBox, QTextEdit,
    QGridLayout, QFrame
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from core.arap_service import ArapService


# ── 往来单位对话框 ──
class PartnerDialog(QDialog):
    def __init__(self, service, ptype, parent=None, pid=None):
        super().__init__(parent)
        self.service = service; self.ptype = ptype; self.pid = pid
        t = '客户' if ptype == 'customer' else '供应商'
        self.setWindowTitle(f'新增{t}' if not pid else f'编辑{t}')
        self.setMinimumWidth(400); self.setModal(True)
        layout = QVBoxLayout(self); form = QFormLayout()
        self._code = QLineEdit(); form.addRow('编号*:', self._code)
        self._name = QLineEdit(); form.addRow('名称*:', self._name)
        self._contact = QLineEdit(); form.addRow('联系人:', self._contact)
        self._phone = QLineEdit(); form.addRow('电话:', self._phone)
        self._addr = QTextEdit(); self._addr.setMaximumHeight(50); form.addRow('地址:', self._addr)
        self._bank = QLineEdit(); form.addRow('银行账号:', self._bank)
        self._credit = QDoubleSpinBox(); self._credit.setRange(0,99999999)
        self._credit.setDecimals(2); self._credit.setPrefix('¥ ')
        form.addRow('信用额度:', self._credit)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        if pid: self._load()

    def _save(self):
        if not self._code.text().strip() or not self._name.text().strip():
            QMessageBox.warning(self,'提示','请输入编号和名称'); return
        try:
            if self.pid:
                self.service.update_partner(self.pid, partner_name=self._name.text().strip(),
                    contact=self._contact.text().strip(), phone=self._phone.text().strip(),
                    address=self._addr.toPlainText().strip(), bank_acct=self._bank.text().strip(),
                    credit_limit=self._credit.value())
            else:
                self.service.add_partner(self._code.text().strip(), self._name.text().strip(),
                    self.ptype, contact=self._contact.text().strip(), phone=self._phone.text().strip(),
                    address=self._addr.toPlainText().strip(), bank=self._bank.text().strip(),
                    credit_limit=self._credit.value())
            self.accept()
        except Exception as e: QMessageBox.critical(self,'错误',str(e))

    def _load(self):
        rows,_ = self.service.list_partners(ptype=self.ptype, status='')
        p = next((x for x in rows if x['partner_id']==self.pid), None)
        if p:
            self._code.setText(p['partner_code']); self._code.setEnabled(False)
            self._name.setText(p['partner_name']); self._contact.setText(p.get('contact',''))
            self._phone.setText(p.get('phone','')); self._addr.setText(p.get('address',''))
            self._bank.setText(p.get('bank_acct','')); self._credit.setValue(p.get('credit_limit',0))


# ── 发票对话框 ──
class InvoiceDialog(QDialog):
    def __init__(self, service, ptype, partners, parent=None):
        super().__init__(parent)
        self.service = service; self.ptype = ptype
        t = '应收' if ptype == 'customer' else '应付'
        self.setWindowTitle(f'新增{t}发票')
        self.setMinimumWidth(450); self.setModal(True)
        layout = QVBoxLayout(self); form = QFormLayout()
        self._partner = QComboBox()
        for p in partners: self._partner.addItem(f'{p["partner_code"]} {p["partner_name"]}', p['partner_id'])
        form.addRow('往来单位:', self._partner)
        self._doc_no = QLineEdit(); form.addRow('单据号*:', self._doc_no)
        self._date = QDateEdit(); self._date.setCalendarPopup(True); self._date.setDate(QDate.currentDate())
        form.addRow('日期:', self._date)
        self._due = QDateEdit(); self._due.setCalendarPopup(True);
        self._due.setDate(QDate.currentDate().addDays(30)); form.addRow('到期日:', self._due)
        self._amount = QDoubleSpinBox(); self._amount.setRange(0,99999999)
        self._amount.setDecimals(2); self._amount.setPrefix('¥ '); self._amount.setSingleStep(1000)
        form.addRow('金额*:', self._amount)
        self._summary = QTextEdit(); self._summary.setMaximumHeight(50); form.addRow('摘要:', self._summary)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _save(self):
        if not self._doc_no.text().strip() or self._amount.value()<=0:
            QMessageBox.warning(self,'提示','请输入单据号和金额'); return
        try:
            pid = self._partner.currentData()
            date = self._date.date().toString('yyyy-MM-dd')
            due = self._due.date().toString('yyyy-MM-dd')
            amt = self._amount.value()
            summary = self._summary.toPlainText().strip()
            if self.ptype == 'customer':
                self.service.add_ar_invoice(self._doc_no.text().strip(), pid, date, due, amt, summary)
            else:
                self.service.add_ap_invoice(self._doc_no.text().strip(), pid, date, due, amt, summary)
            self.accept()
        except Exception as e: QMessageBox.critical(self,'错误',str(e))


# ── 收款/付款对话框 ──
class PaymentDialog(QDialog):
    def __init__(self, service, ptype, invoice, parent=None):
        super().__init__(parent)
        self.service = service; self.ptype = ptype; self.invoice = invoice
        t = '收款' if ptype == 'customer' else '付款'
        self.setWindowTitle(f'{t} - {invoice.get("doc_no","")}')
        self.setMinimumWidth(400); self.setModal(True)
        layout = QVBoxLayout(self)
        info = QLabel(f'<b>单据:</b> {invoice.get("doc_no","")} '
                      f'<b>金额:</b> ¥{invoice.get("amount",0):,.2f} '
                      f'<b>已{t}:</b> ¥{invoice.get("paid_amount",0):,.2f} '
                      f'<b>余额:</b> ¥{invoice.get("balance",0):,.2f}')
        info.setStyleSheet("padding:8px;background:#F5F6FA;border-radius:4px;")
        layout.addWidget(info)
        form = QFormLayout()
        self._amount = QDoubleSpinBox(); self._amount.setRange(0,99999999)
        self._amount.setDecimals(2); self._amount.setPrefix('¥ ')
        self._amount.setValue(invoice.get('balance',0))
        form.addRow(f'{t}金额:', self._amount)
        self._date = QDateEdit(); self._date.setCalendarPopup(True); self._date.setDate(QDate.currentDate())
        form.addRow('日期:', self._date)
        self._method = QComboBox(); self._method.addItems(['银行转账','现金','支票','其他'])
        form.addRow('方式:', self._method)
        self._summary = QTextEdit(); self._summary.setMaximumHeight(50); form.addRow('备注:', self._summary)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)

    def _save(self):
        try:
            amt = self._amount.value()
            date = self._date.date().toString('yyyy-MM-dd')
            method = self._method.currentText()
            summary = self._summary.toPlainText().strip()
            if self.ptype == 'customer':
                self.service.record_ar_payment(self.invoice['invoice_id'], date, amt, method, summary)
            else:
                self.service.record_ap_payment(self.invoice['invoice_id'], date, amt, method, summary)
            self.accept()
        except Exception as e: QMessageBox.critical(self,'错误',str(e))


class ArapPage(QWidget):
    def __init__(self, db_manager, tab='ar'):
        super().__init__()
        self.db_manager = db_manager
        self.service = ArapService(db_manager)
        self._setup()
        tmap = {'ar':1, 'ap':2, 'aging':3}
        self._tabs.setCurrentIndex(tmap.get(tab, 1))

    def _setup(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border:none; background:#F5F6FA; }
            QTabBar::tab { padding:10px 20px; font-size:13px; border:none;
                          border-bottom:2px solid transparent; }
            QTabBar::tab:selected { color:#1A73E8; border-bottom:2px solid #1A73E8; font-weight:bold; }
        """)
        self._tabs.addTab(self._build_partner_tab(), '👥 往来单位')
        self._tabs.addTab(self._build_ar_tab(), '📤 应收账款')
        self._tabs.addTab(self._build_ap_tab(), '📥 应付账款')
        self._tabs.addTab(self._build_aging_tab(), '📊 账龄分析')
        layout.addWidget(self._tabs)

    # ── 往来单位 ──
    def _build_partner_tab(self):
        tab=QWidget(); l=QVBoxLayout(tab); l.setContentsMargins(16,16,16,16)
        t=QHBoxLayout()
        t.addWidget(QLabel('<b>👥 往来单位</b>')); t.addStretch()
        self._p_kind=QComboBox(); self._p_kind.addItems(['全部','客户','供应商']); t.addWidget(self._p_kind)
        self._p_search=QLineEdit(); self._p_search.setPlaceholderText('搜索...'); self._p_search.setFixedWidth(150); t.addWidget(self._p_search)
        btn_q=QPushButton('🔍'); btn_q.clicked.connect(self._refresh_partner); t.addWidget(btn_q)
        btn_a=QPushButton('➕ 新增')
        btn_a.setStyleSheet("background:#34A853;color:white;padding:6px 16px;border-radius:4px;")
        btn_a.clicked.connect(self._add_partner); t.addWidget(btn_a)
        btn_r=QPushButton('🔄'); btn_r.clicked.connect(self._refresh_partner); t.addWidget(btn_r)
        l.addLayout(t)
        self._pt=QTableWidget(0,6)
        self._pt.setHorizontalHeaderLabels(['编号','名称','类型','联系人','电话','余额'])
        self._pt.horizontalHeader().setStretchLastSection(True)
        self._pt.setAlternatingRowColors(True); self._pt.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._pt.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        l.addWidget(self._pt,1)
        return tab

    def _refresh_partner(self):
        kw=self._p_search.text().strip()
        pt=self._p_kind.currentText()
        pt_map={'客户':'customer','供应商':'supplier'}
        ptype=pt_map.get(pt,'')
        try:
            rows,total=self.service.list_partners(ptype=ptype, keyword=kw)
            self._pt.setRowCount(len(rows))
            for i,r in enumerate(rows):
                self._pt.setItem(i,0,QTableWidgetItem(r['partner_code']))
                self._pt.setItem(i,1,QTableWidgetItem(r['partner_name']))
                t='客户' if r['partner_type']=='customer' else '供应商'
                self._pt.setItem(i,2,QTableWidgetItem(t))
                self._pt.setItem(i,3,QTableWidgetItem(r.get('contact','')))
                self._pt.setItem(i,4,QTableWidgetItem(r.get('phone','')))
                b=QTableWidgetItem(f"¥{r.get('balance',0):,.2f}")
                if r.get('balance',0)>0: b.setForeground(QColor('#EA4335'))
                elif r.get('balance',0)<0: b.setForeground(QColor('#34A853'))
                self._pt.setItem(i,5,b)
                self._pt.item(i,0).setData(Qt.ItemDataRole.UserRole,r['partner_id'])
        except: pass

    def _add_partner(self):
        pt='customer' if self._p_kind.currentText() in ('客户','全部') else 'supplier'
        dlg=PartnerDialog(self.service,pt,self)
        if dlg.exec(): self._refresh_partner()

    # ── 应收账款 ──
    def _build_ar_tab(self):
        tab=QWidget(); l=QVBoxLayout(tab); l.setContentsMargins(16,16,16,16)
        t=QHBoxLayout()
        t.addWidget(QLabel('<b>📤 应收账款</b>')); t.addStretch()
        self._ar_status=QComboBox(); self._ar_status.addItems(['全部','未清(unpaid)','已结清(paid)','逾期(overdue)']); t.addWidget(self._ar_status)
        self._ar_search=QLineEdit(); self._ar_search.setPlaceholderText('搜索单据/客户...'); self._ar_search.setFixedWidth(180); t.addWidget(self._ar_search)
        btn_q=QPushButton('🔍'); btn_q.clicked.connect(self._refresh_ar); t.addWidget(btn_q)
        btn_a=QPushButton('➕ 新增发票')
        btn_a.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;")
        btn_a.clicked.connect(lambda:self._add_invoice('customer')); t.addWidget(btn_a)
        btn_p=QPushButton('💰 收款')
        btn_p.setStyleSheet("background:#34A853;color:white;padding:6px 12px;border-radius:4px;")
        btn_p.clicked.connect(lambda:self._do_payment('customer')); t.addWidget(btn_p)
        l.addLayout(t)
        self._ar_t=QTableWidget(0,8)
        self._ar_t.setHorizontalHeaderLabels(['单据号','客户','日期','到期日','金额','已收','余额','状态'])
        self._ar_t.horizontalHeader().setStretchLastSection(True)
        self._ar_t.setAlternatingRowColors(True); self._ar_t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        l.addWidget(self._ar_t,1)
        return tab

    def _refresh_ar(self):
        kw=self._ar_search.text().strip()
        st=self._ar_status.currentText()
        status_map={'未清(unpaid)':'unpaid','已结清(paid)':'paid','逾期(overdue)':'overdue'}
        status=status_map.get(st,'')
        try:
            rows,total=self.service.get_ar_invoices(status=status, keyword=kw)
            self._ar_t.setRowCount(len(rows))
            for i,r in enumerate(rows):
                self._ar_t.setItem(i,0,QTableWidgetItem(r['doc_no']))
                self._ar_t.setItem(i,1,QTableWidgetItem(r.get('partner_name','')))
                self._ar_t.setItem(i,2,QTableWidgetItem(r.get('doc_date','')))
                self._ar_t.setItem(i,3,QTableWidgetItem(r.get('due_date','')))
                self._ar_t.setItem(i,4,QTableWidgetItem(f"¥{r['amount']:,.2f}"))
                self._ar_t.setItem(i,5,QTableWidgetItem(f"¥{r.get('paid_amount',0):,.2f}"))
                bal=QTableWidgetItem(f"¥{r.get('balance',0):,.2f}")
                if r.get('balance',0)>0: bal.setForeground(QColor('#EA4335'))
                self._ar_t.setItem(i,6,bal)
                self._ar_t.setItem(i,7,QTableWidgetItem(r.get('status','')))
                self._ar_t.item(i,0).setData(Qt.ItemDataRole.UserRole,r['invoice_id'])
        except: pass

    # ── 应付账款 ──
    def _build_ap_tab(self):
        tab=QWidget(); l=QVBoxLayout(tab); l.setContentsMargins(16,16,16,16)
        t=QHBoxLayout()
        t.addWidget(QLabel('<b>📥 应付账款</b>')); t.addStretch()
        self._ap_status=QComboBox(); self._ap_status.addItems(['全部','未清(unpaid)','已结清(paid)']);
        t.addWidget(self._ap_status)
        self._ap_search=QLineEdit(); self._ap_search.setPlaceholderText('搜索单据/供应商...'); self._ap_search.setFixedWidth(180); t.addWidget(self._ap_search)
        btn_q=QPushButton('🔍'); btn_q.clicked.connect(self._refresh_ap); t.addWidget(btn_q)
        btn_a=QPushButton('➕ 新增发票')
        btn_a.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;")
        btn_a.clicked.connect(lambda:self._add_invoice('supplier')); t.addWidget(btn_a)
        btn_p=QPushButton('💰 付款')
        btn_p.setStyleSheet("background:#EA4335;color:white;padding:6px 12px;border-radius:4px;")
        btn_p.clicked.connect(lambda:self._do_payment('supplier')); t.addWidget(btn_p)
        l.addLayout(t)
        self._ap_t=QTableWidget(0,8)
        self._ap_t.setHorizontalHeaderLabels(['单据号','供应商','日期','到期日','金额','已付','余额','状态'])
        self._ap_t.horizontalHeader().setStretchLastSection(True)
        self._ap_t.setAlternatingRowColors(True); self._ap_t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        l.addWidget(self._ap_t,1)
        return tab

    def _refresh_ap(self):
        kw=self._ap_search.text().strip()
        st=self._ap_status.currentText()
        status={'未清(unpaid)':'unpaid','已结清(paid)':'paid'}.get(st,'')
        try:
            rows,total=self.service.get_ap_invoices(status=status, keyword=kw)
            self._ap_t.setRowCount(len(rows))
            for i,r in enumerate(rows):
                self._ap_t.setItem(i,0,QTableWidgetItem(r['doc_no']))
                self._ap_t.setItem(i,1,QTableWidgetItem(r.get('partner_name','')))
                self._ap_t.setItem(i,2,QTableWidgetItem(r.get('doc_date','')))
                self._ap_t.setItem(i,3,QTableWidgetItem(r.get('due_date','')))
                self._ap_t.setItem(i,4,QTableWidgetItem(f"¥{r['amount']:,.2f}"))
                self._ap_t.setItem(i,5,QTableWidgetItem(f"¥{r.get('paid_amount',0):,.2f}"))
                bal=QTableWidgetItem(f"¥{r.get('balance',0):,.2f}")
                if r.get('balance',0)>0: bal.setForeground(QColor('#EA4335'))
                self._ap_t.setItem(i,6,bal)
                self._ap_t.setItem(i,7,QTableWidgetItem(r.get('status','')))
                self._ap_t.item(i,0).setData(Qt.ItemDataRole.UserRole,r['invoice_id'])
        except: pass

    # ── 账龄分析 ──
    def _build_aging_tab(self):
        tab=QWidget(); l=QVBoxLayout(tab); l.setContentsMargins(16,16,16,16)
        t=QHBoxLayout()
        t.addWidget(QLabel('<b>📊 账龄分析</b>')); t.addStretch()
        self._ag_type=QComboBox(); self._ag_type.addItems(['应收账款','应付账款']); t.addWidget(self._ag_type)
        btn_q=QPushButton('🔍 分析'); btn_q.clicked.connect(self._refresh_aging); t.addWidget(btn_q)
        self._ag_sum=QLabel(''); self._ag_sum.setStyleSheet("padding:6px 12px;background:#F5F6FA;border-radius:4px;")
        t.addWidget(self._ag_sum)
        l.addLayout(t)

        self._ag_t=QTableWidget(0,8)
        self._ag_t.setHorizontalHeaderLabels(['单位','未到期','1-30天','31-60天','61-90天','91-180天','180天+','合计'])
        self._ag_t.horizontalHeader().setStretchLastSection(True)
        self._ag_t.setAlternatingRowColors(True); self._ag_t.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        l.addWidget(self._ag_t,1)

        # 汇总行
        self._ag_total=QFrame(); tl=QHBoxLayout(self._ag_total)
        self._ag_total.setStyleSheet("background:#F8F9FA;border:1px solid #E0E0E0;border-radius:4px;padding:8px;")
        self._ag_total_labels={}
        for label in ['单位数','余额合计','未到期','逾期30天','逾期60天','逾期90天','逾期180天','180天+']:
            lb=QLabel(f'{label}: 0'); tl.addWidget(lb); self._ag_total_labels[label]=lb
        l.addWidget(self._ag_total)
        return tab

    def _refresh_aging(self):
        ptype='customer' if self._ag_type.currentText()=='应收账款' else 'supplier'
        try:
            data=self.service.aging_analysis(ptype)
            summary=self.service.get_aging_summary(ptype)
            self._ag_t.setRowCount(len(data))
            for i,r in enumerate(data):
                self._ag_t.setItem(i,0,QTableWidgetItem(r['partner_name']))
                self._ag_t.setItem(i,1,QTableWidgetItem(f"¥{r['not_due']:,.2f}"))
                self._ag_t.setItem(i,2,QTableWidgetItem(f"¥{r['within_30']:,.2f}"))
                self._ag_t.setItem(i,3,QTableWidgetItem(f"¥{r['within_60']:,.2f}"))
                self._ag_t.setItem(i,4,QTableWidgetItem(f"¥{r['within_90']:,.2f}"))
                self._ag_t.setItem(i,5,QTableWidgetItem(f"¥{r['within_180']:,.2f}"))
                self._ag_t.setItem(i,6,QTableWidgetItem(f"¥{r['over_180']:,.2f}"))
                total_item=QTableWidgetItem(f"¥{r['total_balance']:,.2f}")
                if r['total_balance']>0: total_item.setForeground(QColor('#EA4335'))
                self._ag_t.setItem(i,7,total_item)

            self._ag_sum.setText(f"{summary['partner_count']}家单位 | "
                f"余额合计 ¥{summary['total_balance']:,.2f}")
            self._ag_total_labels['单位数'].setText(f'单位数: {summary["partner_count"]}')
            self._ag_total_labels['余额合计'].setText(f'余额合计: ¥{summary["total_balance"]:,.2f}')
            self._ag_total_labels['未到期'].setText(f'未到期: ¥{summary["not_due"]:,.2f}')
            self._ag_total_labels['逾期30天'].setText(f'逾期30天: ¥{summary["within_30"]:,.2f}')
            self._ag_total_labels['逾期60天'].setText(f'逾期60天: ¥{summary["within_60"]:,.2f}')
            self._ag_total_labels['逾期90天'].setText(f'逾期90天: ¥{summary["within_90"]:,.2f}')
            self._ag_total_labels['逾期180天'].setText(f'逾期180天: ¥{summary["within_180"]:,.2f}')
            self._ag_total_labels['180天+'].setText(f'180天+: ¥{summary["over_180"]:,.2f}')
        except: pass

    # ── 公共 ──
    def _add_invoice(self,ptype):
        partners,_=self.service.list_partners(ptype=ptype)
        if not partners:
            QMessageBox.warning(self,'提示','请先新增往来单位'); return
        dlg=InvoiceDialog(self.service,ptype,partners,self)
        if dlg.exec(): self._refresh_ar() if ptype=='customer' else self._refresh_ap()

    def _do_payment(self,ptype):
        table=self._ar_t if ptype=='customer' else self._ap_t
        row=table.currentRow()
        if row<0: QMessageBox.warning(self,'提示','请选择一条记录'); return
        iid=table.item(row,0).data(Qt.ItemDataRole.UserRole)
        inv = None
        fn = self.service.get_ar_invoices if ptype=='customer' else self.service.get_ap_invoices
        rows,_ = fn()
        inv = next((r for r in rows if r['invoice_id']==iid), None)
        if not inv: return
        dlg=PaymentDialog(self.service,ptype,inv,self)
        if dlg.exec(): self._refresh_ar() if ptype=='customer' else self._refresh_ap()

    def on_activate(self,bid): self.refresh()
    def refresh(self):
        self._refresh_partner()
        self._refresh_ar()
        self._refresh_ap()