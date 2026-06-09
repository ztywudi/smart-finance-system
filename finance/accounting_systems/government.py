"""
===================================================
 government.py - 政府会计准则制度预设数据
===================================================
核心特点：双功能（预算会计+财务会计）并行
财务会计：资产/负债/净资产/收入/费用（权责发生制）
预算会计：预算收入/预算支出/预算结余（收付实现制）

编码规则：4位编码（财务会计）+ 3位预算编码
"""

from accounting_systems.base_system import BaseAccountingSystem
from typing import List, Dict


class GovernmentSystem(BaseAccountingSystem):
    """政府会计准则制度"""

    code = 'GOV'
    name = '政府会计准则制度'

    def get_chart_of_accounts(self) -> List[Dict]:
        return [
            # ═══════════════ 财务会计科目 ═══════════════
            # ----- 资产类 -----
            {'acct_code': '1001', 'acct_name': '库存现金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1002', 'acct_name': '银行存款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit', 'is_bank_acct': True},
            {'acct_code': '1011', 'acct_name': '零余额账户用款额度', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1021', 'acct_name': '其他货币资金', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1201', 'acct_name': '财政应返还额度', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120101', 'acct_name': '财政直接支付', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '120102', 'acct_name': '财政授权支付', 'acct_level': 2, 'parent_code': '1201', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1211', 'acct_name': '应收票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1212', 'acct_name': '应收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1215', 'acct_name': '预付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1218', 'acct_name': '其他应收款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1219', 'acct_name': '坏账准备', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1301', 'acct_name': '在途物品', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1302', 'acct_name': '库存物品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1303', 'acct_name': '加工物品', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1501', 'acct_name': '长期股权投资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '150101', 'acct_name': '股权投资', 'acct_level': 2, 'parent_code': '1501', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1502', 'acct_name': '长期债券投资', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1601', 'acct_name': '固定资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160101', 'acct_name': '房屋及构筑物', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160102', 'acct_name': '通用设备', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160103', 'acct_name': '专用设备', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160104', 'acct_name': '文物和陈列品', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160105', 'acct_name': '图书、档案', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '160106', 'acct_name': '家具用具装具', 'acct_level': 2, 'parent_code': '1601', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1602', 'acct_name': '固定资产累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1611', 'acct_name': '工程物资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1613', 'acct_name': '在建工程', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1701', 'acct_name': '无形资产', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '170101', 'acct_name': '专利权', 'acct_level': 2, 'parent_code': '1701', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '170102', 'acct_name': '软件', 'acct_level': 2, 'parent_code': '1701', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1702', 'acct_name': '无形资产累计摊销', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1801', 'acct_name': '公共基础设施', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1802', 'acct_name': '公共基础设施累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1811', 'acct_name': '政府储备物资', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1831', 'acct_name': '保障性住房', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1832', 'acct_name': '保障性住房累计折旧', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'credit'},
            {'acct_code': '1901', 'acct_name': '长期待摊费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'asset', 'balance_side': 'debit'},
            {'acct_code': '1902', 'acct_name': '待处理财产损溢', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'asset', 'balance_side': 'debit'},

            # ----- 负债类 -----
            {'acct_code': '2001', 'acct_name': '短期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2101', 'acct_name': '应交增值税', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2102', 'acct_name': '其他应交税费', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2103', 'acct_name': '应缴财政款', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2201', 'acct_name': '应付职工薪酬', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '220101', 'acct_name': '基本工资', 'acct_level': 2, 'parent_code': '2201', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '220102', 'acct_name': '津贴补贴', 'acct_level': 2, 'parent_code': '2201', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '220103', 'acct_name': '绩效工资', 'acct_level': 2, 'parent_code': '2201', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2301', 'acct_name': '应付票据', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2302', 'acct_name': '应付账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2305', 'acct_name': '预收账款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2307', 'acct_name': '其他应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2401', 'acct_name': '预提费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2501', 'acct_name': '长期借款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2502', 'acct_name': '长期应付款', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'liability', 'balance_side': 'credit'},
            {'acct_code': '2601', 'acct_name': '预计负债', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'liability', 'balance_side': 'credit'},

            # ----- 净资产类 -----
            {'acct_code': '3001', 'acct_name': '累计盈余', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3101', 'acct_name': '专用基金', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3201', 'acct_name': '无偿调拨净资产', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},
            {'acct_code': '3301', 'acct_name': '权益法调整', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'net_asset', 'balance_side': 'credit'},

            # ----- 收入类（财务会计） -----
            {'acct_code': '4001', 'acct_name': '财政拨款收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4101', 'acct_name': '事业收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4201', 'acct_name': '上级补助收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4301', 'acct_name': '附属单位上缴收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4401', 'acct_name': '经营收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4501', 'acct_name': '非同级财政拨款收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4601', 'acct_name': '投资收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4602', 'acct_name': '捐赠收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4603', 'acct_name': '利息收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4604', 'acct_name': '租金收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'income', 'balance_side': 'credit'},
            {'acct_code': '4605', 'acct_name': '其他收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'income', 'balance_side': 'credit'},

            # ----- 费用类（财务会计） -----
            {'acct_code': '5001', 'acct_name': '业务活动费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500101', 'acct_name': '工资福利费用', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500102', 'acct_name': '商品和服务费用', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '500103', 'acct_name': '对个人和家庭的补助', 'acct_level': 2, 'parent_code': '5001', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5101', 'acct_name': '单位管理费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5201', 'acct_name': '经营费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5301', 'acct_name': '资产处置费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5401', 'acct_name': '上缴上级费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5501', 'acct_name': '对附属单位补助费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5601', 'acct_name': '所得税费用', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'expense', 'balance_side': 'debit'},
            {'acct_code': '5801', 'acct_name': '其他费用', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'expense', 'balance_side': 'debit'},

            # ═══════════════ 预算会计科目 ═══════════════
            # 预算收入类
            {'acct_code': '6001', 'acct_name': '财政拨款预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6101', 'acct_name': '事业预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6201', 'acct_name': '上级补助预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6301', 'acct_name': '附属单位上缴预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6401', 'acct_name': '经营预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6501', 'acct_name': '债务预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6601', 'acct_name': '非同级财政拨款预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6701', 'acct_name': '投资预算收益', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_income', 'balance_side': 'credit'},
            {'acct_code': '6801', 'acct_name': '其他预算收入', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_income', 'balance_side': 'credit'},

            # 预算支出类
            {'acct_code': '7001', 'acct_name': '行政支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '700101', 'acct_name': '基本工资', 'acct_level': 2, 'parent_code': '7001', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '700102', 'acct_name': '办公经费', 'acct_level': 2, 'parent_code': '7001', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '700103', 'acct_name': '差旅费', 'acct_level': 2, 'parent_code': '7001', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '700104', 'acct_name': '维修(护)费', 'acct_level': 2, 'parent_code': '7001', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7101', 'acct_name': '事业支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7201', 'acct_name': '经营支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7301', 'acct_name': '上缴上级支出', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7401', 'acct_name': '对附属单位补助支出', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7501', 'acct_name': '投资支出', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7601', 'acct_name': '债务还本支出', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_expense', 'balance_side': 'debit'},
            {'acct_code': '7701', 'acct_name': '其他支出', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_expense', 'balance_side': 'debit'},

            # 预算结余类
            {'acct_code': '8001', 'acct_name': '资金结存', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'debit'},
            {'acct_code': '800101', 'acct_name': '零余额账户用款额度', 'acct_level': 2, 'parent_code': '8001', 'is_detail': True, 'acct_type': 'budget_balance', 'balance_side': 'debit'},
            {'acct_code': '800102', 'acct_name': '货币资金', 'acct_level': 2, 'parent_code': '8001', 'is_detail': True, 'acct_type': 'budget_balance', 'balance_side': 'debit'},
            {'acct_code': '8101', 'acct_name': '财政拨款结转', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8102', 'acct_name': '财政拨款结余', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8201', 'acct_name': '非财政拨款结转', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8202', 'acct_name': '非财政拨款结余', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8301', 'acct_name': '专用结余', 'acct_level': 1, 'parent_code': '', 'is_detail': False, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8401', 'acct_name': '经营结余', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8501', 'acct_name': '其他结余', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
            {'acct_code': '8701', 'acct_name': '非财政拨款结余分配', 'acct_level': 1, 'parent_code': '', 'is_detail': True, 'acct_type': 'budget_balance', 'balance_side': 'credit'},
        ]

    def get_report_templates(self) -> List[Dict]:
        return [
            {'report_id': 'BALANCE', 'report_name': '资产负债表', 'report_type': 'balance_sheet'},
            {'report_id': 'INCOME', 'report_name': '收入费用表', 'report_type': 'income_statement'},
            {'report_id': 'CASHFLOW', 'report_name': '现金流量表', 'report_type': 'cash_flow'},
            {'report_id': 'BUDGET_EXEC', 'report_name': '预算收入支出表', 'report_type': 'budget_report'},
            {'report_id': 'BUDGET_BALANCE', 'report_name': '预算结转结余变动表', 'report_type': 'budget_report'},
        ]

    def get_voucher_types(self) -> List[Dict]:
        return [
            {'type_code': '记', 'type_name': '记账凭证'},
            {'type_code': '预', 'type_name': '预算凭证'},
        ]

    def get_opening_balance_rules(self) -> Dict:
        return {
            'must_balanced': True,
            'dual_basis_check': True,            # 需要双基础平衡检查
            'asset_equals_liability_net_asset': True,
            'budget_must_match_financial': False,  # 预算与财务不必完全相等
            'max_level': 6,
        }