"""
========================================
 models/voucher.py - 凭证模型
========================================
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime


@dataclass
class VoucherEntry:
    """凭证分录"""
    entry_id: Optional[int] = None
    voucher_id: Optional[int] = None
    entry_order: int = 0
    summary: str = ''
    acct_code: str = ''
    acct_name: str = ''           # 非持久化，显示用
    debit_amount: float = 0.0
    credit_amount: float = 0.0
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    aux_item_id: Optional[int] = None
    aux_item_name: str = ''       # 非持久化，显示用

    def to_dict(self) -> Dict:
        return {
            'entry_order': self.entry_order,
            'summary': self.summary,
            'acct_code': self.acct_code,
            'debit_amount': self.debit_amount,
            'credit_amount': self.credit_amount,
            'quantity': self.quantity,
            'unit_price': self.unit_price,
            'aux_item_id': self.aux_item_id,
        }

    @property
    def is_debit(self) -> bool:
        return self.debit_amount > 0

    @property
    def is_credit(self) -> bool:
        return self.credit_amount > 0


@dataclass
class Voucher:
    """记账凭证"""
    voucher_id: Optional[int] = None
    period: str = ''               # 会计期间 e.g. '2026-05'
    voucher_date: str = ''         # 凭证日期 e.g. '2026-05-31'
    voucher_type: str = '记'       # 凭证字
    voucher_no: Optional[int] = None
    attachment_count: int = 0
    status: str = 'draft'          # draft / approved / posted / voided
    created_by: str = ''
    created_at: str = ''
    posted_at: Optional[str] = None
    remark: str = ''
    entries: List[VoucherEntry] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            'voucher_id': self.voucher_id,
            'period': self.period,
            'voucher_date': self.voucher_date,
            'voucher_type': self.voucher_type,
            'voucher_no': self.voucher_no,
            'attachment_count': self.attachment_count,
            'status': self.status,
            'created_by': self.created_by,
            'remark': self.remark,
            'entries': [e.to_dict() for e in self.entries],
        }

    @property
    def total_debit(self) -> float:
        return sum(e.debit_amount for e in self.entries)

    @property
    def total_credit(self) -> float:
        return sum(e.credit_amount for e in self.entries)

    @property
    def is_balanced(self) -> bool:
        """检查借贷是否平衡"""
        return abs(self.total_debit - self.total_credit) < 0.01

    def validate(self) -> List[str]:
        """校验凭证合法性，返回错误信息列表"""
        errors = []
        if not self.entries:
            errors.append("凭证至少需要一条分录")
        if len(self.entries) < 2:
            errors.append("凭证至少需要两条分录（一借一贷）")
        if not self.is_balanced:
            errors.append(f"借贷不平衡：借方 {self.total_debit:.2f} ≠ 贷方 {self.total_credit:.2f}")
        for e in self.entries:
            if not e.acct_code:
                errors.append(f"第{e.entry_order}行缺少会计科目")
            if e.debit_amount == 0 and e.credit_amount == 0:
                errors.append(f"第{e.entry_order}行金额不能为0")
            if e.debit_amount > 0 and e.credit_amount > 0:
                errors.append(f"第{e.entry_order}行不能同时有借方和贷方金额")
        return errors
