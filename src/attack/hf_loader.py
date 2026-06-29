"""HF model loader for image classification detectors.

Loads any Hugging Face image-classification model (Swin, ViT, ResNet, etc.)
and provides unified forward / preprocessing utilities.
"""

from __future__ import annotations

from typing import Any, Tuple

import torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForImageClassification


class HFDetector:
    """Wrapper around a Hugging Face image classification model."""

    def __init__(self, repo_id: str, device: str | None = None):
        self.repo_id = repo_id
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.processor = AutoImageProcessor.from_pretrained(repo_id)
        self.model = AutoModelForImageClassification.from_pretrained(repo_id).to(self.device).eval()

    def forward_logits(self, img_tensor: torch.Tensor) -> torch.Tensor:
        """Run the model and return raw logits (with grad enabled for attack)."""
        outputs = self.model(img_tensor)
        # Handle both plain tensor and HF output objects
        if hasattr(outputs, "logits"):
            return outputs.logits
        return outputs

    def preprocess(self, img: Image.Image) -> torch.Tensor:
        """Convert PIL image to model input tensor (normalized)."""
        inputs = self.processor(images=img, return_tensors="pt")
        return inputs.pixel_values.to(self.device)

    def get_target_class(self, img: Image.Image) -> int:
        """Return the predicted class id for the given image."""
        tensor = self.preprocess(img)
        logits = self.forward_logits(tensor)
        return int(logits.argmax(dim=-1).item())

    def __call__(self, img: Image.Image) -> Tuple[str, float]:
        """Return (label, score) for convenience."""
        tensor = self.preprocess(img)
        logits = self.forward_logits(tensor)
        probs = torch.softmax(logits, dim=-1)
        score, idx = probs.max(dim=-1)
        label = self.model.config.id2label[int(idx)]
        return label, float(score)