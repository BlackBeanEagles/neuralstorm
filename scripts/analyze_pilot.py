"""Summarize completed pilot responses without inventing missing observations.

Usage: python scripts/analyze_pilot.py
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def rows(path: Path) -> list[dict]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


def summarize(observations: list[dict]) -> dict:
    if not observations:
        return {"n": 0, "accuracy": None, "mean_seconds": None}
    return {
        "n": len(observations),
        "accuracy": round(statistics.mean(x["correct"] for x in observations), 4),
        "mean_seconds": round(statistics.mean(x["seconds"] for x in observations), 2),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", type=Path, default=ROOT / "pilot" / "items.csv")
    parser.add_argument(
        "--sessions", type=Path, default=ROOT / "pilot" / "sessions.csv"
    )
    parser.add_argument("--output", type=Path, default=ROOT / "pilot" / "results.json")
    args = parser.parse_args()
    items = {item["item_id"]: item for item in rows(args.items)}
    if any(not item["expected_action"].strip() for item in items.values()):
        parser.error("Set the ground-truth expected_action for every pilot item first.")
    observations = []
    scheduled = rows(args.sessions)
    for row in scheduled:
        if not row["response_action"].strip() and not row["seconds"].strip():
            continue
        if row["item_id"] not in items:
            parser.error(f"Unknown item_id: {row['item_id']}")
        if row["condition"] not in {"app", "no_app"}:
            parser.error(f"Invalid condition for {row['item_id']}")
        if not row["response_action"].strip() or not row["seconds"].strip():
            parser.error(
                f"Incomplete response for {row['participant_id']} / {row['item_id']}"
            )
        try:
            seconds = float(row["seconds"])
        except ValueError:
            parser.error(
                f"Invalid seconds for {row['participant_id']} / {row['item_id']}"
            )
        if seconds <= 0:
            parser.error("Every recorded time must be positive.")
        observations.append(
            {
                **row,
                "seconds": seconds,
                "correct": row["response_action"].strip().lower()
                == items[row["item_id"]]["expected_action"].strip().lower(),
            }
        )
    if not observations:
        parser.error("No completed pilot responses yet. Do not report pilot results.")
    by_condition = {
        name: summarize([x for x in observations if x["condition"] == name])
        for name in ("no_app", "app")
    }
    by_person = defaultdict(list)
    for observation in observations:
        by_person[observation["participant_id"]].append(observation)
    paired = []
    for person, person_rows in by_person.items():
        baseline = summarize([x for x in person_rows if x["condition"] == "no_app"])
        assisted = summarize([x for x in person_rows if x["condition"] == "app"])
        if baseline["n"] and assisted["n"]:
            paired.append(
                {
                    "participant_id": person,
                    "accuracy_change": round(
                        assisted["accuracy"] - baseline["accuracy"], 4
                    ),
                    "mean_seconds_change": round(
                        assisted["mean_seconds"] - baseline["mean_seconds"], 2
                    ),
                }
            )
    result = {
        "study_type": "small counterbalanced convenience pilot, descriptive only",
        "completed_observations": len(observations),
        "scheduled_observations": len(scheduled),
        "participants_with_both_conditions": len(paired),
        "conditions": by_condition,
        "paired_mean_accuracy_change": round(
            statistics.mean(x["accuracy_change"] for x in paired), 4
        )
        if paired
        else None,
        "paired_mean_seconds_change": round(
            statistics.mean(x["mean_seconds_change"] for x in paired), 2
        )
        if paired
        else None,
        "app_declines_observed": sum(
            x["app_declined"].strip().lower() in {"yes", "true", "1"}
            for x in observations
            if x["condition"] == "app"
        ),
        "limitations": "Convenience sample and few physical items; do not generalize this result to all people, items, sites, or cities.",
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
