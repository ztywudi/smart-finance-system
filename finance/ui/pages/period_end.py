"""
==============================================
 ui/pages/period_end.py - 期末处理页面
==============================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QTableWidget, QTableWidgetItem, QHeaderView,
    QGroupBox, QCheckBox, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt


class PeriodEndPage(QWidget):
    """期末处理页面"""

    def __init__(self, db_manager, tab='close'):
        super().__init__()
        self.db_manager = db_manager
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel('<h2>🔄 期末处理</h2>')
        layout.addWidget(title)

        # 检查清单
        check_group = QGroupBox('结账前检查清单')
        check_group.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; }
        """)
        check_layout = QVBoxLayout(check_group)
        check_layout.setSpacing(8)

        checks = [
            '所有凭证是否已审核',
            '所有凭证是否已过账',
            '试算平衡是否通过',
            '固定资产折旧是否已计提',
            '工资是否已计提',
            '税费是否已计提',
            '损益类科目是否已结转',
            '是否有未处理的暂估/待摊',
        ]

        self._checkboxes = {}
        for text in checks:
            cb = QCheckBox(text)
            cb.setStyleSheet("font-size: 13px; padding: 4px 0;")
            self._checkboxes[text] = cb
            check_layout.addWidget(cb)

        # 操作按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        btn_check = QPushButton('🔍 全部检查')
        btn_check.setStyleSheet("""
            QPushButton { background: #FBBC04; color: white; padding: 8px 24px;
                          border-radius: 4px; font-size: 13px; }
            QPushButton:hover { background: #F9A825; }
        """)
        btn_layout.addWidget(btn_check)

        self._btn_close = QPushButton('🔒 执行结账')
        self._btn_close.setStyleSheet("""
            QPushButton { background: #EA4335; color: white; padding: 8px 24px;
                          border-radius: 4px; font-size: 13px; font-weight: bold; }
            QPushButton:hover { background: #D32F2F; }
        """)
        self._btn_close.clicked.connect(self._execute_close)
        btn_layout.addWidget(self._btn_close)

        layout.addWidget(check_group)
        layout.addLayout(btn_layout)

        # 进度
        self._progress = QProgressBar()
        self._progress.setVisible(False)
        layout.addWidget(self._progress)

        layout.addStretch()

    def _execute_close(self):
        """执行结账"""
        reply = QMessageBox.question(
            self, '确认结账',
            '确定要进行期末结账吗？\n'
            '结账后该期间不能修改凭证。\n\n'
            '请确保已完成所有检查项！',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, '提示', '期末结账功能开发中...')

    def refresh(self):
        pass

    def on_activate(self, book_id):
        pass