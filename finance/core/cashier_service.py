"""
==========================================
 core/cashier_service.py - 出纳管理服务
==========================================
功能：
  - 现金日记账：登记/查询/余额计算
  - 银行日记账：登记/查询/余额计算
  - 银行对账：导入银行流水，自动/手动勾对
  - 余额调节表：自动生成
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Optional, Dict, Tuple


class CashierService:
    """出纳管理服务"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ═══════════════════════════════════════════
    #  现金日记账
    # ═══════════════════════════════════════════

    def cash_entry(self, date: str, summary: str, income: float,
                   expense: float, acct_code: str = '',
                   voucher_id: int = None) -> int:
        """登记现金日记账"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")
        now = datetime.now().isoformat()
        # 计算最新余额
        cursor = conn.execute(
            "SELECT balance FROM cash_journal ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        last_balance = row[0] if row else 0.0
        balance = last_balance + income - expense
        cursor = conn.execute('''
            INSERT INTO cash_journal (date, summary, voucher_id, acct_code,
                                      income, expense, balance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, summary, voucher_id, acct_code, income, expense, balance, now))
        conn.commit()
        return cursor.lastrowid

    def query_cash(self, date_from: str = '', date_to: str = '',
                   page: int = 1, page_size: int = 50) -> Tuple[List[Dict], int]:
        """查询现金日记账"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0
        conditions, params = [], []
        if date_from:
            conditions.append("date>=?"); params.append(date_from)
        if date_to:
            conditions.append("date<=?"); params.append(date_to)
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(f"SELECT COUNT(*) FROM cash_journal WHERE {where}", params)
        total = cursor.fetchone()[0]
        offset = (page - 1) * page_size
        cursor = conn.execute(
            f"SELECT * FROM cash_journal WHERE {where} ORDER BY date DESC, id DESC LIMIT ? OFFSET ?",
            params + [page_size, offset])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()], total

    def get_cash_balance(self) -> float:
        """获取当前现金余额"""
        conn = self.db_manager.get_current_conn()
        cursor = conn.execute(
            "SELECT balance FROM cash_journal ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0.0

    def get_cash_summary(self, date_from: str = '', date_to: str = '') -> Dict:
        """现金汇总"""
        conn = self.db_manager.get_current_conn()
        conditions, params = [], []
        if date_from:
            conditions.append("date>=?"); params.append(date_from)
        if date_to:
            conditions.append("date<=?"); params.append(date_to)
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(
            f"SELECT COALESCE(SUM(income),0), COALESCE(SUM(expense),0) FROM cash_journal WHERE {where}",
            params)
        row = cursor.fetchone()
        return {
            'total_income': row[0], 'total_expense': row[1],
            'balance': self.get_cash_balance(),
        }

    # ═══════════════════════════════════════════
    #  银行日记账
    # ═══════════════════════════════════════════

    def bank_entry(self, date: str, summary: str, income: float, expense: float,
                   bank_acct: str = '', acct_code: str = '',
                   voucher_id: int = None) -> int:
        """登记银行日记账"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")
        now = datetime.now().isoformat()
        cursor = conn.execute(
            "SELECT balance FROM bank_journal ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        last_balance = row[0] if row else 0.0
        balance = last_balance + income - expense
        cursor = conn.execute('''
            INSERT INTO bank_journal (date, summary, voucher_id, bank_acct,
                                      acct_code, income, expense, balance, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, summary, voucher_id, bank_acct, acct_code, income, expense, balance, now))
        conn.commit()
        return cursor.lastrowid

    def query_bank(self, bank_acct: str = '', date_from: str = '', date_to: str = '',
                   page: int = 1, page_size: int = 50) -> Tuple[List[Dict], int]:
        """查询银行日记账"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0
        conditions, params = [], []
        if bank_acct:
            conditions.append("bank_acct=?"); params.append(bank_acct)
        if date_from:
            conditions.append("date>=?"); params.append(date_from)
        if date_to:
            conditions.append("date<=?"); params.append(date_to)
        where = " AND ".join(conditions) if conditions else "1=1"
        cursor = conn.execute(f"SELECT COUNT(*) FROM bank_journal WHERE {where}", params)
        total = cursor.fetchone()[0]
        offset = (page - 1) * page_size
        cursor = conn.execute(
            f"SELECT * FROM bank_journal WHERE {where} ORDER BY date DESC, id DESC LIMIT ? OFFSET ?",
            params + [page_size, offset])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()], total

    def get_bank_balance(self, bank_acct: str = '') -> float:
        """获取银行存款余额"""
        conn = self.db_manager.get_current_conn()
        if bank_acct:
            cursor = conn.execute(
                "SELECT balance FROM bank_journal WHERE bank_acct=? ORDER BY id DESC LIMIT 1",
                (bank_acct,))
        else:
            cursor = conn.execute(
                "SELECT balance FROM bank_journal ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        return row[0] if row else 0.0

    # ═══════════════════════════════════════════
    #  银行对账
    # ═══════════════════════════════════════════

    def import_bank_statement(self, entries: List[Dict], bank_acct: str,
                              period: str) -> Tuple[int, int]:
        """
        导入银行流水（手工录入或批量导入）
        entries: [{date, summary, income, expense}, ...]
        返回：(导入条数, 匹配条数)
        """
        # 暂存在一个临时表逻辑中，简单处理：直接比对银行日记账
        conn = self.db_manager.get_current_conn()
        matched = 0
        now = datetime.now().isoformat()

        for entry in entries:
            # 尝试自动匹配银行日记账中日期和金额都一致的记录
            cursor = conn.execute('''
                SELECT id FROM bank_journal
                WHERE date=? AND ABS(income-?)<0.01 AND ABS(expense-?)<0.01
                AND (bank_acct=? OR ?='')
                LIMIT 1
            ''', (entry['date'], entry.get('income', 0), entry.get('expense', 0),
                  bank_acct, bank_acct))
            if cursor.fetchone():
                matched += 1
        return len(entries), matched

    def reconcile(self, period: str, bank_acct: str,
                  book_balance: float, bank_balance: float,
                  income_book_unrec: float = 0, expense_book_unrec: float = 0,
                  income_bank_unrec: float = 0, expense_bank_unrec: float = 0) -> Dict:
        """
        生成余额调节表
        企业余额 + 银行已收企业未收 - 银行已付企业未付 = 调整后余额
        银行余额 + 企业已收银行未收 - 企业已付银行未付 = 调整后余额
        """
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()

        adjusted_book = book_balance + income_bank_unrec - expense_bank_unrec
        adjusted_bank = bank_balance + income_book_unrec - expense_book_unrec
        matched = abs(adjusted_book - adjusted_bank) < 0.01

        conn.execute('''
            INSERT INTO bank_reconciliation
            (period, bank_acct, book_balance, bank_balance,
             income_book_unrec, expense_book_unrec,
             income_bank_unrec, expense_bank_unrec,
             adjusted_book, adjusted_bank, matched, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (period, bank_acct, book_balance, bank_balance,
              income_book_unrec, expense_book_unrec,
              income_bank_unrec, expense_bank_unrec,
              adjusted_book, adjusted_bank, 1 if matched else 0, now))
        conn.commit()

        return {
            'period': period,
            'bank_acct': bank_acct,
            'book_balance': book_balance,
            'bank_balance': bank_balance,
            'income_book_unrec': income_book_unrec,
            'expense_book_unrec': expense_book_unrec,
            'income_bank_unrec': income_bank_unrec,
            'expense_bank_unrec': expense_bank_unrec,
            'adjusted_book': adjusted_book,
            'adjusted_bank': adjusted_bank,
            'matched': matched,
        }

    def get_reconciliation_history(self, bank_acct: str = '',
                                   page: int = 1, page_size: int = 20) -> Tuple[List[Dict], int]:
        """查询余额调节表历史"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0
        if bank_acct:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM bank_reconciliation WHERE bank_acct=?", (bank_acct,))
            total = cursor.fetchone()[0]
            offset = (page - 1) * page_size
            cursor = conn.execute(
                "SELECT * FROM bank_reconciliation WHERE bank_acct=? ORDER BY period DESC LIMIT ? OFFSET ?",
                (bank_acct, page_size, offset))
        else:
            cursor = conn.execute("SELECT COUNT(*) FROM bank_reconciliation")
            total = cursor.fetchone()[0]
            offset = (page - 1) * page_size
            cursor = conn.execute(
                "SELECT * FROM bank_reconciliation ORDER BY period DESC LIMIT ? OFFSET ?",
                (page_size, offset))
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()], total

    def synch_from_vouchers(self, period: str):
        """从已过账凭证同步生成日记账"""
        from core.voucher_service import VoucherService
        vs = VoucherService(self.db_manager)
        vouchers, _ = vs.query_vouchers(period=period, status='posted')
        conn = self.db_manager.get_current_conn()
        if not conn:
            return

        for v in vouchers:
            # 获取分录
            cursor = conn.execute(
                "SELECT * FROM voucher_entries WHERE voucher_id=?", (v['voucher_id'],))
            columns = [desc[0] for desc in cursor.description]
            entries = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # 查找现金科目(1001)和银行科目(1002开头)
            cash_amount = 0
            bank_amount = 0
            bank_acct = ''
            for e in entries:
                if e['acct_code'] == '1001':
                    cash_amount = e['debit_amount'] - e['credit_amount']
                elif e['acct_code'].startswith('1002'):
                    bank_amount = e['debit_amount'] - e['credit_amount']
                    conn.execute("SELECT acct_name FROM accounts WHERE acct_code=?", (e['acct_code'],))
                    r = conn.execute("SELECT acct_name FROM accounts WHERE acct_code=?", (e['acct_code'],)).fetchone()
                    bank_acct = r[0] if r else ''

            if abs(cash_amount) > 0:
                self.cash_entry(
                    v['voucher_date'],
                    f"[凭证#{v['voucher_no']}] {v.get('remark','')}",
                    max(cash_amount, 0), max(-cash_amount, 0),
                    voucher_id=v['voucher_id'])
            if abs(bank_amount) > 0:
                self.bank_entry(
                    v['voucher_date'],
                    f"[凭证#{v['voucher_no']}] {v.get('remark','')}",
                    max(bank_amount, 0), max(-bank_amount, 0),
                    bank_acct=bank_acct,
                    voucher_id=v['voucher_id'])