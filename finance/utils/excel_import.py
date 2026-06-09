"""
==========================================
 utils/excel_import.py - Excel 导入工具
==========================================
支持导入：
  - 科目表（从Excel初始化）
  - 凭证（批量导入）
  - 期初余额
  - 辅助核算档案
"""

from typing import List, Dict, Optional


class ExcelImporter:
    """Excel导入工具"""

    def import_accounts(self, filepath: str) -> List[Dict]:
        """从Excel导入科目表"""
        pass

    def import_vouchers(self, filepath: str) -> int:
        """批量导入凭证，返回导入数量"""
        pass

    def import_opening_balances(self, filepath: str) -> bool:
        """导入期初余额"""
        pass
