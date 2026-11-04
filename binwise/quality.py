"""Conservative, fast quality checks before image inference."""

from __future__ import annotations

import numpy as np
from PIL import Image, ImageOps


def assess_photo(image: Image.Image) -> dict[str, str] | None:
    """Return a retake reason for clearly unusable photos, else None.

    Thresholds are deliberately low. They were checked against TrashNet images,
    not calibrated for all phones or lighting conditions.
    """
    if min(image.size) < 160:
        return {
            "code": "too_small",
            "message": "The photo is too small. Move closer and take a new photo.",
        }
    sample = ImageOps.exif_transpose(image).convert("L").resize((256, 256))
    pixels = np.asarray(sample, dtype=np.float32)
    if float(pixels.mean()) < 35:
        return {
            "code": "too_dark",
            "message": "This photo is too dark. Add light and take it again.",
        }
    laplacian = (
        4 * pixels[1:-1, 1:-1]
        - pixels[:-2, 1:-1]
        - pixels[2:, 1:-1]
        - pixels[1:-1, :-2]
        - pixels[1:-1, 2:]
    )
    if float(laplacian.var()) < 5:
        return {
            "code": "too_blurry",
            "message": "This photo looks too blurry or plain. Hold steady and show one item clearly.",
        }
    return None
