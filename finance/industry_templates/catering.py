"""
industry_templates/catering.py - 餐饮酒店企业模板
特有科目：原材料(食材)/库存商品(酒水)/主营业务成本等
"""

from typing import List, Dict
from industry_templates.base import BaseIndustryTemplate


class CateringTemplate(BaseIndustryTemplate):
    code = 'catering'
    name = '餐饮酒店企业'
    compatible_systems = ['ENT_STANDARD', 'ENT_SMALL']

    def customize(self, accounts: List[Dict]) -> List[Dict]:
        result = list(accounts)
        extra = [
            # 原材料明细（食材）
            {'acct_code': '140301', 'acct_name': '粮食及干货', 'acct_level': 2,
             'parent_code': '1403', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140302', 'acct_name': '鲜货及蔬菜', 'acct_level': 2,
             'parent_code': '1403', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140303', 'acct_name': '调料', 'acct_level': 2,
             'parent_code': '1403', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            # 库存商品（酒水饮料）
            {'acct_code': '140501', 'acct_name': '酒水', 'acct_level': 2,
             'parent_code': '1405', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140502', 'acct_name': '饮料', 'acct_level': 2,
             'parent_code': '1405', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140503', 'acct_name': '烟', 'acct_level': 2,
             'parent_code': '1405', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            # 主营业务成本明细
            {'acct_code': '640101', 'acct_name': '食材成本', 'acct_level': 2,
             'parent_code': '6401', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '640102', 'acct_name': '酒水成本', 'acct_level': 2,
             'parent_code': '6401', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            # 其他
            {'acct_code': '660201', 'acct_name': '餐具及消耗品', 'acct_level': 2,
             'parent_code': '6602', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]
        existing = {a['acct_code'] for a in result}
        for a in extra:
            if a['acct_code'] not in existing:
                result.append(a)
        return result