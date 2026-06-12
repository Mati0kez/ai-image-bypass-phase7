"""Pytest 配置：确保 src 目录可被发现。"""

import sys
from pathlib import Path

# 将项目 src 目录加入 Python 路径
src_path = Path(__file__).parent.parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
