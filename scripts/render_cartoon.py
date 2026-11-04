"""Render the BinWise concept animation from the included scene illustrations.

Run with: python scripts/render_cartoon.py
Requires Pillow, numpy, and imageio-ffmpeg (video authoring only).
"""

from __future__ import annotations

import math
import subprocess
import wave
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
OUT = MEDIA / "binwise-concept.mp4"
FPS = 24
W, H = 1280, 720
DURATION = 23


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "arialbd.ttf" if bold else "arial.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def ease(x: float) -> float:
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)


def alpha(t: float, start: float, end: float) -> float:
    return ease((t - start) / 0.55) * (1 - ease((t - (end - 0.55)) / 0.55))


def draw_text(
    layer: Image.Image,
    xy: tuple[int, int],
    value: str,
    size: int,
    color: str,
    *,
    bold: bool = False,
    opacity: int = 255,
) -> None:
    ink = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    d = ImageDraw.Draw(ink)
    d.text(xy, value, font=font(size, bold), fill=color)
    if opacity < 255:
        ink.putalpha(ink.getchannel("A").point(lambda p: p * opacity // 255))
    layer.alpha_composite(ink)


def panel(frame: Image.Image, opacity: int) -> Image.Image:
    lay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(lay)
    d.rounded_rectangle((782, 98, 1235, 620), radius=34, fill=(255, 255, 255, 238))
    d.rounded_rectangle((805, 122, 1017, 158), radius=18, fill=(20, 91, 75, 255))
    draw_text(lay, (826, 131), "BINWISE  /  GP-05", 18, "#FFFFFF", bold=True)
    if opacity < 255:
        lay.putalpha(lay.getchannel("A").point(lambda p: p * opacity // 255))
    frame.alpha_composite(lay)
    return frame


def compose_scene(image: Image.Image, t: float, scene_start: float) -> Image.Image:
    # Very gentle camera move gives the illustrations motion without hiding the bin choice.
    phase = (t - scene_start) / 6
    zoom = 1.015 + 0.018 * max(0, min(1, phase))
    rw, rh = round(W * zoom), round(H * zoom)
    bg = image.resize((rw, rh), Image.Resampling.LANCZOS)
    x = round((rw - W) * max(0, min(1, phase)))
    y = round((rh - H) / 2)
    return bg.crop((x, y, x + W, y + H)).convert("RGBA")


def scene_frame(t: float, images: list[Image.Image]) -> Image.Image:
    if t >= 19:
        frame = Image.new("RGBA", (W, H), "#0B4E46")
        d = ImageDraw.Draw(frame)
        d.ellipse((-85, 390, 480, 940), fill="#116457")
        d.ellipse((920, -220, 1440, 300), fill="#1D7564")
        d.rounded_rectangle((100, 120, 1180, 595), radius=42, fill="#FFFFFF")
        d.rounded_rectangle((150, 165, 330, 209), radius=22, fill="#DBEFE3")
        draw_text(frame, (175, 176), "GREEN PLANET", 18, "#0B6352", bold=True)
        draw_text(frame, (150, 255), "BinWise", 90, "#103F37", bold=True)
        draw_text(frame, (153, 370), "Know where it goes.", 43, "#24675A", bold=True)
        draw_text(frame, (153, 440), "Photo  •  Material  •  Local rule", 30, "#4D746D")
        draw_text(
            frame, (153, 519), "Built by Hridya Jain  |  Solo entry", 21, "#4D746D"
        )
        draw_text(
            frame,
            (153, 553),
            "Concept animation  |  Actual app demo is separate",
            17,
            "#66877F",
        )
        return frame.convert("RGB")

    if t < 5:
        frame = compose_scene(images[0], t, 0)
        panel(frame, round(255 * alpha(t, 0, 5)))
        draw_text(frame, (818, 210), "One item.", 48, "#173F37", bold=True)
        draw_text(frame, (818, 272), "Two bins.", 48, "#173F37", bold=True)
        draw_text(frame, (818, 353), "Where should it go?", 29, "#4C6D65")
        draw_text(frame, (818, 495), "A small decision, made", 24, "#54776E")
        draw_text(frame, (818, 531), "millions of times a day.", 24, "#54776E")
    elif t < 10:
        frame = compose_scene(images[1], t, 5)
        panel(frame, round(255 * alpha(t, 5, 10)))
        draw_text(frame, (818, 215), "Take a photo.", 47, "#173F37", bold=True)
        draw_text(frame, (818, 315), "BinWise identifies the", 27, "#4C6D65")
        draw_text(frame, (818, 352), "likely material.", 27, "#4C6D65")
        d = ImageDraw.Draw(frame)
        d.rounded_rectangle((818, 440, 1198, 516), radius=22, fill="#E4F3E9")
        draw_text(
            frame, (842, 460), "Plastic bottle detected", 25, "#1A6857", bold=True
        )
    elif t < 14:
        frame = compose_scene(images[1], t, 5)
        panel(frame, 255)
        d = ImageDraw.Draw(frame)
        draw_text(frame, (818, 205), "Then check the", 39, "#173F37", bold=True)
        draw_text(frame, (818, 255), "local rules.", 39, "#173F37", bold=True)
        d.rounded_rectangle((818, 354, 1198, 488), radius=22, fill="#E4F3E9")
        draw_text(frame, (842, 379), "SAMPLE SITE", 17, "#397B6B", bold=True)
        draw_text(frame, (842, 416), "Recycling bin", 34, "#0D654E", bold=True)
        draw_text(frame, (818, 530), "Rules can vary by location.", 23, "#617B73")
    else:
        frame = compose_scene(images[2], t, 14)
        panel(frame, round(255 * alpha(t, 14, 19)))
        draw_text(frame, (818, 220), "Check. Sort.", 46, "#173F37", bold=True)
        draw_text(frame, (818, 281), "Do better.", 46, "#173F37", bold=True)
        draw_text(frame, (818, 385), "If unsure, BinWise asks", 26, "#4C6D65")
        draw_text(frame, (818, 422), "you to confirm instead", 26, "#4C6D65")
        draw_text(frame, (818, 459), "of guessing.", 26, "#4C6D65")
    # Persistent disclosure so the illustrated UI is not mistaken for a capture.
    tag = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    ImageDraw.Draw(tag).rounded_rectangle(
        (24, 672, 230, 704), radius=13, fill=(10, 47, 42, 185)
    )
    draw_text(tag, (40, 679), "CONCEPT ANIMATION", 16, "#FFFFFF", bold=True)
    frame.alpha_composite(tag)
    return frame.convert("RGB")


def create_audio(path: Path) -> None:
    rate = 44100
    seconds = DURATION
    audio = np.zeros(rate * seconds, dtype=np.float64)
    # Soft, original background motif; no external music or voice asset.
    notes = [261.63, 329.63, 392.0, 329.63, 293.66, 349.23, 440.0, 392.0]
    for start in np.arange(0, seconds, 0.75):
        freq = notes[int(start / 0.75) % len(notes)]
        count = min(int(rate * 0.7), len(audio) - int(start * rate))
        x = np.arange(count) / rate
        envelope = np.exp(-5.0 * x) * np.minimum(1.0, x * 25)
        note = np.sin(2 * math.pi * freq * x) + 0.22 * np.sin(4 * math.pi * freq * x)
        audio[int(start * rate) : int(start * rate) + count] += 0.08 * envelope * note
    fade = np.minimum(1.0, np.arange(len(audio)) / (rate * 0.6))
    fade *= np.minimum(1.0, np.arange(len(audio))[::-1] / (rate * 1.2))
    pcm = np.clip(audio * fade, -1, 1)
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes((pcm * 32767).astype("<i2").tobytes())


def main() -> None:
    MEDIA.mkdir(exist_ok=True)
    images = [Image.open(MEDIA / f"scene-{i}.png").convert("RGB") for i in range(1, 4)]
    audio_path = MEDIA / "cartoon-audio.wav"
    create_audio(audio_path)
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    args = [
        ffmpeg,
        "-y",
        "-loglevel",
        "error",
        "-f",
        "rawvideo",
        "-pix_fmt",
        "rgb24",
        "-s",
        f"{W}x{H}",
        "-r",
        str(FPS),
        "-i",
        "-",
        "-i",
        str(audio_path),
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "20",
        "-pix_fmt",
        "yuv420p",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        "-shortest",
        str(OUT),
    ]
    process = subprocess.Popen(args, stdin=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for index in range(DURATION * FPS):
            process.stdin.write(scene_frame(index / FPS, images).tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg failed to render the animation")
    finally:
        if process.poll() is None:
            process.kill()
    audio_path.unlink(missing_ok=True)
    print(OUT)


if __name__ == "__main__":
    main()
