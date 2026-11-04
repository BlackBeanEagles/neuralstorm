"""Image model used by both training and the web API."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
import torch
from PIL import Image, ImageOps
from torchvision.models import mobilenet_v3_small
from torchvision.models.mobilenetv3 import MobileNet_V3_Small_Weights

ROOT = Path(__file__).resolve().parents[1]
MODEL_DIR = ROOT / "models"


def make_backbone(pretrained: bool = False) -> torch.nn.Module:
    weights = MobileNet_V3_Small_Weights.DEFAULT if pretrained else None
    model = mobilenet_v3_small(weights=weights)
    model.classifier = torch.nn.Identity()
    model.eval()
    return model


def image_transform():
    return MobileNet_V3_Small_Weights.DEFAULT.transforms()


class WasteClassifier:
    def __init__(self, model_dir: Path = MODEL_DIR):
        self.model_dir = Path(model_dir)
        self.backbone = make_backbone()
        self.backbone.load_state_dict(
            torch.load(
                self.model_dir / "feature_extractor.pt",
                map_location="cpu",
                weights_only=True,
            )
        )
        self.backbone.eval()
        self.classifier = joblib.load(self.model_dir / "material_classifier.joblib")
        guard_data = joblib.load(self.model_dir / "supported_item_guard.joblib")
        self.guard = guard_data["model"]
        self.guard_threshold = float(guard_data["threshold"])
        self.transform = image_transform()
        with (self.model_dir / "metrics.json").open(encoding="utf-8") as stream:
            self.classes = json.load(stream)["classes"]
        self.threshold = float(joblib.load(self.model_dir / "threshold.joblib"))
        torch.set_num_threads(min(4, torch.get_num_threads()))

    def predict(self, image: Image.Image) -> dict:
        image = ImageOps.exif_transpose(image).convert("RGB")
        with torch.inference_mode():
            embedding = self.backbone(self.transform(image).unsqueeze(0)).numpy()
        probabilities = self.classifier.predict_proba(embedding)[0]
        supported_score = float(self.guard.predict_proba(embedding)[0, 1])
        ranked = np.argsort(probabilities)[::-1]
        top = int(ranked[0])
        second = int(ranked[1])
        confidence = float(probabilities[top])
        margin = confidence - float(probabilities[second])
        if supported_score < self.guard_threshold:
            return {
                "material": None,
                "confidence": None,
                "unsupported_item": True,
                "needs_confirmation": True,
                "alternatives": [],
            }
        return {
            "material": self.classes[top],
            "confidence": round(confidence, 4),
            "unsupported_item": False,
            "needs_confirmation": confidence < self.threshold or margin < 0.12,
            "alternatives": [
                {
                    "material": self.classes[int(i)],
                    "confidence": round(float(probabilities[i]), 4),
                }
                for i in ranked[:3]
            ],
        }
