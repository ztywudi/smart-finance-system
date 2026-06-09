"""
==========================================
 models/auxiliary.py - 辅助核算模型
==========================================
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict


@dataclass
class AuxType:
    """辅助核算类型"""
    type_id: Optional[int] = None
    type_name: str = ''    # 客户/供应商/部门/职员/项目/存货/自定义
    enabled: bool = True

    TYPES = ['客户', '供应商', '部门', '职员', '项目', '存货', '自定义']


@dataclass
class AuxItem:
    """辅助核算档案项"""
    item_id: Optional[int] = None
    type_id: int = 0
    type_name: str = ''        # 非持久化
    item_code: str = ''
    item_name: str = ''
    enabled: bool = True


@dataclass
class AccountAux:
    """科目与辅助核算类型关联"""
    id: Optional[int] = None
    acct_code: str = ''
    type_id: int = 0
    type_name: str = ''        # 非持久化
