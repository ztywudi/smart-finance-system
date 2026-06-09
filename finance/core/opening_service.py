"""
==========================================
 core/opening_service.py - 期初余额导入服务
==========================================
功能：
  - 科目期初余额录入/导入
  - 固定资产期初卡片导入
  - 应收应付期初导入
  - Excel模板生成
"""

import sys, os, csv, json
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Dict, Tuple


class OpeningService:
    """期初余额服务"""

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ── 数据库初始化 ──
    def ensure_tables(self):
        """确保期初相关表存在"""
        conn = self.db_manager.get_current_conn()
        if not conn: return
        conn.execute('''
            CREATE TABLE IF NOT EXISTS opening_balances (
                ob_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                acct_code   TEXT NOT NULL,
                acct_name   TEXT,
                debit_bal   REAL DEFAULT 0.0,
                credit_bal  REAL DEFAULT 0.0,
                fiscal_year INTEGER DEFAULT 2026,
                created_at  TEXT NOT NULL,
                UNIQUE(acct_code, fiscal_year)
            )
        ''')
        conn.execute('''
            CREATE TABLE IF NOT EXISTS opening_assets (
                oa_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code  TEXT NOT NULL,
                asset_name  TEXT NOT NULL,
                category    TEXT,
                department  TEXT,
                location    TEXT,
                original_value  REAL DEFAULT 0.0,
                accumulated_depr REAL DEFAULT 0.0,
                residual_rate   REAL DEFAULT 0.05,
                depr_method     TEXT DEFAULT 'straight',
                total_months    INTEGER DEFAULT 60,
                depr_months     INTEGER DEFAULT 0,
                purchase_date   TEXT,
                start_use_date  TEXT,
                fiscal_year INTEGER DEFAULT 2026,
                created_at  TEXT NOT NULL
            )
        ''')
        conn.commit()

    # ═══ 科目期初余额 ═══

    def set_balance(self, acct_code: str, acct_name: str,
                    debit_bal: float, credit_bal: float,
                    fiscal_year: int = None) -> int:
        conn = self.db_manager.get_current_conn()
        self.ensure_tables()
        now = datetime.now().isoformat()
        fy = fiscal_year or datetime.now().year
        conn.execute('''
            INSERT OR REPLACE INTO opening_balances
            (acct_code, acct_name, debit_bal, credit_bal, fiscal_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (acct_code, acct_name, debit_bal, credit_bal, fy, now))
        conn.commit()
        cur = conn.execute("SELECT ob_id FROM opening_balances WHERE acct_code=? AND fiscal_year=?",
                          (acct_code, fy))
        return cur.fetchone()[0]

    def get_balances(self, fiscal_year: int = None) -> List[Dict]:
        conn = self.db_manager.get_current_conn()
        if not conn: return []
        self.ensure_tables()
        fy = fiscal_year or datetime.now().year
        cur = conn.execute('''
            SELECT o.*, a.acct_name as sys_acct_name
            FROM opening_balances o
            LEFT JOIN accounts a ON o.acct_code=a.acct_code
            WHERE o.fiscal_year=? ORDER BY o.acct_code
        ''', (fy,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def import_balances_csv(self, filepath: str, fiscal_year: int = None) -> Tuple[int, int]:
        """导入科目期初余额CSV"""
        self.ensure_tables()
        success = fail = 0
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.set_balance(
                        row['科目编码'], row.get('科目名称', ''),
                        float(row.get('借方余额', 0) or 0),
                        float(row.get('贷方余额', 0) or 0),
                        fiscal_year)
                    success += 1
                except Exception:
                    fail += 1
        return success, fail

    def export_balances_template(self, filepath: str):
        """导出科目期初余额模板"""
        conn = self.db_manager.get_current_conn()
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['科目编码', '科目名称', '借方余额', '贷方余额'])
            if conn:
                cur = conn.execute(
                    "SELECT acct_code, acct_name FROM accounts WHERE enabled=1 ORDER BY acct_code")
                for code, name in cur:
                    w.writerow([code, name, '', ''])

    # ═══ 固定资产期初卡片 ═══

    def add_opening_asset(self, asset_code: str, asset_name: str,
                          original_value: float, accumulated_depr: float = 0,
                          category: str = '', department: str = '',
                          residual_rate: float = 0.05,
                          depr_method: str = 'straight',
                          total_months: int = 60, depr_months: int = 0,
                          purchase_date: str = '', start_use_date: str = '',
                          fiscal_year: int = None) -> int:
        conn = self.db_manager.get_current_conn()
        self.ensure_tables()
        now = datetime.now().isoformat()
        fy = fiscal_year or datetime.now().year
        cur = conn.execute('''
            INSERT INTO opening_assets
            (asset_code, asset_name, category, department, location,
             original_value, accumulated_depr, residual_rate, depr_method,
             total_months, depr_months, purchase_date, start_use_date, fiscal_year, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (asset_code, asset_name, category, department, '',
              original_value, accumulated_depr, residual_rate, depr_method,
              total_months, depr_months, purchase_date, start_use_date, fy, now))
        conn.commit()

        # 同时写入固定资产主表
        conn.execute('''
            INSERT INTO fixed_assets
            (asset_code, asset_name, category, department, location,
             original_value, accumulated_depr, residual_rate, depr_method,
             total_months, depr_months, purchase_date, start_use_date,
             status, remark, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_use', '期初导入', ?, ?)
        ''', (asset_code, asset_name, category, department, '',
              original_value, accumulated_depr, residual_rate, depr_method,
              total_months, depr_months, purchase_date, start_use_date, now, now))
        conn.commit()
        return cur.lastrowid

    def get_opening_assets(self, fiscal_year: int = None) -> List[Dict]:
        conn = self.db_manager.get_current_conn()
        if not conn: return []
        self.ensure_tables()
        fy = fiscal_year or datetime.now().year
        cur = conn.execute(
            "SELECT * FROM opening_assets WHERE fiscal_year=? ORDER BY asset_code", (fy,))
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def import_assets_csv(self, filepath: str, fiscal_year: int = None) -> Tuple[int, int]:
        """导入固定资产期初CSV"""
        success = fail = 0
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    self.add_opening_asset(
                        row['资产编码'], row['资产名称'],
                        float(row['原值']), float(row.get('累计折旧', 0) or 0),
                        row.get('类别', ''), row.get('使用部门', ''),
                        float(row.get('残值率', 0.05) or 0.05),
                        row.get('折旧方法', 'straight'),
                        int(row.get('折旧期限(月)', 60) or 60),
                        int(row.get('已折旧月数', 0) or 0),
                        row.get('购入日期', ''), row.get('使用日期', ''),
                        fiscal_year)
                    success += 1
                except Exception as e:
                    fail += 1
        return success, fail

    def export_assets_template(self, filepath: str):
        """导出固定资产期初模板"""
        with open(filepath, 'w', newline='', encoding='utf-8-sig') as f:
            w = csv.writer(f)
            w.writerow(['资产编码', '资产名称', '类别', '使用部门', '原值', '累计折旧',
                       '残值率', '折旧方法', '折旧期限(月)', '已折旧月数', '购入日期', '使用日期'])

    # ═══ 期初上线（一次性写入科目期初） ═══

    def post_opening(self, fiscal_year: int = None) -> Dict:
        """
        将期初余额写入正式账簿
        生成一张"期初建账"凭证
        """
        from core.voucher_service import VoucherService
        conn = self.db_manager.get_current_conn()
        fy = fiscal_year or datetime.now().year

        balances = self.get_balances(fy)
        total_debit = sum(b['debit_bal'] for b in balances)
        total_credit = sum(b['credit_bal'] for b in balances)
        if abs(total_debit - total_credit) > 0.01:
            return {'success': False, 'message': f'借贷不平衡！借{total_debit:.2f}≠贷{total_credit:.2f}'}

        # 生成期初凭证
        entries = []
        for b in balances:
            if b['debit_bal'] > 0:
                entries.append({
                    'summary': '期初余额', 'acct_code': b['acct_code'],
                    'debit_amount': b['debit_bal'], 'credit_amount': 0
                })
            if b['credit_bal'] > 0:
                entries.append({
                    'summary': '期初余额', 'acct_code': b['acct_code'],
                    'debit_amount': 0, 'credit_amount': b['credit_bal']
                })

        if entries:
            vs = VoucherService(self.db_manager)
            period = f'{fy}-01'
            vid = vs.create_voucher(period, f'{fy}-01-01', '记', entries,
                                    remark=f'期初建账（{fy}年）')
            return {'success': True, 'message': f'期初余额已上线，凭证ID: {vid}',
                    'voucher_id': vid, 'total_debit': total_debit}
        return {'success': False, 'message': '无期初数据'}