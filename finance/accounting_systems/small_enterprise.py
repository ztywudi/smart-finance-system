"""
===================================================
 small_enterprise.py - 小企业会计准则预设数据
===================================================
编码规则：4位固定编码
特点：科目简化，不计提减值，不设共同类
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class SmallEnterpriseSystem(BaseAccountingSystem):
    """小企业会计准则"""

    code = 'ENT_SMALL'
    name = '小企业会计准则'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # 资产类
            {'acct_code': '1001', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1012', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '短期投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1121', 'acct_name': '应收票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1122', 'acct_name': '应收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1123', 'acct_name': '预付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1131', 'acct_name': '应收股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1132', 'acct_name': '应收利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1221', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            # 小企业不计提坏账准备 → 无 1231
            {'acct_code': '1401', 'acct_name': '在途物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1402', 'acct_name': '原材料', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1404', 'acct_name': '库存商品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            # 无存货跌价准备
            {'acct_code': '1501', 'acct_name': '长期债券投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1511', 'acct_name': '长期股权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1601', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1602', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            # 无固定资产减值准备
            {'acct_code': '1604', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1605', 'acct_name': '工程物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1606', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1701', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1702', 'acct_name': '累计摊销', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1801', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            # 无递延所得税资产

            # 负债类
            {'acct_code': '2001', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '应付票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2202', 'acct_name': '应付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2203', 'acct_name': '预收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2211', 'acct_name': '应付职工薪酬', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2221', 'acct_name': '应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2231', 'acct_name': '应付利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2232', 'acct_name': '应付利润', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2241', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2401', 'acct_name': '递延收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2501', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2701', 'acct_name': '长期应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # 所有者权益类
            {'acct_code': '3001', 'acct_name': '实收资本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3002', 'acct_name': '资本公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3101', 'acct_name': '盈余公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3103', 'acct_name': '本年利润', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3104', 'acct_name': '利润分配', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},

            # 成本类
            {'acct_code': '4001', 'acct_name': '生产成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '4101', 'acct_name': '制造费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '4201', 'acct_name': '研发支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},

            # 损益类
            {'acct_code': '5001', 'acct_name': '主营业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5051', 'acct_name': '其他业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5111', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5301', 'acct_name': '营业外收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5401', 'acct_name': '主营业务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5402', 'acct_name': '其他业务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5403', 'acct_name': '税金及附加', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5601', 'acct_name': '销售费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5602', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5603', 'acct_name': '财务费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5711', 'acct_name': '营业外支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5801', 'acct_name': '所得税费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '利润表', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
        ]
