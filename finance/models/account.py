"""
========================================
 models/account.py - 科目模型
========================================
功能：
  - 科目数据结构定义
  - 科目增删改查
  - 科目树构建
  - 科目导入/导出
  - 按会计制度初始化科目表
"""

from typing import List, Optional, Dict
from dataclasses import dataclass, field


@dataclass
class Account:
    """会计科目"""
    acct_code: str          # 科目编码 e.g. '1001'
    acct_name: str          # 科目名称 e.g. '库存现金'
    acct_level: int = 1     # 科目级次
    parent_code: str = ''   # 上级科目编码
    is_detail: bool = False # 是否末级科目
    acct_type: str = ''     # 科目类型：asset/liability/equity/cost/pl
    balance_side: str = 'debit'  # 余额方向：debit/credit
    is_cash_eq: bool = False     # 是否现金等价物
    is_bank_acct: bool = False   # 是否银行科目
    enabled: bool = True         # 是否启用
    children: List['Account'] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'acct_code': self.acct_code,
            'acct_name': self.acct_name,
            'acct_level': self.acct_level,
            'parent_code': self.parent_code,
            'is_detail': self.is_detail,
            'acct_type': self.acct_type,
            'balance_side': self.balance_side,
            'is_cash_eq': self.is_cash_eq,
            'is_bank_acct': self.is_bank_acct,
            'enabled': self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Account':
        return cls(**{
            k: v for k, v in data.items()
            if k in cls.__dataclass_fields__
        })


class AccountTreeBuilder:
    """科目树构建器"""

    @staticmethod
    def build_tree(accounts: List[Account]) -> List[Account]:
        """将科目列表构建为树形结构"""
        acct_map = {a.acct_code: a for a in accounts}
        roots = []

        for acct in accounts:
            if acct.parent_code and acct.parent_code in acct_map:
                parent = acct_map[acct.parent_code]
                parent.children.append(acct)
            else:
                roots.append(acct)

        # 按编码排序
        roots.sort(key=lambda x: x.acct_code)
        AccountTreeBuilder._sort_children(roots)
        return roots

    @staticmethod
    def _sort_children(accounts: List[Account]):
        for acct in accounts:
            if acct.children:
                acct.children.sort(key=lambda x: x.acct_code)
                AccountTreeBuilder._sort_children(acct.children)

    @staticmethod
    def flatten_tree(roots: List[Account], level: int = 0) -> List[Account]:
        """将科目树展平为列表"""
        result = []
        for acct in roots:
            result.append(acct)
            if acct.children:
                result.extend(
                    AccountTreeBuilder.flatten_tree(acct.children, level + 1))
        return result

    @staticmethod
    def get_leaf_accounts(roots: List[Account]) -> List[Account]:
        """获取所有末级科目"""
        leaves = []
        for acct in AccountTreeBuilder.flatten_tree(roots):
            if acct.is_detail:
                leaves.append(acct)
        return leaves
