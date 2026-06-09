"""
===================================================
 non_profit.py - 民间非营利组织会计制度预设数据
===================================================
5要素：资产/负债/净资产/收入/费用
特点：无"所有者权益"改"净资产"
     分"限定性"和"非限定性"
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class NonProfitSystem(BaseAccountingSystem):
    """民间非营利组织会计制度"""

    code = 'NON_PROFIT'
    name = '民间非营利组织会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100201', 'acct_name': '人民币存款', 'acct_level': 2, 'parent_code': '1002', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100202', 'acct_name': '外币存款', 'acct_level': 2, 'parent_code': '1002', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1011', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '短期投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '股票投资', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110102', 'acct_name': '债券投资', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1111', 'acct_name': '短期投资跌价准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1121', 'acct_name': '应收票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1122', 'acct_name': '应收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1123', 'acct_name': '预付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1124', 'acct_name': '应收其他款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1125', 'acct_name': '坏账准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1141', 'acct_name': '受托代理资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '存货', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120101', 'acct_name': '材料', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120102', 'acct_name': '库存商品', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1202', 'acct_name': '存货跌价准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1301', 'acct_name': '待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1401', 'acct_name': '长期股权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140101', 'acct_name': '股权投资', 'acct_level': 2, 'parent_code': '1401', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1402', 'acct_name': '长期债权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140201', 'acct_name': '债券投资', 'acct_level': 2, 'parent_code': '1402', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1501', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150101', 'acct_name': '房屋建筑物', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150102', 'acct_name': '设备', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150103', 'acct_name': '交通工具', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1502', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '150201', 'acct_name': '房屋建筑物折旧', 'acct_level': 2, 'parent_code': '1502', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '150202', 'acct_name': '设备折旧', 'acct_level': 2, 'parent_code': '1502', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1505', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1506', 'acct_name': '文物文化资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1509', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1601', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1701', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1801', 'acct_name': '受托代理资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2101', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2102', 'acct_name': '应付款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '210201', 'acct_name': '应付账款', 'acct_level': 2, 'parent_code': '2102', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '210202', 'acct_name': '应付票据', 'acct_level': 2, 'parent_code': '2102', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2103', 'acct_name': '应付工资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2104', 'acct_name': '应交税金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2105', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2106', 'acct_name': '预提费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2202', 'acct_name': '长期应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2301', 'acct_name': '受托代理负债', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 净资产类 ═══════════════
            {'acct_code': '3101', 'acct_name': '非限定性净资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '310101', 'acct_name': '非限定性净资产（初始）', 'acct_level': 2, 'parent_code': '3101', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '310102', 'acct_name': '非限定性净资产（期末）', 'acct_level': 2, 'parent_code': '3101', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3102', 'acct_name': '限定性净资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '4101', 'acct_name': '捐赠收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '410101', 'acct_name': '限定性', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '410102', 'acct_name': '非限定性', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4201', 'acct_name': '会费收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '420101', 'acct_name': '限定性', 'acct_level': 2, 'parent_code': '4201', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '420102', 'acct_name': '非限定性', 'acct_level': 2, 'parent_code': '4201', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4301', 'acct_name': '提供服务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4401', 'acct_name': '政府补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '440101', 'acct_name': '限定性', 'acct_level': 2, 'parent_code': '4401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '440102', 'acct_name': '非限定性', 'acct_level': 2, 'parent_code': '4401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4501', 'acct_name': '商品销售收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4601', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4901', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 费用类 ═══════════════
            {'acct_code': '5101', 'acct_name': '业务活动成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '510101', 'acct_name': '项目直接成本', 'acct_level': 2, 'parent_code': '5101', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '510102', 'acct_name': '服务采购', 'acct_level': 2, 'parent_code': '5101', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5201', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '520101', 'acct_name': '办公费', 'acct_level': 2, 'parent_code': '5201', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '520102', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '5201', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '520103', 'acct_name': '折旧费', 'acct_level': 2, 'parent_code': '5201', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '520104', 'acct_name': '工资福利', 'acct_level': 2, 'parent_code': '5201', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5301', 'acct_name': '筹资费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '530101', 'acct_name': '利息费用', 'acct_level': 2, 'parent_code': '5301', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5401', 'acct_name': '其他费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '业务活动表（收入费用表）', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
        ]