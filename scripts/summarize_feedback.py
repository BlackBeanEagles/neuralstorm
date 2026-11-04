"""Print descriptive counts for anonymous BinWise feedback."""

from __future__ import annotations

import argparse
import sqlite3
from contextlib import closing
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--db", type=Path, default=ROOT / "data" / "feedback.sqlite3"
    )
    args = parser.parse_args()
    if not args.db.exists():
        print("No feedback database yet.")
        return
    with closing(sqlite3.connect(args.db)) as connection:
        rows = connection.execute(
            """SELECT location_id, channel, rating, COUNT(*)
               FROM feedback GROUP BY location_id, channel, rating
               ORDER BY location_id, channel, rating"""
        ).fetchall()
        corrections = connection.execute(
            """SELECT shown_material, corrected_material, COUNT(*)
               FROM feedback WHERE rating = 'wrong_material'
               GROUP BY shown_material, corrected_material
               ORDER BY COUNT(*) DESC"""
        ).fetchall()
    print("Self-reported feedback counts (not verified ground truth)")
    for location, channel, rating, count in rows:
        print(f"{location:16} {channel:6} {rating:15} {count}")
    print("Material corrections")
    for shown, corrected, count in corrections:
        print(f"{shown} -> {corrected}: {count}")


if __name__ == "__main__":
    main()
