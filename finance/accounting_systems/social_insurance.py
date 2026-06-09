"""
===================================================
 social_insurance.py - 社会保险基金会计制度预设数据
===================================================
特点：按险种独立核算，专款专用
      5要素：资产/负债/基金/收入/支出
      适用：企业职工基本养老保险、城乡居民基本养老保险、
           机关事业单位基本养老保险、职工基本医疗保险、
           城乡居民基本医疗保险、工伤保险、失业保险
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class SocialInsuranceSystem(BaseAccountingSystem):
    """社会保险基金会计制度"""

    code = 'SOCIAL_INSUR'
    name = '社会保险基金会计制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '收入户存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1003', 'acct_name': '支出户存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1004', 'acct_name': '财政专户存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1005', 'acct_name': '国库存款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '暂付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '预付账款', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110102', 'acct_name': '其他暂付款', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '债券投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120101', 'acct_name': '国债投资', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120102', 'acct_name': '其他债券投资', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1301', 'acct_name': '委托投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2001', 'acct_name': '暂收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '200101', 'acct_name': '预收保险费', 'acct_level': 2, 'parent_code': '2001', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '200102', 'acct_name': '其他暂收款', 'acct_level': 2, 'parent_code': '2001', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2002', 'acct_name': '应付利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2003', 'acct_name': '应付受托管理费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2004', 'acct_name': '应付托管费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2005', 'acct_name': '应付投资管理费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 基金类 ═══════════════
            {'acct_code': '3001', 'acct_name': '基本养老保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '300101', 'acct_name': '企业职工基本养老保险基金', 'acct_level': 2, 'parent_code': '3001', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '300102', 'acct_name': '城乡居民基本养老保险基金', 'acct_level': 2, 'parent_code': '3001', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '300103', 'acct_name': '机关事业单位基本养老保险基金', 'acct_level': 2, 'parent_code': '3001', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3002', 'acct_name': '基本医疗保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '300201', 'acct_name': '职工基本医疗保险基金', 'acct_level': 2, 'parent_code': '3002', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '300202', 'acct_name': '城乡居民基本医疗保险基金', 'acct_level': 2, 'parent_code': '3002', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3003', 'acct_name': '工伤保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3004', 'acct_name': '失业保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3005', 'acct_name': '生育保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3006', 'acct_name': '其他社会保险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3101', 'acct_name': '风险基金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},
            {'acct_code': '3102', 'acct_name': '储备金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'fund', 'balance_side': 'credit'},

            # ═══════════════ 收入类 ═══════════════
            {'acct_code': '4001', 'acct_name': '社会保险费收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400101', 'acct_name': '单位缴费收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '400102', 'acct_name': '个人缴费收入', 'acct_level': 2, 'parent_code': '4001', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4002', 'acct_name': '财政补贴收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4003', 'acct_name': '利息收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4004', 'acct_name': '委托投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4005', 'acct_name': '转移收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4006', 'acct_name': '上级补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4007', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},

            # ═══════════════ 支出类 ═══════════════
            {'acct_code': '5001', 'acct_name': '社会保险待遇支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500101', 'acct_name': '基本养老金', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '医疗费用', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500103', 'acct_name': '工伤待遇', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500104', 'acct_name': '失业保险金', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500105', 'acct_name': '生育待遇', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5002', 'acct_name': '转移支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5003', 'acct_name': '补助下级支出', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5004', 'acct_name': '委托投资管理费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5005', 'acct_name': '其他支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '收支表', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
        ]