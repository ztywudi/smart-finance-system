"""
==============================================
 ui/pages/payroll.py - 工资管理页面（重构版）
==============================================
包含：工资项目管理、员工管理（导入导出）、工资计算（动态项目）、工资表（导入导出+工资条）
"""

import sys, os, csv
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QHeaderView,
    QTabWidget, QMessageBox, QAbstractItemView, QDialog, QFormLayout,
    QDoubleSpinBox, QGroupBox, QDialogButtonBox, QFileDialog,
    QSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QColor

from core.payroll_service import PayrollService


# ── 对话框 ──
class ItemDialog(QDialog):
    def __init__(self, service, parent=None, item_id=None):
        super().__init__(parent)
        self.service = service; self.item_id = item_id
        self.setWindowTitle('新增工资项目' if not item_id else '编辑工资项目')
        self.setMinimumWidth(350); self.setModal(True)
        layout = QVBoxLayout(self)
        form = QFormLayout()
        self._name = QLineEdit(); form.addRow('项目名称*:', self._name)
        self._type = QComboBox()
        self._type.addItems(['收入项(income)', '扣款项(deduction)', '参考项(reference)'])
        form.addRow('项目类型:', self._type)
        self._order = QSpinBox(); self._order.setRange(0, 999); form.addRow('排序:', self._order)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        if item_id: self._load(item_id)

    def _save(self):
        if not self._name.text().strip():
            QMessageBox.warning(self, '提示', '请输入项目名称'); return
        itype = self._type.currentText().split('(')[1].rstrip(')')
        try:
            if self.item_id:
                self.service.update_payroll_item(self.item_id,
                    item_name=self._name.text().strip(), item_type=itype,
                    calc_order=self._order.value())
            else:
                self.service.add_payroll_item(self._name.text().strip(), itype, self._order.value())
            self.accept()
        except Exception as e: QMessageBox.critical(self, '错误', str(e))

    def _load(self, iid):
        items = self.service.get_payroll_items(enabled_only=False)
        it = next((i for i in items if i['item_id'] == iid), None)
        if it:
            self._name.setText(it['item_name'])
            idx = self._type.findText('收入项') if it['item_type']=='income' else \
                  self._type.findText('扣款项') if it['item_type']=='deduction' else \
                  self._type.findText('参考项')
            if idx >= 0: self._type.setCurrentIndex(idx)
            self._order.setValue(it.get('calc_order', 0))

class EmpDialog(QDialog):
    def __init__(self, service, parent=None, emp_id=None):
        super().__init__(parent)
        self.service = service; self.emp_id = emp_id
        self.setWindowTitle('新增员工' if not emp_id else '编辑员工')
        self.setMinimumWidth(400); self.setModal(True)
        layout = QVBoxLayout(self); form = QFormLayout()
        self._code = QLineEdit(); form.addRow('编号*:', self._code)
        self._name = QLineEdit(); form.addRow('姓名*:', self._name)
        self._dept = QLineEdit(); form.addRow('部门:', self._dept)
        self._pos = QLineEdit(); form.addRow('职务:', self._pos)
        self._salary = QDoubleSpinBox(); self._salary.setRange(0,999999)
        self._salary.setDecimals(2); self._salary.setPrefix('¥ ')
        form.addRow('基本工资:', self._salary)
        self._bank = QLineEdit(); form.addRow('工资卡:', self._bank)
        layout.addLayout(form)
        btns = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(self._save); btns.rejected.connect(self.reject)
        layout.addWidget(btns)
        if emp_id: self._load(emp_id)
    def _save(self):
        if not self._code.text().strip() or not self._name.text().strip():
            QMessageBox.warning(self,'提示','请输入编号和姓名'); return
        try:
            if self.emp_id:
                self.service.update_employee(self.emp_id, emp_name=self._name.text().strip(),
                    department=self._dept.text().strip(), position=self._pos.text().strip(),
                    base_salary=self._salary.value(), bank_acct=self._bank.text().strip())
            else:
                self.service.add_employee(self._code.text().strip(), self._name.text().strip(),
                    department=self._dept.text().strip(), position=self._pos.text().strip(),
                    base_salary=self._salary.value(), bank_acct=self._bank.text().strip())
            self.accept()
        except Exception as e: QMessageBox.critical(self,'错误',str(e))
    def _load(self,iid):
        emps,_ = self.service.list_employees(status='')
        e = next((x for x in emps if x['emp_id']==iid),None)
        if e:
            self._code.setText(e['emp_code']); self._code.setEnabled(False)
            self._name.setText(e['emp_name']); self._dept.setText(e.get('department',''))
            self._pos.setText(e.get('position',''))
            self._salary.setValue(e.get('base_salary',0))
            self._bank.setText(e.get('bank_acct',''))


class PayrollPage(QWidget):
    def __init__(self, db_manager, tab='payroll'):
        super().__init__()
        self.db_manager = db_manager
        self.service = PayrollService(db_manager)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self); layout.setContentsMargins(0,0,0,0)
        self._tabs = QTabWidget()
        self._tabs.setStyleSheet("""
            QTabWidget::pane { border:none; background:#F5F6FA; }
            QTabBar::tab { padding:10px 20px; font-size:13px; border:none;
                          border-bottom:2px solid transparent; }
            QTabBar::tab:selected { color:#1A73E8; border-bottom:2px solid #1A73E8; font-weight:bold; }
        """)
        self._tabs.addTab(self._build_items_tab(), '⚙️ 工资项目')
        self._tabs.addTab(self._build_emp_tab(), '👤 员工管理')
        self._tabs.addTab(self._build_calc_tab(), '💰 工资计算')
        self._tabs.addTab(self._build_result_tab(), '📋 工资表')
        layout.addWidget(self._tabs)

    # ── 工资项目 ──
    def _build_items_tab(self):
        tab = QWidget(); layout = QVBoxLayout(tab); layout.setContentsMargins(16,16,16,16)
        tool = QHBoxLayout()
        tool.addWidget(QLabel('<b>⚙️ 自定义工资项目</b>')); tool.addStretch()
        btn = QPushButton('➕ 新增项目')
        btn.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;")
        btn.clicked.connect(self._add_item); tool.addWidget(btn)
        btn_e = QPushButton('✏️ 编辑'); btn_e.clicked.connect(self._edit_item); tool.addWidget(btn_e)
        btn_d = QPushButton('🗑️ 删除'); btn_d.clicked.connect(self._del_item); tool.addWidget(btn_d)
        btn_r = QPushButton('🔄 刷新'); btn_r.clicked.connect(self._refresh_items); tool.addWidget(btn_r)
        layout.addLayout(tool)
        self._item_table = QTableWidget(0,4)
        self._item_table.setHorizontalHeaderLabels(['项目名称','类型','排序','启用'])
        self._item_table.horizontalHeader().setStretchLastSection(True)
        self._item_table.setAlternatingRowColors(True)
        self._item_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self._item_table,1)
        return tab

    def _refresh_items(self):
        items = self.service.get_payroll_items(enabled_only=False)
        tmap = {'income':'收入项','deduction':'扣款项','reference':'参考项'}
        self._item_table.setRowCount(len(items))
        for i,it in enumerate(items):
            self._item_table.setItem(i,0,QTableWidgetItem(it['item_name']))
            self._item_table.setItem(i,1,QTableWidgetItem(tmap.get(it['item_type'],it['item_type'])))
            self._item_table.setItem(i,2,QTableWidgetItem(str(it.get('calc_order',0))))
            self._item_table.setItem(i,3,QTableWidgetItem('✅' if it.get('enabled') else '❌'))
            self._item_table.item(i,0).setData(Qt.ItemDataRole.UserRole,it['item_id'])
    def _add_item(self):
        dlg = ItemDialog(self.service,self)
        if dlg.exec(): self._refresh_items()
    def _edit_item(self):
        r=self._item_table.currentRow()
        if r<0: QMessageBox.warning(self,'提示','请选择项目'); return
        iid=self._item_table.item(r,0).data(Qt.ItemDataRole.UserRole)
        dlg=ItemDialog(self.service,self,iid)
        if dlg.exec(): self._refresh_items()
    def _del_item(self):
        r=self._item_table.currentRow()
        if r<0: return
        iid=self._item_table.item(r,0).data(Qt.ItemDataRole.UserRole)
        name=self._item_table.item(r,0).text()
        reply=QMessageBox.question(self,'确认',f'确定删除项目"{name}"？',
            QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)
        if reply==QMessageBox.StandardButton.Yes:
            self.service.delete_payroll_item(iid); self._refresh_items()

    # ── 员工管理 ──
    def _build_emp_tab(self):
        tab=QWidget(); layout=QVBoxLayout(tab); layout.setContentsMargins(16,16,16,16)
        tool=QHBoxLayout()
        tool.addWidget(QLabel('<b>👤 员工列表</b>')); tool.addStretch()
        btn=QPushButton('➕ 新增员工')
        btn.setStyleSheet("background:#34A853;color:white;padding:6px 16px;border-radius:4px;")
        btn.clicked.connect(self._add_emp); tool.addWidget(btn)
        btn_e=QPushButton('✏️ 编辑'); btn_e.clicked.connect(self._edit_emp); tool.addWidget(btn_e)
        btn_ex=QPushButton('📤 导出CSV'); btn_ex.clicked.connect(self._export_emp); tool.addWidget(btn_ex)
        btn_im=QPushButton('📥 导入CSV'); btn_im.clicked.connect(self._import_emp); tool.addWidget(btn_im)
        btn_r=QPushButton('🔄 刷新'); btn_r.clicked.connect(self._refresh_emp); tool.addWidget(btn_r)
        layout.addLayout(tool)
        self._emp_table=QTableWidget(0,7)
        self._emp_table.setHorizontalHeaderLabels(['编号','姓名','部门','职务','基本工资','状态','银行卡'])
        self._emp_table.horizontalHeader().setStretchLastSection(True)
        self._emp_table.setAlternatingRowColors(True); self._emp_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._emp_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        layout.addWidget(self._emp_table,1)
        return tab

    def _refresh_emp(self):
        try:
            rows,total=self.service.list_employees(status='')
            self._emp_table.setRowCount(len(rows))
            for i,r in enumerate(rows):
                self._emp_table.setItem(i,0,QTableWidgetItem(r.get('emp_code','')))
                self._emp_table.setItem(i,1,QTableWidgetItem(r.get('emp_name','')))
                self._emp_table.setItem(i,2,QTableWidgetItem(r.get('department','')))
                self._emp_table.setItem(i,3,QTableWidgetItem(r.get('position','')))
                self._emp_table.setItem(i,4,QTableWidgetItem(f"¥{r.get('base_salary',0):,.2f}"))
                self._emp_table.setItem(i,5,QTableWidgetItem(r.get('status','')))
                self._emp_table.setItem(i,6,QTableWidgetItem(r.get('bank_acct','')))
                self._emp_table.item(i,0).setData(Qt.ItemDataRole.UserRole,r['emp_id'])
        except: pass

    def _add_emp(self):
        dlg=EmpDialog(self.service,self)
        if dlg.exec(): self._refresh_emp()
    def _edit_emp(self):
        r=self._emp_table.currentRow()
        if r<0: QMessageBox.warning(self,'提示','请选择员工'); return
        eid=self._emp_table.item(r,0).data(Qt.ItemDataRole.UserRole)
        dlg=EmpDialog(self.service,self,eid)
        if dlg.exec(): self._refresh_emp()
    def _export_emp(self):
        path,_=QFileDialog.getSaveFileName(self,'导出员工','employees.csv','CSV(*.csv)')
        if path:
            n=self.service.export_employees_csv(path)
            QMessageBox.information(self,'成功',f'已导出 {n} 名员工')
    def _import_emp(self):
        path,_=QFileDialog.getOpenFileName(self,'导入员工','','CSV(*.csv)')
        if path:
            ok,fail=self.service.import_employees_csv(path)
            QMessageBox.information(self,'完成',f'导入成功 {ok} 条，失败 {fail} 条')
            self._refresh_emp()

    # ── 工资计算 ──
    def _build_calc_tab(self):
        tab=QWidget(); layout=QVBoxLayout(tab); layout.setContentsMargins(16,16,16,16)
        tool=QHBoxLayout()
        tool.addWidget(QLabel('<b>💰 工资计算（动态项目）</b>')); tool.addStretch()
        tool.addWidget(QLabel('期间:'))
        self._c_period=QComboBox()
        for y in range(2024,2031):
            for m in range(1,13): self._c_period.addItem(f'{y}-{m:02d}')
        now=datetime.now(); idx=self._c_period.findText(f'{now.year}-{now.month:02d}')
        if idx>=0: self._c_period.setCurrentIndex(idx)
        tool.addWidget(self._c_period)
        btn_l=QPushButton('📥 载入员工')
        btn_l.setStyleSheet("background:#9C27B0;color:white;padding:6px 16px;border-radius:4px;")
        btn_l.clicked.connect(self._load_calc_emps); tool.addWidget(btn_l)
        btn_c=QPushButton('🧮 计算全部')
        btn_c.setStyleSheet("background:#1A73E8;color:white;padding:6px 16px;border-radius:4px;font-weight:bold;")
        btn_c.clicked.connect(self._batch_calc); tool.addWidget(btn_c)
        layout.addLayout(tool)

        # 动态标题
        self._calc_table=QTableWidget(0,5)
        self._calc_table.setHorizontalHeaderLabels(['编号','姓名','部门','项目值','操作'])
        self._calc_table.horizontalHeader().setStretchLastSection(True)
        self._calc_table.setAlternatingRowColors(True)
        layout.addWidget(self._calc_table,1)
        return tab

    def _load_calc_emps(self):
        items=self.service.get_payroll_items()
        income_items=[i for i in items if i['item_type']=='income']
        deduct_items=[i for i in items if i['item_type']=='deduction']
        # 动态表头
        cols=['编号','姓名','部门']
        for i in income_items: cols.append(i['item_name'])
        for i in deduct_items:
            if i['item_name'] not in ('个税','社保个人部分','公积金个人部分'):
                cols.append(i['item_name'])
        cols+=['操作']
        self._calc_table.setColumnCount(len(cols))
        self._calc_table.setHorizontalHeaderLabels(cols)
        self._calc_header=cols

        emps,_=self.service.list_employees()
        self._calc_table.setRowCount(len(emps))
        for ri,e in enumerate(emps):
            self._calc_table.setItem(ri,0,QTableWidgetItem(e['emp_code']))
            self._calc_table.setItem(ri,1,QTableWidgetItem(e['emp_name']))
            self._calc_table.setItem(ri,2,QTableWidgetItem(e.get('department','')))
            col=3
            for ii in income_items:
                it=QTableWidgetItem('0.00')
                self._calc_table.setItem(ri,col,it)
                self._calc_table.item(ri,col).setData(Qt.ItemDataRole.UserRole+1,ii['item_id'])
                col+=1
            for di in deduct_items:
                if di['item_name'] in ('个税','社保个人部分','公积金个人部分'): continue
                it=QTableWidgetItem('0.00')
                self._calc_table.setItem(ri,col,it)
                self._calc_table.item(ri,col).setData(Qt.ItemDataRole.UserRole+1,di['item_id'])
                col+=1
            # 操作列
            btn=QPushButton('✏️ 编辑')
            btn.clicked.connect(lambda _,r=ri: self._edit_calc_row(r))
            self._calc_table.setCellWidget(ri,col,btn)
            self._calc_table.item(ri,0).setData(Qt.ItemDataRole.UserRole,e['emp_id'])

    def _edit_calc_row(self, row):
        """编辑单行各项金额"""
        items=self.service.get_payroll_items()
        inames={i['item_id']:i['item_name'] for i in items}
        emp_name=self._calc_table.item(row,1).text() if self._calc_table.item(row,1) else ''
        dlg=QDialog(self); dlg.setWindowTitle(f'工资录入 - {emp_name}')
        dlg.setMinimumWidth(350); dlg.setModal(True)
        layout=QVBoxLayout(dlg); form=QFormLayout()
        widgets={}
        for c in range(3,self._calc_table.columnCount()-1):
            it=self._calc_table.item(row,c)
            if it:
                iid=it.data(Qt.ItemDataRole.UserRole+1)
                name=inames.get(iid,'')
                w=QDoubleSpinBox(); w.setRange(0,999999); w.setDecimals(2)
                w.setPrefix('¥ '); w.setSingleStep(500)
                try: w.setValue(float(it.text().replace(',','') or '0'))
                except: pass
                form.addRow(f'{name}:',w)
                widgets[iid]=w
        layout.addLayout(form)
        btns=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        btns.accepted.connect(dlg.accept); btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        if dlg.exec():
            for c in range(3,self._calc_table.columnCount()-1):
                it=self._calc_table.item(row,c)
                if it:
                    iid=it.data(Qt.ItemDataRole.UserRole+1)
                    w=widgets.get(iid)
                    if w: it.setText(f'{w.value():,.2f}')

    def _batch_calc(self):
        period=self._c_period.currentText()
        items=self.service.get_payroll_items()
        # 收集收入/扣款项目ID
        income_ids=[i['item_id'] for i in items if i['item_type']=='income']
        deduct_ids=[i['item_id'] for i in items if i['item_type']=='deduction'
                    and i['item_name'] not in ('个税','社保个人部分','公积金个人部分')]
        emp_data=[]
        for r in range(self._calc_table.rowCount()):
            i0=self._calc_table.item(r,0)
            if not i0 or not i0.data(Qt.ItemDataRole.UserRole): continue
            eid=i0.data(Qt.ItemDataRole.UserRole)
            item_values={}
            col=3
            for iid in income_ids:
                it=self._calc_table.item(r,col)
                if it:
                    try: item_values[iid]=float(it.text().replace(',','') or '0')
                    except: pass
                col+=1
            for iid in deduct_ids:
                it=self._calc_table.item(r,col)
                if it:
                    try: item_values[iid]=float(it.text().replace(',','') or '0')
                    except: pass
                col+=1
            emp_data.append({'emp_id':eid,'item_values':item_values})
        try:
            count=self.service.batch_calc_and_save(period,emp_data)
            QMessageBox.information(self,'成功',f'已计算并保存 {count} 位员工工资')
            self._load_result()
            self._tabs.setCurrentIndex(3)
        except Exception as e: QMessageBox.critical(self,'错误',str(e))

    # ── 工资表 ──
    def _build_result_tab(self):
        tab=QWidget(); layout=QVBoxLayout(tab); layout.setContentsMargins(16,16,16,16)
        tool=QHBoxLayout()
        tool.addWidget(QLabel('<b>📋 工资表</b>')); tool.addStretch()
        tool.addWidget(QLabel('期间:'))
        self._r_period=QComboBox()
        for y in range(2024,2031):
            for m in range(1,13): self._r_period.addItem(f'{y}-{m:02d}')
        now=datetime.now(); idx=self._r_period.findText(f'{now.year}-{now.month:02d}')
        if idx>=0: self._r_period.setCurrentIndex(idx)
        tool.addWidget(self._r_period)
        btn_q=QPushButton('🔍 查询'); btn_q.clicked.connect(self._load_result); tool.addWidget(btn_q)
        btn_ex=QPushButton('📤 导出CSV')
        btn_ex.setStyleSheet("background:#FF9800;color:white;padding:6px 12px;border-radius:4px;")
        btn_ex.clicked.connect(self._export_payroll); tool.addWidget(btn_ex)
        btn_im=QPushButton('📥 导入CSV')
        btn_im.setStyleSheet("background:#9C27B0;color:white;padding:6px 12px;border-radius:4px;")
        btn_im.clicked.connect(self._import_payroll); tool.addWidget(btn_im)
        btn_slip=QPushButton('📄 导出工资条')
        btn_slip.setStyleSheet("background:#00BCD4;color:white;padding:6px 12px;border-radius:4px;")
        btn_slip.clicked.connect(self._export_slips); tool.addWidget(btn_slip)
        btn_gen=QPushButton('📝 生成凭证')
        btn_gen.setStyleSheet("background:#34A853;color:white;padding:6px 12px;border-radius:4px;font-weight:bold;")
        btn_gen.clicked.connect(self._gen_voucher); tool.addWidget(btn_gen)
        self._sum_label=QLabel('')
        self._sum_label.setStyleSheet("padding:6px 12px;background:#E8F5E9;border-radius:4px;font-weight:bold;")
        tool.addWidget(self._sum_label)
        layout.addLayout(tool)

        self._r_table=QTableWidget(0,5)
        self._r_table.setHorizontalHeaderLabels(['编号','姓名','部门','项目明细','实发工资'])
        self._r_table.horizontalHeader().setStretchLastSection(True)
        self._r_table.setAlternatingRowColors(True)
        self._r_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self._r_table,1)
        return tab

    def _load_result(self):
        period=self._r_period.currentText()
        try:
            rows,summary=self.service.get_payroll(period)
            self._r_table.setRowCount(len(rows))
            for i,r in enumerate(rows):
                self._r_table.setItem(i,0,QTableWidgetItem(r.get('emp_code','')))
                self._r_table.setItem(i,1,QTableWidgetItem(r.get('emp_name','')))
                self._r_table.setItem(i,2,QTableWidgetItem(r.get('department','')))

                # 动态项目明细
                dets=r.get('items',{})
                detail_lines=[]
                income_total=0; deduct_total=0
                for name,amt in dets.items():
                    if name in ('应发工资','实发工资'): continue
                    if amt>0:
                        detail_lines.append(f'{name} ¥{amt:,.2f}')
                self._r_table.setItem(i,3,QTableWidgetItem(' | '.join(detail_lines)))

                net_item=QTableWidgetItem(f"¥{r.get('net_pay',0):,.2f}")
                net_item.setForeground(QColor('#34A853'))
                self._r_table.setItem(i,4,net_item)
                self._r_table.item(i,0).setData(Qt.ItemDataRole.UserRole,r['record_id'])
            if summary:
                self._sum_label.setText(
                    f'{summary["emp_count"]}人 | 应发¥{summary["total_gross"]:,.2f} | 实发¥{summary["total_net"]:,.2f}')
        except: pass

    def _export_payroll(self):
        path,_=QFileDialog.getSaveFileName(self,'导出工资表','payroll.csv','CSV(*.csv)')
        if path:
            n=self.service.export_payroll_csv(self._r_period.currentText(),path)
            QMessageBox.information(self,'成功',f'已导出 {n} 条工资记录')
    def _import_payroll(self):
        path,_=QFileDialog.getOpenFileName(self,'导入工资数据','','CSV(*.csv)')
        if path:
            ok,fail=self.service.import_payroll_csv(self._r_period.currentText(),path)
            QMessageBox.information(self,'完成',f'导入成功 {ok} 条，失败 {fail} 条')
            self._load_result()
    def _export_slips(self):
        dir_path=QFileDialog.getExistingDirectory(self,'选择导出目录')
        if dir_path:
            n=self.service.export_pay_slips(self._r_period.currentText(),dir_path)
            QMessageBox.information(self,'成功',f'已导出 {n} 位员工工资条')
    def _gen_voucher(self):
        try:
            vid=self.service.generate_voucher(self._r_period.currentText())
            QMessageBox.information(self,'成功',f'工资计提凭证已生成！ID: {vid}')
        except Exception as e: QMessageBox.critical(self,'错误',str(e))

    def on_activate(self,book_id): self.refresh()
    def refresh(self):
        self._refresh_items()
        self._refresh_emp()