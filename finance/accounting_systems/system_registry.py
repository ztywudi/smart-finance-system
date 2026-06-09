"""
============================================
 system_registry.py - 会计制度注册表
============================================
统一注册所有会计制度，提供工厂方法

已实现全部 11 种会计制度：
  企业类：
    1. ENT_STANDARD  - 企业会计准则
    2. ENT_SMALL     - 小企业会计准则
    3. ENT_OLD       - 企业会计制度（2001版）
  政府及非营利组织类：
    4. GOV           - 政府会计准则制度
    5. NON_PROFIT    - 民间非营利组织会计制度
    6. LABOR_UNION   - 工会会计制度
  基金（资金）类：
    7. SOCIAL_INSUR  - 社会保险基金会计制度
    8. SECURITIES_FUND - 证券投资基金会计核算业务指引
    9. HOUSING_FUND  - 住房公积金会计制度
  农村及合作组织类：
    10. RURAL_COLLECTIVE - 农村集体经济组织会计制度
    11. FARMER_COOP   - 农民专业合作社财务会计制度
"""

from typing import Dict, Type
from accounting_systems.base_system import BaseAccountingSystem

# 企业类
from accounting_systems.enterprise_standard import EnterpriseStandardSystem
from accounting_systems.small_enterprise import SmallEnterpriseSystem
from accounting_systems.enterprise_old import EnterpriseOldSystem

# 政府及非营利组织类
from accounting_systems.government import GovernmentSystem
from accounting_systems.non_profit import NonProfitSystem
from accounting_systems.labor_union import LaborUnionSystem

# 基金（资金）类
from accounting_systems.social_insurance import SocialInsuranceSystem
from accounting_systems.securities_fund import SecuritiesFundSystem
from accounting_systems.housing_fund import HousingFundSystem

# 农村及合作组织类
from accounting_systems.rural_collective import RuralCollectiveSystem
from accounting_systems.farmer_coop import FarmerCoopSystem

# 2026新版
from accounting_systems.enterprise_2026 import Enterprise2026System


# 全部 12 种会计制度注册表
_SYSTEM_CLASSES: Dict[str, Type[BaseAccountingSystem]] = {
    # 企业类
    'ENT_STANDARD': EnterpriseStandardSystem,
    'ENT_SMALL': SmallEnterpriseSystem,
    'ENT_OLD': EnterpriseOldSystem,
    # 政府及非营利组织类
    'GOV': GovernmentSystem,
    'NON_PROFIT': NonProfitSystem,
    'LABOR_UNION': LaborUnionSystem,
    # 基金（资金）类
    'SOCIAL_INSUR': SocialInsuranceSystem,
    'SECURITIES_FUND': SecuritiesFundSystem,
    'HOUSING_FUND': HousingFundSystem,
    # 农村及合作组织类
    'RURAL_COLLECTIVE': RuralCollectiveSystem,
    'FARMER_COOP': FarmerCoopSystem,
    # 2026新版
    'ENT_2026': Enterprise2026System,
}


def get_system(code: str) -> BaseAccountingSystem:
    """工厂方法：获取会计制度实例"""
    cls = _SYSTEM_CLASSES.get(code)
    if cls is None:
        raise ValueError(f"不支持的会计制度: {code}，可选: {list(_SYSTEM_CLASSES.keys())}")
    return cls()


def get_available_systems() -> list:
    """获取已实现的会计制度列表"""
    return [
        {'code': code, 'name': cls().name}
        for code, cls in _SYSTEM_CLASSES.items()
    ]
