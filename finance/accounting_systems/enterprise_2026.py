"""
======================================================
 enterprise_2026.py - 2026版企业会计制度（模拟新版）
======================================================
假设财政部2026年发布了新版制度，科目编码改为5位
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class Enterprise2026System(BaseAccountingSystem):
    """2026版企业会计制度（示例）"""

    code = 'ENT_2026'
    name = '2026版企业会计制度（新版示例）'
    depreciation_rule = 'next_month'  # 次月计提折旧

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═════ 资产类（新编码5位） ═════
            {'acct_code': '10001', 'acct_name': '库存现金', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '10002', 'acct_name': '银行存款', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset',
             'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1000201', 'acct_name': '工行存款', 'acct_level': 2,
             'parent_code': '10002', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '10013', 'acct_name': '应收账款', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '10014', 'acct_name': '预付账款', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '20001', 'acct_name': '库存商品', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '30001', 'acct_name': '固定资产', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '3000101', 'acct_name': '房屋建筑物', 'acct_level': 2,
             'parent_code': '30001', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '3000102', 'acct_name': '机器设备', 'acct_level': 2,
             'parent_code': '30001', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'debit'},

            # ═════ 负债类 ═════
            {'acct_code': '40001', 'acct_name': '短期借款', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'liability',
             'balance_side': 'credit'},
            {'acct_code': '40002', 'acct_name': '应付账款', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'liability',
             'balance_side': 'credit'},
            {'acct_code': '40003', 'acct_name': '应付职工薪酬', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'liability',
             'balance_side': 'credit'},
            {'acct_code': '40004', 'acct_name': '应交税费', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'liability',
             'balance_side': 'credit'},

            # ═════ 所有者权益类 ═════
            {'acct_code': '50001', 'acct_name': '实收资本', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'equity',
             'balance_side': 'credit'},
            {'acct_code': '50002', 'acct_name': '资本公积', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'equity',
             'balance_side': 'credit'},
            {'acct_code': '50003', 'acct_name': '本年利润', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'equity',
             'balance_side': 'credit'},

            # ═════ 成本类 ═════
            {'acct_code': '60001', 'acct_name': '生产成本', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'cost',
             'balance_side': 'debit'},
            {'acct_code': '60002', 'acct_name': '制造费用', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'cost',
             'balance_side': 'debit'},

            # ═════ 损益类 ═════
            {'acct_code': '70001', 'acct_name': '主营业务收入', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'income',
             'balance_side': 'credit'},
            {'acct_code': '70002', 'acct_name': '主营业务成本', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'expense',
             'balance_side': 'debit'},
            {'acct_code': '70003', 'acct_name': '管理费用', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'expense',
             'balance_side': 'debit'},
            {'acct_code': '70004', 'acct_name': '销售费用', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'expense',
             'balance_side': 'debit'},
            {'acct_code': '70005', 'acct_name': '财务费用', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'expense',
             'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> Dict:
        return {
            'balance': [
                {'name': '资产总计', 'formula': '10001+10002+10013+10014+20001+30001'},
            ],
        }

    def get_opening_balances(self) -> List[Dict]:
        return []