"""
==========================================
 utils/excel_export.py - Excel 导出工具
==========================================
使用 openpyxl 库实现数据导出
"""

from typing import List, Dict, Optional


class ExcelExporter:
    """Excel导出工具"""

    def export_vouchers(self, vouchers: List[Dict], filepath: str):
        """导出凭证到Excel"""
        pass

    def export_account_balances(self, balances: List[Dict], filepath: str):
        """导出科目余额表到Excel"""
        pass

    def export_report(self, report_data: List[List], filepath: str, title: str = ''):
        """导出报表到Excel"""
        pass
