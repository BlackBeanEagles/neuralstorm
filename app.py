"""BinWise API and static site."""

from __future__ import annotations

import io
import os
from functools import lru_cache
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image, UnidentifiedImageError

from binwise.feedback import FeedbackIn, save_feedback
from binwise.model import WasteClassifier
from binwise.quality import assess_photo
from binwise.rules import guidance, load_locations
from binwise.sharing import qr_payload

ROOT = Path(__file__).resolve().parent
MAX_UPLOAD_BYTES = 10 * 1024 * 1024
app = FastAPI(title="BinWise", version="0.1.0")
app.mount("/static", StaticFiles(directory=ROOT / "static"), name="static")


@lru_cache(maxsize=1)
def classifier() -> WasteClassifier:
    return WasteClassifier()


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/api/health")
def health():
    model_files = [
        ROOT / "models" / x
        for x in (
            "feature_extractor.pt",
            "material_classifier.joblib",
            "threshold.joblib",
            "supported_item_guard.joblib",
            "metrics.json",
        )
    ]
    return {"ok": True, "model_ready": all(x.exists() for x in model_files)}


@app.get("/api/locations")
def locations():
    return [
        {
            "id": x["id"],
            "sample": x.get("sample", False),
            "name": x["name"],
            "name_hi": x.get("name_hi"),
            "description": x["description"],
            "description_hi": x.get("description_hi"),
            "scope": x.get("scope"),
            "source": x.get("source"),
            "qr_shareable": x.get("qr_shareable", False),
            "manual_materials": x.get("manual_materials", []),
            "bins": x["bins"],
        }
        for x in load_locations()
    ]


@app.get("/api/qr/{location_id}")
def share_qr(location_id: str, request: Request):
    public_base = os.environ.get("BINWISE_PUBLIC_URL") or str(request.base_url)
    try:
        return qr_payload(location_id, public_base)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None


@app.post("/api/feedback", status_code=201)
def feedback(data: FeedbackIn):
    path = Path(os.environ.get("BINWISE_FEEDBACK_DB", ROOT / "data" / "feedback.sqlite3"))
    try:
        save_feedback(data, path)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
    return {"saved": True}


@app.post("/api/predict")
async def predict(
    file: Annotated[UploadFile, File()],
    location_id: Annotated[str, Form()] = "campus-demo",
):
    if file.content_type not in {"image/jpeg", "image/png", "image/webp"}:
        raise HTTPException(400, "Upload a JPEG, PNG, or WebP image.")
    raw = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(raw) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "Image exceeds the 10 MB limit.")
    try:
        image = Image.open(io.BytesIO(raw))
        image.verify()
        image = Image.open(io.BytesIO(raw))
        if image.width * image.height > 20_000_000:
            raise HTTPException(413, "Image dimensions are too large.")
        issue = assess_photo(image)
        if issue:
            raise HTTPException(422, issue)
        result = classifier().predict(image)
        # Validate the collection point even when we withhold uncertain guidance.
        if location_id not in {site["id"] for site in load_locations()}:
            raise ValueError("Unknown collection point")
        if not result["unsupported_item"]:
            local_guidance = guidance(location_id, result["material"])
            if not result["needs_confirmation"]:
                result["guidance"] = local_guidance
        return result
    except UnidentifiedImageError:
        raise HTTPException(400, "The uploaded file is not a readable image.") from None
    except OSError:
        raise HTTPException(400, "The uploaded file is not a readable image.") from None
    except FileNotFoundError:
        raise HTTPException(
            503, "Model files are missing. Run the training script first."
        ) from None
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None


@app.get("/api/guidance/{location_id}/{material}")
def manual_guidance(location_id: str, material: str):
    try:
        return guidance(location_id, material, confirmed=True)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from None
