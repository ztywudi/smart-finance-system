"""
==========================================
 portable/build_portable.py - U盘便携版构建
==========================================
功能：
  - 将财务软件打包为U盘便携版
  - 打包成单个可执行文件 + 便携数据库
  - 无需安装，双击即用

构建命令：
  python build_portable.py
"""

import os
import sys
import shutil
import subprocess
from datetime import datetime


def build_portable():
    """构建U盘便携版"""
    # 项目根目录
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    build_dir = os.path.join(project_root, 'portable', 'dist')

    print("=" * 50)
    print("正在构建财务软件便携版...")
    print("=" * 50)

    # 1. 使用 PyInstaller 打包为单个exe
    print("\n[1/3] 打包主程序...")
    subprocess.run([
        'pyinstaller',
        '--onefile',           # 单文件
        '--windowed',          # 无控制台窗口
        '--name', '财务软件',
        '--icon', os.path.join(project_root, 'resources', 'icons', 'app.ico'),
        '--distpath', build_dir,
        '--add-data', f'{project_root}/resources{os.pathsep}resources',
        '--add-data', f'{project_root}/data/default{os.pathsep}data/default',
        os.path.join(project_root, 'main.py')
    ], cwd=project_root)

    # 2. 创建便携版目录结构
    print("\n[2/3] 构建便携版目录结构...")
    portable_dir = os.path.join(build_dir, '财务软件_便携版')
    data_dir = os.path.join(portable_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # 复制主程序
    shutil.copy2(
        os.path.join(build_dir, '财务软件.exe'),
        os.path.join(portable_dir, '财务软件.exe')
    )

    # 3. 创建使用说明
    print("\n[3/3] 创建使用说明...")
    readme = """财务软件 - U盘便携版
===================================

使用说明：
1. 将整个"财务软件_便携版"文件夹复制到U盘
2. 在任意电脑上双击"财务软件.exe"运行
3. 首次使用请先"新建账套"并选择会计制度
4. 数据默认保存在 data/ 目录下

同步说明：
- 出差在外：在U盘上直接录入凭证
- 回办公室：插上U盘，在主电脑上打开软件
  → 软件自动检测U盘数据 → 确认同步 → 合并完成

系统要求：
- Windows 7/10/11
- 无需安装Python或任何依赖
- 不会在电脑上留下任何痕迹

版本：1.0.0
构建时间：{build_time}
"""

    with open(os.path.join(portable_dir, '使用说明.txt'), 'w', encoding='utf-8') as f:
        f.write(readme.format(build_time=datetime.now().strftime('%Y-%m-%d %H:%M')))

    print("\n✅ 便携版构建完成！")
    print(f"   输出目录: {portable_dir}")
    print(f"   直接复制整个文件夹到U盘即可使用！")

    return portable_dir


if __name__ == '__main__':
    build_portable()
