"""
======================================================
 industry_templates/base.py - 行业模板基类
======================================================
行业模板 = 在会计制度基础上定制科目表
适用场景：同一会计制度下不同行业的科目差异
"""

from abc import ABC, abstractmethod
from typing import List, Dict


class BaseIndustryTemplate(ABC):
    """行业模板基类"""

    @property
    @abstractmethod
    def code(self) -> str:
        """行业代码"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """行业名称"""
        pass

    @property
    def compatible_systems(self) -> List[str]:
        """兼容的会计制度代码列表（空=兼容全部）"""
        return []

    @abstractmethod
    def customize(self, accounts: List[Dict]) -> List[Dict]:
        """
        定制科目表
        在基础科目表上增/删/改科目
        """
        pass

    def get_report_templates(self) -> Dict:
        """行业报表模板（可覆盖）"""
        return {}