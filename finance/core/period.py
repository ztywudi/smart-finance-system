"""
========================================
 period.py - 会计期间管理
========================================
功能：
  - 按会计年度生成会计期间
  - 期间状态管理（未结账/已结账/已反结账）
  - 校验期间连续性
  - 支持自定义会计年度起始月（如非1月起始）
"""

from datetime import datetime, date
from typing import List, Optional, Tuple


class PeriodManager:
    """会计期间管理器"""

    def __init__(self, fiscal_year_start: int = 1):
        """
        :param fiscal_year_start: 会计年度起始月份，1=1月起始，4=4月起始
        """
        self.fiscal_year_start = fiscal_year_start

    def get_periods_for_year(self, year: int) -> List[str]:
        """获取某会计年度的所有期间列表"""
        periods = []
        start_month = self.fiscal_year_start
        for i in range(12):
            month = (start_month + i - 1) % 12 + 1
            fiscal_year = year if start_month == 1 else (
                year if month >= start_month else year + 1
            )
            periods.append(f"{fiscal_year:04d}-{month:02d}")
        return periods

    def get_current_period(self) -> str:
        """获取当前会计期间"""
        today = date.today()
        month = today.month
        year = today.year

        # 如果当前月份小于起始月，属于上一个会计年度
        if month < self.fiscal_year_start:
            year -= 1

        return f"{year:04d}-{month:02d}"

    def get_previous_period(self, period: str) -> Optional[str]:
        """获取上一个期间"""
        year, month = self._parse_period(period)
        if month == 1:
            year -= 1
            month = 12
        else:
            month -= 1
        return f"{year:04d}-{month:02d}"

    def get_next_period(self, period: str) -> Optional[str]:
        """获取下一个期间"""
        year, month = self._parse_period(period)
        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
        return f"{year:04d}-{month:02d}"

    def compare_period(self, a: str, b: str) -> int:
        """比较两个期间：a < b 返回 -1，相等返回 0，a > b 返回 1"""
        ay, am = self._parse_period(a)
        by, bm = self._parse_period(b)
        av = ay * 12 + am
        bv = by * 12 + bm
        return -1 if av < bv else (1 if av > bv else 0)

    def is_valid_period(self, period: str) -> bool:
        """检查期间格式是否合法"""
        try:
            year, month = self._parse_period(period)
            return 1 <= month <= 12 and 2000 <= year <= 2100
        except (ValueError, IndexError):
            return False

    @staticmethod
    def _parse_period(period: str) -> Tuple[int, int]:
        """解析期间字符串 '2026-05' → (2026, 5)"""
        parts = period.split('-')
        return int(parts[0]), int(parts[1])

    @staticmethod
    def format_period(year: int, month: int) -> str:
        """格式化期间"""
        return f"{year:04d}-{month:02d}"

    @staticmethod
    def get_period_year(period: str) -> int:
        """获取期间所属年份"""
        return int(period.split('-')[0])

    @staticmethod
    def get_period_month(period: str) -> int:
        """获取期间所属月份"""
        return int(period.split('-')[1])
