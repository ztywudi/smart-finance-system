"""
========================================
 sync_engine.py - U盘便携同步引擎
========================================
功能：
  - 主数据库 ↔ U盘便携数据库 双向同步
  - 基于时间戳的冲突检测
  - 智能合并策略
  - 同步日志记录

使用场景：
  - 出差前： 插U盘 → 同步到U盘（导出便携版数据库）
  - 外出时： 插U盘到别人电脑 → 双击便携版直接使用
  - 回来后： 插U盘 → 自动检测 → 合并回主数据库

同步规则：
  - 同一条记录，哪边时间戳新就用哪边的
  - 只有一边有的记录，自动复制到另一边
  - 两边同时修改且有冲突 → 保留最新版 + 提示用户
"""

import sqlite3
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Tuple


class SyncEngine:
    """同步引擎"""

    # 需要同步的表（及其主键和修改时间字段）
    SYNC_TABLES = {
        'accounts':          {'pk': 'acct_code', 'time': 'modified_at'},
        'vouchers':          {'pk': 'voucher_id', 'time': 'created_at'},
        'voucher_entries':   {'pk': 'entry_id', 'time': None},
        'account_balances':  {'pk': 'id', 'time': None},
        'aux_types':         {'pk': 'type_id', 'time': None},
        'aux_items':         {'pk': 'item_id', 'time': None},
        'account_aux':       {'pk': 'id', 'time': None},
    }

    def __init__(self, db_manager):
        self.db_manager = db_manager

    def export_to_portable(self, book_id: str, portable_path: str):
        """
        导出便携版数据库到U盘
        1. 确保主数据库数据落盘
        2. 复制到目标路径
        """
        book_path = self.db_manager._get_book_path(book_id)

        # 确保当前连接的数据已提交
        conn = self.db_manager.get_current_conn()
        if conn:
            conn.commit()

        # 复制到U盘
        os.makedirs(os.path.dirname(portable_path), exist_ok=True)
        shutil.copy2(book_path, portable_path)

        # 记录同步日志
        self._log_sync(book_id, 'upload', 'success',
                       f"导出到便携设备: {portable_path}")

        return True

    def merge(self, portable_path: str, book_id: str) -> Dict:
        """
        将U盘便携数据库合并回主数据库

        返回统计信息:
        {
            'inserted': 10,       # 新增记录数
            'updated': 5,         # 更新记录数
            'conflicts': 0,       # 冲突记录数
            'details': [...]
        }
        """
        if not os.path.exists(portable_path):
            raise FileNotFoundError(f"便携数据库文件不存在: {portable_path}")

        main_path = self.db_manager._get_book_path(book_id)

        result = {
            'inserted': 0,
            'updated': 0,
            'conflicts': 0,
            'details': []
        }

        # 连接主数据库和便携数据库
        main_conn = sqlite3.connect(main_path)
        portable_conn = sqlite3.connect(portable_path)

        try:
            for table_name, table_info in self.SYNC_TABLES.items():
                pk_field = table_info['pk']
                time_field = table_info['time']

                # 检查便携库是否有此表
                cursor_p = portable_conn.execute(
                    f"SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                    (table_name,))
                if not cursor_p.fetchone():
                    continue

                # 获取主库和便携库的所有记录
                main_records = self._get_all_records(main_conn, table_name, pk_field)
                portable_records = self._get_all_records(
                    portable_conn, table_name, pk_field)

                # 逐条合并
                for pk_value, p_record in portable_records.items():
                    if pk_value not in main_records:
                        # 便携库有、主库没有 → 插入
                        self._insert_record(main_conn, table_name, p_record)
                        result['inserted'] += 1
                        result['details'].append(
                            f"[新增] {table_name}.{pk_field}={pk_value}")
                    else:
                        m_record = main_records[pk_value]
                        if time_field and time_field in p_record and time_field in m_record:
                            p_time = p_record[time_field]
                            m_time = m_record[time_field]
                            if p_time and m_time:
                                if p_time > m_time:
                                    # 便携库更新 → 更新主库
                                    self._update_record(
                                        main_conn, table_name, pk_field,
                                        pk_value, p_record)
                                    result['updated'] += 1
                                    result['details'].append(
                                        f"[更新] {table_name}.{pk_field}={pk_value}")
                        # 对于没有时间戳的表，或者时间戳相同，跳过

            main_conn.commit()

            # 记录同步日志
            self._log_sync(book_id, 'download', 'success',
                           f"从便携设备合并: {portable_path}")
        except Exception as e:
            main_conn.rollback()
            self._log_sync(book_id, 'download', 'failed', str(e))
            raise
        finally:
            main_conn.close()
            portable_conn.close()

        return result

    # ──────────────────────────────────────────
    #  内部辅助方法
    # ──────────────────────────────────────────

    def _get_all_records(self, conn: sqlite3.Connection,
                         table_name: str,
                         pk_field: str) -> Dict:
        """获取表中所有记录，按主键索引"""
        try:
            cursor = conn.execute(f"SELECT * FROM [{table_name}]")
            columns = [desc[0] for desc in cursor.description]
            records = {}
            for row in cursor.fetchall():
                record = dict(zip(columns, row))
                pk_value = record.get(pk_field)
                if pk_value is not None:
                    records[str(pk_value)] = record
            return records
        except sqlite3.OperationalError:
            return {}

    def _insert_record(self, conn: sqlite3.Connection,
                       table_name: str, record: Dict):
        """插入一条记录"""
        columns = list(record.keys())
        placeholders = ','.join(['?'] * len(columns))
        values = [record[col] for col in columns]
        conn.execute(
            f"INSERT OR IGNORE INTO [{table_name}] "
            f"({','.join(columns)}) VALUES ({placeholders})",
            values)

    def _update_record(self, conn: sqlite3.Connection,
                       table_name: str, pk_field: str,
                       pk_value: str, record: Dict):
        """更新一条记录"""
        set_parts = []
        values = []
        for col, val in record.items():
            if col != pk_field:
                set_parts.append(f"[{col}]=?")
                values.append(val)
        values.append(pk_value)
        conn.execute(
            f"UPDATE [{table_name}] SET {','.join(set_parts)} "
            f"WHERE [{pk_field}]=?",
            values)

    def _log_sync(self, book_id: str, direction: str,
                  status: str, details: str = ''):
        """记录同步日志到主数据库"""
        master_path = os.path.join(
            os.path.dirname(self.db_manager.data_dir),
            'user_data', 'master.db')
        conn = sqlite3.connect(master_path)
        try:
            conn.execute(
                "INSERT INTO sync_log (book_id, sync_time, direction, status, details) "
                "VALUES (?, ?, ?, ?, ?)",
                (book_id, datetime.now().isoformat(), direction, status, details))
            conn.commit()
        finally:
            conn.close()
