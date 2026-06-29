"""CLI tool to measure bypass rate using HF Inference API or local model."""

import argparse
from pathlib import Path
from PIL import Image

from attack.verification import hf_api_verifier, compute_bypass_rate


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True, help="HF repo id")
    parser.add_argument("--images", required=True, help="folder with images")
    parser.add_argument("--token", default=None)
    args = parser.parse_args()

    verifier = hf_api_verifier(args.model, args.token)
    images = [Image.open(p).convert("RGB") for p in Path(args.images).glob("*") if p.suffix.lower() in {".jpg", ".png"}]
    stats = compute_bypass_rate(verifier, images)
    print(stats)


if __name__ == "__main__":
    main()