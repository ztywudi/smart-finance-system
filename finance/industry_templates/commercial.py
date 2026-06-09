"""
industry_templates/commercial.py - 商品流通企业模板
特有科目：商品进销差价 / 存货跌价准备调整等
"""

from typing import List, Dict
from industry_templates.base import BaseIndustryTemplate


class CommercialTemplate(BaseIndustryTemplate):
    code = 'commercial'
    name = '商品流通企业'
    compatible_systems = ['ENT_STANDARD', 'ENT_SMALL']

    def customize(self, accounts: List[Dict]) -> List[Dict]:
        result = list(accounts)
        extra = [
            {'acct_code': '1404', 'acct_name': '商品进销差价', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset',
             'balance_side': 'credit'},
            {'acct_code': '1407', 'acct_name': '发出商品', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1411', 'acct_name': '委托代销商品', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1412', 'acct_name': '受托代销商品', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1413', 'acct_name': '代销商品款', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            # 销售费用明细
            {'acct_code': '660101', 'acct_name': '运输费', 'acct_level': 2,
             'parent_code': '6601', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '660102', 'acct_name': '装卸费', 'acct_level': 2,
             'parent_code': '6601', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '660103', 'acct_name': '仓储费', 'acct_level': 2,
             'parent_code': '6601', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
        ]
        existing = {a['acct_code'] for a in result}
        for a in extra:
            if a['acct_code'] not in existing:
                result.append(a)
        return result