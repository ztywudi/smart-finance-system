"""
==========================================
 core/cashflow_service.py - 现金流量服务
==========================================
功能：
  - 标准现金流量项目（21项）初始化
  - 凭证现金流量标注/查询
  - 现金流量表生成
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime
from typing import List, Dict, Tuple


class CashFlowService:
    """现金流量服务"""

    # 标准现金流量项目（企业会计准则）
    DEFAULT_ITEMS = [
        # 经营活动 - 流入
        ('CF01', '销售商品、提供劳务收到的现金', 'operating', 1),
        ('CF02', '收到的税费返还', 'operating', 2),
        ('CF03', '收到其他与经营活动有关的现金', 'operating', 3),
        # 经营活动 - 流出
        ('CF04', '购买商品、接受劳务支付的现金', 'operating', 4),
        ('CF05', '支付给职工以及为职工支付的现金', 'operating', 5),
        ('CF06', '支付的各项税费', 'operating', 6),
        ('CF07', '支付其他与经营活动有关的现金', 'operating', 7),
        # 投资活动 - 流入
        ('CF08', '收回投资收到的现金', 'investing', 8),
        ('CF09', '取得投资收益收到的现金', 'investing', 9),
        ('CF10', '处置固定资产、无形资产和其他长期资产收回的现金', 'investing', 10),
        ('CF11', '处置子公司及其他营业单位收到的现金', 'investing', 11),
        ('CF12', '收到其他与投资活动有关的现金', 'investing', 12),
        # 投资活动 - 流出
        ('CF13', '购建固定资产、无形资产和其他长期资产支付的现金', 'investing', 13),
        ('CF14', '投资支付的现金', 'investing', 14),
        ('CF15', '支付其他与投资活动有关的现金', 'investing', 15),
        # 筹资活动 - 流入
        ('CF16', '吸收投资收到的现金', 'financing', 16),
        ('CF17', '取得借款收到的现金', 'financing', 17),
        ('CF18', '收到其他与筹资活动有关的现金', 'financing', 18),
        # 筹资活动 - 流出
        ('CF19', '偿还债务支付的现金', 'financing', 19),
        ('CF20', '分配股利、利润或偿付利息支付的现金', 'financing', 20),
        ('CF21', '支付其他与筹资活动有关的现金', 'financing', 21),
    ]

    # 现金/银行科目编码前缀
    CASH_ACCT_PREFIXES = ('1001', '1002')

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def init_default_items(self):
        """初始化标准现金流量项目"""
        conn = self.db_manager.get_current_conn()
        if not conn: return
        cur = conn.execute("SELECT COUNT(*) FROM cash_flow_items")
        if cur.fetchone()[0] > 0: return

        for code, name, ctype, order in self.DEFAULT_ITEMS:
            conn.execute('''
                INSERT INTO cash_flow_items (cf_code, cf_name, cf_type, cf_order, enabled)
                VALUES (?, ?, ?, ?, 1)
            ''', (code, name, ctype, order))
        conn.commit()

    def get_items(self, cf_type: str = '') -> List[Dict]:
        """获取现金流量项目"""
        conn = self.db_manager.get_current_conn()
        if not conn: return []
        self.init_default_items()
        if cf_type:
            cur = conn.execute(
                "SELECT * FROM cash_flow_items WHERE cf_type=? AND enabled=1 ORDER BY cf_order",
                (cf_type,))
        else:
            cur = conn.execute(
                "SELECT * FROM cash_flow_items WHERE enabled=1 ORDER BY cf_order")
        cols = [d[0] for d in cur.description]
        return [dict(zip(cols, r)) for r in cur.fetchall()]

    def is_cash_acct(self, acct_code: str) -> bool:
        """判断科目是否为现金/银行类"""
        if not acct_code: return False
        return any(acct_code.startswith(p) for p in self.CASH_ACCT_PREFIXES)

    def get_entry_cf_item(self, entry_id: int) -> int:
        """获取分录的现金流量项目"""
        conn = self.db_manager.get_current_conn()
        if not conn: return 0
        cur = conn.execute(
            "SELECT cf_item_id FROM voucher_entries WHERE entry_id=?", (entry_id,))
        row = cur.fetchone()
        return row[0] if row else 0

    def set_entry_cf_item(self, entry_id: int, cf_item_id: int):
        """设置分录的现金流量项目"""
        conn = self.db_manager.get_current_conn()
        conn.execute("UPDATE voucher_entries SET cf_item_id=? WHERE entry_id=?",
                     (cf_item_id, entry_id))
        conn.commit()

    def get_cash_flow_report(self, period_from: str, period_to: str) -> Dict:
        """
        生成现金流量表
        返回结构化数据
        """
        conn = self.db_manager.get_current_conn()
        if not conn: return {}

        items = self.get_items()
        type_map = {'operating': '经营活动', 'investing': '投资活动', 'financing': '筹资活动'}
        result = {}

        for item in items:
            cf_id = item['cf_id']
            cur = conn.execute('''
                SELECT COALESCE(SUM(
                    CASE WHEN e.debit_amount > 0 THEN e.debit_amount
                         ELSE -e.credit_amount END
                ), 0)
                FROM voucher_entries e
                JOIN vouchers v ON e.voucher_id = v.voucher_id
                WHERE e.cf_item_id=? AND v.status='posted'
                AND v.period >= ? AND v.period <= ?
            ''', (cf_id, period_from, period_to))
            amount = cur.fetchone()[0]

            ctype = type_map.get(item['cf_type'], item['cf_type'])
            if ctype not in result:
                result[ctype] = []
            result[ctype].append({
                'cf_code': item['cf_code'],
                'cf_name': item['cf_name'],
                'amount': amount,
            })

        return result

    def auto_assign_cf_item(self, acct_code: str,
                            opposite_acct: str = '',
                            summary: str = '') -> int:
        """
        自动匹配现金流量项目（基于对方科目、摘要）
        返回 cf_item_id，0表示无法自动匹配
        """
        items = {i['cf_code']: i for i in self.get_items()}
        if not items: return 0

        # 常见匹配规则
        rules = [
            # 销售收款
            (('1001', '1002'), ('6001', '6002', '6051'), 'CF01'),
            # 税费返还
            (('1001', '1002'), ('6801', '2221'), 'CF02'),
            # 工资支付
            (('1001', '1002'), ('2211', '660201'), 'CF05'),
            # 税费支付
            (('1001', '1002'), ('2221',), 'CF06'),
            # 购建固定资产
            (('1001', '1002'), ('1601', '1604', '1605'), 'CF13'),
            # 借款
            (('1001', '1002'), ('2001', '2501'), 'CF17'),
            # 还债
            (('1001', '1002'), ('2001',), 'CF19'),
        ]

        for cash_prefixes, opp_prefixes, cf_code in rules:
            if any(acct_code.startswith(p) for p in cash_prefixes):
                if any(opposite_acct.startswith(p) for p in opp_prefixes):
                    item = items.get(cf_code)
                    if item: return item['cf_id']

        return 0  # 无法自动匹配