"""
========================================
  database.py - 数据库连接与账套管理
========================================
功能：
  - 多账套数据库管理（每个账套独立 .db 文件）
  - 账套的创建、打开、备份、恢复
  - 主数据库（记录所有账套元信息）
  - 便携数据库检测与合并

数据库文件结构：
  data/user_data/
    ├── master.db          ← 主数据库（账套列表、用户信息）
    ├── AB001_xx公司.db     ← 账套1
    ├── AB002_xx工会.db     ← 账套2
    └── ...

设计原则：
  - 账套之间完全隔离，互不干扰
  - 支持热插拔U盘数据库
  - 所有数据库操作通过此处统一管理
"""

import sqlite3
import os
import shutil
import json
from datetime import datetime
from typing import Optional


class DatabaseManager:
    """数据库管理器 - 单例模式"""

    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @staticmethod
    def _find_writable_dir() -> str:
        """自动寻找可写的数据库目录（SQLite直测）"""
        candidates = [
            os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                         'data', 'user_data'),
            os.path.join(os.path.expanduser('~'), '.finance_data'),
            '/tmp/finance_data',
        ]
        for path in candidates:
            try:
                os.makedirs(path, exist_ok=True)
                test_db = os.path.join(path, '.perm_test.db')
                conn = sqlite3.connect(test_db)
                conn.execute('CREATE TABLE IF NOT EXISTS t (x INT)')
                conn.execute('INSERT INTO t VALUES (1)')
                conn.commit()
                conn.close()
                os.remove(test_db)
                return path
            except (PermissionError, OSError, sqlite3.OperationalError):
                continue
        # 保底
        fallback = '/tmp/finance_data'
        os.makedirs(fallback, exist_ok=True)
        return fallback

    def __init__(self, data_dir: str = None):
        if hasattr(self, '_initialized') and self._initialized:
            return
        self._initialized = True

        # 用户数据目录（自动探测可写路径）
        if data_dir:
            self.data_dir = data_dir
        else:
            self.data_dir = self._find_writable_dir()
        os.makedirs(self.data_dir, exist_ok=True)

        # 当前打开的账套连接
        self._current_conn: Optional[sqlite3.Connection] = None
        self._current_book_id: Optional[str] = None

        # 初始化主数据库
        self._init_master_db()

    # ──────────────────────────────────────────
    #  主数据库管理（记录所有账套的元信息）
    # ──────────────────────────────────────────

    def _get_master_path(self) -> str:
        return os.path.join(self.data_dir, 'master.db')

    def _init_master_db(self):
        """创建/初始化主数据库"""
        conn = sqlite3.connect(self._get_master_path())
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_books (
                book_id         TEXT PRIMARY KEY,          -- 账套编号 AB001
                book_name       TEXT NOT NULL,              -- 账套名称
                company_name    TEXT,                       -- 单位全称
                accounting_system TEXT NOT NULL,             -- 会计制度代码
                fiscal_year_start INTEGER DEFAULT 1,        -- 会计年度起始月
                currency        TEXT DEFAULT 'CNY',         -- 本位币
                created_at      TEXT NOT NULL,              -- 创建时间
                updated_at      TEXT NOT NULL,              -- 最后修改时间
                status          TEXT DEFAULT 'active',      -- active/disabled/archived
                description     TEXT,                       -- 备注说明
                db_file_name    TEXT NOT NULL               -- 对应数据库文件名
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id     TEXT PRIMARY KEY,
                username    TEXT NOT NULL UNIQUE,
                password    TEXT NOT NULL,
                role        TEXT DEFAULT 'operator',  -- admin / operator / viewer
                created_at  TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sync_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                book_id     TEXT NOT NULL,
                sync_time   TEXT NOT NULL,
                direction   TEXT NOT NULL,   -- upload / download
                status      TEXT NOT NULL,   -- success / conflict / failed
                details     TEXT
            )
        ''')

        # 旧数据库迁移：增加行业模板列
        try:
            cursor.execute("ALTER TABLE account_books ADD COLUMN industry_code TEXT DEFAULT 'none'")
        except Exception:
            pass

        conn.commit()
        conn.close()

    # ──────────────────────────────────────────
    #  账套 CRUD
    # ──────────────────────────────────────────

    def create_account_book(self, book_name: str, accounting_system: str,
                            company_name: str = '', fiscal_year_start: int = 1,
                            currency: str = 'CNY', description: str = '',
                            industry_code: str = 'none') -> str:
        """
        创建新账套
        - 生成唯一 book_id
        - 在 master.db 中注册
        - 创建独立的 .db 文件并初始化科目表
        - 应用行业模板（如有）
        """
        master_conn = sqlite3.connect(self._get_master_path())
        cursor = master_conn.cursor()

        # 生成账套编号
        cursor.execute("SELECT COUNT(*) FROM account_books")
        count = cursor.fetchone()[0]
        book_id = f"AB{count + 1:04d}"

        now = datetime.now().isoformat()
        db_file_name = f"{book_id}_{book_name}.db"

        cursor.execute('''
            INSERT INTO account_books
            (book_id, book_name, company_name, accounting_system,
             fiscal_year_start, currency, created_at, updated_at,
             status, description, db_file_name, industry_code)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'active', ?, ?, ?)
        ''', (book_id, book_name, company_name, accounting_system,
              fiscal_year_start, currency, now, now, description, db_file_name, industry_code))

        master_conn.commit()
        master_conn.close()

        # 创建账套数据库并初始化
        self._init_book_db(book_id, accounting_system, fiscal_year_start, industry_code)

        return book_id

    def _init_book_db(self, book_id: str, accounting_system: str,
                      fiscal_year_start: int, industry_code: str = 'none'):
        """初始化账套数据库结构"""
        book_path = self._get_book_path(book_id)
        conn = sqlite3.connect(book_path)
        cursor = conn.cursor()

        # 账套参数表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS book_params (
                key   TEXT PRIMARY KEY,
                value TEXT
            )
        ''')
        cursor.execute(
            "INSERT OR REPLACE INTO book_params VALUES ('accounting_system', ?)",
            (accounting_system,))
        cursor.execute(
            "INSERT OR REPLACE INTO book_params VALUES ('fiscal_year_start', ?)",
            (str(fiscal_year_start),))
        cursor.execute(
            "INSERT OR REPLACE INTO book_params VALUES ('version', '1.0.0')",)

        # 会计科目表（每账套独立库，无需book_id字段）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS accounts (
                acct_code       TEXT PRIMARY KEY,          -- 科目编码 1001
                acct_name       TEXT NOT NULL,              -- 科目名称 库存现金
                acct_level      INTEGER DEFAULT 1,          -- 科目级次 1-6
                parent_code     TEXT,                       -- 上级科目编码
                is_detail       INTEGER DEFAULT 0,          -- 是否末级科目
                acct_type       TEXT,                       -- 资产/负债/权益/成本/损益
                balance_side    TEXT DEFAULT 'debit',       -- 余额方向 debit/credit
                is_cash_equivalent INTEGER DEFAULT 0,       -- 是否现金等价物
                is_bank_account INTEGER DEFAULT 0,          -- 是否银行科目
                enabled         INTEGER DEFAULT 1,          -- 是否启用
                created_at      TEXT NOT NULL,
                modified_at     TEXT NOT NULL
            )
        ''')

        # 辅助核算类型
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aux_types (
                type_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                type_name   TEXT NOT NULL,  -- 客户/供应商/部门/职员/项目/存货
                enabled     INTEGER DEFAULT 1
            )
        ''')

        # 辅助核算档案
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aux_items (
                item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                type_id     INTEGER NOT NULL,
                item_code   TEXT NOT NULL,
                item_name   TEXT NOT NULL,
                enabled     INTEGER DEFAULT 1,
                FOREIGN KEY (type_id) REFERENCES aux_types(type_id)
            )
        ''')

        # 科目辅助核算关联
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_aux (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                acct_code   TEXT NOT NULL,
                type_id     INTEGER NOT NULL,
                FOREIGN KEY (type_id) REFERENCES aux_types(type_id)
            )
        ''')

        # 凭证表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS vouchers (
                voucher_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                period          TEXT NOT NULL,          -- 会计期间 2026-05
                voucher_date    TEXT NOT NULL,          -- 凭证日期
                voucher_type    TEXT DEFAULT '记',      -- 凭证字 记/收/付/转
                voucher_no      INTEGER NOT NULL,       -- 凭证号
                attachment_count INTEGER DEFAULT 0,     -- 附件张数
                status          TEXT DEFAULT 'draft',   -- draft/posted/voided
                created_by      TEXT,
                created_at      TEXT NOT NULL,
                posted_at       TEXT,
                remark          TEXT                    -- 摘要
            )
        ''')

        # 凭证分录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS voucher_entries (
                entry_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                voucher_id      INTEGER NOT NULL,
                entry_order     INTEGER NOT NULL,       -- 分录序号
                summary         TEXT,                   -- 摘要
                acct_code       TEXT NOT NULL,          -- 科目编码
                debit_amount    REAL DEFAULT 0.0,
                credit_amount   REAL DEFAULT 0.0,
                quantity        REAL,                   -- 数量（数量金额式）
                unit_price      REAL,                   -- 单价
                aux_item_id     INTEGER,                -- 辅助核算项
                FOREIGN KEY (voucher_id) REFERENCES vouchers(voucher_id)
            )
        ''')

        # 科目余额表（按月）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_balances (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                period          TEXT NOT NULL,          -- 2026-05
                acct_code       TEXT NOT NULL,
                begin_debit     REAL DEFAULT 0.0,
                begin_credit    REAL DEFAULT 0.0,
                period_debit    REAL DEFAULT 0.0,
                period_credit   REAL DEFAULT 0.0,
                end_debit       REAL DEFAULT 0.0,
                end_credit      REAL DEFAULT 0.0,
                UNIQUE(period, acct_code)
            )
        ''')

        # ═══════════════ 固定资产表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS fixed_assets (
                asset_id        INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_code      TEXT NOT NULL UNIQUE,
                asset_name      TEXT NOT NULL,
                category        TEXT,
                specification   TEXT,
                department      TEXT,
                location        TEXT,
                original_value  REAL DEFAULT 0.0,
                accumulated_depr REAL DEFAULT 0.0,
                residual_rate   REAL DEFAULT 0.05,
                depr_method     TEXT DEFAULT 'straight',
                total_months    INTEGER DEFAULT 60,
                depr_months     INTEGER DEFAULT 0,
                purchase_date   TEXT,
                start_use_date  TEXT,
                last_depr_date  TEXT,
                status          TEXT DEFAULT 'in_use',
                remark          TEXT,
                created_at      TEXT NOT NULL,
                modified_at     TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS depr_details (
                id              INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id        INTEGER NOT NULL,
                period          TEXT NOT NULL,
                depr_amount     REAL DEFAULT 0.0,
                created_at      TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES fixed_assets(asset_id),
                UNIQUE(asset_id, period)
            )
        ''')

        # ═══════════════ 资产变动记录表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS asset_changes (
                change_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                asset_id        INTEGER NOT NULL,
                change_type     TEXT NOT NULL,
                change_amount   REAL DEFAULT 0.0,
                old_value       REAL DEFAULT 0.0,
                new_value       REAL DEFAULT 0.0,
                old_depr        REAL DEFAULT 0.0,
                new_depr        REAL DEFAULT 0.0,
                change_date     TEXT NOT NULL,
                reason          TEXT,
                target_asset_ids TEXT,
                change_details  TEXT,           -- JSON: 记录具体改了哪些字段 {field: {old:..., new:...}}
                created_at      TEXT NOT NULL,
                FOREIGN KEY (asset_id) REFERENCES fixed_assets(asset_id)
            )
        ''')

        # 兼容旧数据库：增加change_details列
        try:
            cursor.execute("ALTER TABLE asset_changes ADD COLUMN change_details TEXT")
        except Exception:
            pass

        # ═══════════════ 出纳管理表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_journal (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                summary     TEXT,
                voucher_id  INTEGER,
                acct_code   TEXT,               -- 对方科目
                income      REAL DEFAULT 0.0,   -- 收入
                expense     REAL DEFAULT 0.0,   -- 支出
                balance     REAL DEFAULT 0.0,   -- 余额
                created_at  TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_journal (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                date        TEXT NOT NULL,
                summary     TEXT,
                voucher_id  INTEGER,
                bank_acct   TEXT,               -- 银行账户
                acct_code   TEXT,               -- 对方科目
                income      REAL DEFAULT 0.0,
                expense     REAL DEFAULT 0.0,
                balance     REAL DEFAULT 0.0,
                created_at  TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bank_reconciliation (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                period      TEXT NOT NULL,       -- 对账期间 2026-05
                bank_acct   TEXT NOT NULL,       -- 银行账户
                book_balance    REAL DEFAULT 0.0, -- 账面余额
                bank_balance    REAL DEFAULT 0.0, -- 银行对账单余额
                income_book_unrec  REAL DEFAULT 0.0,  -- 企业已收银行未收
                expense_book_unrec REAL DEFAULT 0.0,  -- 企业已付银行未付
                income_bank_unrec  REAL DEFAULT 0.0,  -- 银行已收企业未收
                expense_bank_unrec REAL DEFAULT 0.0,  -- 银行已付企业未付
                adjusted_book REAL DEFAULT 0.0,  -- 调整后企业余额
                adjusted_bank REAL DEFAULT 0.0,  -- 调整后银行余额
                matched       INTEGER DEFAULT 0, -- 是否平衡
                created_at    TEXT NOT NULL
            )
        ''')

        # ═══════════════ 工资管理表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employees (
                emp_id      INTEGER PRIMARY KEY AUTOINCREMENT,
                emp_code    TEXT NOT NULL UNIQUE,
                emp_name    TEXT NOT NULL,
                department  TEXT,
                position    TEXT,
                base_salary REAL DEFAULT 0.0,
                hire_date   TEXT,
                status      TEXT DEFAULT 'active',
                bank_acct   TEXT,
                created_at  TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll_records (
                record_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                period      TEXT NOT NULL,
                emp_id      INTEGER NOT NULL,
                base_salary     REAL DEFAULT 0.0,
                overtime_pay    REAL DEFAULT 0.0,
                bonus           REAL DEFAULT 0.0,
                subsidy         REAL DEFAULT 0.0,
                social_insurance REAL DEFAULT 0.0,
                housing_fund    REAL DEFAULT 0.0,
                tax             REAL DEFAULT 0.0,
                other_deduct    REAL DEFAULT 0.0,
                gross_pay       REAL DEFAULT 0.0,
                net_pay         REAL DEFAULT 0.0,
                status          TEXT DEFAULT 'draft',
                created_at      TEXT NOT NULL,
                FOREIGN KEY (emp_id) REFERENCES employees(emp_id),
                UNIQUE(period, emp_id)
            )
        ''')

        # ═══════════════ 自定义工资项目 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll_items (
                item_id     INTEGER PRIMARY KEY AUTOINCREMENT,
                item_name   TEXT NOT NULL,
                item_type   TEXT NOT NULL,   -- income(收入项)/deduction(扣款项)/reference(参考项)
                calc_order  INTEGER DEFAULT 0,
                enabled     INTEGER DEFAULT 1,
                created_at  TEXT NOT NULL
            )
        ''')

        # 工资明细（EAV模式：每条记录存一个项目值）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS payroll_details (
                detail_id   INTEGER PRIMARY KEY AUTOINCREMENT,
                record_id   INTEGER NOT NULL,
                item_id     INTEGER NOT NULL,
                amount      REAL DEFAULT 0.0,
                FOREIGN KEY (record_id) REFERENCES payroll_records(record_id),
                FOREIGN KEY (item_id) REFERENCES payroll_items(item_id),
                UNIQUE(record_id, item_id)
            )
        ''')

        # 兼容旧数据库：增加details_json列
        try:
            cursor.execute("ALTER TABLE payroll_records ADD COLUMN details_json TEXT")
        except Exception:
            pass

        # ═══════════════ 应收应付表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ar_ap_partners (
                partner_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                partner_code TEXT NOT NULL UNIQUE,
                partner_name TEXT NOT NULL,
                partner_type TEXT NOT NULL,  -- customer(客户)/supplier(供应商)
                contact     TEXT,
                phone       TEXT,
                address     TEXT,
                bank_acct   TEXT,
                credit_limit REAL DEFAULT 0.0,
                balance     REAL DEFAULT 0.0,  -- 应收/应付余额
                status      TEXT DEFAULT 'active',
                created_at  TEXT NOT NULL
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ar_invoices (
                invoice_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_no      TEXT NOT NULL UNIQUE,
                partner_id  INTEGER NOT NULL,
                doc_date    TEXT NOT NULL,
                due_date    TEXT NOT NULL,
                amount      REAL DEFAULT 0.0,    -- 发票金额
                paid_amount REAL DEFAULT 0.0,    -- 已收金额
                balance     REAL DEFAULT 0.0,    -- 余额
                summary     TEXT,
                status      TEXT DEFAULT 'unpaid',  -- unpaid/partial/paid/overdue
                created_at  TEXT NOT NULL,
                FOREIGN KEY (partner_id) REFERENCES ar_ap_partners(partner_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ap_invoices (
                invoice_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_no      TEXT NOT NULL UNIQUE,
                partner_id  INTEGER NOT NULL,
                doc_date    TEXT NOT NULL,
                due_date    TEXT NOT NULL,
                amount      REAL DEFAULT 0.0,
                paid_amount REAL DEFAULT 0.0,
                balance     REAL DEFAULT 0.0,
                summary     TEXT,
                status      TEXT DEFAULT 'unpaid',
                created_at  TEXT NOT NULL,
                FOREIGN KEY (partner_id) REFERENCES ar_ap_partners(partner_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ar_payments (
                payment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id  INTEGER NOT NULL,
                pay_date    TEXT NOT NULL,
                amount      REAL DEFAULT 0.0,
                method      TEXT DEFAULT 'bank',  -- cash/bank/other
                summary     TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES ar_invoices(invoice_id)
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ap_payments (
                payment_id  INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id  INTEGER NOT NULL,
                pay_date    TEXT NOT NULL,
                amount      REAL DEFAULT 0.0,
                method      TEXT DEFAULT 'bank',
                summary     TEXT,
                created_at  TEXT NOT NULL,
                FOREIGN KEY (invoice_id) REFERENCES ap_invoices(invoice_id)
            )
        ''')

        # ═══════════════ 现金流量项目表 ═══════════════
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cash_flow_items (
                cf_id       INTEGER PRIMARY KEY AUTOINCREMENT,
                cf_code     TEXT NOT NULL UNIQUE,
                cf_name     TEXT NOT NULL,
                cf_type     TEXT NOT NULL,
                cf_order    INTEGER DEFAULT 0,
                enabled     INTEGER DEFAULT 1
            )
        ''')

        # 兼容：给凭证分录加现金流量项目列
        try:
            cursor.execute("ALTER TABLE voucher_entries ADD COLUMN cf_item_id INTEGER DEFAULT 0")
        except Exception:
            pass

        conn.commit()

        # 导入会计制度的预置科目表
        self._import_default_accounts(conn, accounting_system, industry_code)

        conn.close()

    def _import_default_accounts(self, conn, accounting_system: str,
                                 industry_code: str = 'none'):
        """导入会计制度的预置科目，并按行业模板定制"""
        try:
            from accounting_systems.system_registry import get_system
            system = get_system(accounting_system)
            accounts = system.get_chart_of_accounts()

            # 应用行业模板
            if industry_code and industry_code != 'none':
                try:
                    from industry_templates import customize_accounts
                    accounts = customize_accounts(industry_code, accounts)
                except Exception:
                    pass  # 行业模板加载失败不影响建账

            now = datetime.now().isoformat()
            cursor = conn.cursor()
            for acct in accounts:
                cursor.execute('''
                    INSERT OR IGNORE INTO accounts
                    (acct_code, acct_name, acct_level, parent_code,
                     is_detail, acct_type, balance_side,
                     is_cash_equivalent, is_bank_account, enabled,
                     created_at, modified_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    acct['acct_code'], acct['acct_name'], acct['acct_level'],
                    acct.get('parent_code', ''),
                    acct['is_detail'], acct['acct_type'], acct['balance_side'],
                    acct.get('is_cash_eq', 0), acct.get('is_bank_acct', 0),
                    1, now, now
                ))
            conn.commit()
        except ImportError:
            pass

    def list_account_books(self, status: str = 'active') -> list:
        """获取账套列表"""
        conn = sqlite3.connect(self._get_master_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM account_books WHERE status = ? ORDER BY created_at DESC",
            (status,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]

    def get_account_book(self, book_id: str) -> Optional[dict]:
        """获取单个账套信息"""
        conn = sqlite3.connect(self._get_master_path())
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM account_books WHERE book_id = ?", (book_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    def get_book_db_path(self, book_id: str) -> str:
        """获取账套数据库文件的完整路径"""
        return self._get_book_path(book_id)

    def register_imported_book(self, book_id: str, book_name: str,
                               accounting_system: str = 'ENT_STANDARD',
                               company_name: str = '') -> bool:
        """注册导入的账套（用于U盘同步导入）"""
        conn = sqlite3.connect(self._get_master_path())
        now = datetime.now().isoformat()
        try:
            conn.execute('''
                INSERT OR REPLACE INTO account_books
                (book_id, book_name, accounting_system, company_name,
                 status, created_at, updated_at)
                VALUES (?, ?, ?, ?, 'active', ?, ?)
            ''', (book_id, book_name, accounting_system, company_name, now, now))
            conn.commit()
            conn.close()
            return True
        except Exception:
            conn.close()
            return False

    # ──────────────────────────────────────────
    #  账套数据库连接管理
    # ──────────────────────────────────────────

    def _get_book_path(self, book_id: str) -> str:
        """获取账套数据库文件路径"""
        conn = sqlite3.connect(self._get_master_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT db_file_name FROM account_books WHERE book_id = ?",
            (book_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return os.path.join(self.data_dir, row[0])
        raise FileNotFoundError(f"账套 {book_id} 不存在")

    def open_book(self, book_id: str) -> sqlite3.Connection:
        """打开指定账套"""
        book_path = self._get_book_path(book_id)
        if self._current_conn:
            self._current_conn.close()
        self._current_conn = sqlite3.connect(book_path)
        self._current_conn.execute("PRAGMA journal_mode=WAL")
        self._current_conn.execute("PRAGMA foreign_keys=ON")
        self._current_book_id = book_id
        return self._current_conn

    def close_book(self):
        """关闭当前账套"""
        if self._current_conn:
            self._current_conn.close()
            self._current_conn = None
            self._current_book_id = None

    def get_current_conn(self) -> Optional[sqlite3.Connection]:
        return self._current_conn

    def get_current_book_id(self) -> Optional[str]:
        return self._current_book_id

    # ──────────────────────────────────────────
    #  备份 / 恢复
    # ──────────────────────────────────────────

    def backup_book(self, book_id: str, backup_dir: str = None) -> str:
        """备份单个账套"""
        book_path = self._get_book_path(book_id)
        if backup_dir is None:
            backup_dir = os.path.join(self.data_dir, 'backup')
        os.makedirs(backup_dir, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{book_id}_backup_{timestamp}.db"
        backup_path = os.path.join(backup_dir, backup_name)

        # 如果是当前打开的，先关闭再拷贝
        need_reopen = False
        if self._current_book_id == book_id and self._current_conn:
            self._current_conn.close()
            self._current_conn = None
            self._current_book_id = None
            need_reopen = True

        shutil.copy2(book_path, backup_path)

        if need_reopen:
            self.open_book(book_id)

        return backup_path

    def restore_book(self, backup_path: str, book_id: str = None) -> str:
        """从备份恢复账套"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        # 如果没指定 book_id，从文件名推断
        if book_id is None:
            basename = os.path.basename(backup_path)
            book_id = basename.split('_backup_')[0]

        # 关闭当前连接（如果是该账套）
        if self._current_book_id == book_id and self._current_conn:
            self._current_conn.close()
            self._current_conn = None
            self._current_book_id = None

        # 覆盖原账套数据库
        book_path = self._get_book_path(book_id)
        shutil.copy2(backup_path, book_path)

        return book_id

    # ──────────────────────────────────────────
    #  便携 / 同步支持
    # ──────────────────────────────────────────

    def export_portable(self, book_id: str, target_path: str):
        """导出便携版数据库到U盘"""
        book_path = self._get_book_path(book_id)

        # 如果当前账套已打开，确保数据落盘
        if self._current_conn:
            self._current_conn.commit()

        shutil.copy2(book_path, target_path)

    def merge_portable(self, portable_path: str, book_id: str) -> dict:
        """
        将便携数据库合并回主数据库
        返回合并统计：{inserted, updated, conflicts}
        """
        # 导入同步引擎
        from .sync_engine import SyncEngine
        engine = SyncEngine(self)
        result = engine.merge(portable_path, book_id)
        return result
