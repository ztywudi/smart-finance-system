"""
===================================================
 enterprise_old.py - 企业会计制度（2001版）预设数据
===================================================
编码规则：4位固定编码
特点：与会计准则相比术语有差异，如"现金"非"库存现金"，
      "应收补贴款""应付福利费""预提费用"等老科目

5大类：资产(1xxx) | 负债(2xxx) | 所有者权益(3xxx)
        成本(4xxx) | 损益(5xxx)
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class EnterpriseOldSystem(BaseAccountingSystem):
    """企业会计制度（2001版）"""

    code = 'ENT_OLD'
    name = '企业会计制度（2001版）'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1009', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '100901', 'acct_name': '外埠存款', 'acct_level': 2, 'parent_code': '1009', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '100902', 'acct_name': '银行本票', 'acct_level': 2, 'parent_code': '1009', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '100903', 'acct_name': '银行汇票', 'acct_level': 2, 'parent_code': '1009', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '短期投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '股票', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110102', 'acct_name': '债券', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1102', 'acct_name': '短期投资跌价准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1111', 'acct_name': '应收票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1121', 'acct_name': '应收股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1122', 'acct_name': '应收利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1131', 'acct_name': '应收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1133', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1141', 'acct_name': '坏账准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1151', 'acct_name': '预付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1161', 'acct_name': '应收补贴款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '物资采购', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1211', 'acct_name': '原材料', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1221', 'acct_name': '包装物', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1231', 'acct_name': '低值易耗品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1241', 'acct_name': '材料成本差异', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1243', 'acct_name': '库存商品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1244', 'acct_name': '商品进销差价', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1251', 'acct_name': '委托加工物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1261', 'acct_name': '委托代销商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1271', 'acct_name': '受托代销商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1281', 'acct_name': '存货跌价准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1291', 'acct_name': '分期收款发出商品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1301', 'acct_name': '待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1401', 'acct_name': '长期股权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140101', 'acct_name': '股票投资', 'acct_level': 2, 'parent_code': '1401', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140102', 'acct_name': '其他股权投资', 'acct_level': 2, 'parent_code': '1401', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1402', 'acct_name': '长期债权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '140201', 'acct_name': '债券投资', 'acct_level': 2, 'parent_code': '1402', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1421', 'acct_name': '长期投资减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1431', 'acct_name': '委托贷款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1501', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150101', 'acct_name': '生产经营用固定资产', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150102', 'acct_name': '非生产经营用固定资产', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1502', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1505', 'acct_name': '固定资产减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1601', 'acct_name': '工程物资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1603', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1605', 'acct_name': '在建工程减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1701', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1801', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1805', 'acct_name': '无形资产减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1815', 'acct_name': '未确认融资费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1901', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1911', 'acct_name': '待处理财产损溢', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '191101', 'acct_name': '待处理流动资产损溢', 'acct_level': 2, 'parent_code': '1911', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '191102', 'acct_name': '待处理固定资产损溢', 'acct_level': 2, 'parent_code': '1911', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2101', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2111', 'acct_name': '应付票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2121', 'acct_name': '应付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2131', 'acct_name': '预收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2141', 'acct_name': '代销商品款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2151', 'acct_name': '应付工资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2153', 'acct_name': '应付福利费', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2161', 'acct_name': '应付股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2171', 'acct_name': '应交税金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '217101', 'acct_name': '应交增值税', 'acct_level': 2, 'parent_code': '2171', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '217105', 'acct_name': '应交企业所得税', 'acct_level': 2, 'parent_code': '2171', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '217106', 'acct_name': '应交个人所得税', 'acct_level': 2, 'parent_code': '2171', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2176', 'acct_name': '其他应交款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2181', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2191', 'acct_name': '预提费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '待转资产价值', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2211', 'acct_name': '预计负债', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2301', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2311', 'acct_name': '应付债券', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '231101', 'acct_name': '债券面值', 'acct_level': 2, 'parent_code': '2311', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '231102', 'acct_name': '债券溢价', 'acct_level': 2, 'parent_code': '2311', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '231103', 'acct_name': '债券折价', 'acct_level': 2, 'parent_code': '2311', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'debit'},
            {'acct_code': '2321', 'acct_name': '长期应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2341', 'acct_name': '递延税款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 所有者权益类 ═══════════════
            {'acct_code': '3101', 'acct_name': '实收资本（股本）', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3111', 'acct_name': '资本公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3121', 'acct_name': '盈余公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '312101', 'acct_name': '法定盈余公积', 'acct_level': 2, 'parent_code': '3121', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '312103', 'acct_name': '任意盈余公积', 'acct_level': 2, 'parent_code': '3121', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3131', 'acct_name': '本年利润', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '3141', 'acct_name': '利润分配', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '314101', 'acct_name': '其他转入', 'acct_level': 2, 'parent_code': '3141', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '314115', 'acct_name': '未分配利润', 'acct_level': 2, 'parent_code': '3141', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},

            # ═══════════════ 成本类 ═══════════════
            {'acct_code': '4101', 'acct_name': '生产成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '410101', 'acct_name': '直接材料', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '410102', 'acct_name': '直接人工', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '410103', 'acct_name': '制造费用', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '4105', 'acct_name': '制造费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '4107', 'acct_name': '劳务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},

            # ═══════════════ 损益类 ═══════════════
            {'acct_code': '5101', 'acct_name': '主营业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5102', 'acct_name': '其他业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5201', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5203', 'acct_name': '补贴收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5301', 'acct_name': '营业外收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '5401', 'acct_name': '主营业务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5402', 'acct_name': '主营业务税金及附加', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5405', 'acct_name': '其他业务支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5501', 'acct_name': '营业费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550101', 'acct_name': '运输装卸费', 'acct_level': 2, 'parent_code': '5501', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550102', 'acct_name': '广告费', 'acct_level': 2, 'parent_code': '5501', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5502', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550201', 'acct_name': '公司经费', 'acct_level': 2, 'parent_code': '5502', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550202', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '5502', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550203', 'acct_name': '折旧费', 'acct_level': 2, 'parent_code': '5502', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5503', 'acct_name': '财务费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550301', 'acct_name': '利息支出', 'acct_level': 2, 'parent_code': '5503', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '550302', 'acct_name': '手续费', 'acct_level': 2, 'parent_code': '5503', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5601', 'acct_name': '营业外支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5701', 'acct_name': '所得税', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '5801', 'acct_name': '以前年度损益调整', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '利润表', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
        ]