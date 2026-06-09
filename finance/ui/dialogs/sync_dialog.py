"""
==================================================
 ui/dialogs/sync_dialog.py - U盘同步对话框
==================================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFileDialog, QMessageBox, QProgressBar,
    QGroupBox, QTextEdit
)
from PyQt6.QtCore import Qt
from datetime import datetime


class SyncDialog(QDialog):
    """同步对话框"""

    def __init__(self, db_manager, parent=None, mode='export'):
        super().__init__(parent)
        self.db_manager = db_manager
        self.mode = mode  # 'export' 导出到U盘 / 'import' 从U盘合并

        title = '同步到U盘' if mode == 'export' else '从U盘合并'
        self.setWindowTitle(title)
        self.setMinimumWidth(500)
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)

        # 标题
        icon = '📤' if self.mode == 'export' else '📥'
        action = '导出到U盘' if self.mode == 'export' else '从U盘合并'
        layout.addWidget(QLabel(f'<h2>{icon} {action}</h2>'))

        # 说明
        hint = QLabel(
            '操作说明：\n'
            '1. 插上U盘\n'
            '2. 选择目标路径（U盘目录）\n'
            '3. 点击开始执行'
        )
        hint.setStyleSheet("color: #666; padding: 10px; background: #F5F6FA; border-radius: 4px;")
        layout.addWidget(hint)

        # 路径选择
        path_group = QGroupBox('选择路径')
        path_layout = QHBoxLayout(path_group)
        self._path_edit = QLabel('未选择')
        self._path_edit.setStyleSheet("color: #999; padding: 4px;")
        path_layout.addWidget(self._path_edit, 1)
        btn_browse = QPushButton('浏览...')
        btn_browse.clicked.connect(self._browse)
        path_layout.addWidget(btn_browse)
        layout.addWidget(path_group)

        # 进度条
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        # 日志
        self._log = QTextEdit()
        self._log.setReadOnly(True)
        self._log.setMaximumHeight(150)
        self._log.setStyleSheet("background: #FAFAFA; border: 1px solid #E0E0E0; border-radius: 4px;")
        layout.addWidget(self._log)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self._btn_exec = QPushButton('🚀 开始执行')
        self._btn_exec.setStyleSheet("""
            QPushButton { background: #1A73E8; color: white; padding: 8px 24px;
                          border-radius: 4px; font-size: 14px; }
            QPushButton:hover { background: #1557B0; }
        """)
        self._btn_exec.clicked.connect(self._execute)
        self._btn_exec.setEnabled(False)
        btn_layout.addWidget(self._btn_exec)
        btn_layout.addWidget(QPushButton('关闭', clicked=self.close))
        layout.addLayout(btn_layout)

    def _browse(self):
        if self.mode == 'export':
            path = QFileDialog.getExistingDirectory(self, '选择U盘目录')
        else:
            path, _ = QFileDialog.getOpenFileName(self, '选择便携数据库文件', '', '数据库文件 (*.db)')
        if path:
            self._path_edit.setText(path)
            self._path_edit.setStyleSheet("color: #333; padding: 4px;")
            self._btn_exec.setEnabled(True)

    def _execute(self):
        path = self._path_edit.text()
        book_id = self.db_manager.get_current_book_id()
        if not book_id:
            QMessageBox.warning(self, '提示', '请先选择账套')
            return

        self._progress.setVisible(True)
        self._progress.setRange(0, 0)  # 忙碌模式
        self._btn_exec.setEnabled(False)

        try:
            if self.mode == 'export':
                target = os.path.join(path, f'{book_id}_portable.db')
                self.db_manager.export_portable(book_id, target)
                self._log.append(f'✅ 已导出到: {target}')
            else:
                from core.sync_engine import SyncEngine
                engine = SyncEngine(self.db_manager)
                result = engine.merge(path, book_id)
                self._log.append(f'✅ 合并完成！新增: {result["inserted"]}, 更新: {result["updated"]}')
                for d in result['details']:
                    self._log.append(f'  {d}')
        except Exception as e:
            self._log.append(f'❌ 错误: {e}')
            QMessageBox.critical(self, '同步失败', str(e))
        finally:
            self._progress.setRange(0, 100)
            self._progress.setValue(100)
            self._btn_exec.setEnabled(True)