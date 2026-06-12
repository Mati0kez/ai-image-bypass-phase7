"""Pytest 根配置：确保 src 与项目根目录在 import 路径中。"""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

for path in (str(SRC), str(ROOT)):
    if path not in sys.path:
        sys.path.insert(0, path)
