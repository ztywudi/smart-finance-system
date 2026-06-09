"""
===================================================
 farmer_coop.py - 农民专业合作社财务会计制度预设数据
===================================================
特点：成员账户核算、盈余分配（按交易量返还+按股分红）
      5要素：资产/负债/所有者权益/收入/支出
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class FarmerCoopSystem(BaseAccountingSystem):
    """农民专业合作社财务会计制度"""

    code = 'FARMER_COOP'
    name = '农民专业合作社财务会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '101', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '102', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '10201', 'acct_name': '基本户', 'acct_level': 2, 'parent_code': '102', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '10202', 'acct_name': '专项户', 'acct_level': 2, 'parent_code': '102', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '103', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '111', 'acct_name': '应收款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '11101', 'acct_name': '成员应收款', 'acct_level': 2, 'parent_code': '111', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '11102', 'acct_name': '外部应收款', 'acct_level': 2, 'parent_code': '111', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '112', 'acct_name': '内部往来', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '121', 'acct_name': '产品物资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12101', 'acct_name': '原材料', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12102', 'acct_name': '农产品', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12103', 'acct_name': '加工产品', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12104', 'acct_name': '包装物', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '124', 'acct_name': '委托加工物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '125', 'acct_name': '委托代销商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '126', 'acct_name': '受托代销商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '127', 'acct_name': '受托代购商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '131', 'acct_name': '对外投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13101', 'acct_name': '股权投资', 'acct_level': 2, 'parent_code': '131', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13102', 'acct_name': '债权投资', 'acct_level': 2, 'parent_code': '131', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '141', 'acct_name': '牲畜（禽）资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14101', 'acct_name': '幼畜及育肥畜', 'acct_level': 2, 'parent_code': '141', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14102', 'acct_name': '产役畜', 'acct_level': 2, 'parent_code': '141', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '142', 'acct_name': '林木资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14201', 'acct_name': '经济林木', 'acct_level': 2, 'parent_code': '142', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14202', 'acct_name': '非经济林木', 'acct_level': 2, 'parent_code': '142', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '151', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15101', 'acct_name': '房屋', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15102', 'acct_name': '建筑物', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15103', 'acct_name': '设备', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15104', 'acct_name': '运输工具', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '152', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '153', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '154', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '161', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '162', 'acct_name': '累计摊销', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '171', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '181', 'acct_name': '待处理财产损溢', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '191', 'acct_name': '待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '201', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '202', 'acct_name': '应付款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '20201', 'acct_name': '成员应付款', 'acct_level': 2, 'parent_code': '202', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '20202', 'acct_name': '外部应付款', 'acct_level': 2, 'parent_code': '202', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '203', 'acct_name': '应付工资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '204', 'acct_name': '应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '211', 'acct_name': '应付盈余返还', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '212', 'acct_name': '应付剩余盈余', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '231', 'acct_name': '专项应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 所有者权益类 ═══════════════
            {'acct_code': '301', 'acct_name': '股金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30101', 'acct_name': '成员股金', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30102', 'acct_name': '国家股金', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30103', 'acct_name': '法人股金', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '302', 'acct_name': '专项基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '311', 'acct_name': '资本公积', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '312', 'acct_name': '盈余公积', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '321', 'acct_name': '盈余分配', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '32101', 'acct_name': '未分配盈余', 'acct_level': 2, 'parent_code': '321', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '401', 'acct_name': '经营收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40101', 'acct_name': '农产品销售收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40102', 'acct_name': '加工收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40103', 'acct_name': '代购代销收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40104', 'acct_name': '服务收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '411', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '421', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 支出类 ═══════════════
            {'acct_code': '501', 'acct_name': '经营支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50101', 'acct_name': '农产品成本', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50102', 'acct_name': '加工材料', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50103', 'acct_name': '包装费', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50104', 'acct_name': '运输费', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '511', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51101', 'acct_name': '办公费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51102', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51103', 'acct_name': '折旧费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51104', 'acct_name': '工资', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '521', 'acct_name': '其他支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '531', 'acct_name': '税金及附加', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '盈余表', 'report_type': 'income_statement'},
            {'report_id': 'DISTRIBUTION', 'report_name': '盈余分配表', 'report_type': 'other'},
            {'report_id': 'MEMBER_ACCT', 'report_name': '成员账户报表', 'report_type': 'other'},
        ]

    def get_aux_types(self) -> List[Dict]:
        return [
            {'type_name': '成员'},
            {'type_name': '产品类型'},
            {'type_name': '项目'},
            {'type_name': '客户'},
        ]