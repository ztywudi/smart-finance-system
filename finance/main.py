"""
==========================================
 main.py - 财务软件主入口
==========================================
启动流程：
  1. 初始化数据库管理器（主数据库 + 检测已有账套）
  2. 初始化会计制度注册表
  3. 加载UI（登录 → 选择/新建账套 → 主界面）
  4. 进入主循环

命令行模式（无GUI）：
  python main.py --cli          # 命令行模式
  python main.py --backup       # 备份所有账套
  python main.py --portable     # 构建便携版
"""

import sys
import os


def main():
    """主入口"""
    # 确保项目根目录在路径中
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)

    # ── 命令行模式 ──
    if len(sys.argv) > 1:
        cli_mode(sys.argv[1:])
        return

    # ── GUI 模式 ──
    print("=" * 50)
    print("  财务软件 v1.0")
    print("  支持多会计制度 · 多账套 · U盘便携同步")
    print("=" * 50)

    # 初始化核心模块
    from core.database import DatabaseManager
    db_manager = DatabaseManager()
    print(f"  ✓ 数据库就绪: {db_manager.data_dir}")

    from accounting_systems.system_registry import get_available_systems
    systems = get_available_systems()
    print(f"  ✓ 已加载 {len(systems)} 种会计制度:")
    for s in systems:
        print(f"     - {s['code']}: {s['name']}")

    # 检测已有账套
    books = db_manager.list_account_books()
    if books:
        print(f"\n  📂 已有 {len(books)} 个账套:")
        for b in books:
            print(f"     [{b['book_id']}] {b['book_name']} ({b['accounting_system']})")
    else:
        print("\n  📂 暂无账套，请先新建账套")

    # 启动GUI
    print("\n  🚀 启动界面...")
    _launch_gui(db_manager)


def _launch_gui(db_manager):
    """启动图形界面（PyQt6）"""
    try:
        from PyQt6.QtWidgets import QApplication
        from ui.main_window import MainWindow

        app = QApplication(sys.argv)

        # 设置应用信息
        app.setApplicationName('财务软件')
        app.setApplicationVersion('1.0.0')

        # 加载样式表
        style_path = os.path.join(
            os.path.dirname(__file__), 'resources', 'styles', 'main.qss')
        if os.path.exists(style_path):
            with open(style_path, 'r', encoding='utf-8') as f:
                app.setStyleSheet(f.read())

        window = MainWindow(db_manager)
        window.show()

        sys.exit(app.exec())

    except ImportError as e:
        print(f"  ⚠️  无法启动GUI: {e}")
        print("  💡 请安装依赖: pip install PyQt6")
        print("  进入命令行模式\n")
        _cli_demo(db_manager)


def _cli_demo(db_manager):
    """命令行演示模式"""
    from core.account_system import AccountingSystemManager

    while True:
        print("\n" + "─" * 40)
        print("  主菜单")
        print("─" * 40)
        print("  1. 新建账套")
        print("  2. 查看账套列表")
        print("  3. 查看会计制度")
        print("  0. 退出")
        print("─" * 40)

        choice = input("  请选择 [0-3]: ").strip()

        if choice == '1':
            _cli_create_book(db_manager)
        elif choice == '2':
            books = db_manager.list_account_books()
            if books:
                print("\n  账套列表:")
                for b in books:
                    sys_info = AccountingSystemManager.get_system(b['accounting_system'])
                    sys_name = sys_info.name if sys_info else b['accounting_system']
                    print(f"  [{b['book_id']}] {b['book_name']} - {sys_name}")
            else:
                print("  📂 暂无账套")
        elif choice == '3':
            print("\n  支持的会计制度:")
            for sys_info in AccountingSystemManager.get_all_systems():
                print(f"\n  [{sys_info.code}] {sys_info.name}")
                print(f"    适用: {sys_info.applicable_to}")
                print(f"    编码: {sys_info.acct_code_length}位")
        elif choice == '0':
            print("  再见！")
            break


def _cli_create_book(db_manager):
    """命令行新建账套"""
    from core.account_system import AccountingSystemManager

    print("\n  新建账套")
    print("─" * 30)
    name = input("  账套名称: ").strip()
    company = input("  单位名称: ").strip() or name

    print("\n  选择会计制度:")
    systems = AccountingSystemManager.get_all_systems()
    for i, s in enumerate(systems, 1):
        print(f"  {i}. {s.name}")

    try:
        idx = int(input("  请选择 [1-{}]: ".format(len(systems))).strip()) - 1
        if 0 <= idx < len(systems):
            system = systems[idx]
            book_id = db_manager.create_account_book(
                book_name=name,
                accounting_system=system.code,
                company_name=company
            )
            print(f"\n  ✅ 账套创建成功！编号: {book_id}")
            print(f"     会计制度: {system.name}")
            print(f"     科目编码: {system.acct_code_length}位")
            print(f"     科目级次: {'-'.join(str(l) for l in system.acct_levels)}")
        else:
            print("  ❌ 选择无效")
    except (ValueError, IndexError):
        print("  ❌ 输入无效")


def cli_mode(args):
    """命令行模式处理"""
    if '--backup' in args:
        from utils.backup import BackupManager
        bm = BackupManager(
            os.path.join(os.path.dirname(__file__), 'data', 'user_data'))
        path = bm.create_full_backup()
        print(f"备份完成: {path}")
    elif '--portable' in args:
        from portable.build_portable import build_portable
        build_portable()
    elif '--help' in args or '-h' in args:
        print("用法: python main.py [选项]")
        print("  无参数   启动GUI界面")
        print("  --backup  备份所有账套")
        print("  --portable 构建U盘便携版")
        print("  --help    显示此帮助")


if __name__ == '__main__':
    main()