"""
==========================================
 voucher_service.py - 凭证业务服务
==========================================
功能：
  - 凭证的增删改查
  - 凭证审核/反审核
  - 凭证过账/反过账
  - 凭证号自动编排
  - 科目余额更新
"""

from datetime import datetime
from typing import List, Optional, Dict, Tuple


class VoucherService:
    """凭证业务服务"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ──────────────────────────────────────────
    #  凭证 CRUD
    # ──────────────────────────────────────────

    def create_voucher(self, period: str, voucher_date: str,
                       voucher_type: str = '记',
                       entries: List[Dict] = None,
                       attachment_count: int = 0,
                       remark: str = '',
                       created_by: str = 'admin') -> int:
        """
        创建凭证
        entries: [{'summary': str, 'acct_code': str,
                   'debit_amount': float, 'credit_amount': float,
                   'aux_item_id': int}, ...]

        返回：凭证ID
        """
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        # 自动编排凭证号
        voucher_no = self._get_next_voucher_no(conn, period, voucher_type)

        now = datetime.now().isoformat()

        cursor = conn.execute('''
            INSERT INTO vouchers
            (period, voucher_date, voucher_type, voucher_no,
             attachment_count, status, created_by, created_at, remark)
            VALUES (?, ?, ?, ?, ?, 'draft', ?, ?, ?)
        ''', (period, voucher_date, voucher_type, voucher_no,
              attachment_count, created_by, now, remark))

        voucher_id = cursor.lastrowid

        # 插入分录
        if entries:
            for i, entry in enumerate(entries):
                conn.execute('''
                    INSERT INTO voucher_entries
                    (voucher_id, entry_order, summary, acct_code,
                     debit_amount, credit_amount, aux_item_id, cf_item_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (voucher_id, i + 1,
                      entry.get('summary', ''),
                      entry['acct_code'],
                      entry.get('debit_amount', 0.0),
                      entry.get('credit_amount', 0.0),
                      entry.get('aux_item_id'),
                      entry.get('cf_item_id', 0)))

        conn.commit()
        return voucher_id

    def get_voucher(self, voucher_id: int) -> Optional[Dict]:
        """获取凭证（含分录）"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        conn.row_factory = sqlite3.Row
        cursor = conn.execute(
            "SELECT * FROM vouchers WHERE voucher_id = ?", (voucher_id,))
        voucher = cursor.fetchone()
        if not voucher:
            return None

        voucher = dict(voucher)
        cursor = conn.execute(
            "SELECT * FROM voucher_entries WHERE voucher_id = ? ORDER BY entry_order",
            (voucher_id,))
        voucher['entries'] = [dict(row) for row in cursor.fetchall()]

        return voucher

    def update_voucher(self, voucher_id: int, entries: List[Dict] = None,
                       attachment_count: int = None,
                       remark: str = None) -> bool:
        """修改凭证（仅草稿状态可修改）"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        # 检查状态
        cursor = conn.execute(
            "SELECT status FROM vouchers WHERE voucher_id = ?",
            (voucher_id,))
        row = cursor.fetchone()
        if not row:
            raise ValueError(f"凭证 {voucher_id} 不存在")
        if row[0] != 'draft':
            raise ValueError(f"凭证 {voucher_id} 状态为 {row[0]}，不可修改")

        # 更新主表
        if attachment_count is not None or remark is not None:
            updates = []
            values = []
            if attachment_count is not None:
                updates.append("attachment_count=?")
                values.append(attachment_count)
            if remark is not None:
                updates.append("remark=?")
                values.append(remark)
            values.append(voucher_id)
            conn.execute(
                f"UPDATE vouchers SET {','.join(updates)} WHERE voucher_id=?",
                values)

        # 更新分录（删除旧分录，插入新分录）
        if entries is not None:
            conn.execute(
                "DELETE FROM voucher_entries WHERE voucher_id=?",
                (voucher_id,))
            for i, entry in enumerate(entries):
                conn.execute('''
                    INSERT INTO voucher_entries
                    (voucher_id, entry_order, summary, acct_code,
                     debit_amount, credit_amount, aux_item_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (voucher_id, i + 1,
                      entry.get('summary', ''),
                      entry['acct_code'],
                      entry.get('debit_amount', 0.0),
                      entry.get('credit_amount', 0.0),
                      entry.get('aux_item_id')))

        conn.commit()
        return True

    def delete_voucher(self, voucher_id: int) -> bool:
        """删除凭证（仅草稿状态可删除）"""
        conn = self.db_manager.get_current_conn()
        cursor = conn.execute(
            "SELECT status FROM vouchers WHERE voucher_id = ?",
            (voucher_id,))
        row = cursor.fetchone()
        if not row:
            return False
        if row[0] != 'draft':
            raise ValueError(f"凭证 {voucher_id} 状态为 {row[0]}，不可删除")

        conn.execute("DELETE FROM voucher_entries WHERE voucher_id=?", (voucher_id,))
        conn.execute("DELETE FROM vouchers WHERE voucher_id=?", (voucher_id,))
        conn.commit()
        return True

    # ──────────────────────────────────────────
    #  审核 / 过账
    # ──────────────────────────────────────────

    def approve_voucher(self, voucher_id: int, user: str = 'admin') -> bool:
        """审核凭证"""
        conn = self.db_manager.get_current_conn()
        conn.execute(
            "UPDATE vouchers SET status='approved' WHERE voucher_id=? AND status='draft'",
            (voucher_id,))
        conn.commit()
        return conn.total_changes > 0

    def unapprove_voucher(self, voucher_id: int) -> bool:
        """反审核凭证"""
        conn = self.db_manager.get_current_conn()
        conn.execute(
            "UPDATE vouchers SET status='draft' WHERE voucher_id=? AND status='approved'",
            (voucher_id,))
        conn.commit()
        return conn.total_changes > 0

    def post_voucher(self, voucher_id: int) -> bool:
        """过账（已审核 → 已过账，同时更新科目余额）"""
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()

        cursor = conn.execute(
            "SELECT * FROM vouchers WHERE voucher_id=? AND status='approved'",
            (voucher_id,))
        voucher = cursor.fetchone()
        if not voucher:
            raise ValueError(f"凭证 {voucher_id} 不存在或未审核")

        # 获取分录
        cursor = conn.execute(
            "SELECT * FROM voucher_entries WHERE voucher_id=?",
            (voucher_id,))
        entries = cursor.fetchall()

        # 更新科目余额
        for entry in entries:
            self._update_balance(conn, voucher[1], entry[3],
                                 entry[5], entry[6])  # period, acct_code, debit, credit

        # 更新凭证状态
        conn.execute(
            "UPDATE vouchers SET status='posted', posted_at=? WHERE voucher_id=?",
            (now, voucher_id))
        conn.commit()
        return True

    def unpost_voucher(self, voucher_id: int) -> bool:
        """反过账"""
        conn = self.db_manager.get_current_conn()
        # ... 反向更新余额逻辑类似，略
        return True

    # ──────────────────────────────────────────
    #  查询
    # ──────────────────────────────────────────

    def query_vouchers(self, period: str = None, status: str = None,
                       voucher_type: str = None,
                       date_from: str = None, date_to: str = None,
                       page: int = 1, page_size: int = 20) -> Tuple[List[Dict], int]:
        """
        查询凭证列表
        返回：(凭证列表, 总条数)
        """
        conn = self.db_manager.get_current_conn()
        conn.row_factory = sqlite3.Row

        conditions = []
        params = []

        if period:
            conditions.append("period=?")
            params.append(period)
        if status:
            conditions.append("status=?")
            params.append(status)
        if voucher_type:
            conditions.append("voucher_type=?")
            params.append(voucher_type)
        if date_from:
            conditions.append("voucher_date>=?")
            params.append(date_from)
        if date_to:
            conditions.append("voucher_date<=?")
            params.append(date_to)

        where = " AND ".join(conditions) if conditions else "1=1"

        # 总数
        cursor = conn.execute(
            f"SELECT COUNT(*) FROM vouchers WHERE {where}", params)
        total = cursor.fetchone()[0]

        # 分页
        offset = (page - 1) * page_size
        cursor = conn.execute(
            f"SELECT * FROM vouchers WHERE {where} "
            f"ORDER BY period DESC, voucher_no DESC "
            f"LIMIT ? OFFSET ?",
            params + [page_size, offset])
        vouchers = [dict(row) for row in cursor.fetchall()]

        return vouchers, total

    # ──────────────────────────────────────────
    #  内部方法
    # ──────────────────────────────────────────

    def _get_next_voucher_no(self, conn, period: str, voucher_type: str) -> int:
        """获取下一个凭证号"""
        cursor = conn.execute(
            "SELECT COALESCE(MAX(voucher_no), 0) + 1 "
            "FROM vouchers WHERE period=? AND voucher_type=?",
            (period, voucher_type))
        return cursor.fetchone()[0]

    def _update_balance(self, conn, period: str, acct_code: str,
                        debit_amount: float, credit_amount: float):
        """更新科目余额"""
        # 检查是否有余额记录
        cursor = conn.execute(
            "SELECT id FROM account_balances WHERE period=? AND acct_code=?",
            (period, acct_code))
        row = cursor.fetchone()

        if row:
            conn.execute('''
                UPDATE account_balances SET
                    period_debit = period_debit + ?,
                    period_credit = period_credit + ?,
                    end_debit = begin_debit + period_debit + ?,
                    end_credit = begin_credit + period_credit + ?
                WHERE period=? AND acct_code=?
            ''', (debit_amount, credit_amount, debit_amount, credit_amount,
                  period, acct_code))
        else:
            # 获取期初余额
            cursor = conn.execute(
                "SELECT end_debit, end_credit FROM account_balances "
                "WHERE period=? AND acct_code=?",
                (self._get_prev_period(period), acct_code))
            prev = cursor.fetchone()
            begin_debit = prev[0] if prev else 0.0
            begin_credit = prev[1] if prev else 0.0

            conn.execute('''
                INSERT INTO account_balances
                (period, acct_code, begin_debit, begin_credit,
                 period_debit, period_credit, end_debit, end_credit)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (period, acct_code, begin_debit, begin_credit,
                  debit_amount, credit_amount,
                  begin_debit + debit_amount,
                  begin_credit + credit_amount))

    def _get_prev_period(self, period: str) -> str:
        parts = period.split('-')
        year, month = int(parts[0]), int(parts[1])
        if month == 1:
            return f"{year - 1:04d}-12"
        return f"{year:04d}-{month - 1:02d}"


import sqlite3
