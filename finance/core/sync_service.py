"""
==========================================
 core/sync_service.py - U盘同步服务
==========================================
功能：
  - 检测U盘/USB设备路径
  - 导出账套到U盘（数据库+元数据打包）
  - 从U盘导入账套
  - 设备列表管理
"""

import sys, os, json, shutil, zipfile, glob
from datetime import datetime
from typing import List, Dict, Tuple


class SyncService:
    """U盘同步服务"""

    SYNC_DIR = '.finance_sync'       # U盘上的同步目录名
    BACKUP_DIR = '.finance_backups'  # 本地备份目录
    DB_DIR = ''                      # 数据库目录（运行时设置）

    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.DB_DIR = db_manager.data_dir

    # ────────────────────────────────
    #  U盘检测
    # ────────────────────────────────
    def detect_usb_drives(self) -> List[Dict]:
        """
        检测系统中的U盘/可移动设备
        返回：[{'path': '/media/usb0', 'label': 'U盘1', 'size': '32G'}, ...]
        """
        drives = []
        checked_paths = set()

        # 常见U盘挂载点
        mount_points = [
            '/media', '/mnt', '/run/media',
            os.path.expanduser('~/Desktop'),
            os.path.expanduser('~/Downloads'),
        ]

        # Windows检测
        if sys.platform == 'win32':
            try:
                import string
                from ctypes import windll
                drives_letters = []
                bitmask = windll.kernel32.GetLogicalDrives()
                for letter in string.ascii_uppercase:
                    if bitmask & 1:
                        path = f'{letter}:\\'
                        if letter != 'C':  # 排除C盘
                            drives_letters.append(path)
                    bitmask >>= 1
                for dp in drives_letters:
                    try:
                        label = os.path.basename(os.path.realpath(dp))
                        drives.append({
                            'path': dp, 'label': label or f'磁盘{len(drives)+1}',
                            'type': 'removable' if dp[0] != 'C' else 'fixed'
                        })
                    except: pass
            except: pass
        else:
            # Linux/macOS
            for mp in mount_points:
                if os.path.isdir(mp):
                    try:
                        for item in os.listdir(mp):
                            full = os.path.join(mp, item)
                            if full in checked_paths:
                                continue
                            checked_paths.add(full)
                            if os.path.isdir(full) and os.access(full, os.W_OK):
                                drives.append({
                                    'path': full,
                                    'label': item,
                                    'type': 'removable'
                                })
                    except PermissionError:
                        pass

        # 如果没找到任何U盘，添加当前目录作为备选
        if not drives:
            drives.append({
                'path': os.path.expanduser('~/Desktop'),
                'label': '桌面',
                'type': 'local'
            })
            drives.append({
                'path': os.path.expanduser('~'),
                'label': '用户目录',
                'type': 'local'
            })

        return drives

    # ────────────────────────────────
    #  导出账套到U盘
    # ────────────────────────────────
    def export_to_usb(self, book_id: str, target_dir: str) -> str:
        """
        导出账套到U盘
        返回导出文件路径
        """
        # 获取账套信息
        book_info = self.db_manager.get_account_book(book_id)
        if not book_info:
            raise ValueError(f"账套 {book_id} 不存在")

        # 创建同步目录
        sync_path = os.path.join(target_dir, self.SYNC_DIR)
        os.makedirs(sync_path, exist_ok=True)

        # 源数据库路径
        db_path = self.db_manager.get_book_db_path(book_id)
        if not os.path.exists(db_path):
            raise ValueError(f"账套数据库文件不存在: {db_path}")

        # 目标文件名：账套名_日期.sync
        book_name = book_info.get('book_name', book_id)
        safe_name = ''.join(c for c in book_name if c.isalnum() or c in ' _-')
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_name = f'{safe_name}_{timestamp}.syncz'
        export_path = os.path.join(sync_path, export_name)

        # 打包：数据库 + 元数据
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            # 1. 数据库文件 - 使用原始文件名
            db_filename = os.path.basename(db_path)
            zf.write(db_path, db_filename)

            # 2. 元数据JSON
            meta = {
                'book_id': book_id,
                'book_name': book_info.get('book_name', ''),
                'accounting_system': book_info.get('accounting_system', ''),
                'company_name': book_info.get('company_name', ''),
                'export_date': datetime.now().isoformat(),
                'db_file': db_filename,
                'version': '1.0',
            }
            zf.writestr('metadata.json', json.dumps(meta, ensure_ascii=False, indent=2))

        return export_path

    # ────────────────────────────────
    #  从U盘导入账套
    # ────────────────────────────────
    def list_sync_files(self, usb_path: str) -> List[Dict]:
        """列出U盘上的同步文件"""
        sync_path = os.path.join(usb_path, self.SYNC_DIR)
        if not os.path.isdir(sync_path):
            return []

        files = []
        for f in sorted(glob.glob(os.path.join(sync_path, '*.syncz')),
                        key=os.path.getmtime, reverse=True):
            try:
                with zipfile.ZipFile(f, 'r') as zf:
                    if 'metadata.json' in zf.namelist():
                        meta = json.loads(zf.read('metadata.json'))
                        files.append({
                            'filepath': f,
                            'filename': os.path.basename(f),
                            'book_name': meta.get('book_name', '未知'),
                            'book_id': meta.get('book_id', ''),
                            'system': meta.get('accounting_system', ''),
                            'export_date': meta.get('export_date', ''),
                            'size': os.path.getsize(f),
                        })
            except Exception as e:
                files.append({
                    'filepath': f,
                    'filename': os.path.basename(f),
                    'error': str(e),
                })
        return files

    def import_from_usb(self, sync_filepath: str) -> Dict:
        """
        从U盘同步文件导入账套
        返回导入结果
        """
        if not os.path.isfile(sync_filepath):
            raise FileNotFoundError(f"文件不存在: {sync_filepath}")

        with zipfile.ZipFile(sync_filepath, 'r') as zf:
            # 读取元数据
            meta = json.loads(zf.read('metadata.json'))
            book_id = meta['book_id']
            book_name = meta.get('book_name', '导入账套')
            company_name = meta.get('company_name', '')
            accounting_system = meta.get('accounting_system', 'ENT_STANDARD')

            # 检查本地是否存在同名账套
            existing = self.db_manager.get_account_book(book_id)
            if existing:
                self._backup_local(book_id)
                db_path = self.db_manager.get_book_db_path(book_id)
                db_fn = meta.get('db_file', f'{book_id}.db')
                if db_fn in zf.namelist():
                    zf.extract(db_fn, os.path.dirname(db_path))
                    if os.path.basename(db_path) != db_fn:
                        shutil.move(os.path.join(os.path.dirname(db_path), db_fn), db_path)
                msg = f'已覆盖更新账套: {book_name}（原数据已备份）'
            else:
                db_path = self.db_manager.get_book_db_path(book_id)
                os.makedirs(os.path.dirname(db_path), exist_ok=True)
                db_fn = meta.get('db_file', f'{book_id}.db')
                if db_fn in zf.namelist():
                    zf.extract(db_fn, os.path.dirname(db_path))
                    if os.path.basename(db_path) != db_fn:
                        shutil.move(os.path.join(os.path.dirname(db_path), db_fn), db_path)
                self.db_manager.register_imported_book(
                    book_id, book_name, accounting_system, company_name)
                msg = f'已导入新账套: {book_name}'

        return {
            'book_id': book_id,
            'book_name': book_name,
            'message': msg,
        }

    # ────────────────────────────────
    #  本地备份
    # ────────────────────────────────
    def _backup_local(self, book_id: str):
        """本地备份一个账套"""
        backup_base = os.path.join(self.DB_DIR, self.BACKUP_DIR)
        os.makedirs(backup_base, exist_ok=True)
        db_path = self.db_manager.get_book_db_path(book_id)
        if not os.path.isfile(db_path):
            return

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = os.path.join(backup_base, f'{book_id}_{timestamp}.bak')
        shutil.copy2(db_path, backup_path)

        # 清理旧备份（保留最近10个）
        backups = sorted(glob.glob(os.path.join(backup_base, f'{book_id}_*.bak')),
                        key=os.path.getmtime, reverse=True)
        for old in backups[10:]:
            try: os.remove(old)
            except: pass

    def list_local_backups(self, book_id: str = None) -> List[Dict]:
        """列出本地备份"""
        backup_base = os.path.join(self.DB_DIR, self.BACKUP_DIR)
        if not os.path.isdir(backup_base):
            return []
        pattern = f'{book_id}_*.bak' if book_id else '*_*.bak'
        backups = []
        for f in sorted(glob.glob(os.path.join(backup_base, pattern)),
                        key=os.path.getmtime, reverse=True):
            fname = os.path.basename(f)
            parts = fname.replace('.bak', '').split('_')
            bid = parts[0] if parts else 'unknown'
            ts = parts[1] if len(parts) > 1 else ''
            backups.append({
                'path': f, 'filename': fname,
                'book_id': bid, 'timestamp': ts,
                'size': os.path.getsize(f),
            })
        return backups

    def restore_from_backup(self, backup_path: str) -> Dict:
        """从本地备份恢复"""
        fname = os.path.basename(backup_path)
        parts = fname.replace('.bak', '').split('_')
        book_id = parts[0] if parts else 'unknown'

        db_path = self.db_manager.get_book_db_path(book_id)
        if not os.path.isfile(backup_path):
            raise FileNotFoundError(f"备份文件不存在: {backup_path}")

        # 当前数据再备份一次
        self._backup_local(book_id)
        shutil.copy2(backup_path, db_path)

        return {
            'book_id': book_id,
            'message': f'已从备份恢复: {fname}',
        }