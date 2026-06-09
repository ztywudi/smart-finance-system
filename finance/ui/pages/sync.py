"""
==============================================
 ui/pages/sync.py - U盘同步页面
==============================================
功能：导出账套到U盘、从U盘导入账套、本地备份管理
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QComboBox, QHeaderView, QMessageBox,
    QAbstractItemView, QGroupBox, QGridLayout, QFrame,
    QFileDialog, QProgressBar, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QColor

from core.sync_service import SyncService


class SyncPage(QWidget):
    """U盘同步页面"""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.service = SyncService(db_manager)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(16)

        # ===== 标题 =====
        title = QLabel('<span style="font-size:18px;font-weight:bold;">💾 U盘同步</span>')
        layout.addWidget(title)

        # ===== 当前账套 =====
        self._book_info = QLabel('当前账套：未选择')
        self._book_info.setStyleSheet("padding:10px;background:#F5F6FA;border-radius:4px;")
        layout.addWidget(self._book_info)

        # ===== U盘检测 =====
        usb_group = QGroupBox('📀 目标位置')
        usb_group.setStyleSheet("QGroupBox{font-weight:bold;padding-top:16px;}")
        usb_layout = QHBoxLayout(usb_group)

        self._usb_combo = QComboBox()
        self._usb_combo.setMinimumWidth(300)
        usb_layout.addWidget(self._usb_combo, 1)

        btn_detect = QPushButton('🔍 检测')
        btn_detect.setStyleSheet("padding:6px 16px;")
        btn_detect.clicked.connect(self._detect_usb)
        usb_layout.addWidget(btn_detect)

        btn_open = QPushButton('📂 浏览...')
        btn_open.clicked.connect(self._browse_folder)
        usb_layout.addWidget(btn_open)

        layout.addWidget(usb_group)

        # ===== 操作按钮 =====
        op_layout = QHBoxLayout()
        op_layout.setSpacing(16)

        btn_export = QPushButton('📤 导出到U盘')
        btn_export.setStyleSheet("""
            QPushButton { background:#1A73E8; color:white; padding:12px 32px;
                         border-radius:6px; font-size:14px; font-weight:bold; }
            QPushButton:hover { background:#1565C0; }
        """)
        btn_export.clicked.connect(self._do_export)
        op_layout.addWidget(btn_export)

        btn_import = QPushButton('📥 从U盘导入')
        btn_import.setStyleSheet("""
            QPushButton { background:#34A853; color:white; padding:12px 32px;
                         border-radius:6px; font-size:14px; font-weight:bold; }
            QPushButton:hover { background:#2E7D32; }
        """)
        btn_import.clicked.connect(self._do_import)
        op_layout.addWidget(btn_import)

        btn_restore = QPushButton('🔄 本地恢复')
        btn_restore.setStyleSheet("""
            QPushButton { background:#FF9800; color:white; padding:12px 32px;
                         border-radius:6px; font-size:14px; font-weight:bold; }
            QPushButton:hover { background:#F57C00; }
        """)
        btn_restore.clicked.connect(self._do_restore)
        op_layout.addWidget(btn_restore)

        op_layout.addStretch()
        layout.addLayout(op_layout)

        # ===== 日志输出 =====
        log_group = QGroupBox('📋 操作日志')
        log_group.setStyleSheet("QGroupBox{font-weight:bold;padding-top:16px;}")
        log_layout = QVBoxLayout(log_group)

        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(150)
        self._log.setStyleSheet("background:#F5F6FA;border:1px solid #E0E0E0;border-radius:4px;padding:8px;")
        log_layout.addWidget(self._log)

        layout.addWidget(log_group)

        # ===== 同步文件列表 =====
        list_group = QGroupBox('📁 U盘上的同步文件')
        list_group.setStyleSheet("QGroupBox{font-weight:bold;padding-top:16px;}")
        list_layout = QVBoxLayout(list_group)

        tool = QHBoxLayout()
        btn_refresh = QPushButton('🔄 刷新列表')
        btn_refresh.clicked.connect(self._refresh_files)
        tool.addWidget(btn_refresh)
        tool.addStretch()
        list_layout.addLayout(tool)

        self._file_table = QTableWidget(0, 5)
        self._file_table.setHorizontalHeaderLabels(['文件名', '账套名', '会计制度', '导出时间', '大小'])
        self._file_table.horizontalHeader().setStretchLastSection(True)
        self._file_table.setAlternatingRowColors(True)
        self._file_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self._file_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        list_layout.addWidget(self._file_table, 1)

        layout.addWidget(list_group, 1)

    def on_activate(self, book_id):
        """页面激活时调用"""
        info = self.db_manager.get_account_book(book_id) if book_id else None
        if info:
            self._book_info.setText(
                f'<b>当前账套：</b>{info.get("book_name", "未知")} '
                f'({info.get("company_name", "")}) '
                f'<span style="color:#999;">ID: {book_id}</span>')
            self._current_book_id = book_id
        else:
            self._book_info.setText('当前账套：未选择')

        self._detect_usb()

    def refresh(self):
        self._detect_usb()

    # ──── 工具方法 ────

    def _log_msg(self, msg, level='info'):
        """记录日志"""
        ts = datetime.now().strftime('%H:%M:%S')
        colors = {'info': '#333', 'success': '#2E7D32', 'error': '#C62828', 'warn': '#F57C00'}
        color = colors.get(level, '#333')
        self._log.append(f'<span style="color:{color};">[{ts}] {msg}</span>')

    def _detect_usb(self):
        """检测U盘"""
        self._usb_combo.clear()
        drives = self.service.detect_usb_drives()
        if drives:
            for d in drives:
                label = d.get('label', '未知')
                path = d['path']
                self._usb_combo.addItem(f'💾 {label} ({path})', path)
            self._log_msg(f'检测到 {len(drives)} 个可用位置', 'success')
        else:
            self._usb_combo.addItem('未检测到U盘，请插入后重试', '')
            self._log_msg('未检测到U盘', 'warn')
        self._refresh_files()

    def _browse_folder(self):
        """手动选择文件夹"""
        path = QFileDialog.getExistingDirectory(self, '选择目标文件夹')
        if path:
            self._usb_combo.insertItem(0, f'📂 {os.path.basename(path)} ({path})', path)
            self._usb_combo.setCurrentIndex(0)
            self._refresh_files()

    def _get_target_path(self) -> str:
        """获取当前选择的U盘路径"""
        return self._usb_combo.currentData() or ''

    def _refresh_files(self):
        """刷新U盘上的同步文件列表"""
        path = self._get_target_path()
        if not path:
            self._file_table.setRowCount(0)
            return
        try:
            files = self.service.list_sync_files(path)
            self._file_table.setRowCount(len(files))
            for i, f in enumerate(files):
                self._file_table.setItem(i, 0, QTableWidgetItem(f.get('filename', '')))
                self._file_table.setItem(i, 1, QTableWidgetItem(f.get('book_name', '')))
                self._file_table.setItem(i, 2, QTableWidgetItem(f.get('system', '')))
                ed = f.get('export_date', '')
                if ed:
                    try:
                        ed = ed[:19].replace('T', ' ')
                    except: pass
                self._file_table.setItem(i, 3, QTableWidgetItem(ed))
                sz = f.get('size', 0)
                size_str = f'{sz/1024:.1f}KB' if sz < 1024*1024 else f'{sz/1024/1024:.1f}MB'
                self._file_table.setItem(i, 4, QTableWidgetItem(size_str))
                self._file_table.item(i, 0).setData(Qt.ItemDataRole.UserRole, f.get('filepath', ''))
        except Exception as e:
            self._log_msg(f'刷新文件列表失败: {e}', 'error')

    def _do_export(self):
        """导出账套到U盘"""
        book_id = getattr(self, '_current_book_id', None)
        if not book_id:
            QMessageBox.warning(self, '提示', '请先选择一个账套')
            return

        path = self._get_target_path()
        if not path:
            QMessageBox.warning(self, '提示', '请选择目标位置')
            return

        try:
            self._log_msg(f'正在导出账套到 {path}...', 'info')
            export_path = self.service.export_to_usb(book_id, path)
            self._log_msg(f'✅ 导出成功！文件: {os.path.basename(export_path)}', 'success')
            self._refresh_files()
        except Exception as e:
            self._log_msg(f'❌ 导出失败: {e}', 'error')
            QMessageBox.critical(self, '导出失败', str(e))

    def _do_import(self):
        """从U盘导入账套"""
        row = self._file_table.currentRow()
        if row < 0:
            QMessageBox.warning(self, '提示', '请先选择要导入的同步文件')
            return

        filepath = self._file_table.item(row, 0).data(Qt.ItemDataRole.UserRole)
        name = self._file_table.item(row, 1).text() or self._file_table.item(row, 0).text()

        reply = QMessageBox.question(self, '确认导入',
            f'确定要从U盘导入账套 "{name}" 吗？\n\n'
            f'• 如果本地已有同名账套，将覆盖更新（原数据会自动备份）\n'
            f'• 如果本地没有同名账套，将新建账套',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            self._log_msg(f'正在导入 {name}...', 'info')
            result = self.service.import_from_usb(filepath)
            self._log_msg(f'✅ {result["message"]}', 'success')
            QMessageBox.information(self, '导入成功', result['message'])
        except Exception as e:
            self._log_msg(f'❌ 导入失败: {e}', 'error')
            QMessageBox.critical(self, '导入失败', str(e))

    def _do_restore(self):
        """从本地备份恢复"""
        backups = self.service.list_local_backups()
        if not backups:
            QMessageBox.information(self, '提示', '没有找到本地备份')
            return

        # 选最近的备份
        b = backups[0]
        reply = QMessageBox.question(self, '确认恢复',
            f'找到最近的备份:\n'
            f'  账套: {b["book_id"]}\n'
            f'  时间: {b["timestamp"]}\n'
            f'  大小: {b["size"]/1024:.1f}KB\n\n'
            f'恢复会覆盖当前数据（当前数据会自动备份）\n确定恢复吗？',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply != QMessageBox.StandardButton.Yes:
            return

        try:
            result = self.service.restore_from_backup(b['path'])
            self._log_msg(f'✅ {result["message"]}', 'success')
            QMessageBox.information(self, '恢复成功', result['message'])
        except Exception as e:
            self._log_msg(f'❌ 恢复失败: {e}', 'error')
            QMessageBox.critical(self, '恢复失败', str(e))