"""
==========================================
 core/fixed_asset_service.py - 固定资产服务
==========================================
功能：
  - 资产卡片的增删改查
  - 折旧计算（直线法/双倍余额递减法/年数总和法）
  - 批量计提折旧
  - 资产变动处理
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from datetime import datetime, date
from typing import List, Optional, Dict, Tuple
import json


class FixedAssetService:
    """固定资产服务"""

    # 折旧方法常量
    METHOD_STRAIGHT = 'straight'           # 直线法（平均年限法）
    METHOD_DOUBLE_DECLINING = 'double'     # 双倍余额递减法
    METHOD_SUM_OF_YEARS = 'sum_years'      # 年数总和法
    METHOD_WORKLOAD = 'workload'           # 工作量法

    def __init__(self, db_manager):
        self.db_manager = db_manager

    # ──────────────────────────────────────────
    #  资产卡片 CRUD
    # ──────────────────────────────────────────

    def create_asset(self, asset_code: str, asset_name: str,
                     category: str = '', specification: str = '',
                     department: str = '', location: str = '',
                     original_value: float = 0.0,
                     residual_rate: float = 0.05,
                     depr_method: str = 'straight',
                     total_months: int = 60,
                     purchase_date: str = '',
                     start_use_date: str = '',
                     remark: str = '') -> int:
        """新增资产卡片，返回 asset_id"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        now = datetime.now().isoformat()
        cursor = conn.execute('''
            INSERT INTO fixed_assets
            (asset_code, asset_name, category, specification,
             department, location, original_value, accumulated_depr,
             residual_rate, depr_method, total_months, depr_months,
             purchase_date, start_use_date, last_depr_date,
             status, remark, created_at, modified_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, ?, ?, 0,
                    ?, ?, NULL, 'in_use', ?, ?, ?)
        ''', (asset_code, asset_name, category, specification,
              department, location, original_value,
              residual_rate, depr_method, total_months,
              purchase_date, start_use_date,
              remark, now, now))
        conn.commit()
        return cursor.lastrowid

    def update_asset(self, asset_id: int, **kwargs) -> bool:
        """更新资产信息"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        allowed = ['asset_name', 'category', 'specification', 'department',
                   'location', 'original_value', 'residual_rate', 'depr_method',
                   'total_months', 'status', 'remark']

        updates = []
        values = []
        for k, v in kwargs.items():
            if k in allowed:
                updates.append(f"{k}=?")
                values.append(v)

        if not updates:
            return False

        updates.append("modified_at=?")
        values.append(datetime.now().isoformat())
        values.append(asset_id)

        conn.execute(
            f"UPDATE fixed_assets SET {','.join(updates)} WHERE asset_id=?",
            values)
        conn.commit()
        return True

    def delete_asset(self, asset_id: int) -> bool:
        """删除资产卡片"""
        conn = self.db_manager.get_current_conn()
        conn.execute("DELETE FROM depr_details WHERE asset_id=?", (asset_id,))
        conn.execute("DELETE FROM fixed_assets WHERE asset_id=?", (asset_id,))
        conn.commit()
        return True

    def get_asset(self, asset_id: int) -> Optional[Dict]:
        """获取单个资产"""
        conn = self.db_manager.get_current_conn()
        conn.row_factory = None  # sqlite3.Row not available in basic mode
        cursor = conn.execute(
            "SELECT * FROM fixed_assets WHERE asset_id=?", (asset_id,))
        row = cursor.fetchone()
        if not row:
            return None
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def list_assets(self, status: str = None, category: str = None,
                    keyword: str = '', page: int = 1,
                    page_size: int = 50) -> Tuple[List[Dict], int]:
        """查询资产列表"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0

        conditions = []
        params = []

        if status:
            conditions.append("status=?")
            params.append(status)
        if category:
            conditions.append("category=?")
            params.append(category)
        if keyword:
            conditions.append(
                "(asset_code LIKE ? OR asset_name LIKE ? OR department LIKE ?)")
            kw = f'%{keyword}%'
            params.extend([kw, kw, kw])

        where = " AND ".join(conditions) if conditions else "1=1"

        cursor = conn.execute(
            f"SELECT COUNT(*) FROM fixed_assets WHERE {where}", params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        cursor = conn.execute(
            f"SELECT * FROM fixed_assets WHERE {where} "
            f"ORDER BY asset_code LIMIT ? OFFSET ?",
            params + [page_size, offset])

        columns = [desc[0] for desc in cursor.description]
        assets = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return assets, total

    # ──────────────────────────────────────────
    #  折旧计算（含会计制度规则）
    # ──────────────────────────────────────────

    def _get_depr_start_rule(self) -> str:
        """
        获取当前账套会计制度的折旧规则
        next_month: 次月计提（企业类、非营利组织等）
        same_month: 当月计提（政府会计制度）
        none:       不计提（社保基金、证券基金等）
        """
        try:
            from core.account_system import AccountingSystemManager
            book_id = self.db_manager.get_current_book_id()
            if not book_id:
                return 'next_month'
            info = self.db_manager.get_account_book(book_id)
            if not info:
                return 'next_month'
            sys_info = AccountingSystemManager.get_system(info['accounting_system'])
            if sys_info:
                return sys_info.depr_start_rule
        except Exception:
            pass
        return 'next_month'  # 默认次月计提

    def _should_depr_in_period(self, start_use_date: str, period: str,
                                depr_start_rule: str = None) -> bool:
        """
        判断资产是否应在某期间计提折旧
        根据会计制度的折旧起始规则 + 开始使用日期
        """
        if not start_use_date:
            return True  # 没有开始使用日期默认计提

        if depr_start_rule is None:
            depr_start_rule = self._get_depr_start_rule()

        # 不计提
        if depr_start_rule == 'none':
            return False

        try:
            start_year, start_month = int(start_use_date[:4]), int(start_use_date[5:7])
            per_year, per_month = int(period[:4]), int(period[5:7])

            start_period = start_year * 12 + start_month
            current_period = per_year * 12 + per_month

            if depr_start_rule == 'same_month':
                # 政府会计：当月增加当月提 → 当前期间 >= 开始使用期间
                return current_period >= start_period
            else:
                # 企业会计等：当月增加次月提 → 当前期间 > 开始使用期间
                return current_period > start_period
        except (ValueError, IndexError):
            return True

    def calc_monthly_depr(self, asset: Dict) -> float:
        """
        计算单月折旧额
        返回当月应提折旧金额
        """
        if asset['status'] != 'in_use':
            return 0.0

        original = asset['original_value']
        residual = original * asset['residual_rate']
        total = asset['total_months']
        depr_months = asset['depr_months']
        method = asset['depr_method']

        residual_value = original * asset['residual_rate']

        if method == self.METHOD_STRAIGHT:
            # 直线法： (原值 - 残值) / 总月数
            return (original - residual_value) / total

        elif method == self.METHOD_DOUBLE_DECLINING:
            # 双倍余额递减法
            if total <= 0:
                return 0.0
            rate = 2.0 / total
            remaining = original - asset['accumulated_depr']
            amount = remaining * rate
            # 最后两年改为直线法
            remaining_months = total - depr_months
            if remaining_months <= 24:
                amount = (remaining - residual_value) / remaining_months
            return max(amount, 0)

        elif method == self.METHOD_SUM_OF_YEARS:
            # 年数总和法
            years = total / 12.0
            remaining_years = (total - depr_months) / 12.0
            if years <= 0:
                return 0.0
            sum_years = years * (years + 1) / 2
            if sum_years <= 0:
                return 0.0
            amount = (original - residual_value) * (remaining_years / sum_years) / 12
            return max(amount, 0)

        return 0.0

    def calc_and_record_depr(self, period: str) -> Dict:
        """
        批量计提折旧
        返回：{'asset_count': int, 'total_amount': float, 'details': [...]}
        """
        conn = self.db_manager.get_current_conn()
        if not conn:
            raise RuntimeError("请先打开账套")

        # 获取当前会计制度的折旧规则
        depr_rule = self._get_depr_start_rule()
        if depr_rule == 'none':
            return {'asset_count': 0, 'total_amount': 0.0, 'details': [],
                    'message': '当前会计制度不计提固定资产折旧'}

        # 获取所有在用的资产
        cursor = conn.execute(
            "SELECT * FROM fixed_assets WHERE status='in_use'")
        columns = [desc[0] for desc in cursor.description]
        assets = [dict(zip(columns, row)) for row in cursor.fetchall()]

        now = datetime.now().isoformat()
        total_amount = 0.0
        details = []

        for asset in assets:
            # 检查该期间是否已计提
            cursor = conn.execute(
                "SELECT id FROM depr_details WHERE asset_id=? AND period=?",
                (asset['asset_id'], period))
            if cursor.fetchone():
                continue  # 已计提，跳过

            # 按会计制度规则判断是否该在本期提折旧
            if not self._should_depr_in_period(
                    asset.get('start_use_date', ''), period, depr_rule):
                continue

            amount = self.calc_monthly_depr(asset)
            if amount <= 0:
                continue

            # 记录折旧明细
            conn.execute('''
                INSERT INTO depr_details (asset_id, period, depr_amount, created_at)
                VALUES (?, ?, ?, ?)
            ''', (asset['asset_id'], period, amount, now))

            # 更新资产累计折旧
            new_accumulated = asset['accumulated_depr'] + amount
            new_depr_months = asset['depr_months'] + 1
            conn.execute('''
                UPDATE fixed_assets SET
                    accumulated_depr=?, depr_months=?, last_depr_date=?,
                    modified_at=?
                WHERE asset_id=?
            ''', (new_accumulated, new_depr_months, period, now, asset['asset_id']))

            total_amount += amount
            details.append({
                'asset_id': asset['asset_id'],
                'asset_name': asset['asset_name'],
                'asset_code': asset['asset_code'],
                'depr_amount': amount,
                'remaining_value': asset['original_value'] - new_accumulated,
            })

        conn.commit()

        return {
            'asset_count': len(details),
            'total_amount': total_amount,
            'details': details,
        }

    def get_depr_detail(self, period: str = None,
                        asset_id: int = None,
                        page: int = 1,
                        page_size: int = 50) -> Tuple[List[Dict], int]:
        """查询折旧明细"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0

        conditions = []
        params = []
        if period:
            conditions.append("d.period=?")
            params.append(period)
        if asset_id:
            conditions.append("d.asset_id=?")
            params.append(asset_id)

        where = " AND ".join(conditions) if conditions else "1=1"

        cursor = conn.execute(
            f"SELECT COUNT(*) FROM depr_details d WHERE {where}", params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        cursor = conn.execute(f'''
            SELECT d.*, a.asset_code, a.asset_name, a.original_value,
                   a.accumulated_depr, a.department
            FROM depr_details d
            LEFT JOIN fixed_assets a ON d.asset_id = a.asset_id
            WHERE {where}
            ORDER BY d.period DESC, a.asset_code
            LIMIT ? OFFSET ?
        ''', params + [page_size, offset])

        columns = [desc[0] for desc in cursor.description]
        records = [dict(zip(columns, row)) for row in cursor.fetchall()]

        return records, total

    # ──────────────────────────────────────────
    #  统计报表
    # ──────────────────────────────────────────

    def get_asset_summary(self) -> Dict:
        """资产汇总统计"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return {}

        cursor = conn.execute('''
            SELECT
                COUNT(*) as total_count,
                SUM(CASE WHEN status='in_use' THEN 1 ELSE 0 END) as in_use_count,
                COALESCE(SUM(original_value), 0) as total_original,
                COALESCE(SUM(CASE WHEN status='in_use' THEN original_value ELSE 0 END), 0) as in_use_original,
                COALESCE(SUM(accumulated_depr), 0) as total_depr,
                COALESCE(SUM(original_value - accumulated_depr), 0) as total_net
            FROM fixed_assets
        ''')
        row = cursor.fetchone()
        columns = [desc[0] for desc in cursor.description]
        return dict(zip(columns, row))

    def get_category_summary(self) -> List[Dict]:
        """按类别汇总"""
        conn = self.db_manager.get_current_conn()
        cursor = conn.execute('''
            SELECT
                COALESCE(category, '未分类') as category,
                COUNT(*) as count,
                COALESCE(SUM(original_value), 0) as original_total,
                COALESCE(SUM(accumulated_depr), 0) as depr_total,
                COALESCE(SUM(original_value - accumulated_depr), 0) as net_total
            FROM fixed_assets
            GROUP BY category
            ORDER BY original_total DESC
        ''')
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def get_depr_summary_by_period(self) -> List[Dict]:
        """按期间汇总折旧"""
        conn = self.db_manager.get_current_conn()
        cursor = conn.execute('''
            SELECT
                period,
                COUNT(*) as asset_count,
                COALESCE(SUM(depr_amount), 0) as total_depr
            FROM depr_details
            GROUP BY period
            ORDER BY period DESC
            LIMIT 12
        ''')
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def generate_depr_voucher(self, period: str) -> int:
        """
        根据当期折旧生成凭证
        借：管理费用/销售费用/制造费用-折旧费
        贷：累计折旧
        返回凭证ID
        """
        from core.voucher_service import VoucherService
        conn = self.db_manager.get_current_conn()

        # 检查会计制度是否计提折旧
        depr_rule = self._get_depr_start_rule()
        if depr_rule == 'none':
            raise ValueError("当前会计制度不计提固定资产折旧，无需生成凭证")

        # 先尝试计提（如有未计提的）
        result = self.calc_and_record_depr(period)

        # 检查当期已有折旧明细
        cursor = conn.execute(
            "SELECT COALESCE(SUM(depr_amount), 0) FROM depr_details WHERE period=?",
            (period,))
        total = cursor.fetchone()[0]

        if total <= 0:
            raise ValueError(f"期间 {period} 没有折旧数据，请先计提折旧")

        # 按部门汇总折旧金额（简化：全部计入管理费用）
        total = result['total_amount']

        vs = VoucherService(self.db_manager)
        entries = [
            {'summary': f'计提{period}折旧',
             'acct_code': '660204',  # 管理费用-折旧费（企业会计准则）
             'debit_amount': total, 'credit_amount': 0},
            {'summary': f'计提{period}折旧',
             'acct_code': '1602',    # 累计折旧
             'debit_amount': 0, 'credit_amount': total},
        ]

        voucher_id = vs.create_voucher(
            period=period,
            voucher_date=datetime.now().strftime('%Y-%m-%d'),
            voucher_type='记',
            entries=entries,
            remark=f'自动生成：计提{period}固定资产折旧',
        )
        return voucher_id

    # ═══════════════════════════════════════════
    #  资产变动管理（增值/拆分/合并）
    # ═══════════════════════════════════════════

    def _record_change(self, asset_id: int, change_type: str,
                       change_amount: float, old_value: float, new_value: float,
                       old_depr: float, new_depr: float,
                       change_date: str, reason: str,
                       target_ids: str = '', change_details: str = '') -> int:
        """记录资产变动到 asset_changes 表"""
        conn = self.db_manager.get_current_conn()
        now = datetime.now().isoformat()
        cursor = conn.execute('''
            INSERT INTO asset_changes
            (asset_id, change_type, change_amount, old_value, new_value,
             old_depr, new_depr, change_date, reason, target_asset_ids, change_details, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (asset_id, change_type, change_amount, old_value, new_value,
              old_depr, new_depr, change_date, reason, target_ids, change_details, now))
        conn.commit()
        return cursor.lastrowid

    MODIFIABLE_FIELDS = {
        'asset_name': '资产名称',
        'category': '类别',
        'specification': '规格型号',
        'department': '使用部门',
        'location': '存放地点',
        'original_value': '原值',
        'accumulated_depr': '累计折旧',
        'residual_rate': '残值率',
        'depr_method': '折旧方法',
        'total_months': '折旧期限(月)',
        'status': '状态',
    }

    def modify_asset(self, asset_id: int, changes: Dict,
                     change_date: str, reason: str = '') -> Dict:
        """
        通用资产信息变更——支持修改任意字段
        changes: {field_name: new_value, ...}
        可修改字段见 MODIFIABLE_FIELDS
        返回变更后的资产信息
        """
        import json
        conn = self.db_manager.get_current_conn()
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"资产 {asset_id} 不存在")

        now = datetime.now().isoformat()
        details = {}        # 记录变更明细 {field: {old: ..., new: ...}}
        update_fields = []  # SQL SET 子句
        update_values = []

        for field, new_val in changes.items():
            if field not in self.MODIFIABLE_FIELDS:
                continue

            old_val = asset.get(field)
            # 数字类型处理
            if isinstance(old_val, (int, float)):
                try:
                    new_val = float(new_val)
                except (ValueError, TypeError):
                    continue
                if abs(old_val - new_val) < 0.001:
                    continue
            else:
                if str(old_val) == str(new_val):
                    continue

            details[field] = {'old': old_val, 'new': new_val}
            update_fields.append(f"{field}=?")
            update_values.append(new_val)

        if not details:
            raise ValueError("没有检测到有效的变更内容")

        # 如果是原值或累计折旧变更，记录变动金额
        old_value = asset['original_value']
        new_value = old_value
        if 'original_value' in details:
            new_value = details['original_value']['new']

        old_depr = asset['accumulated_depr']
        new_depr = old_depr
        if 'accumulated_depr' in details:
            new_depr = details['accumulated_depr']['new']

        change_amount = new_value - old_value

        # 执行更新
        update_fields.append("modified_at=?")
        update_values.append(now)
        update_values.append(asset_id)

        conn.execute(
            f"UPDATE fixed_assets SET {','.join(update_fields)} WHERE asset_id=?",
            update_values)
        conn.commit()

        # 记录变动历史
        self._record_change(
            asset_id=asset_id,
            change_type='modify',
            change_amount=change_amount,
            old_value=old_value, new_value=new_value,
            old_depr=old_depr, new_depr=new_depr,
            change_date=change_date, reason=reason,
            change_details=json.dumps(details, ensure_ascii=False)
        )

        return self.get_asset(asset_id)

    def get_change_history(self, asset_id: int = None, page: int = 1,
                           page_size: int = 50) -> Tuple[List[Dict], int]:
        """查询资产变动历史"""
        conn = self.db_manager.get_current_conn()
        if not conn:
            return [], 0

        if asset_id:
            where, params = "c.asset_id=?", [asset_id]
        else:
            where, params = "1=1", []

        cursor = conn.execute(f"SELECT COUNT(*) FROM asset_changes c WHERE {where}", params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        cursor = conn.execute(f'''
            SELECT c.*, a.asset_code, a.asset_name
            FROM asset_changes c
            LEFT JOIN fixed_assets a ON c.asset_id = a.asset_id
            WHERE {where} ORDER BY c.created_at DESC LIMIT ? OFFSET ?
        ''', params + [page_size, offset])
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()], total

    def value_change(self, asset_id: int, change_amount: float,
                     change_date: str, reason: str = '') -> Dict:
        """
        资产原值变动（增值/减值）
        change_amount > 0 = 增值, < 0 = 减值
        返回变动后的资产信息
        """
        conn = self.db_manager.get_current_conn()
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"资产 {asset_id} 不存在")
        if asset['status'] != 'in_use':
            raise ValueError("只有使用中的资产才能进行原值变动")

        change_type = 'value_up' if change_amount > 0 else 'value_down'
        old_value = asset['original_value']
        new_value = old_value + change_amount
        if new_value <= 0:
            raise ValueError("变动后原值不能小于等于0")

        old_depr = asset['accumulated_depr']
        old_depr_rate = old_depr / old_value if old_value > 0 else 0
        new_depr = round(new_value * old_depr_rate, 2)

        now = datetime.now().isoformat()
        conn.execute('''
            UPDATE fixed_assets SET
                original_value=?, accumulated_depr=?,
                modified_at=?, remark=CASE WHEN ?!='' THEN ? ELSE remark END
            WHERE asset_id=?
        ''', (new_value, new_depr, now, reason, reason, asset_id))
        conn.commit()

        import json
        details = json.dumps({
            'original_value': {'old': old_value, 'new': new_value},
            'accumulated_depr': {'old': old_depr, 'new': new_depr},
        }, ensure_ascii=False)

        self._record_change(asset_id, change_type, change_amount,
                            old_value, new_value, old_depr, new_depr,
                            change_date, reason, change_details=details)

        return self.get_asset(asset_id)

    def split_asset(self, asset_id: int, parts: List[Dict],
                    change_date: str, reason: str = '') -> List[Dict]:
        """
        资产拆分
        parts: [{'asset_name': str, 'original_value': float,
                  'department': str, 'category': str}, ...]
        返回新创建的资产列表
        """
        conn = self.db_manager.get_current_conn()
        asset = self.get_asset(asset_id)
        if not asset:
            raise ValueError(f"资产 {asset_id} 不存在")

        total_split = sum(p['original_value'] for p in parts)
        if abs(total_split - asset['original_value']) > 0.01:
            raise ValueError(
                f"拆分金额合计 {total_split:,.2f} ≠ 原资产原值 {asset['original_value']:,.2f}")

        now = datetime.now().isoformat()
        old_value = asset['original_value']
        old_depr = asset['accumulated_depr']
        old_rate = old_depr / old_value if old_value > 0 else 0

        # 原始资产标记为已拆分
        conn.execute('''
            UPDATE fixed_assets SET status='deprecated', remark=?,
                modified_at=? WHERE asset_id=?
        ''', (f'已拆分:{reason}', now, asset_id))

        # 创建新资产
        new_ids = []
        for p in parts:
            part_depr = round(p['original_value'] * old_rate, 2)
            cursor = conn.execute('''
                INSERT INTO fixed_assets
                (asset_code, asset_name, category, specification, department,
                 location, original_value, accumulated_depr,
                 residual_rate, depr_method, total_months, depr_months,
                 purchase_date, start_use_date, last_depr_date,
                 status, remark, created_at, modified_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'in_use', ?, ?, ?)
            ''', (
                p.get('asset_code', f'{asset["asset_code"]}-SP{len(new_ids)+1}'),
                p['asset_name'],
                p.get('category', asset['category']),
                p.get('specification', asset.get('specification', '')),
                p.get('department', asset.get('department', '')),
                p.get('location', asset.get('location', '')),
                p['original_value'], part_depr,
                asset['residual_rate'], asset['depr_method'], asset['total_months'],
                asset['depr_months'],
                asset['purchase_date'], asset['start_use_date'], asset.get('last_depr_date', ''),
                reason, now, now
            ))
            new_ids.append(str(cursor.lastrowid))

        conn.commit()

        # 记录变动
        target_ids = ','.join(new_ids)
        import json
        parts_info = [{'name': p['asset_name'], 'value': p['original_value'],
                       'dept': p.get('department', ''),
                       'cat': p.get('category', '')} for p in parts]
        self._record_change(asset_id, 'split', 0,
                            old_value, 0, old_depr, 0,
                            change_date, reason, target_ids,
                            change_details=json.dumps({'parts': parts_info}, ensure_ascii=False))

        return [self.get_asset(int(pid)) for pid in new_ids]

    def merge_assets(self, source_ids: List[int], target_id: int,
                     change_date: str, reason: str = '') -> Dict:
        """
        资产合并：将多个资产合并到目标资产
        source_ids: 被合并的资产ID列表
        target_id: 目标资产ID（合并后保留的资产）
        """
        conn = self.db_manager.get_current_conn()
        target = self.get_asset(target_id)
        if not target:
            raise ValueError(f"目标资产 {target_id} 不存在")

        if target_id in source_ids:
            source_ids.remove(target_id)

        if not source_ids:
            raise ValueError("没有需要合并的资产")

        now = datetime.now().isoformat()
        total_add_value = 0.0
        total_add_depr = 0.0
        merged_codes = []

        for sid in source_ids:
            src = self.get_asset(sid)
            if not src:
                raise ValueError(f"资产 {sid} 不存在")
            if src['status'] != 'in_use':
                raise ValueError(f"资产 {src['asset_code']} 状态不是'使用中'")

            total_add_value += src['original_value']
            total_add_depr += src['accumulated_depr']
            merged_codes.append(src['asset_code'])

            # 被合并资产标记为已合并
            conn.execute('''
                UPDATE fixed_assets SET status='deprecated',
                    remark=CASE WHEN remark!='' THEN remark||';' ELSE '' END||?,
                    modified_at=? WHERE asset_id=?
            ''', (f'已合并至{target["asset_code"]}:{reason}', now, sid))

        # 更新目标资产
        new_value = target['original_value'] + total_add_value
        new_depr = target['accumulated_depr'] + total_add_depr
        conn.execute('''
            UPDATE fixed_assets SET
                original_value=?, accumulated_depr=?, modified_at=?
            WHERE asset_id=?
        ''', (new_value, new_depr, now, target_id))
        conn.commit()

        # 记录变动
        self._record_change(target_id, 'merge', total_add_value,
                            target['original_value'], new_value,
                            target['accumulated_depr'], new_depr,
                            change_date, f"{reason} (合并: {', '.join(merged_codes)})",
                            ','.join(str(s) for s in source_ids),
                            change_details=json.dumps({
                                'merged_assets': merged_codes,
                                'added_value': total_add_value,
                                'added_depr': total_add_depr,
                            }, ensure_ascii=False))

        return self.get_asset(target_id)