"""
==========================================
 core/arap_service.py - 应收应付服务
==========================================
功能：
  - 客户/供应商管理
  - 应收/应付单据管理（发票、收款、付款）
  - 账龄分析
  - 往来对账
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from typing import List, Dict, Tuple


class ArapService:
    """应收应付服务"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ────────────────────────────────
    #  客户/供应商管理
    # ────────────────────────────────
    def add_partner(self, code: str, name: str, ptype: str,
                    contact='', phone='', address='', bank='',
                    credit_limit=0) -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cur = conn.execute('''
            INSERT INTO ar_ap_partners
            (partner_code, partner_name, partner_type, contact, phone,
             address, bank_acct, credit_limit, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?)
        ''', (code, name, ptype, contact, phone, address, bank, credit_limit, now))
        conn.commit()
        return cur.lastrowid

    def update_partner(self, pid, **kw) -> bool:
        conn = self.db_manager.get_current_conn()
        allowed = ['partner_name', 'contact', 'phone', 'address', 'bank_acct',
                   'credit_limit', 'status']
        up, vals = [], []
        for k, v in kw.items():
            if k in allowed: up.append(f"{k}=?"); vals.append(v)
        if not up: return False
        vals.append(pid)
        conn.execute(f"UPDATE ar_ap_partners SET {','.join(up)} WHERE partner_id=?", vals)
        conn.commit()
        return True

    def list_partners(self, ptype='', status='active', keyword='',
                      page=1, page_size=100) -> Tuple[List[Dict], int]:
        conn = self.db_manager.get_current_conn()
        if not conn: return [], 0
        cond, par = [], []
        if ptype: cond.append("partner_type=?"); par.append(ptype)
        if status: cond.append("status=?"); par.append(status)
        if keyword:
            cond.append("(partner_code LIKE ? OR partner_name LIKE ? OR contact LIKE ?)")
            kw = f'%{keyword}%'; par.extend([kw, kw, kw])
        where = " AND ".join(cond) if cond else "1=1"
        cur = conn.execute(f"SELECT COUNT(*) FROM ar_ap_partners WHERE {where}", par)
        total = cur.fetchone()[0]
        off = (page - 1) * page_size
        cur = conn.execute(
            f"SELECT * FROM ar_ap_partners WHERE {where} ORDER BY partner_code LIMIT ? OFFSET ?",
            par + [page_size, off])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()], total

    # ────────────────────────────────
    #  应收管理
    # ────────────────────────────────
    def add_ar_invoice(self, doc_no: str, partner_id: int, doc_date: str,
                       due_date: str, amount: float, summary='') -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cur = conn.execute('''
            INSERT INTO ar_invoices (doc_no, partner_id, doc_date, due_date,
                amount, paid_amount, balance, summary, status, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, 'unpaid', ?)
        ''', (doc_no, partner_id, doc_date, due_date, amount, amount, summary, now))
        conn.commit()
        self._update_partner_balance(partner_id)
        return cur.lastrowid

    def record_ar_payment(self, invoice_id: int, pay_date: str,
                          amount: float, method='bank', summary='') -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cur = conn.execute('''
            INSERT INTO ar_payments (invoice_id, pay_date, amount, method, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (invoice_id, pay_date, amount, method, summary, now))
        conn.commit()

        # 更新发票已收金额和余额
        conn.execute('''
            UPDATE ar_invoices SET
                paid_amount = paid_amount + ?,
                balance = amount - (paid_amount + ?),
                status = CASE
                    WHEN ABS(amount - (paid_amount + ?)) < 0.01 THEN 'paid'
                    WHEN paid_amount + ? > 0 THEN 'partial'
                    ELSE status END
            WHERE invoice_id=?
        ''', (amount, amount, amount, amount, invoice_id))
        conn.commit()

        # 更新往来单位余额
        cur = conn.execute("SELECT partner_id FROM ar_invoices WHERE invoice_id=?", (invoice_id,))
        row = cur.fetchone()
        if row:
            self._update_partner_balance(row[0])
        return cur.lastrowid

    def get_ar_invoices(self, partner_id=None, status='', keyword='',
                        page=1, page_size=50) -> Tuple[List[Dict], int]:
        conn = self.db_manager.get_current_conn()
        if not conn: return [], 0
        cond, par = [], []
        if partner_id: cond.append("i.partner_id=?"); par.append(partner_id)
        if status: cond.append("i.status=?"); par.append(status)
        if keyword:
            cond.append("(i.doc_no LIKE ? OR p.partner_name LIKE ?)")
            kw = f'%{keyword}%'; par.extend([kw, kw])
        where = " AND ".join(cond) if cond else "1=1"
        cur = conn.execute(
            f"SELECT COUNT(*) FROM ar_invoices i LEFT JOIN ar_ap_partners p ON i.partner_id=p.partner_id WHERE {where}", par)
        total = cur.fetchone()[0]
        off = (page - 1) * page_size
        cur = conn.execute(f'''
            SELECT i.*, p.partner_code, p.partner_name
            FROM ar_invoices i LEFT JOIN ar_ap_partners p ON i.partner_id=p.partner_id
            WHERE {where} ORDER BY i.doc_date DESC LIMIT ? OFFSET ?''', par + [page_size, off])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()], total

    # ────────────────────────────────
    #  应付管理
    # ────────────────────────────────
    def add_ap_invoice(self, doc_no, partner_id, doc_date, due_date,
                       amount, summary='') -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cur = conn.execute('''
            INSERT INTO ap_invoices (doc_no, partner_id, doc_date, due_date,
                amount, paid_amount, balance, summary, status, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?, ?, 'unpaid', ?)
        ''', (doc_no, partner_id, doc_date, due_date, amount, amount, summary, now))
        conn.commit()
        self._update_partner_balance(partner_id)
        return cur.lastrowid

    def record_ap_payment(self, invoice_id, pay_date, amount,
                          method='bank', summary='') -> int:
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cur = conn.execute('''
            INSERT INTO ap_payments (invoice_id, pay_date, amount, method, summary, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (invoice_id, pay_date, amount, method, summary, now))
        conn.commit()
        conn.execute('''
            UPDATE ap_invoices SET
                paid_amount = paid_amount + ?,
                balance = amount - (paid_amount + ?),
                status = CASE
                    WHEN ABS(amount - (paid_amount + ?)) < 0.01 THEN 'paid'
                    WHEN paid_amount + ? > 0 THEN 'partial'
                    ELSE status END
            WHERE invoice_id=?
        ''', (amount, amount, amount, amount, invoice_id))
        conn.commit()
        cur = conn.execute("SELECT partner_id FROM ap_invoices WHERE invoice_id=?", (invoice_id,))
        row = cur.fetchone()
        if row: self._update_partner_balance(row[0])
        return cur.lastrowid

    def get_ap_invoices(self, partner_id=None, status='', keyword='',
                        page=1, page_size=50) -> Tuple[List[Dict], int]:
        conn = self.db_manager.get_current_conn()
        if not conn: return [], 0
        cond, par = [], []
        if partner_id: cond.append("i.partner_id=?"); par.append(partner_id)
        if status: cond.append("i.status=?"); par.append(status)
        if keyword:
            cond.append("(i.doc_no LIKE ? OR p.partner_name LIKE ?)")
            kw = f'%{keyword}%'; par.extend([kw, kw])
        where = " AND ".join(cond) if cond else "1=1"
        cur = conn.execute(
            f"SELECT COUNT(*) FROM ap_invoices i LEFT JOIN ar_ap_partners p ON i.partner_id=p.partner_id WHERE {where}", par)
        total = cur.fetchone()[0]
        off = (page - 1) * page_size
        cur = conn.execute(f'''
            SELECT i.*, p.partner_code, p.partner_name
            FROM ap_invoices i LEFT JOIN ar_ap_partners p ON i.partner_id=p.partner_id
            WHERE {where} ORDER BY i.doc_date DESC LIMIT ? OFFSET ?''', par + [page_size, off])
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()], total

    def _update_partner_balance(self, partner_id):
        """更新往来单位余额"""
        conn = self.db_manager.get_current_conn()
        # 应收账款余额
        cur = conn.execute(
            "SELECT COALESCE(SUM(balance),0) FROM ar_invoices WHERE partner_id=?", (partner_id,))
        ar_bal = cur.fetchone()[0]
        # 应付账款余额
        cur = conn.execute(
            "SELECT COALESCE(SUM(balance),0) FROM ap_invoices WHERE partner_id=?", (partner_id,))
        ap_bal = cur.fetchone()[0]
        conn.execute(
            "UPDATE ar_ap_partners SET balance=? WHERE partner_id=?",
            (ar_bal - ap_bal, partner_id))
        conn.commit()

    # ────────────────────────────────
    #  账龄分析
    # ────────────────────────────────
    def aging_analysis(self, ptype='customer') -> List[Dict]:
        """
        账龄分析
        ptype: 'customer'=应收账龄 / 'supplier'=应付账龄
        返回按往来单位汇总的账龄分段
        """
        conn = self.db_manager.get_current_conn()
        if not conn: return []
        now_date = date.today()

        table = 'ar_invoices' if ptype == 'customer' else 'ap_invoices'

        cur = conn.execute(f'''
            SELECT p.partner_id, p.partner_code, p.partner_name,
                   COUNT(i.invoice_id) as invoice_count,
                   SUM(i.balance) as total_balance
            FROM {table} i
            LEFT JOIN ar_ap_partners p ON i.partner_id=p.partner_id
            WHERE i.balance > 0.01
            GROUP BY p.partner_id
            ORDER BY total_balance DESC
        ''')

        results = []
        for row in cur.fetchall():
            partner_id = row[0]
            total = row[4] or 0
            # 按账龄分段的余额
            cur2 = conn.execute(f'''
                SELECT
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) <= 30
                        THEN i.balance ELSE 0 END),
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) BETWEEN 31 AND 60
                        THEN i.balance ELSE 0 END),
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) BETWEEN 61 AND 90
                        THEN i.balance ELSE 0 END),
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) BETWEEN 91 AND 180
                        THEN i.balance ELSE 0 END),
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) > 180
                        THEN i.balance ELSE 0 END),
                    SUM(CASE WHEN julianday('{now_date}') - julianday(i.due_date) <= 0
                        THEN i.balance ELSE 0 END)
                FROM {table} i WHERE i.partner_id=? AND i.balance > 0.01
            ''', (partner_id,))
            seg = cur2.fetchone()
            results.append({
                'partner_id': partner_id,
                'partner_code': row[1], 'partner_name': row[2],
                'invoice_count': row[3],
                'total_balance': total,
                'not_due': seg[5] or 0,
                'within_30': seg[0] or 0,
                'within_60': seg[1] or 0,
                'within_90': seg[2] or 0,
                'within_180': seg[3] or 0,
                'over_180': seg[4] or 0,
            })
        return results

    def get_aging_summary(self, ptype='customer') -> Dict:
        """账龄汇总"""
        data = self.aging_analysis(ptype)
        total = sum(d['total_balance'] for d in data)
        return {
            'partner_count': len(data),
            'total_balance': total,
            'not_due': sum(d['not_due'] for d in data),
            'within_30': sum(d['within_30'] for d in data),
            'within_60': sum(d['within_60'] for d in data),
            'within_90': sum(d['within_90'] for d in data),
            'within_180': sum(d['within_180'] for d in data),
            'over_180': sum(d['over_180'] for d in data),
        }