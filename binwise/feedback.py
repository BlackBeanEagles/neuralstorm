"""Minimal anonymous feedback store; no image or contact fields."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from binwise.rules import load_locations


class FeedbackIn(BaseModel):
    model_config = ConfigDict(extra="forbid")

    location_id: str = Field(max_length=64)
    shown_material: str = Field(max_length=64)
    channel: Literal["model", "manual", "text"]
    rating: Literal["correct", "wrong_material", "wrong_rule"]
    corrected_material: str | None = Field(default=None, max_length=64)


def save_feedback(data: FeedbackIn, db_path: Path) -> None:
    location = next((item for item in load_locations() if item["id"] == data.location_id), None)
    if location is None:
        raise ValueError("Unknown collection point")
    materials = set(location["materials"])
    if data.shown_material not in materials:
        raise ValueError("Unknown shown material")
    if data.rating == "wrong_material":
        if data.corrected_material not in materials | {"unsupported"}:
            raise ValueError("Choose the correct material or Something else")
        if data.corrected_material == data.shown_material:
            raise ValueError("Choose a different material")
    elif data.corrected_material is not None:
        raise ValueError("Correction is only valid for wrong-material feedback")

    db_path.parent.mkdir(parents=True, exist_ok=True)
    with closing(sqlite3.connect(db_path, timeout=5)) as connection, connection:
        connection.execute(
            """CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                location_id TEXT NOT NULL,
                shown_material TEXT NOT NULL,
                channel TEXT NOT NULL,
                rating TEXT NOT NULL,
                corrected_material TEXT
            )"""
        )
        connection.execute(
            """INSERT INTO feedback
                (location_id, shown_material, channel, rating, corrected_material)
                VALUES (?, ?, ?, ?, ?)""",
            (
                data.location_id,
                data.shown_material,
                data.channel,
                data.rating,
                data.corrected_material,
            ),
        )
