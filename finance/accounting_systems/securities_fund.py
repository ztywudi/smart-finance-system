"""
===================================================
 securities_fund.py - 证券投资基金会计核算预设数据
===================================================
特点：每日估值、每日净值计算
      资产主要按金融资产分类（交易性/持有至到期等）
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class SecuritiesFundSystem(BaseAccountingSystem):
    """证券投资基金会计核算业务指引"""

    code = 'SECURITIES_FUND'
    name = '证券投资基金会计核算业务指引'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1021', 'acct_name': '清算备付金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '102101', 'acct_name': '交收备付金', 'acct_level': 2, 'parent_code': '1021', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1031', 'acct_name': '交易保证金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '股票投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '股票投资成本', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110102', 'acct_name': '股票投资估值增值', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '债券投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120101', 'acct_name': '债券投资成本', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120102', 'acct_name': '债券投资估值增值', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120103', 'acct_name': '债券投资利息调整', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1301', 'acct_name': '权证投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1401', 'acct_name': '资产支持证券投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1501', 'acct_name': '买入返售金融资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150101', 'acct_name': '买入返售证券', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150102', 'acct_name': '买入返售票据', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1601', 'acct_name': '应收利息', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160101', 'acct_name': '应收银行存款利息', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160102', 'acct_name': '应收债券利息', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160103', 'acct_name': '应收买入返售利息', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1602', 'acct_name': '应收股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1603', 'acct_name': '应收申购款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1604', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1701', 'acct_name': '其他资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2001', 'acct_name': '应付赎回款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2002', 'acct_name': '应付赎回费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2101', 'acct_name': '应付管理人报酬', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2102', 'acct_name': '应付托管费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2103', 'acct_name': '应付销售服务费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2104', 'acct_name': '应付交易费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2105', 'acct_name': '应付利息', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2106', 'acct_name': '应付利润', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2107', 'acct_name': '应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2301', 'acct_name': '卖出回购金融资产款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2401', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 持有人权益类 ═══════════════
            {'acct_code': '3001', 'acct_name': '实收基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3101', 'acct_name': '损益平准金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3201', 'acct_name': '未分配利润', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '320101', 'acct_name': '已实现损益', 'acct_level': 2, 'parent_code': '3201', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '320102', 'acct_name': '未实现损益', 'acct_level': 2, 'parent_code': '3201', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '4001', 'acct_name': '利息收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400101', 'acct_name': '存款利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400102', 'acct_name': '债券利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400103', 'acct_name': '买入返售利息收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4002', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400201', 'acct_name': '股票投资收益', 'acct_level': 2, 'parent_code': '4002', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400202', 'acct_name': '债券投资收益', 'acct_level': 2, 'parent_code': '4002', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400203', 'acct_name': '权证投资收益', 'acct_level': 2, 'parent_code': '4002', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400204', 'acct_name': '资产支持证券投资收益', 'acct_level': 2, 'parent_code': '4002', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4003', 'acct_name': '公允价值变动损益', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400301', 'acct_name': '股票估值增值', 'acct_level': 2, 'parent_code': '4003', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400302', 'acct_name': '债券估值增值', 'acct_level': 2, 'parent_code': '4003', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4004', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 费用类 ═══════════════
            {'acct_code': '5001', 'acct_name': '管理人报酬', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5002', 'acct_name': '托管费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5003', 'acct_name': '销售服务费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5004', 'acct_name': '交易费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500401', 'acct_name': '股票交易费用', 'acct_level': 2, 'parent_code': '5004', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500402', 'acct_name': '债券交易费用', 'acct_level': 2, 'parent_code': '5004', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5005', 'acct_name': '利息支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500501', 'acct_name': '卖出回购利息支出', 'acct_level': 2, 'parent_code': '5005', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5006', 'acct_name': '其他费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5007', 'acct_name': '所得税费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '利润表（经营业绩表）', 'report_type': 'income_statement'},
            {'report_id': 'HOLDER_CHANGE', 'report_name': '持有人权益变动表', 'report_type': 'equity_changes'},
            {'report_id': 'NET_VALUE', 'report_name': '基金份额净值变动表', 'report_type': 'other'},
        ]

    def get_voucher_types(self) -> List[Dict]:
        return [
            {'type_code': '记', 'type_name': '记账凭证'},
            {'type_code': '估', 'type_name': '估值凭证'},
        ]