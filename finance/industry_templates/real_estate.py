"""
======================================================
 industry_templates/real_estate.py - 房地产开发企业模板
======================================================
特有科目：开发成本/开发产品/预收账款/应交税费等
"""

from industry_templates.base import BaseIndustryTemplate
from typing import List, Dict


class RealEstateTemplate(BaseIndustryTemplate):
    """房地产开发企业行业模板"""

    code = 'real_estate'
    name = '房地产开发企业'
    compatible_systems = ['ENT_STANDARD', 'ENT_SMALL', 'ENT_OLD']

    def customize(self, accounts: List[Dict]) -> List[Dict]:
        result = list(accounts)
        # 房地产专用科目（使用不冲突的编码）
        extra = [
            {'acct_code': '1474', 'acct_name': '开发成本', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset',
             'balance_side': 'debit'},
            {'acct_code': '147401', 'acct_name': '土地征用及拆迁补偿费', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147402', 'acct_name': '前期工程费', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147403', 'acct_name': '建筑安装工程费', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147404', 'acct_name': '基础设施建设费', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147405', 'acct_name': '公共配套设施费', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147406', 'acct_name': '开发间接费用', 'acct_level': 2,
             'parent_code': '1474', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1475', 'acct_name': '开发产品', 'acct_level': 1,
             'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147501', 'acct_name': '住宅', 'acct_level': 2,
             'parent_code': '1475', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '147502', 'acct_name': '商业', 'acct_level': 2,
             'parent_code': '1475', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1476', 'acct_name': '出租开发产品', 'acct_level': 1,
             'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '220301', 'acct_name': '预收房款', 'acct_level': 2,
             'parent_code': '2203', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '220302', 'acct_name': '预收购房定金', 'acct_level': 2,
             'parent_code': '2203', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
        ]
        # 合并：去重（按acct_code）
        existing = {a['acct_code'] for a in result}
        for a in extra:
            if a['acct_code'] not in existing:
                result.append(a)
        return result