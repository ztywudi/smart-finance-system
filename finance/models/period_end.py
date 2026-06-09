"""
========================================
 models/period_end.py - 期末处理模型
========================================
"""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class PeriodEndCheck:
    """期末结账检查项"""
    check_name: str = ''          # 检查项名称
    check_func: str = ''          # 检查函数名
    passed: bool = False          # 是否通过
    message: str = ''             # 检查结果描述
    severity: str = 'error'       # error / warning

    # 标准检查项列表
    STANDARD_CHECKS = [
        '凭证是否全部审核',
        '凭证是否全部过账',
        '是否试算平衡',
        '损益类科目是否结转',
        '固定资产折旧是否计提',
        '工资是否计提',
        '税费是否计提',
        '是否有未审核凭证',
        '是否有未过账凭证',
    ]


@dataclass
class PeriodEndResult:
    """期末结账结果"""
    period: str = ''
    success: bool = False
    checks: List[PeriodEndCheck] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
