"""
===================================================
 enterprise_standard.py - 企业会计准则预设数据
===================================================
预置一级科目约 160+ 个，覆盖：
  资产类(1xxx) | 负债类(2xxx) | 共同类(3xxx)
  所有者权益类(4xxx) | 成本类(5xxx) | 损益类(6xxx)

编码规则：4-2-2 结构，总长6位
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class EnterpriseStandardSystem(BaseAccountingSystem):
    """企业会计准则"""

    code = 'ENT_STANDARD'
    name = '企业会计准则'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 资产类 ═══════════════
            {'acct_code': '1001', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100201', 'acct_name': '工行存款', 'acct_level': 2, 'parent_code': '1002', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '100202', 'acct_name': '建行存款', 'acct_level': 2, 'parent_code': '1002', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1011', 'acct_name': '存放同业', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1012', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '101201', 'acct_name': '外埠存款', 'acct_level': 2, 'parent_code': '1012', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '101202', 'acct_name': '银行本票', 'acct_level': 2, 'parent_code': '1012', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1101', 'acct_name': '交易性金融资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '110101', 'acct_name': '股票投资', 'acct_level': 2, 'parent_code': '1101', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1121', 'acct_name': '应收票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1122', 'acct_name': '应收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '112201', 'acct_name': '应收A公司', 'acct_level': 2, 'parent_code': '1122', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1123', 'acct_name': '预付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1131', 'acct_name': '应收股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1132', 'acct_name': '应收利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1221', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1231', 'acct_name': '坏账准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1401', 'acct_name': '材料采购', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1402', 'acct_name': '在途物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1403', 'acct_name': '原材料', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1405', 'acct_name': '库存商品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1461', 'acct_name': '存货跌价准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1471', 'acct_name': '合同资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1472', 'acct_name': '合同资产减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1501', 'acct_name': '持有待售资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1503', 'acct_name': '债权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1511', 'acct_name': '长期股权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1601', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160101', 'acct_name': '房屋建筑物', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160102', 'acct_name': '机器设备', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160103', 'acct_name': '电子设备', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160104', 'acct_name': '运输设备', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1602', 'acct_name': '累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '160201', 'acct_name': '房屋建筑物累计折旧', 'acct_level': 2, 'parent_code': '1602', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1603', 'acct_name': '固定资产减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1604', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1605', 'acct_name': '工程物资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1606', 'acct_name': '固定资产清理', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1701', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1702', 'acct_name': '累计摊销', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1703', 'acct_name': '无形资产减值准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1801', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1811', 'acct_name': '递延所得税资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1901', 'acct_name': '待处理财产损溢', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ═══════════════ 负债类 ═══════════════
            {'acct_code': '2001', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2101', 'acct_name': '交易性金融负债', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '应付票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2202', 'acct_name': '应付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2203', 'acct_name': '预收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2211', 'acct_name': '应付职工薪酬', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221101', 'acct_name': '工资', 'acct_level': 2, 'parent_code': '2211', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221102', 'acct_name': '社保费', 'acct_level': 2, 'parent_code': '2211', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221103', 'acct_name': '住房公积金', 'acct_level': 2, 'parent_code': '2211', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '221104', 'acct_name': '工会经费', 'acct_level': 2, 'parent_code': '2211', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2221', 'acct_name': '应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '222101', 'acct_name': '应交增值税', 'acct_level': 2, 'parent_code': '2221', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '222106', 'acct_name': '应交企业所得税', 'acct_level': 2, 'parent_code': '2221', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2231', 'acct_name': '应付利息', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2232', 'acct_name': '应付股利', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2241', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2401', 'acct_name': '递延收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2501', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2502', 'acct_name': '应付债券', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2701', 'acct_name': '长期应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2801', 'acct_name': '预计负债', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2901', 'acct_name': '递延所得税负债', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ═══════════════ 共同类 ═══════════════
            {'acct_code': '3101', 'acct_name': '衍生工具', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'common', 'balance_side': 'debit'},

            # ═══════════════ 所有者权益类 ═══════════════
            {'acct_code': '4001', 'acct_name': '实收资本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '4002', 'acct_name': '资本公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '4101', 'acct_name': '盈余公积', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '410101', 'acct_name': '法定盈余公积', 'acct_level': 2, 'parent_code': '4101', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '4103', 'acct_name': '本年利润', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '4104', 'acct_name': '利润分配', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'equity', 'balance_side': 'credit'},
            {'acct_code': '410401', 'acct_name': '未分配利润', 'acct_level': 2, 'parent_code': '4104', 'is_detail': True, 'acct_type': 'equity', 'balance_side': 'credit'},

            # ═══════════════ 成本类 ═══════════════
            {'acct_code': '5001', 'acct_name': '生产成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500101', 'acct_name': '直接材料', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '直接人工', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '500103', 'acct_name': '制造费用转入', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '5101', 'acct_name': '制造费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '5201', 'acct_name': '劳务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'cost', 'balance_side': 'debit'},
            {'acct_code': '5301', 'acct_name': '研发支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'cost', 'balance_side': 'debit'},

            # ═══════════════ 损益类 ═══════════════
            {'acct_code': '6001', 'acct_name': '主营业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '6051', 'acct_name': '其他业务收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '6101', 'acct_name': '公允价值变动损益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '6111', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '6301', 'acct_name': '营业外收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'credit'},
            {'acct_code': '6401', 'acct_name': '主营业务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6402', 'acct_name': '其他业务成本', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6403', 'acct_name': '税金及附加', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6601', 'acct_name': '销售费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660101', 'acct_name': '工资', 'acct_level': 2, 'parent_code': '6601', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660102', 'acct_name': '广告宣传费', 'acct_level': 2, 'parent_code': '6601', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660103', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '6601', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6602', 'acct_name': '管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660201', 'acct_name': '工资', 'acct_level': 2, 'parent_code': '6602', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660202', 'acct_name': '办公费', 'acct_level': 2, 'parent_code': '6602', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660203', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '6602', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660204', 'acct_name': '折旧费', 'acct_level': 2, 'parent_code': '6602', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660205', 'acct_name': '租赁费', 'acct_level': 2, 'parent_code': '6602', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6603', 'acct_name': '财务费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660301', 'acct_name': '利息支出', 'acct_level': 2, 'parent_code': '6603', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '660302', 'acct_name': '手续费', 'acct_level': 2, 'parent_code': '6603', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6701', 'acct_name': '资产减值损失', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6711', 'acct_name': '信用减值损失', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6801', 'acct_name': '所得税费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'debit'},
            {'acct_code': '6901', 'acct_name': '以前年度损益调整', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'pl', 'balance_side': 'credit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '利润表', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
        ]
