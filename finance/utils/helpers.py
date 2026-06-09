"""
==========================================
 utils/helpers.py - 通用工具函数
==========================================
"""

import re
from datetime import datetime, date
from typing import Optional


def validate_acct_code(code: str, system_code: str = 'ENT_SMALL') -> bool:
    """校验科目编码格式"""
    if system_code in ('ENT_SMALL',):
        return bool(re.match(r'^\d{4}$', code))
    elif system_code in ('ENT_STANDARD', 'GOV'):
        return bool(re.match(r'^\d{4,6}$', code))
    return bool(re.match(r'^\d{3,6}$', code))


def format_money(amount: float) -> str:
    """格式化金额，千分位分隔"""
    return f"{amount:,.2f}"


def parse_date(date_str: str) -> Optional[date]:
    """解析日期字符串"""
    formats = ['%Y-%m-%d', '%Y/%m/%d', '%Y%m%d', '%Y.%m.%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except (ValueError, TypeError):
            continue
    return None


def today_str() -> str:
    """获取今天的日期字符串"""
    return date.today().isoformat()
