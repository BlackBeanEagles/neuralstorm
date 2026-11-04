"""Train a limited guard for material categories outside BinWise's six classes.

The negative examples are RealWaste food organics, vegetation, and textile trash.
This is not a universal unknown-object detector; see guard_metrics.json.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import zipfile
from pathlib import Path

import joblib
import numpy as np
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from torch.utils.data import ConcatDataset, Dataset
from torchvision.datasets import ImageFolder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from binwise.model import image_transform, make_backbone
from scripts.train import RealWasteZipDataset, extract, split_indices

UNSUPPORTED_FOLDERS = ("Food Organics", "Vegetation", "Textile Trash")


class UnsupportedZipDataset(Dataset):
    def __init__(self, path: Path):
        self.archive = zipfile.ZipFile(path)
        self.transform = image_transform()
        self.samples = []
        for index, folder in enumerate(UNSUPPORTED_FOLDERS):
            prefix = f"realwaste-main/RealWaste/{folder}/"
            self.samples.extend(
                (name, index)
                for name in self.archive.namelist()
                if name.startswith(prefix) and name.lower().endswith(".jpg")
            )
        self.samples.sort()

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, index):
        name, label = self.samples[index]
        with self.archive.open(name) as stream:
            image = Image.open(io.BytesIO(stream.read())).convert("RGB")
        return self.transform(image), label


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "dataset-resized")
    parser.add_argument("--realwaste-zip", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=ROOT / "models")
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    torch.manual_seed(42)
    np.random.seed(42)
    torch.set_num_threads(min(4, torch.get_num_threads()))

    trashnet = ImageFolder(args.data, transform=image_transform())
    trash_labels = np.array([label for _, label in trashnet.samples])
    trash_train, trash_validation, trash_test = split_indices(trash_labels)
    realwaste = RealWasteZipDataset(args.realwaste_zip, trashnet.classes)
    real_labels = np.array([label for _, label in realwaste.samples])
    real_train, real_validation, real_test = split_indices(
        real_labels, offset=len(trashnet)
    )
    supported = ConcatDataset([trashnet, realwaste])
    known_indices = (
        np.concatenate([trash_train, real_train]),
        np.concatenate([trash_validation, real_validation]),
        np.concatenate([trash_test, real_test]),
    )

    unsupported = UnsupportedZipDataset(args.realwaste_zip)
    unknown_labels = np.array([label for _, label in unsupported.samples])
    unknown_indices = split_indices(unknown_labels)

    backbone = make_backbone()
    backbone.load_state_dict(
        torch.load(
            args.output / "feature_extractor.pt", map_location="cpu", weights_only=True
        )
    )
    backbone.eval()
    known_embeddings = []
    unknown_embeddings = []
    for name, indices in zip(("train", "validation", "test"), known_indices):
        print(f"Embedding supported {name}: {len(indices)}", flush=True)
        known_embeddings.append(extract(backbone, supported, indices, args.batch_size))
    for name, indices in zip(("train", "validation", "test"), unknown_indices):
        print(f"Embedding unsupported {name}: {len(indices)}", flush=True)
        unknown_embeddings.append(
            extract(backbone, unsupported, indices, args.batch_size)
        )

    x_train = np.vstack([known_embeddings[0], unknown_embeddings[0]])
    y_train = np.concatenate(
        [np.ones(len(known_embeddings[0])), np.zeros(len(unknown_embeddings[0]))]
    )
    guard = make_pipeline(
        StandardScaler(),
        LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
    )
    print("Fitting supported-item guard", flush=True)
    guard.fit(x_train, y_train)

    valid_known = guard.predict_proba(known_embeddings[1])[:, 1]
    valid_unknown = guard.predict_proba(unknown_embeddings[1])[:, 1]
    # Choose on validation only: reject at least 90% of the three known
    # unsupported categories while retaining as many supported items as possible.
    thresholds = np.unique(np.r_[0.0, valid_known, valid_unknown, 1.0])
    eligible = [t for t in thresholds if np.mean(valid_unknown < t) >= 0.90]
    threshold = float(min(eligible)) if eligible else 1.0

    test_known = guard.predict_proba(known_embeddings[2])[:, 1]
    test_unknown = guard.predict_proba(unknown_embeddings[2])[:, 1]
    known_accepted = test_known >= threshold
    unknown_rejected = test_unknown < threshold
    material_model = joblib.load(args.output / "material_classifier.joblib")
    material_threshold = float(joblib.load(args.output / "threshold.joblib"))
    known_material_probs = material_model.predict_proba(known_embeddings[2])
    unknown_material_probs = material_model.predict_proba(unknown_embeddings[2])

    def automatic(probs):
        ranked = np.sort(probs, axis=1)
        return (ranked[:, -1] >= material_threshold) & (
            ranked[:, -1] - ranked[:, -2] >= 0.12
        )

    known_auto_before = automatic(known_material_probs)
    unknown_auto_before = automatic(unknown_material_probs)
    metrics = {
        "guard_scope": "RealWaste Food Organics, Vegetation, Textile Trash versus BinWise's six supported materials",
        "unsupported_categories": list(UNSUPPORTED_FOLDERS),
        "split_seed": 42,
        "supported_test_images": len(test_known),
        "unsupported_test_images": len(test_unknown),
        "validation_target_unknown_rejection": 0.90,
        "guard_threshold": round(threshold, 6),
        "supported_test_acceptance": round(float(known_accepted.mean()), 4),
        "unsupported_test_rejection": round(float(unknown_rejected.mean()), 4),
        "supported_auto_guidance_before_guard": round(
            float(known_auto_before.mean()), 4
        ),
        "supported_auto_guidance_after_guard": round(
            float((known_auto_before & known_accepted).mean()), 4
        ),
        "unsupported_auto_guidance_before_guard": round(
            float(unknown_auto_before.mean()), 4
        ),
        "unsupported_auto_guidance_after_guard": round(
            float((unknown_auto_before & ~unknown_rejected).mean()), 4
        ),
        "unsupported_rejection_by_category": {
            folder: round(
                float(
                    unknown_rejected[
                        unknown_labels[unknown_indices[2]] == category
                    ].mean()
                ),
                4,
            )
            for category, folder in enumerate(UNSUPPORTED_FOLDERS)
        },
        "limitations": "This guard has only been tested on three RealWaste unsupported categories. It cannot certify that batteries, electronics, mixed packaging, or every novel item will be rejected. Use the manual 'Something else' path for those items.",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {"model": guard, "threshold": threshold},
        args.output / "supported_item_guard.joblib",
        compress=3,
    )
    with (args.output / "guard_metrics.json").open("w", encoding="utf-8") as stream:
        json.dump(metrics, stream, indent=2)
    print(json.dumps(metrics, indent=2), flush=True)


if __name__ == "__main__":
    main()
