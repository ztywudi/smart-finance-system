"""
industry_templates/construction.py - 建筑施工企业模板
特有科目：工程施工/工程结算/机械作业等
"""

from typing import List, Dict
from industry_templates.base import BaseIndustryTemplate


class ConstructionTemplate(BaseIndustryTemplate):
    code = 'construction'
    name = '建筑施工企业'
    compatible_systems = ['ENT_STANDARD', 'ENT_SMALL', 'ENT_OLD']

    def customize(self, accounts: List[Dict]) -> List[Dict]:
        result = list(accounts)
        # 移除标准的5001/5002（施工企业不用）
        result = [a for a in result if a['acct_code'] not in ('5001', '5002')]
        extra = [
            # 工程施工
            {'acct_code': '5001', 'acct_name': '工程施工', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500101', 'acct_name': '合同成本', 'acct_level': 2,
             'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '间接费用', 'acct_level': 2,
             'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '5002', 'acct_name': '工程结算', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'credit'},
            {'acct_code': '5003', 'acct_name': '机械作业', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500301', 'acct_name': '人工费', 'acct_level': 2,
             'parent_code': '5003', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500302', 'acct_name': '燃料及动力', 'acct_level': 2,
             'parent_code': '5003', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500303', 'acct_name': '折旧及修理', 'acct_level': 2,
             'parent_code': '5003', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
        ]
        existing = {a['acct_code'] for a in result}
        for a in extra:
            if a['acct_code'] not in existing:
                result.append(a)
        return result