"""bypass-ai-detector CLI 入口行为测试。"""

import subprocess
import sys
import tempfile
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).parent.parent
BYPASS_SCRIPT = ROOT / "bypass_ai_detector.py"


def _make_test_image(path: Path) -> None:
    img = Image.fromarray(np.zeros((32, 32, 3), dtype=np.uint8))
    img.save(path)


def test_main_with_flags_writes_output():
    """--input/--output 应成功写出 JPEG。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "in.jpg"
        output_path = tmp_path / "out.jpg"
        _make_test_image(input_path)

        result = subprocess.run(
            [
                sys.executable,
                str(BYPASS_SCRIPT),
                "--input",
                str(input_path),
                "--output",
                str(output_path),
                "--profile",
                "quick",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        assert output_path.exists()
        assert output_path.stat().st_size > 0


def test_main_with_positional_writes_output():
    """positional input output 仍应可用。"""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        input_path = tmp_path / "in.jpg"
        output_path = tmp_path / "out.jpg"
        _make_test_image(input_path)

        result = subprocess.run(
            [
                sys.executable,
                str(BYPASS_SCRIPT),
                str(input_path),
                str(output_path),
                "--profile",
                "quick",
            ],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            check=False,
        )

        assert result.returncode == 0, result.stderr
        assert output_path.exists()


def test_help_shows_input_output_flags():
    """--help 应显示 --input 与 --output。"""
    result = subprocess.run(
        [sys.executable, str(BYPASS_SCRIPT), "--help"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0
    assert "--input" in result.stdout
    assert "--output" in result.stdout
