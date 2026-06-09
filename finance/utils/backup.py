"""
==========================================
 utils/backup.py - 备份恢复工具
==========================================
"""

import os
import shutil
import zipfile
from datetime import datetime
from typing import List


class BackupManager:
    """备份管理器"""

    def __init__(self, data_dir: str):
        self.data_dir = data_dir

    def create_full_backup(self, backup_path: str = None) -> str:
        """创建完整备份（所有账套 + master.db，打包为zip）"""
        if backup_path is None:
            backup_dir = os.path.join(os.path.dirname(self.data_dir), 'backup')
            os.makedirs(backup_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(backup_dir, f'full_backup_{timestamp}.zip')

        with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for root, dirs, files in os.walk(self.data_dir):
                for file in files:
                    if file.endswith('.db') or file.endswith('.db-wal') or file.endswith('.db-shm'):
                        filepath = os.path.join(root, file)
                        arcname = os.path.relpath(filepath, os.path.dirname(self.data_dir))
                        zf.write(filepath, arcname)

        return backup_path

    def restore_from_backup(self, backup_path: str):
        """从备份文件恢复"""
        with zipfile.ZipFile(backup_path, 'r') as zf:
            zf.extractall(os.path.dirname(self.data_dir))
        return True

    def list_backups(self) -> List[str]:
        """列出可用备份"""
        backup_dir = os.path.join(os.path.dirname(self.data_dir), 'backup')
        if not os.path.exists(backup_dir):
            return []
        return sorted([
            os.path.join(backup_dir, f)
            for f in os.listdir(backup_dir)
            if f.endswith('.zip')
        ], reverse=True)
