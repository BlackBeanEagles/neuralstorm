"""Train a small material classifier on ImageNet MobileNetV3 embeddings."""

from __future__ import annotations

import argparse
import io
import json
import random
import sys
import zipfile
from pathlib import Path

import joblib
import numpy as np
import torch
from PIL import Image
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from torch.utils.data import ConcatDataset, DataLoader, Dataset, Subset
from torchvision.datasets import ImageFolder

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from binwise.model import image_transform, make_backbone

REALWASTE_FOLDERS = {
    "Cardboard": "cardboard",
    "Glass": "glass",
    "Metal": "metal",
    "Paper": "paper",
    "Plastic": "plastic",
    "Miscellaneous Trash": "trash",
}


class RealWasteZipDataset(Dataset):
    def __init__(self, path: Path, classes: list[str]):
        self.archive = zipfile.ZipFile(path)
        self.transform = image_transform()
        self.samples = []
        for folder, material in REALWASTE_FOLDERS.items():
            prefix = f"realwaste-main/RealWaste/{folder}/"
            self.samples.extend(
                (name, classes.index(material))
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


def split_indices(labels, offset=0):
    indices = np.arange(len(labels))
    train_val, test = train_test_split(
        indices, test_size=0.15, stratify=labels, random_state=42
    )
    train, validation = train_test_split(
        train_val, test_size=0.15 / 0.85, stratify=labels[train_val], random_state=42
    )
    return train + offset, validation + offset, test + offset


def extract(backbone, dataset, indices, batch_size):
    loader = DataLoader(
        Subset(dataset, list(indices)),
        batch_size=batch_size,
        shuffle=False,
        num_workers=0,
    )
    blocks = []
    with torch.inference_mode():
        for batch_number, (images, _) in enumerate(loader, 1):
            blocks.append(backbone(images).numpy())
            if batch_number % 10 == 0:
                print(
                    f"  embedded {min(batch_number * batch_size, len(indices))}/{len(indices)} images",
                    flush=True,
                )
    return np.vstack(blocks)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=ROOT / "data" / "dataset-resized")
    parser.add_argument("--output", type=Path, default=ROOT / "models")
    parser.add_argument(
        "--realwaste-zip",
        type=Path,
        help="Optional UCI RealWaste ZIP for training across two image domains",
    )
    parser.add_argument("--batch-size", type=int, default=32)
    args = parser.parse_args()
    random.seed(42)
    np.random.seed(42)
    torch.manual_seed(42)
    torch.set_num_threads(min(4, torch.get_num_threads()))

    trashnet = ImageFolder(args.data, transform=image_transform())
    trashnet_labels = np.array([label for _, label in trashnet.samples])
    trash_train, trash_validation, trash_test = split_indices(trashnet_labels)
    datasets = [trashnet]
    labels = trashnet_labels
    real_test = np.array([], dtype=int)
    real_validation = np.array([], dtype=int)
    if args.realwaste_zip:
        realwaste = RealWasteZipDataset(args.realwaste_zip, trashnet.classes)
        real_labels = np.array([label for _, label in realwaste.samples])
        real_train, real_validation, real_test = split_indices(
            real_labels, offset=len(trashnet)
        )
        datasets.append(realwaste)
        labels = np.concatenate([trashnet_labels, real_labels])
        train = np.concatenate([trash_train, real_train])
        validation = np.concatenate([trash_validation, real_validation])
        test = np.concatenate([trash_test, real_test])
    else:
        train, validation, test = trash_train, trash_validation, trash_test
    dataset = ConcatDataset(datasets)
    print(
        f"Classes: {trashnet.classes}; train/validation/test: {len(train)}/{len(validation)}/{len(test)}",
        flush=True,
    )

    backbone = make_backbone(pretrained=True)
    backbone.eval()
    print("Extracting train embeddings", flush=True)
    x_train = extract(backbone, dataset, train, args.batch_size)
    print("Extracting validation embeddings", flush=True)
    x_validation = extract(backbone, dataset, validation, args.batch_size)
    print("Extracting test embeddings", flush=True)
    x_test = extract(backbone, dataset, test, args.batch_size)

    candidates = {
        "logistic_regression": make_pipeline(
            StandardScaler(),
            LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42),
        ),
        "rbf_svm": make_pipeline(
            StandardScaler(),
            SVC(
                C=5,
                kernel="rbf",
                gamma="scale",
                probability=True,
                class_weight="balanced",
                random_state=42,
            ),
        ),
    }
    selection_mask = (
        np.isin(validation, real_validation)
        if len(real_validation)
        else np.ones(len(validation), dtype=bool)
    )
    candidate_scores = {}
    for name, candidate in candidates.items():
        print(f"Fitting {name}", flush=True)
        candidate.fit(x_train, labels[train])
        predicted = candidate.predict_proba(x_validation[selection_mask]).argmax(axis=1)
        candidate_scores[name] = round(
            float(
                f1_score(labels[validation][selection_mask], predicted, average="macro")
            ),
            4,
        )
    selected_name = max(candidate_scores, key=candidate_scores.get)
    model = candidates[selected_name]
    print(
        f"Selected {selected_name} on validation macro F1: {candidate_scores}",
        flush=True,
    )
    validation_probs = model.predict_proba(x_validation)
    validation_predictions = validation_probs.argmax(axis=1)
    validation_correct = validation_predictions == labels[validation]
    # Select a cautious threshold from validation data. This is not a real-world calibration guarantee.
    threshold = 0.85
    threshold_subset = (
        np.isin(validation, real_validation)
        if len(real_validation)
        else np.ones(len(validation), dtype=bool)
    )
    for candidate in np.arange(0.50, 0.96, 0.025):
        accepted = (validation_probs.max(axis=1) >= candidate) & threshold_subset
        if accepted.sum() >= 30 and validation_correct[accepted].mean() >= 0.85:
            threshold = float(candidate)
            break

    test_probs = model.predict_proba(x_test)
    test_predictions = test_probs.argmax(axis=1)
    top_scores = test_probs.max(axis=1)
    margins = np.sort(test_probs, axis=1)[:, -1] - np.sort(test_probs, axis=1)[:, -2]
    accepted = (top_scores >= threshold) & (margins >= 0.12)
    metrics = {
        "dataset": "TrashNet and RealWaste six overlapping material classes"
        if args.realwaste_zip
        else "TrashNet dataset-resized, six material classes",
        "dataset_sources": ["https://github.com/garythung/trashnet"]
        + (
            ["https://archive.ics.uci.edu/dataset/908/realwaste"]
            if args.realwaste_zip
            else []
        ),
        "split_seed": 42,
        "train_images": len(train),
        "validation_images": len(validation),
        "test_images": len(test),
        "classes": trashnet.classes,
        "selected_model": selected_name,
        "candidate_validation_macro_f1": candidate_scores,
        "test_accuracy": round(
            float(accuracy_score(labels[test], test_predictions)), 4
        ),
        "test_macro_f1": round(
            float(f1_score(labels[test], test_predictions, average="macro")), 4
        ),
        "trashnet_test_accuracy": round(
            float(
                accuracy_score(labels[trash_test], test_predictions[: len(trash_test)])
            ),
            4,
        ),
        "realwaste_test_accuracy": round(
            float(
                accuracy_score(labels[real_test], test_predictions[len(trash_test) :])
            ),
            4,
        )
        if len(real_test)
        else None,
        "trashnet_test_images": len(trash_test),
        "realwaste_test_images": len(real_test),
        "confirmation_threshold": round(float(threshold), 3),
        "test_auto_decision_coverage": round(float(accepted.mean()), 4),
        "test_auto_decision_accuracy": round(
            float((test_predictions[accepted] == labels[test][accepted]).mean()), 4
        )
        if accepted.any()
        else None,
        "per_class": classification_report(
            labels[test],
            test_predictions,
            target_names=trashnet.classes,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(labels[test], test_predictions).tolist(),
        "limitations": "TrashNet is controlled and RealWaste is landfill imagery; neither is a field test at this collection point. Collect independently labelled phone photos before claiming real-site performance.",
    }
    args.output.mkdir(parents=True, exist_ok=True)
    torch.save(backbone.state_dict(), args.output / "feature_extractor.pt")
    joblib.dump(model, args.output / "material_classifier.joblib", compress=3)
    joblib.dump(threshold, args.output / "threshold.joblib")
    with (args.output / "metrics.json").open("w", encoding="utf-8") as stream:
        json.dump(metrics, stream, indent=2)
    print(
        json.dumps(
            {
                key: value
                for key, value in metrics.items()
                if key not in {"per_class", "confusion_matrix"}
            },
            indent=2,
        ),
        flush=True,
    )


if __name__ == "__main__":
    main()
