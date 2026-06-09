"""
===========================================
 models/fixed_asset.py - 固定资产模型
===========================================
"""

from dataclasses import dataclass, field
from typing import Optional, Dict
from datetime import date


@dataclass
class FixedAsset:
    """固定资产卡片"""
    asset_id: Optional[int] = None
    asset_code: str = ''           # 资产编号
    asset_name: str = ''           # 资产名称
    category: str = ''             # 类别：房屋建筑物/机器设备/运输设备/电子设备/其他
    specification: str = ''        # 规格型号
    department: str = ''           # 使用部门
    location: str = ''             # 存放地点

    # 金额信息
    original_value: float = 0.0    # 原值
    accumulated_depr: float = 0.0  # 累计折旧
    net_value: float = 0.0         # 净值
    residual_rate: float = 0.05    # 残值率
    residual_value: float = 0.0    # 残值
    total_depr_months: int = 60    # 折旧总月数

    # 折旧信息
    depr_method: str = 'straight'  # 折旧方法：straight(直线法)/double_declining/年数总和/工作量法
    depr_per_month: float = 0.0    # 月折旧额
    depr_months: int = 0           # 已折旧月数

    # 时间信息
    purchase_date: str = ''        # 购入日期
    start_use_date: str = ''       # 开始使用日期
    last_depr_date: str = ''       # 最后折旧日期
    status: str = 'in_use'         # in_use/deprecated/scrapped

    remark: str = ''

    def to_dict(self) -> Dict:
        return {
            'asset_code': self.asset_code,
            'asset_name': self.asset_name,
            'category': self.category,
            'original_value': self.original_value,
            'accumulated_depr': self.accumulated_depr,
            'net_value': self.original_value - self.accumulated_depr,
            'residual_rate': self.residual_rate,
            'depr_method': self.depr_method,
            'purchase_date': self.purchase_date,
            'status': self.status,
        }

    def calc_depreciation(self) -> float:
        """计算当月应计提折旧"""
        if self.status != 'in_use':
            return 0.0
        if self.depr_method == 'straight':
            return (self.original_value * (1 - self.residual_rate)) / self.total_depr_months
        # 其他折旧方法略
        return self.depr_per_month
