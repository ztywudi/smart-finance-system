"""
==========================================
 core/payroll_service.py - 工资管理服务（重构版）
==========================================
功能：
  - 自定义工资项目（收入/扣款/参考项）自由增删
  - 员工管理+动态工资计算
  - 个税计算（累计预扣法）
  - Excel/CSV导入导出
  - 工资条生成
"""

import sys, os, csv, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional, Dict, Tuple


class PayrollService:
    """工资管理服务"""

    TAX_TABLE = [
        (36000, 0.03, 0), (144000, 0.10, 2520), (300000, 0.20, 16920),
        (420000, 0.25, 31920), (660000, 0.30, 52920), (960000, 0.35, 85920),
        (float('inf'), 0.45, 181920),
    ]

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ═══════════════════════════════════════════
    #  自定义工资项目管理
    # ═══════════════════════════════════════════
    def _init_default_items(self):
        """初始化默认工资项目（首次使用时调用）"""
        conn = self.db_manager.get_current_conn()
        cursor = conn.execute("SELECT COUNT(*) FROM payroll_items")
        if cursor.fetchone()[0] > 0:
            return
        now = datetime.now().isoformat()
        defaults = [
            ('基本工资', 'income', 1),
            ('加班费', 'income', 2),
            ('奖金', 'income', 3),
            ('补贴', 'income', 4),
            ('社保个人部分', 'deduction', 10),
            ('公积金个人部分', 'deduction', 11),
            ('个税', 'deduction', 12),
            ('其他扣款', 'deduction', 13),
            ('应发工资', 'reference', 50),  # 自动计算
            ('实发工资', 'reference', 51),
        ]
        for name, itype, order in defaults:
            conn.execute('''
                INSERT INTO payroll_items (item_name, item_type, calc_order, enabled, created_at)
                VALUES (?, ?, ?, 1, ?)
            ''', (name, itype, order, now))
        conn.commit()

    def get_payroll_items(self, enabled_only=True) -> List[Dict]:
        """获取工资项目列表"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return []
        self._init_default_items()
        where = "WHERE enabled=1" if enabled_only else ""
        cursor = conn.execute(
            f"SELECT * FROM payroll_items {where} ORDER BY calc_order")
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def add_payroll_item(self, name: str, item_type: str, order: int = 0) -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cursor = conn.execute('''
            INSERT INTO payroll_items (item_name, item_type, calc_order, enabled, created_at)
            VALUES (?, ?, ?, 1, ?)
        ''', (name, item_type, order, now))
        conn.commit()
        return cursor.lastrowid

    def update_payroll_item(self, item_id: int, **kwargs) -> bool:
        conn = self.db_manager.get_current_conn()
        allowed = ['item_name', 'item_type', 'calc_order', 'enabled']
        updates, values = [], []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k}=?"); values.append(v)
        if not updates:
            return False
        values.append(item_id)
        conn.execute(
            f"UPDATE payroll_items SET {','.join(updates)} WHERE item_id=?", values)
        conn.commit()
        return True

    def delete_payroll_item(self, item_id: int) -> bool:
        conn = self.db_manager.get_current_conn()
        conn.execute("DELETE FROM payroll_items WHERE item_id=?", (item_id,))
        conn.execute("DELETE FROM payroll_details WHERE item_id=?", (item_id,))
        conn.commit()
        return True

    # ═══════════════════════════════════════════
    #  员工管理（增减导出）
    # ═══════════════════════════════════════════
    def add_employee(self, emp_code: str, emp_name: str, **kw) -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cursor = conn.execute('''
            INSERT INTO employees (emp_code, emp_name, department, position,
                base_salary, hire_date, bank_acct, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (emp_code, emp_name, kw.get('department', ''), kw.get('position', ''),
              kw.get('base_salary', 0), kw.get('hire_date', ''), kw.get('bank_acct', ''), now))
        conn.commit()
        return cursor.lastrowid

    def update_employee(self, emp_id, **kw) -> bool:
        conn = self.db_manager.get_current_conn()
        allowed = ['emp_name', 'department', 'position', 'base_salary', 'status', 'bank_acct']
        up, vals = [], []
        for k, v in kw.items():
            if k in allowed:
                up.append(f"{k}=?"); vals.append(v)
        if not up: return False
        vals.append(emp_id)
        conn.execute(f"UPDATE employees SET {','.join(up)} WHERE emp_id=?", vals)
        conn.commit()
        return True

    def list_employees(self, status='active', dept='',
                       page=1, page_size=200) -> Tuple[List[Dict], int]:
        conn = self.db_manager.get_current_conn()
        if not conn: return [], 0
        cond, par = [], []
        if status: cond.append("status=?"); par.append(status)
        if dept: cond.append("department=?"); par.append(dept)
        where = " AND ".join(cond) if cond else "1=1"
        cur = conn.execute(f"SELECT COUNT(*) FROM employees WHERE {where}", par)
        total = cur.fetchone()[0]
        off = (page - 1) * page_size
        cur = conn.execute(
            f"SELECT * FROM employees WHERE {where} ORDER BY emp_code LIMIT ? OFFSET ?",
            par + [page_size, off])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()], total

    def export_employees_csv(self, filepath: str):
        """导出员工到CSV"""
        emps, _ = self.list_employees(status='')
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.DictWriter(f, fieldnames=['emp_code', 'emp_name', 'department',
                                               'position', 'base_salary', 'hire_date', 'bank_acct', 'status'])
            w.writeheader()
            for e in emps:
                w.writerow({k: e.get(k, '') for k in w.fieldnames})
        return len(emps)

    def import_employees_csv(self, filepath: str) -> Tuple[int, int]:
        """从CSV导入员工 返回(成功, 失败)"""
        success = fail = 0
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.add_employee(
                        row['emp_code'], row['emp_name'],
                        department=row.get('department', ''),
                        position=row.get('position', ''),
                        base_salary=float(row.get('base_salary', 0) or 0),
                        hire_date=row.get('hire_date', ''),
                        bank_acct=row.get('bank_acct', ''))
                    success += 1
                except Exception:
                    fail += 1
        return success, fail

    # ═══════════════════════════════════════════
    #  工资计算（动态项目）
    # ═══════════════════════════════════════════
    def calc_tax(self, year_income: float, year_deduct: float = 60000) -> float:
        taxable = max(0, year_income - year_deduct)
        for limit, rate, quick in self.TAX_TABLE:
            if taxable <= limit:
                return max(0, taxable * rate - quick)
        return 0.0

    def calc_payroll(self, emp: Dict, period: str,
                     item_values: Dict[int, float] = None) -> Dict:
        """
        计算单员工工资
        item_values: {item_id: amount, ...} 用户输入的工资项目值
        返回：{item_id: amount, ...} 含自动计算项
        """
        items = self.get_payroll_items()
        items_map = {i['item_id']: i for i in items}
        results = {}

        # 收入项：取用户输入值
        total_income = 0.0
        for it in items:
            if it['item_type'] == 'income':
                val = (item_values or {}).get(it['item_id'], 0)
                results[it['item_id']] = val
                total_income += val

        # 自动社保/公积金（基于基本工资）
        soc_ins_item = next((i for i in items if i['item_name'] == '社保个人部分'), None)
        fund_item = next((i for i in items if i['item_name'] == '公积金个人部分'), None)
        base = emp.get('base_salary', 0)

        if soc_ins_item and soc_ins_item['item_id'] not in (item_values or {}):
            amt = round(base * 0.105, 2)
            results[soc_ins_item['item_id']] = amt
        elif soc_ins_item:
            results[soc_ins_item['item_id']] = (item_values or {}).get(soc_ins_item['item_id'], 0)

        if fund_item and fund_item['item_id'] not in (item_values or {}):
            amt = round(base * 0.07, 2)
            results[fund_item['item_id']] = amt
        elif fund_item:
            results[fund_item['item_id']] = (item_values or {}).get(fund_item['item_id'], 0)

        # 扣款项
        total_deduct = 0.0
        for it in items:
            if it['item_type'] == 'deduction' and it['item_name'] not in ('个税', '社保个人部分', '公积金个人部分'):
                val = (item_values or {}).get(it['item_id'], 0)
                results[it['item_id']] = val
                total_deduct += val

        # 社保公积金
        if soc_ins_item:
            total_deduct += results.get(soc_ins_item['item_id'], 0)
        if fund_item:
            total_deduct += results.get(fund_item['item_id'], 0)

        # 个税
        tax_item = next((i for i in items if i['item_name'] == '个税'), None)
        if tax_item:
            month = int(period.split('-')[1])
            year_income = total_income * (month / max(month, 1))  # 简算
            year_deduct = 5000 * month
            tax = round(self.calc_tax(year_income, year_deduct) / max(month, 1), 2)
            results[tax_item['item_id']] = tax
            total_deduct += tax

        # 其他扣款
        for it in items:
            if it['item_type'] == 'deduction' and it['item_id'] not in results:
                val = (item_values or {}).get(it['item_id'], 0)
                results[it['item_id']] = val
                total_deduct += val

        # 参考项
        ref_item = next((i for i in items if i['item_name'] == '应发工资'), None)
        if ref_item:
            results[ref_item['item_id']] = round(total_income, 2)
        net_item = next((i for i in items if i['item_name'] == '实发工资'), None)
        if net_item:
            results[net_item['item_id']] = round(total_income - total_deduct, 2)

        return results

    def batch_calc_and_save(self, period: str,
                            emp_values: List[Dict]) -> int:
        """
        批量计算并保存工资
        emp_values: [{emp_id, item_values: {item_id: amount}}, ...]
        """
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        count = 0

        for data in emp_values:
            emp_id = data['emp_id']
            cur = conn.execute("SELECT * FROM employees WHERE emp_id=?", (emp_id,))
            cols = [d[0] for d in cur.description]
            emp = dict(zip(cols, cur.fetchone()))
            if not emp: continue

            results = self.calc_payroll(emp, period, data.get('item_values', {}))

            # 汇总
            items = self.get_payroll_items()
            names = {i['item_id']: i['item_name'] for i in items}
            types = {i['item_id']: i['item_type'] for i in items}
            total_income = sum(v for iid, v in results.items() if types.get(iid) == 'income')
            total_deduct = sum(v for iid, v in results.items() if types.get(iid) == 'deduction')
            gross = results.get(
                next((i['item_id'] for i in items if i['item_name']=='应发工资'), 0), total_income)
            net = results.get(
                next((i['item_id'] for i in items if i['item_name']=='实发工资'), 0), total_income - total_deduct)

            det_json = json.dumps(results, ensure_ascii=False)

            cur = conn.execute('''
                INSERT OR REPLACE INTO payroll_records
                (period, emp_id, base_salary, gross_pay, net_pay, status, details_json, created_at)
                VALUES (?, ?, ?, ?, ?, 'draft', ?, ?)
            ''', (period, emp_id, emp.get('base_salary', 0), round(gross, 2),
                  round(net, 2), det_json, now))
            record_id = cur.lastrowid

            # 保存明细到payroll_details
            conn.execute("DELETE FROM payroll_details WHERE record_id=?", (record_id,))
            for iid, amt in results.items():
                conn.execute('''
                    INSERT INTO payroll_details (record_id, item_id, amount)
                    VALUES (?, ?, ?)
                ''', (record_id, iid, round(amt, 2)))
            count += 1

        conn.commit()
        return count

    def get_payroll(self, period: str) -> Tuple[List[Dict], Dict]:
        """获取工资表"""
        conn = self.db_manager.get_current_conn()
        if not conn: return [], {}

        cur = conn.execute('''
            SELECT p.*, e.emp_code, e.emp_name, e.department, e.position
            FROM payroll_records p
            LEFT JOIN employees e ON p.emp_id = e.emp_id
            WHERE p.period=? ORDER BY e.emp_code
        ''', (period,))
        cols = [d[0] for d in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        if not rows: return [], {}

        items = self.get_payroll_items()
        inames = {i['item_id']: i['item_name'] for i in items}

        for r in rows:
            det = json.loads(r.get('details_json') or '{}')
            r['items'] = {inames.get(int(k), k): v for k, v in det.items()}

        summary = {
            'emp_count': len(rows),
            'total_gross': sum(r['gross_pay'] for r in rows),
            'total_net': sum(r['net_pay'] for r in rows),
        }
        return rows, summary

    # ═══════════════════════════════════════════
    #  导入导出
    # ═══════════════════════════════════════════
    def export_payroll_csv(self, period: str, filepath: str):
        """导出工资表到CSV"""
        rows, summary = self.get_payroll(period)
        if not rows: raise ValueError(f"期间 {period} 没有工资数据")
        items = self.get_payroll_items()
        inames = {i['item_id']: i['item_name'] for i in items}

        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            fields = ['emp_code', 'emp_name', 'department']
            for i in items:
                fields.append(i['item_name'])
            fields += ['gross_pay', 'net_pay']

            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in rows:
                row = {'emp_code': r.get('emp_code', ''),
                       'emp_name': r.get('emp_name', ''),
                       'department': r.get('department', '')}
                det = json.loads(r.get('details_json') or '{}')
                for i in items:
                    row[i['item_name']] = det.get(str(i['item_id']),
                                          det.get(i['item_id'], ''))
                row['gross_pay'] = r['gross_pay']
                row['net_pay'] = r['net_pay']
                w.writerow(row)
        return len(rows)

    def import_payroll_csv(self, period: str, filepath: str) -> Tuple[int, int]:
        """从CSV导入工资数据"""
        import csv as csvmod
        items = self.get_payroll_items()
        name_to_id = {i['item_name']: i['item_id'] for i in items}
        success = fail = 0

        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    cur = self.db_manager.get_current_conn().execute(
                        "SELECT emp_id FROM employees WHERE emp_code=?", (row['emp_code'],))
                    r = cur.fetchone()
                    if not r: fail += 1; continue
                    emp_id = r[0]
                    item_values = {}
                    for name, iid in name_to_id.items():
                        if name in row and row[name].strip():
                            item_values[iid] = float(row[name].replace(',', ''))
                    self.batch_calc_and_save(period, [{'emp_id': emp_id, 'item_values': item_values}])
                    success += 1
                except Exception:
                    fail += 1
        return success, fail

    # ═══════════════════════════════════════════
    #  工资条
    # ═══════════════════════════════════════════
    def get_pay_slip(self, record_id: int) -> Dict:
        """生成单员工工资条"""
        conn = self.db_manager.get_current_conn()
        cur = conn.execute('''
            SELECT p.*, e.emp_code, e.emp_name, e.department, e.position
            FROM payroll_records p
            LEFT JOIN employees e ON p.emp_id = e.emp_id
            WHERE p.record_id=?
        ''', (record_id,))
        cols = [d[0] for d in cur.description]
        row = dict(zip(cols, cur.fetchone()))
        if not row: return {}

        items = self.get_payroll_items()
        inames = {i['item_id']: i['item_name'] for i in items}
        itypes = {i['item_id']: i['item_type'] for i in items}
        det = json.loads(row.get('details_json') or '{}')

        slip = {
            'emp_name': row['emp_name'], 'emp_code': row['emp_code'],
            'department': row.get('department', ''),
            'period': row['period'],
            'gross_pay': row['gross_pay'], 'net_pay': row['net_pay'],
            'income_items': [], 'deduction_items': [], 'reference_items': [],
        }
        for iid_str, amt in det.items():
            iid = int(iid_str) if iid_str.isdigit() else iid_str
            name = inames.get(iid, f'项目{iid}')
            itype = itypes.get(iid, 'income')
            entry = {'name': name, 'amount': amt}
            if itype == 'income':
                slip['income_items'].append(entry)
            elif itype == 'deduction':
                slip['deduction_items'].append(entry)
            else:
                slip['reference_items'].append(entry)
        return slip

    def export_pay_slips(self, period: str, output_dir: str) -> int:
        """导出全部员工工资条到CSV（每行一条）"""
        rows, _ = self.get_payroll(period)
        if not rows: raise ValueError(f"期间 {period} 没有工资数据")
        items = self.get_payroll_items()
        inames = {i['item_id']: i['item_name'] for i in items}
        itypes = {i['item_id']: i['item_type'] for i in items}

        with open(os.path.join(output_dir, f'工资条_{period}.csv'),
                  'w', newline='', encoding='utf-8-sig') as f:
            fields = ['姓名', '部门', '项目', '金额', '类型']
            w = csv.writer(f)
            w.writerow(fields)
            for r in rows:
                det = json.loads(r.get('details_json') or '{}')
                w.writerow([r['emp_name'], r.get('department', ''),
                           f'【应发】{r["gross_pay"]}', '收入'])
                for iid_str, amt in sorted(det.items()):
                    iid = int(iid_str)
                    name = inames.get(iid, f'项目{iid}')
                    itype = itypes.get(iid, '')
                    tname = {'income': '收入', 'deduction': '扣款', 'reference': '参考'}.get(itype, '')
                    w.writerow([r['emp_name'], r.get('department', ''),
                               f'{name}  ¥{amt:,.2f}', tname])
                w.writerow([r['emp_name'], r.get('department', ''),
                           f'【实发】{r["net_pay"]}', '实发'])
                w.writerow([])
        return len(rows)

    # ═══════════════════════════════════════════
    #  凭证
    # ═══════════════════════════════════════════
    def generate_voucher(self, period: str) -> int:
        from core.voucher_service import VoucherService
        rows, summary = self.get_payroll(period)
        if not rows: raise ValueError(f"期间 {period} 没有工资数据")
        vs = VoucherService(self.db_manager)
        total = summary['total_gross']
        vid = vs.create_voucher(period, datetime.now().strftime('%Y-%m-%d'), '记', [
            {'summary': f'计提{period}工资', 'acct_code': '660201',
             'debit_amount': total, 'credit_amount': 0},
            {'summary': f'计提{period}工资', 'acct_code': '221101',
             'debit_amount': 0, 'credit_amount': total},
        ], remark=f'自动生成：计提{period}工资')
        return vid