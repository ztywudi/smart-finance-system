#!/usr/bin/env python3
"""
智能财务系统 - 自动打包脚本
支持Windows、Mac、Linux打包
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

class Colors:
    """终端颜色"""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    END = '\033[0m'

def print_step(msg):
    """打印步骤信息"""
    print(f"{Colors.BLUE}[步骤]{Colors.END} {msg}")

def print_success(msg):
    """打印成功信息"""
    print(f"{Colors.GREEN}[成功]{Colors.END} {msg}")

def print_warning(msg):
    """打印警告信息"""
    print(f"{Colors.YELLOW}[警告]{Colors.END} {msg}")

def print_error(msg):
    """打印错误信息"""
    print(f"{Colors.RED}[错误]{Colors.END} {msg}")

def check_dependencies():
    """检查依赖"""
    print_step("检查依赖...")
    
    required = ['PyQt6', 'openpyxl', 'pyinstaller']
    missing = []
    
    for pkg in required:
        try:
            __import__(pkg.lower().replace('-', '_'))
            print(f"  ✅ {pkg}")
        except ImportError:
            print(f"  ❌ {pkg} (缺失)")
            missing.append(pkg)
    
    if missing:
        print_error(f"缺少依赖: {', '.join(missing)}")
        print_warning("请运行: pip install " + " ".join(missing))
        return False
    
    print_success("所有依赖已安装")
    return True

def clean_build():
    """清理之前的打包文件"""
    print_step("清理之前的打包文件...")
    
    dirs_to_clean = ['build', 'dist', '__pycache__']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"  已删除: {dir_name}/")
    
    # 删除.spec文件
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"  已删除: {spec_file.name}")
    
    print_success("清理完成")

def build_windows():
    """打包Windows版本"""
    print_step("开始打包Windows版本...")
    
    cmd = [
        'pyinstaller',
        '--onefile',           # 单个exe文件
        '--windowed',          # 不显示命令行窗口
        '--name', '智能财务系统',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'sqlite3',
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtGui',
        '--hidden-import', 'PyQt6.QtWidgets',
        'main.py'
    ]
    
    # 如果有图标，添加图标参数
    if os.path.exists('resources/icons/app.ico'):
        cmd.extend(['--icon', 'resources/icons/app.ico'])
    
    # 如果有资源文件夹，添加
    if os.path.exists('resources'):
        cmd.extend(['--add-data', 'resources;resources'])
    
    try:
        subprocess.run(cmd, check=True)
        print_success("Windows版本打包完成！")
        print(f"{Colors.GREEN}EXE文件位置: {os.path.abspath('dist/智能财务系统.exe')}{Colors.END}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        return False

def build_mac():
    """打包Mac版本"""
    print_step("开始打包Mac版本...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--windowed',
        '--name', '智能财务系统',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print_success("Mac版本打包完成！")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        return False

def build_linux():
    """打包Linux版本"""
    print_step("开始打包Linux版本...")
    
    cmd = [
        'pyinstaller',
        '--onefile',
        '--name', '智能财务系统',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print_success("Linux版本打包完成！")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"打包失败: {e}")
        return False

def create_portable_version():
    """创建便携版（打包成文件夹）"""
    print_step("创建便携版（文件夹模式）...")
    
    cmd = [
        'pyinstaller',
        '--windowed',
        '--name', '智能财务系统',
        '--hidden-import', 'openpyxl',
        '--hidden-import', 'sqlite3',
        'main.py'
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print_success("便携版创建完成！")
        print(f"文件夹位置: {os.path.abspath('dist/智能财务系统/')}")
        return True
    except subprocess.CalledProcessError as e:
        print_error(f"创建失败: {e}")
        return False

def main():
    """主函数"""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BLUE}  智能财务系统 - 自动打包工具{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    # 检查是否在正确目录
    if not os.path.exists('main.py'):
        print_error("未在项目根目录！请在finance目录下运行此脚本。")
        sys.exit(1)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 清理
    clean_build()
    
    # 根据系统打包
    success = False
    if sys.platform == 'win32':
        success = build_windows()
    elif sys.platform == 'darwin':
        success = build_mac()
    else:
        print_warning("当前系统为Linux，打包的exe无法在Windows上运行。")
        print_warning("建议在Windows系统上运行此脚本。")
        success = build_linux()
    
    if success:
        print(f"\n{Colors.GREEN}{'='*60}{Colors.END}")
        print(f"{Colors.GREEN}  ✅ 打包成功！{Colors.END}")
        print(f"{Colors.GREEN}{'='*60}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}📝 下一步：{Colors.END}")
        print("  1. 测试exe文件是否能正常运行")
        print("  2. 测试所有功能（记账、报表、导出等）")
        print("  3. 在其他电脑上测试")
        print("  4. 如果一切正常，可以分发给用户\n")
    else:
        print(f"\n{Colors.RED}{'='*60}{Colors.END}")
        print(f"{Colors.RED}  ❌ 打包失败！{Colors.END}")
        print(f"{Colors.RED}{'='*60}{Colors.END}\n")
        sys.exit(1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print_warning("\n用户取消操作")
        sys.exit(0)
    except Exception as e:
        print_error(f"发生错误: {e}")
        sys.exit(1)
