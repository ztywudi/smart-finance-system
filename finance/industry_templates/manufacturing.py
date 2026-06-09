"""
industry_templates/manufacturing.py - 制造业企业模板
特有科目：生产成本/制造费用/半成品等
"""

from typing import List, Dict
from industry_templates.base import BaseIndustryTemplate


class ManufacturingTemplate(BaseIndustryTemplate):
    code = 'manufacturing'
    name = '制造业企业'
    compatible_systems = ['ENT_STANDARD', 'ENT_SMALL']

    def customize(self, accounts: List[Dict]) -> List[Dict]:
        result = list(accounts)
        extra = [
            # 成本类明细
            {'acct_code': '500101', 'acct_name': '直接材料', 'acct_level': 2,
             'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '直接人工', 'acct_level': 2,
             'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500103', 'acct_name': '制造费用转入', 'acct_level': 2,
             'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            # 制造费用明细
            {'acct_code': '500201', 'acct_name': '机物料消耗', 'acct_level': 2,
             'parent_code': '5002', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500202', 'acct_name': '人工费', 'acct_level': 2,
             'parent_code': '5002', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500203', 'acct_name': '折旧费', 'acct_level': 2,
             'parent_code': '5002', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500204', 'acct_name': '水电费', 'acct_level': 2,
             'parent_code': '5002', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            # 半成品/产成品
            {'acct_code': '1404', 'acct_name': '半成品', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140401', 'acct_name': '自制半成品', 'acct_level': 2,
             'parent_code': '1404', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140402', 'acct_name': '外购半成品', 'acct_level': 2,
             'parent_code': '1404', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
        ]
        existing = {a['acct_code'] for a in result}
        for a in extra:
            if a['acct_code'] not in existing:
                result.append(a)
        return result