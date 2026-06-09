"""
==============================================
 ui/pages/dashboard.py - 工作台页面
==============================================
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QTableWidget,
    QTableWidgetItem, QHeaderView, QGroupBox, QScrollArea
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QColor


class StatCard(QFrame):
    """统计卡片组件"""

    def __init__(self, title, value, subtitle='', color='#1A73E8', icon='📊'):
        super().__init__()
        self.setStyleSheet(f"""
            StatCard {{
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 8px;
                border-left: 4px solid {color};
            }}
        """)
        self.setMinimumHeight(120)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 12, 16, 12)

        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)

        val_label = QLabel(str(value))
        val_label.setStyleSheet(f"font-size: 28px; font-weight: bold; color: {color};")
        layout.addWidget(val_label)

        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 13px; color: #666;")
        layout.addWidget(title_label)

        if subtitle:
            sub = QLabel(subtitle)
            sub.setStyleSheet("font-size: 11px; color: #999;")
            layout.addWidget(sub)


class QuickActionBtn(QPushButton):
    """快捷操作按钮"""

    def __init__(self, text, icon='', color='#1A73E8'):
        super().__init__(f'{icon}  {text}')
        self.setMinimumHeight(50)
        self.setStyleSheet(f"""
            QPushButton {{
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 6px;
                font-size: 14px;
                text-align: left;
                padding: 12px 16px;
            }}
            QPushButton:hover {{
                background: #F0F6FF;
                border-color: {color};
            }}
        """)
        self.setCursor(Qt.CursorShape.PointingHandCursor)


class DashboardPage(QWidget):
    """工作台概览页面"""

    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self._setup()

    def _setup(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # 欢迎标题
        title = QLabel(f'<h1>📊 工作台</h1>')
        title.setStyleSheet("color: #333;")
        layout.addWidget(title)

        # 统计卡片
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(16)

        stats_layout.addWidget(StatCard('本月凭证数', '--', '待生成', '#1A73E8', '📝'))
        stats_layout.addWidget(StatCard('已审核', '--', '待审核', '#34A853', '✅'))
        stats_layout.addWidget(StatCard('已过账', '--', '待过账', '#FBBC04', '📌'))
        stats_layout.addWidget(StatCard('本期状态', '--', '未结账', '#EA4335', '🔄'))

        layout.addLayout(stats_layout)

        # 快捷操作
        action_group = QGroupBox('快捷操作')
        action_group.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; }
        """)
        action_layout = QGridLayout(action_group)
        action_layout.setSpacing(10)

        actions = [
            ('📝', '录入凭证', '#1A73E8'),
            ('✅', '审核凭证', '#34A853'),
            ('📌', '过账', '#FBBC04'),
            ('📑', '生成报表', '#EA4335'),
            ('💰', '银行对账', '#9C27B0'),
            ('🏭', '计提折旧', '#FF9800'),
            ('🔄', '结转损益', '#00BCD4'),
            ('📋', '科目余额表', '#607D8B'),
        ]

        for i, (icon, text, color) in enumerate(actions):
            btn = QuickActionBtn(text, icon, color)
            row, col = i // 4, i % 4
            action_layout.addWidget(btn, row, col)

        layout.addWidget(action_group)

        # 最近凭证
        recent_group = QGroupBox('最近凭证')
        recent_group.setStyleSheet("""
            QGroupBox { font-weight: bold; font-size: 14px; padding-top: 16px; }
        """)
        recent_layout = QVBoxLayout(recent_group)

        self._recent_table = QTableWidget(0, 5)
        self._recent_table.setHorizontalHeaderLabels(['日期', '凭证号', '摘要', '金额', '状态'])
        self._recent_table.horizontalHeader().setStretchLastSection(True)
        self._recent_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self._recent_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._recent_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._recent_table.setAlternatingRowColors(True)
        self._recent_table.setMaximumHeight(200)
        self._recent_table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 1px solid #E0E0E0;
                border-radius: 4px;
            }
            QHeaderView::section {
                background: #F8F9FA;
                border: none;
                border-bottom: 2px solid #E0E0E0;
                padding: 8px;
                font-weight: bold;
            }
        """)
        self._recent_table.setRowCount(0)
        recent_layout.addWidget(self._recent_table)

        layout.addWidget(recent_group)
        layout.addStretch()

    def on_activate(self, book_id):
        """页面被激活时刷新"""
        self.refresh()

    def refresh(self):
        """刷新数据"""
        # 这里后续从数据库加载真实数据
        pass