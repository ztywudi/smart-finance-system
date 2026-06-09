"""
===========================================
 base_system.py - 会计制度基类
===========================================
所有会计制度的统一接口，子类需实现：
  - get_chart_of_accounts()   -> 标准科目表
  - get_report_templates()    -> 报表模板
  - get_opening_balances()    -> 期初建账规则
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from models.account import Account


class BaseAccountingSystem(ABC):
    """会计制度基类"""

    @property
    @abstractmethod
    def code(self) -> str:
        """制度代码"""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """制度名称"""
        pass

    @abstractmethod
    def get_chart_of_accounts(self) -> List[Dict]:
        """
        获取标准科目表
        返回：[{acct_code, acct_name, acct_level, parent_code,
                is_detail, acct_type, balance_side, ...}]
        """
        pass

    @abstractmethod
    def get_report_templates(self) -> List[Dict]:
        """
        获取预置报表模板
        返回：[{report_id, report_name, report_type, cells: [...]}]
        """
        pass

    def get_voucher_types(self) -> List[Dict]:
        """
        获取凭证分类
        返回：[{type_code, type_name}]
        """
        return [{'type_code': '记', 'type_name': '记账凭证'}]

    def get_aux_types(self) -> List[Dict]:
        """获取默认辅助核算类型"""
        return [
            {'type_name': '客户'},
            {'type_name': '供应商'},
            {'type_name': '部门'},
            {'type_name': '职员'},
            {'type_name': '项目'},
        ]

    def get_opening_balance_rules(self) -> Dict:
        """获取期初余额设置规则"""
        return {
            'must_balanced': True,            # 期初必须试算平衡
            'asset_equals_liability_equity': True,  # 资产 = 负债 + 权益
            'max_level': 6,                   # 最大科目级次
        }

    def get_init_sql(self) -> str:
        """获取初始化时执行的特殊SQL（如有）"""
        return ""
