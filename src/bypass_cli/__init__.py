"""bypass-ai-detector 控制台入口（可安装包内）。"""

from __future__ import annotations

import argparse

from transform_core.config import TransformConfig
from transform_core.pipeline import post_process_image as run_pipeline

METHOD_FAMILIES = (
    "metadata",
    "encoding",
    "noise",
    "frequency",
    "texture",
    "camera",
    "regeneration_surrogate",
)

PROFILE_METHODS = {
    "quick": ("metadata", "encoding", "noise", "frequency"),
    "full": METHOD_FAMILIES,
    "texture": ("texture",),
    "camera": ("camera",),
    "metadata": ("metadata",),
}


def _build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="AI image detector robustness transform suite")
    parser.add_argument("--input", dest="input_path", help="Input image path (preferred)")
    parser.add_argument("--output", dest="output_path", help="Output image path (preferred)")
    parser.add_argument("input", nargs="?", help="Input image (positional, deprecated; use --input)")
    parser.add_argument("output", nargs="?", help="Output image (positional, deprecated; use --output)")
    parser.add_argument("--real", default=None, help="Reference JPEG for EXIF copy mode")
    parser.add_argument("--noise", type=float, default=0.8)
    parser.add_argument("--skin", type=float, default=0.75)
    parser.add_argument("--fft", type=float, default=0.48)
    parser.add_argument("--pixel", type=float, default=0.028)
    parser.add_argument("--glcm", type=float, default=0.6)
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--profile", choices=sorted(PROFILE_METHODS), default="full")
    parser.add_argument(
        "--methods",
        default=None,
        help=f"Comma-separated method families: {', '.join(METHOD_FAMILIES)}",
    )
    parser.add_argument(
        "--metadata-mode",
        choices=("copy", "strip", "synthetic"),
        default="copy",
    )
    parser.add_argument("--manifest", default=None)
    parser.add_argument("--seed", type=int, default=None)
    return parser


def _resolve_io_paths(args: argparse.Namespace) -> tuple[str, str]:
    input_path = args.input_path or args.input
    output_path = args.output_path or args.output
    if not input_path or not output_path:
        raise SystemExit("Error: provide --input/--output or positional input output paths.")
    if args.input_path is None and args.input is not None:
        print("Warning: positional input/output is deprecated; use --input and --output.")
    return input_path, output_path


def main(argv: list[str] | None = None) -> None:
    """CLI 入口。"""
    parser = _build_arg_parser()
    args = parser.parse_args(argv)
    input_path, output_path = _resolve_io_paths(args)

    config = TransformConfig(
        input_path=input_path,
        output_path=output_path,
        manifest_path=args.manifest,
        profile=args.profile,
        seed=args.seed,
        quality=args.quality,
        noise_strength=args.noise,
        fft_strength=args.fft,
        pixel_strength=args.pixel,
        glcm_strength=args.glcm,
        skin_strength=args.skin,
        metadata_mode=args.metadata_mode,
        real_photo_path=args.real,
    )
    run_pipeline(config)


if __name__ == "__main__":
    main()
