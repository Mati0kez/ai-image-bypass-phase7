"""Pytest 配置：添加 src 到 Python 路径。"""

import sys
from pathlib import Path

# 将 src 目录加入 sys.path，使 transform_core 可被导入
src_path = Path(__file__).parent.parent.parent / "src"
sys.path.insert(0, str(src_path))
