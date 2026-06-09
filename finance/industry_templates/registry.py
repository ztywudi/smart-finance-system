"""
======================================================
 industry_templates/registry.py - 行业模板注册表
======================================================
"""

from typing import Dict, List, Type
from industry_templates.base import BaseIndustryTemplate


# 所有行业模板在此注册
_TEMPLATES: Dict[str, Type[BaseIndustryTemplate]] = {}


def register(code: str, cls: Type[BaseIndustryTemplate]):
    """注册行业模板"""
    _TEMPLATES[code] = cls


def get_template(code: str) -> BaseIndustryTemplate:
    """获取行业模板实例"""
    cls = _TEMPLATES.get(code)
    if not cls:
        raise ValueError(f"不支持的行业模板: {code}")
    return cls()


def get_available_templates() -> List[Dict]:
    """获取可用行业模板列表"""
    return [
        {'code': code, 'name': cls().name}
        for code, cls in _TEMPLATES.items()
    ]


def customize_accounts(industry_code: str, accounts: List[Dict]) -> List[Dict]:
    """
    对基础科目表应用行业定制
    如果 industry_code 为空或 'none'，则返回原科目表
    """
    if not industry_code or industry_code == 'none':
        return accounts
    tmpl = get_template(industry_code)
    return tmpl.customize(accounts)