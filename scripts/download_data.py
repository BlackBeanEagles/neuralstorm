"""Download the public TrashNet data into ./data (excluded from Git)."""

from __future__ import annotations

import argparse
import hashlib
import shutil
import urllib.request
import zipfile
from pathlib import Path

URL = "https://raw.githubusercontent.com/garythung/trashnet/master/data/dataset-resized.zip"
EXPECTED_BYTES = 42_834_870
EXPECTED_SHA256 = "0bf472790f8b20e5c950d5b5012a9d38af0d3392efd65f8ce171334fc16b07c2"
REALWASTE_URL = "https://archive.ics.uci.edu/static/public/908/realwaste.zip"
REALWASTE_BYTES = 688_545_323
REALWASTE_SHA256 = "1ede08b32358ee62065bcc1c8cb47a2ece04e8dff5b1fb53342bb8750895b2f3"
ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "data")
    parser.add_argument(
        "--realwaste",
        action="store_true",
        help="Also download the larger UCI RealWaste dataset",
    )
    args = parser.parse_args()
    output = args.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    archive = output / "dataset-resized.zip"
    if not archive.exists():
        with (
            urllib.request.urlopen(URL, timeout=180) as response,
            archive.open("wb") as destination,
        ):
            shutil.copyfileobj(response, destination)
    if archive.stat().st_size != EXPECTED_BYTES:
        raise RuntimeError("Unexpected dataset size; remove the partial ZIP and retry.")
    if sha256_file(archive) != EXPECTED_SHA256:
        raise RuntimeError("Dataset checksum does not match; remove the ZIP and retry.")
    destination = output / "dataset-resized"
    if not destination.exists():
        with zipfile.ZipFile(archive) as source:
            for item in source.infolist():
                path = (output / item.filename).resolve()
                if not path.is_relative_to(output):
                    raise RuntimeError("Unsafe path in dataset ZIP")
            source.extractall(output)
    print(destination)
    if args.realwaste:
        realwaste_archive = output / "realwaste.zip"
        if not realwaste_archive.exists():
            with (
                urllib.request.urlopen(REALWASTE_URL, timeout=900) as response,
                realwaste_archive.open("wb") as target,
            ):
                shutil.copyfileobj(response, target)
        if realwaste_archive.stat().st_size != REALWASTE_BYTES:
            raise RuntimeError(
                "Unexpected RealWaste size; remove the partial ZIP and retry."
            )
        if sha256_file(realwaste_archive) != REALWASTE_SHA256:
            raise RuntimeError(
                "RealWaste checksum does not match; remove the ZIP and retry."
            )
        print(realwaste_archive)


if __name__ == "__main__":
    main()
