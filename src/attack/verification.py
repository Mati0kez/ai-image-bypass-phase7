"""Cloud verification helpers for bypass rate measurement."""

from __future__ import annotations

from typing import Callable, Dict, List

from PIL import Image
from huggingface_hub import InferenceClient


def hf_api_verifier(repo_id: str, token: str | None = None) -> Callable[[Image.Image], Dict]:
    """Return a verifier that calls HF Inference API and returns label + score."""
    client = InferenceClient(model=repo_id, token=token)

    def _verify(img: Image.Image) -> Dict:
        import tempfile, os
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            img.save(tmp.name, format='JPEG')
            result = client.image_classification(tmp.name)
            os.unlink(tmp.name)
        best = max(result, key=lambda x: x["score"])
        return {"label": best["label"], "score": float(best["score"])}

    return _verify


def compute_bypass_rate(
    verifier: Callable[[Image.Image], Dict],
    images: List[Image.Image],
    threshold: float = 0.5,
) -> Dict:
    """Compute bypass rate (score < threshold) for a list of images."""
    total = len(images)
    bypassed = 0
    for img in images:
        res = verifier(img)
        if res["score"] < threshold:
            bypassed += 1
    return {
        "total": total,
        "bypassed": bypassed,
        "bypass_rate": bypassed / total if total else 0.0,
    }