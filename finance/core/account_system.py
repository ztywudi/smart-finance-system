"""
==========================================
 account_system.py - 会计制度管理器
==========================================
功能：
  - 注册所有支持的会计制度
  - 根据用户选择匹配对应的制度
  - 提供制度的元信息（名称、描述、科目级次、特点）
  - 动态加载制度预设数据

支持的会计制度（共11种）：
  企业类：
    ENT_STANDARD  - 企业会计准则
    ENT_SMALL     - 小企业会计准则
    ENT_OLD       - 企业会计制度（2001版）
  政府及非营利组织类：
    GOV           - 政府会计准则制度
    NON_PROFIT    - 民间非营利组织会计制度
    LABOR_UNION   - 工会会计制度
  基金（资金）类：
    SOCIAL_INSUR  - 社会保险基金会计制度
    SECURITIES_FUND - 证券投资基金会计核算
    HOUSING_FUND  - 住房公积金会计制度
  农村及合作组织类：
    RURAL_COLLECTIVE - 农村集体经济组织会计制度
    FARMER_COOP   - 农民专业合作社财务会计制度
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AccountingSystemInfo:
    """会计制度元信息"""
    code: str               # 制度代码
    name: str               # 制度名称
    category: str           # 分类：企业/政府非营利/基金/农村
    applicable_to: str      # 适用对象描述
    acct_code_length: int   # 科目编码总长度
    acct_levels: List[int]  # 每级编码长度，如 [4, 2, 2] → 1001-01-01
    has_auxiliary: bool     # 是否支持辅助核算
    has_budget_acct: bool   # 是否有预算会计（政府会计专用）
    tax_method: str         # 税务方法：normal / simplified
    description: str        # 详细说明
    version: str            # 制度版本
    effective_date: str     # 施行日期
    depr_start_rule: str = 'next_month'  # 折旧起始规则：next_month(次月) / same_month(当月) / none(不计提)


class AccountingSystemManager:
    """会计制度管理器"""

    _systems: Dict[str, AccountingSystemInfo] = {}

    @classmethod
    def register(cls, info: AccountingSystemInfo):
        """注册会计制度"""
        cls._systems[info.code] = info

    @classmethod
    def get_system(cls, code: str) -> Optional[AccountingSystemInfo]:
        """获取会计制度信息"""
        return cls._systems.get(code)

    @classmethod
    def get_all_systems(cls) -> List[AccountingSystemInfo]:
        """获取所有已注册的会计制度"""
        return list(cls._systems.values())

    @classmethod
    def get_systems_by_category(cls, category: str) -> List[AccountingSystemInfo]:
        """按分类获取会计制度"""
        return [s for s in cls._systems.values() if s.category == category]

    @classmethod
    def get_categories(cls) -> List[str]:
        """获取所有分类"""
        categories = set()
        for s in cls._systems.values():
            categories.add(s.category)
        return sorted(categories)


# ──────────────────────────────────────────
#  注册全部 11 种会计制度
# ──────────────────────────────────────────

AccountingSystemManager.register(AccountingSystemInfo(
    code='ENT_STANDARD',
    name='企业会计准则',
    category='企业',
    applicable_to='上市公司、大中型企业、金融机构',
    acct_code_length=6,
    acct_levels=[4, 2, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='normal',
    description='企业会计准则体系（基本准则+42项具体准则+应用指南），'
                '包括资产减值、所得税、金融工具、收入确认等复杂会计处理。',
    version='2024版',
    depr_start_rule='next_month',
    effective_date='2007-01-01（陆续修订）'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='ENT_SMALL',
    name='小企业会计准则',
    category='企业',
    applicable_to='符合《中小企业划型标准规定》的小型企业',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='simplified',
    description='简化处理：不计提资产减值准备、不确认递延所得税资产/负债、'
                '长期股权投资采用成本法、利息收入按合同利率确认。',
    version='2013版',
    depr_start_rule='next_month',
    effective_date='2013-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='ENT_OLD',
    name='企业会计制度（2001版）',
    category='企业',
    applicable_to='尚未执行新准则的企业（老企业沿用）',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='normal',
    description='2001年发布的《企业会计制度》，属于过渡性制度，'
                '部分科目名称与会计准则不一致。',
    version='2001版',
    depr_start_rule='next_month',
    effective_date='2001-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='GOV',
    name='政府会计准则制度',
    category='政府及非营利组织',
    applicable_to='各级各类行政事业单位',
    acct_code_length=6,
    acct_levels=[4, 2, 2],
    has_auxiliary=True,
    has_budget_acct=True,
    tax_method='normal',
    description='双功能（预算会计+财务会计）、双基础（收付实现制+权责发生制）、'
                '双报告（决算报告+财务报告）并轨核算。',
    version='2019版',
    depr_start_rule='same_month',
    effective_date='2019-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='NON_PROFIT',
    name='民间非营利组织会计制度',
    category='政府及非营利组织',
    applicable_to='社会团体、基金会、民办非企业单位、寺院等',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='simplified',
    description='无"所有者权益"改为"净资产"，区分"限定性净资产"和'
                '"非限定性净资产"。5个会计要素：资产/负债/净资产/收入/费用。',
    version='2025修订版',
    depr_start_rule='next_month',
    effective_date='2026-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='LABOR_UNION',
    name='工会会计制度',
    category='政府及非营利组织',
    applicable_to='各级工会组织（含基层工会和县级以上工会）',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='none',
    description='5个会计要素：资产/负债/净资产/收入/支出。'
                '分基层工会和县级以上工会两套科目表，科目编号略有不同。',
    version='2021修订版',
    depr_start_rule='next_month',
    effective_date='2022-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='SOCIAL_INSUR',
    name='社会保险基金会计制度',
    category='基金（资金）',
    applicable_to='社会保险经办机构（养老/医疗/失业/工伤/生育保险基金）',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=False,
    has_budget_acct=False,
    tax_method='none',
    description='按险种独立核算，专款专用。资产/负债/基金/收入/支出五要素。',
    version='2017修订版',
    depr_start_rule='none',
    effective_date='2018-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='SECURITIES_FUND',
    name='证券投资基金会计核算业务指引',
    category='基金（资金）',
    applicable_to='证券投资基金（公募基金等）',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=False,
    has_budget_acct=False,
    tax_method='normal',
    description='金融资产分类核算（交易性金融资产、持有至到期投资等），'
                '每日估值、每日计算基金份额净值。',
    version='现行版',
    depr_start_rule='none',
    effective_date='2007-07-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='HOUSING_FUND',
    name='住房公积金会计制度',
    category='基金（资金）',
    applicable_to='住房公积金管理中心',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=False,
    has_budget_acct=False,
    tax_method='none',
    description='归集/提取/贷款三大业务核算。资产/负债/净资产/收入/支出五要素。',
    version='现行版',
    depr_start_rule='next_month',
    effective_date='2000-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='RURAL_COLLECTIVE',
    name='农村集体经济组织会计制度',
    category='农村及合作组织',
    applicable_to='村级集体经济组织',
    acct_code_length=5,
    acct_levels=[3, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='simplified',
    description='三资（资金/资产/资源）管理，资源性资产（耕地、林地、水面等）核算。'
                '资产/负债/所有者权益/收入/费用五要素。',
    version='2023修订版',
    depr_start_rule='next_month',
    effective_date='2024-01-01'
))

AccountingSystemManager.register(AccountingSystemInfo(
    code='FARMER_COOP',
    name='农民专业合作社财务会计制度',
    category='农村及合作组织',
    applicable_to='农民专业合作社',
    acct_code_length=4,
    acct_levels=[4, 2],
    has_auxiliary=True,
    has_budget_acct=False,
    tax_method='simplified',
    description='成员账户核算、盈余分配（按交易量返还+按股分红）特殊处理。'
                '资产/负债/所有者权益/收入/支出五要素。',
    version='2008版',
    depr_start_rule='next_month',
    effective_date='2008-01-01'
))
