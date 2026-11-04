"""Create a counterbalanced, anonymous BinWise pilot schedule.

Usage: python scripts/prepare_pilot.py --participants 6
"""

from __future__ import annotations

import argparse
import csv
import random
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, default=ROOT / "pilot" / "items.csv")
    parser.add_argument("--participants", type=int, default=6)
    parser.add_argument("--output", type=Path, default=ROOT / "pilot" / "sessions.csv")
    args = parser.parse_args()
    if args.participants < 2 or args.participants % 2:
        parser.error("Use an even number of participants, at least 2.")
    with args.items.open(newline="", encoding="utf-8") as stream:
        items = list(csv.DictReader(stream))
    if len(items) < 4 or len(items) % 2:
        parser.error("Provide an even number of items, at least 4.")
    if any(not item["expected_action"].strip() for item in items):
        parser.error(
            "Fill every expected_action in items.csv from the site's rules first."
        )
    if len({item["item_id"] for item in items}) != len(items):
        parser.error("Item IDs must be unique.")
    if args.output.exists():
        with args.output.open(newline="", encoding="utf-8") as stream:
            existing = list(csv.DictReader(stream))
        if any(row.get("response_action") or row.get("seconds") for row in existing):
            parser.error(
                "The output already contains responses. Choose another --output path so pilot data is not overwritten."
            )

    fieldnames = [
        "participant_id",
        "order",
        "item_id",
        "condition",
        "response_action",
        "seconds",
        "app_declined",
        "note",
    ]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fieldnames)
        writer.writeheader()
        for person_index in range(args.participants):
            assignments = [
                {
                    "participant_id": f"P{person_index + 1:02d}",
                    "item_id": item["item_id"],
                    "condition": (
                        "app" if (item_index + person_index) % 2 == 0 else "no_app"
                    ),
                    "response_action": "",
                    "seconds": "",
                    "app_declined": "",
                    "note": "",
                }
                for item_index, item in enumerate(items)
            ]
            random.Random(42 + person_index).shuffle(assignments)
            for order, assignment in enumerate(assignments, 1):
                writer.writerow({**assignment, "order": order})
    print(
        f"Created {args.output} for {args.participants} participants and {len(items)} items"
    )


if __name__ == "__main__":
    main()
