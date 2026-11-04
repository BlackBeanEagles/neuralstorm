"""Create the calm neural narration for the BinWise feature tour.

Optional video-authoring dependencies: edge-tts and imageio-ffmpeg.
This script needs an internet connection. The matching PowerShell script creates
an offline Windows voice fallback from the same narration text.
"""

from __future__ import annotations

import argparse
import asyncio
import subprocess
from pathlib import Path

import edge_tts
import imageio_ffmpeg

SCRIPT = Path(__file__).resolve()
LINES = SCRIPT.with_name("comic_tour_100_narration.txt")


async def create_mp3(index: int, line: str, output: Path,
                     semaphore: asyncio.Semaphore, voice: str, rate: str) -> None:
    target = output / f"voice-{index:02d}.mp3"
    async with semaphore:
        for attempt in range(3):
            try:
                await edge_tts.Communicate(line, voice, rate=rate).save(str(target))
                print(f"Narrated scene {index+1}/16", flush=True)
                return
            except Exception:
                if attempt == 2:
                    raise
                await asyncio.sleep(1.5 * (attempt + 1))


async def synthesize(lines: list[str], output: Path, voice: str, rate: str) -> None:
    semaphore = asyncio.Semaphore(3)
    await asyncio.gather(*(
        create_mp3(index, line, output, semaphore, voice, rate)
        for index, line in enumerate(lines)
    ))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-directory", type=Path, required=True)
    parser.add_argument("--voice", default="en-IN-NeerjaNeural")
    parser.add_argument("--rate", default="+10%")
    args = parser.parse_args()
    lines = [line.strip() for line in LINES.read_text(encoding="utf-8").splitlines()
             if line.strip()]
    if len(lines) != 16:
        raise ValueError("Expected exactly 16 narration lines")
    args.output_directory.mkdir(parents=True, exist_ok=True)
    asyncio.run(synthesize(lines, args.output_directory, args.voice, args.rate))
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    for index in range(len(lines)):
        source = args.output_directory / f"voice-{index:02d}.mp3"
        target = args.output_directory / f"voice-{index:02d}.wav"
        subprocess.run(
            [ffmpeg, "-y", "-loglevel", "error", "-i", str(source),
             "-ac", "1", "-ar", "16000", "-c:a", "pcm_s16le", str(target)],
            check=True,
        )
    print(f"Saved 16 narration WAV files in {args.output_directory}")


if __name__ == "__main__":
    main()
