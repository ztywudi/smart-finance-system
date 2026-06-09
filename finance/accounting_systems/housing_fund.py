"""
===================================================
 housing_fund.py - 住房公积金会计制度预设数据
===================================================
特点：住房公积金管理中心专用
      归集/提取/贷款三大业务
      5要素：资产/负债/净资产/收入/支出
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class HousingFundSystem(BaseAccountingSystem):
    """住房公积金会计制度"""

    code = 'HOUSING_FUND'
    name = '住房公积金会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '住房公积金存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100101', 'acct_name': '活期存款', 'acct_level': 2, 'parent_code': '1001', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100102', 'acct_name': '定期存款', 'acct_level': 2, 'parent_code': '1001', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1002', 'acct_name': '增值收益存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1101', 'acct_name': '应收利息', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '应收住房公积金存款利息', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110102', 'acct_name': '应收委托贷款利息', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110103', 'acct_name': '应收国家债券利息', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '委托贷款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120101', 'acct_name': '个人住房公积金贷款', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120102', 'acct_name': '保障性住房项目贷款', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1202', 'acct_name': '逾期贷款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1203', 'acct_name': '贷款损失准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1301', 'acct_name': '国家债券', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1401', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2001', 'acct_name': '应付利息', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '200101', 'acct_name': '应付个人公积金利息', 'acct_level': 2, 'parent_code': '2001', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '200102', 'acct_name': '应付贷款利息', 'acct_level': 2, 'parent_code': '2001', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2002', 'acct_name': '专项应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2003', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 净资产类 ═══════════════
            {'acct_code': '3001', 'acct_name': '住房公积金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3002', 'acct_name': '增值收益', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '300201', 'acct_name': '待分配增值收益', 'acct_level': 2, 'parent_code': '3002', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '300202', 'acct_name': '已分配增值收益', 'acct_level': 2, 'parent_code': '3002', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3003', 'acct_name': '贷款风险准备金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '4001', 'acct_name': '业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400101', 'acct_name': '住房公积金利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400102', 'acct_name': '委托贷款利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400103', 'acct_name': '国家债券利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400104', 'acct_name': '其他收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 支出类 ═══════════════
            {'acct_code': '5001', 'acct_name': '业务支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500101', 'acct_name': '住房公积金利息支出', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '手续费支出', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500103', 'acct_name': '其他支出', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5002', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500201', 'acct_name': '人员经费', 'acct_level': 2, 'parent_code': '5002', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500202', 'acct_name': '公用经费', 'acct_level': 2, 'parent_code': '5002', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '增值收益表', 'report_type': 'income_statement'},
            {'report_id': 'DISTRIBUTION', 'report_name': '增值收益分配表', 'report_type': 'other'},
        ]