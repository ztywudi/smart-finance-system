"""
==============================================
 labor_union.py - 工会会计制度预设数据
==============================================
分基层工会和县级以上工会两套科目表
5要素：资产/负债/净资产/收入/支出
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class LaborUnionSystem(BaseAccountingSystem):
    """工会会计制度"""

    code = 'LABOR_UNION'
    name = '工会会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ══════════ 资产类 ══════════
            {'acct_code': '101', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '102', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '111', 'acct_name': '零余额账户用款额度', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '112', 'acct_name': '财政应返还额度', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '121', 'acct_name': '借出款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '131', 'acct_name': '应收上级经费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '132', 'acct_name': '应收下级经费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '135', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '141', 'acct_name': '库存物品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '151', 'acct_name': '投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ══════════ 负债类 ══════════
            {'acct_code': '201', 'acct_name': '应付工资（离退休费）', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '202', 'acct_name': '应付地方（部门）津贴补贴', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '203', 'acct_name': '应付其他个人收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '211', 'acct_name': '借入款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221', 'acct_name': '应付上级经费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '222', 'acct_name': '应付下级经费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '225', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '231', 'acct_name': '代管经费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ══════════ 净资产类 ══════════
            {'acct_code': '301', 'acct_name': '固定基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '302', 'acct_name': '在建工程占用资金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '303', 'acct_name': '投资基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '311', 'acct_name': '工会资金结转', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '321', 'acct_name': '工会资金结余', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},

            # ══════════ 收入类 ══════════
            {'acct_code': '401', 'acct_name': '会费收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '402', 'acct_name': '拨缴经费收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '403', 'acct_name': '上级补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '404', 'acct_name': '政府补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '405', 'acct_name': '行政补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '406', 'acct_name': '事业收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '407', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '408', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},

            # ══════════ 支出类 ══════════
            {'acct_code': '501', 'acct_name': '职工活动支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '502', 'acct_name': '维权支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '503', 'acct_name': '业务支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '504', 'acct_name': '行政支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '505', 'acct_name': '资本性支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '506', 'acct_name': '补助下级支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '507', 'acct_name': '事业支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
            {'acct_code': '508', 'acct_name': '其他支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expenditure', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '工会经费收支情况表', 'report_type': 'income_statement'},
        ]
