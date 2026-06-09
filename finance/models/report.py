"""
========================================
 models/report.py - 报表模型
========================================
功能：
  - 报表模板定义
  - 报表取数公式
  - 报表生成
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Callable
from enum import Enum


class ReportType(Enum):
    """报表类型"""
    BALANCE_SHEET = 'balance_sheet'       # 资产负债表
    INCOME_STATEMENT = 'income_statement'  # 利润表
    CASH_FLOW = 'cash_flow'               # 现金流量表
    EQUITY_CHANGES = 'equity_changes'      # 所有者权益变动表
    ACCT_BALANCE = 'acct_balance'          # 科目余额表
    TRIAL_BALANCE = 'trial_balance'        # 试算平衡表
    DETAIL_LEDGER = 'detail_ledger'        # 明细账
    GENERAL_LEDGER = 'general_ledger'      # 总分类账


@dataclass
class ReportCell:
    """报表单元格定义"""
    row: int = 0
    col: int = 0
    label: str = ''            # 显示名称
    formula: str = ''          # 取数公式 e.g. 'ACCT(1001)+ACCT(1002)'
    value: object = None       # 计算后的值
    format: str = 'text'       # text / number / money / date


@dataclass
class ReportTemplate:
    """报表模板"""
    report_id: str = ''
    report_name: str = ''
    report_type: ReportType = ReportType.BALANCE_SHEET
    accounting_system: str = ''   # 适用的会计制度
    cells: List[ReportCell] = field(default_factory=list)

    def generate(self, data_provider) -> List[List[object]]:
        """执行报表生成，返回二维表格数据"""
        # 遍历单元格，解析公式，从 data_provider 取数
        # 略，后续详细实现
        pass
