"""
===================================================
 rural_collective.py - 农村集体经济组织会计制度预设数据
===================================================
2023修订版，2024.1.1施行
特点：含资源性资产（耕地/林地/水面等）核算
      5要素：资产/负债/所有者权益/收入/费用
      编码规则：3-2结构，5位编码
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class RuralCollectiveSystem(BaseAccountingSystem):
    """农村集体经济组织会计制度"""

    code = 'RURAL_COLLECTIVE'
    name = '农村集体经济组织会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '101', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '102', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '10201', 'acct_name': '基本存款账户', 'acct_level': 2, 'parent_code': '102', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '10202', 'acct_name': '专用存款账户', 'acct_level': 2, 'parent_code': '102', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '111', 'acct_name': '短期投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '112', 'acct_name': '应收款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '11201', 'acct_name': '应收外部单位', 'acct_level': 2, 'parent_code': '112', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '11202', 'acct_name': '应收农户', 'acct_level': 2, 'parent_code': '112', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '113', 'acct_name': '内部往来', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '121', 'acct_name': '库存物资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12101', 'acct_name': '种子', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12102', 'acct_name': '化肥', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12103', 'acct_name': '农药', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '12104', 'acct_name': '其他物资', 'acct_level': 2, 'parent_code': '121', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '131', 'acct_name': '牲畜（禽）资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13101', 'acct_name': '幼畜及育肥畜', 'acct_level': 2, 'parent_code': '131', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13102', 'acct_name': '产役畜', 'acct_level': 2, 'parent_code': '131', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '132', 'acct_name': '林木资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13201', 'acct_name': '经济林木', 'acct_level': 2, 'parent_code': '132', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '13202', 'acct_name': '非经济林木', 'acct_level': 2, 'parent_code': '132', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '141', 'acct_name': '长期投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14101', 'acct_name': '股权投资', 'acct_level': 2, 'parent_code': '141', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '14102', 'acct_name': '债权投资', 'acct_level': 2, 'parent_code': '141', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '151', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15101', 'acct_name': '房屋', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15102', 'acct_name': '建筑物', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15103', 'acct_name': '机器设备', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15104', 'acct_name': '农机具', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15105', 'acct_name': '运输工具', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '15106', 'acct_name': '其他固定资产', 'acct_level': 2, 'parent_code': '151', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '152', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '15201', 'acct_name': '房屋折旧', 'acct_level': 2, 'parent_code': '152', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '15202', 'acct_name': '设备折旧', 'acct_level': 2, 'parent_code': '152', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '153', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '154', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '161', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '16101', 'acct_name': '土地使用权', 'acct_level': 2, 'parent_code': '161', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '16102', 'acct_name': '其他无形资产', 'acct_level': 2, 'parent_code': '161', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '162', 'acct_name': '累计摊销', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '171', 'acct_name': '待处理财产损溢', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '17101', 'acct_name': '待处理流动资产损溢', 'acct_level': 2, 'parent_code': '171', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '17102', 'acct_name': '待处理固定资产损溢', 'acct_level': 2, 'parent_code': '171', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 资源性资产明细 ═══════════════
            {'acct_code': '181', 'acct_name': '资源性资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18101', 'acct_name': '耕地', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18102', 'acct_name': '林地', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18103', 'acct_name': '园地', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18104', 'acct_name': '草地', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18105', 'acct_name': '水面', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '18106', 'acct_name': '其他资源性资产', 'acct_level': 2, 'parent_code': '181', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '201', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '202', 'acct_name': '应付款项', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '20201', 'acct_name': '应付外部单位', 'acct_level': 2, 'parent_code': '202', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '20202', 'acct_name': '应付农户', 'acct_level': 2, 'parent_code': '202', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '203', 'acct_name': '应付工资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '204', 'acct_name': '应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '211', 'acct_name': '内部往来', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '212', 'acct_name': '长期借款及应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '21201', 'acct_name': '长期借款', 'acct_level': 2, 'parent_code': '212', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '21202', 'acct_name': '长期应付款', 'acct_level': 2, 'parent_code': '212', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221', 'acct_name': '专项应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 所有者权益类 ═══════════════
            {'acct_code': '301', 'acct_name': '资本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30101', 'acct_name': '村集体投入', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30102', 'acct_name': '成员入股', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '30103', 'acct_name': '国家拨款形成', 'acct_level': 2, 'parent_code': '301', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '302', 'acct_name': '公积公益金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '311', 'acct_name': '未分配收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '401', 'acct_name': '经营收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40101', 'acct_name': '农产品销售收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40102', 'acct_name': '租赁收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '40103', 'acct_name': '服务收入', 'acct_level': 2, 'parent_code': '401', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '411', 'acct_name': '发包及上交收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '41101', 'acct_name': '承包金收入', 'acct_level': 2, 'parent_code': '411', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '41102', 'acct_name': '企业上交利润', 'acct_level': 2, 'parent_code': '411', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '421', 'acct_name': '补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '42101', 'acct_name': '财政补助', 'acct_level': 2, 'parent_code': '421', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '42102', 'acct_name': '其他补助', 'acct_level': 2, 'parent_code': '421', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '431', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '441', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 费用类 ═══════════════
            {'acct_code': '501', 'acct_name': '经营支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50101', 'acct_name': '农产品成本', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '50102', 'acct_name': '租赁成本', 'acct_level': 2, 'parent_code': '501', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '511', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51101', 'acct_name': '办公费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51102', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51103', 'acct_name': '折旧费', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '51104', 'acct_name': '干部报酬', 'acct_level': 2, 'parent_code': '511', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '521', 'acct_name': '其他支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '531', 'acct_name': '税金及附加', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '收益及收益分配表', 'report_type': 'income_statement'},
        ]

    def get_aux_types(self) -> List[Dict]:
        return [
            {'type_name': '农户'},
            {'type_name': '村组'},
            {'type_name': '项目'},
            {'type_name': '资源类型'},
        ]