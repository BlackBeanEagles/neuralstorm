"""Render the BinWise product film inspired by a problem-to-product demo structure.

Run capture_demo_states.py and narrate_comic_tour_100_neural.py with
cinematic_narration.txt before this authoring script. The film uses only original
BinWise illustrations and captures of the working app.
"""

from __future__ import annotations

import math
import subprocess
import wave
from bisect import bisect_right
from pathlib import Path

import imageio_ffmpeg
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageOps

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
VOICE = ROOT.parent.parent / "work" / "cinematic-voice"
OUT = MEDIA / "binwise-cinematic-demo.mp4"
W, H, FPS = 1280, 720, 24
TRANSITION = 0.55
DARK = "#102D29"
DEEP = "#09211E"
MINT = "#A8DFBF"
WHITE = "#F7F8F2"

CAPTIONS = [
    "One bottle. Two bins. No idea.",
    "A simple answer should not be a guessing game.",
    "Too dark? BinWise asks for another photo.",
    "One clear photo. One visible item.",
    "Real model result · TrashNet dataset photo",
    "Check the condition before the sorting step.",
    "No confident match means no bin guess.",
    "No camera? Type or tap an item.",
    "Food scraps → wet waste stream in the India guide.",
    "Battery → special-care waste, away from ordinary bins.",
    "Hindi guidance can be read aloud.",
    "Scan for the official source rules.",
    "Report a mistake without a photo or name.",
    "Sample site rules show how the answer can change.",
    "Follow your actual local collection signs.",
    "BinWise. Know where it goes.",
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "segoeuib.ttf" if bold else "segoeui.ttf"
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") / name), size)


def ease(value: float) -> float:
    value = max(0.0, min(1.0, value))
    return value * value * (3 - 2 * value)


def cover(path: Path) -> Image.Image:
    return ImageOps.fit(Image.open(path).convert("RGB"), (W, H),
                        method=Image.Resampling.LANCZOS)


def load_assets() -> dict[str, Image.Image]:
    filenames = {
        "story": "scene-1.png",
        "sort": "scene-3.png",
        "retake": "demo-retake.png",
        "choose": "demo-choose.png",
        "cardboard": "app-result-polished.png",
        "prep": "demo-prep.png",
        "no_guess": "demo-no-guess.png",
        "food": "demo-food.png",
        "battery": "demo-battery.png",
        "hindi": "demo-hindi.png",
        "sample": "demo-sample-site.png",
    }
    assets = {name: cover(MEDIA / filename) for name, filename in filenames.items()}
    assets["typed"] = Image.open(MEDIA / "demo-typed-panel.png").convert("RGB")
    assets["feedback"] = Image.open(MEDIA / "demo-feedback-panel.png").convert("RGB")
    assets["qr"] = Image.open(MEDIA / "official-rules-qr.png").convert("RGB")
    return assets


def load_voice() -> tuple[list[float], list[np.ndarray], int]:
    parts: list[np.ndarray] = []
    rate = 0
    for index in range(16):
        with wave.open(str(VOICE / f"voice-{index:02d}.wav"), "rb") as wav:
            if wav.getnchannels() != 1 or wav.getsampwidth() != 2:
                raise ValueError("Narration WAV must be mono, 16-bit PCM")
            rate = wav.getframerate()
            parts.append(np.frombuffer(wav.readframes(wav.getnframes()),
                                       dtype="<i2").astype(np.float32) / 32768)
    durations = [len(part) / rate + 1.0 + (TRANSITION if index < 15 else 0)
                 for index, part in enumerate(parts)]
    durations[11] += 2.0  # The QR stays in view without animation.
    return durations, parts, rate


def scene_starts(durations: list[float]) -> list[float]:
    starts = [0.0]
    for duration in durations[:-1]:
        starts.append(starts[-1] + duration - TRANSITION)
    return starts


def camera(image: Image.Image, t: float, duration: float,
           zoom: float = 1.07, focus_x: int = 640) -> Image.Image:
    progress = ease(t / max(0.1, duration))
    scale = 1.0 + (zoom - 1.0) * progress
    crop_w, crop_h = W / scale, H / scale
    desired_x = 640 + (focus_x - 640) * progress
    center_x = min(W - crop_w / 2, max(crop_w / 2, desired_x))
    left = round(center_x - crop_w / 2)
    top = round((H - crop_h) / 2)
    return image.crop((left, top, left + round(crop_w), top + round(crop_h))).resize(
        (W, H), Image.Resampling.BICUBIC)


def caption(frame: Image.Image, index: int) -> None:
    d = ImageDraw.Draw(frame)
    d.rectangle((0, 652, W, H), fill=DEEP)
    label = CAPTIONS[index]
    label_font = font(26, True)
    bounds = d.textbbox((0, 0), label, font=label_font)
    x = (W - (bounds[2] - bounds[0])) // 2
    d.text((x, 667), label, font=label_font, fill=WHITE)


def line_art(t: float) -> Image.Image:
    frame = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(frame)
    d.text((88, 91), "ONE ITEM.", font=font(73, True), fill=WHITE)
    d.text((88, 182), "TWO BINS.", font=font(73, True), fill=MINT)
    d.text((93, 306), "Which one?", font=font(33), fill="#D5EBDF")
    # A simple moving bottle and two outlined bins echo the reference's line art.
    bob = round(6 * math.sin(t * 3))
    bx, by = 589, 278 + bob
    d.rounded_rectangle((bx, by + 48, bx + 125, by + 242), radius=26,
                        outline=WHITE, width=6)
    d.rounded_rectangle((bx + 33, by + 15, bx + 92, by + 56), radius=8,
                        outline=WHITE, width=6)
    d.line((bx + 42, by + 17, bx + 42, by - 3, bx + 84, by - 3,
            bx + 84, by + 17), fill=WHITE, width=6)
    for eye_x in (bx + 42, bx + 83):
        d.ellipse((eye_x, by + 112, eye_x + 9, by + 122), fill=MINT)
    d.arc((bx + 48, by + 136, bx + 85, by + 168), 15, 165, fill=MINT, width=4)
    for x, label, accent in ((797, "DRY", MINT), (1012, "WET", "#9CCBE7")):
        d.rounded_rectangle((x, 306, x + 164, 516), radius=17,
                            outline=accent, width=6)
        d.line((x - 10, 306, x + 174, 306), fill=accent, width=7)
        d.text((x + 38, 390), label, font=font(30, True), fill=accent)
    # The dotted path deliberately stops before a bin: the decision is still open.
    for step in range(6):
        x = 731 + step * 19
        y = 349 + round(9 * math.sin(t * 2 + step * 0.65))
        d.ellipse((x, y, x + 6, y + 6), fill=MINT)
    return frame


def product_screen(source: Image.Image, t: float, duration: float,
                   focus_x: int = 640) -> Image.Image:
    frame = Image.new("RGB", (W, H), DEEP)
    screenshot = camera(source, t, duration, 1.08, focus_x)
    screenshot = screenshot.resize((1144, 644), Image.Resampling.LANCZOS)
    mask = Image.new("L", screenshot.size)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, 1143, 643), radius=24, fill=255)
    frame.paste(screenshot, (68, 8), mask)
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((68, 8, 1211, 651), radius=24,
                        outline="#42655A", width=3)
    return frame


def inset_panel(image: Image.Image, heading: str, subheading: str,
                t: float, duration: float) -> Image.Image:
    frame = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(frame)
    lines = heading.split("\n")
    for number, line in enumerate(lines):
        d.text((73, 153 + number * 83), line, font=font(67, True), fill=WHITE)
    d.text((79, 246 + (len(lines) - 1) * 83), subheading,
           font=font(34), fill=MINT)
    width = 660
    height = round(image.height * width / image.width)
    screenshot = image.resize((width, height), Image.Resampling.LANCZOS)
    offset = round(5 * math.sin(t / duration * math.pi))
    x, y = 532, 198 - offset
    d.rounded_rectangle((x + 10, y + 11, x + width + 10,
                         y + height + 11), radius=25, fill="#31544A")
    d.rounded_rectangle((x - 7, y - 7, x + width + 7,
                         y + height + 7), radius=25, fill=WHITE)
    frame.paste(screenshot, (x, y))
    return frame


def qr_scene(assets: dict[str, Image.Image]) -> Image.Image:
    frame = Image.new("RGB", (W, H), DEEP)
    d = ImageDraw.Draw(frame)
    d.text((87, 151), "SOURCE", font=font(78, True), fill=WHITE)
    d.text((87, 245), "YOU CAN SCAN.", font=font(49, True), fill=MINT)
    d.text((93, 363), "Official waste-sorting rules", font=font(29), fill=WHITE)
    d.text((93, 407), "for the India-wide guide.", font=font(29), fill=WHITE)
    d.text((93, 504), "App sharing needs a public link.", font=font(24), fill="#A8C9B8")
    d.rounded_rectangle((762, 87, 1211, 566), radius=27, fill=WHITE)
    qr = assets["qr"].resize((386, 386), Image.Resampling.NEAREST)
    frame.paste(qr, (795, 116))
    d.text((828, 510), "OFFICIAL SOURCE QR", font=font(24, True), fill=DARK)
    return frame


def ending() -> Image.Image:
    frame = Image.new("RGB", (W, H), WHITE)
    d = ImageDraw.Draw(frame)
    d.rounded_rectangle((436, 152, 520, 236), radius=24, fill=DARK)
    for x, top in ((458, 177), (477, 167), (496, 177)):
        d.line((x, top, x, top + 37), fill=WHITE, width=7)
    d.text((545, 148), "binwise.", font=font(87, True), fill=DARK)
    d.text((439, 290), "Know where it goes.", font=font(43, True), fill="#287A5C")
    d.line((437, 384, 844, 384), fill="#C6DACB", width=3)
    d.text((440, 425), "Check  •  Prepare  •  Sort", font=font(29), fill=DARK)
    d.text((440, 510), "Created by Hridya Jain", font=font(25), fill="#55766A")
    return frame


def render_scene(index: int, t: float, duration: float,
                 assets: dict[str, Image.Image]) -> Image.Image:
    if index == 0:
        frame = camera(assets["story"], t, duration, 1.045, 640)
    elif index == 1:
        frame = line_art(t)
    elif index == 7:
        frame = inset_panel(assets["typed"], "NO CAMERA?", "Type it, or tap a choice.", t, duration)
    elif index == 11:
        frame = qr_scene(assets)
    elif index == 12:
        frame = inset_panel(assets["feedback"], "SPOT A\nMISTAKE?",
                            "Tell BinWise what changed.", t, duration)
    elif index == 14:
        frame = camera(assets["sort"], t, duration, 1.045, 640)
        d = ImageDraw.Draw(frame)
        d.text((815, 125), "LOCAL SIGNS", font=font(48, True), fill=DARK,
               stroke_width=2, stroke_fill=WHITE)
        d.text((815, 189), "DECIDE.", font=font(48, True), fill=DARK,
               stroke_width=2, stroke_fill=WHITE)
        d.text((827, 592), "Illustrated example", font=font(19, True), fill=DARK)
    elif index == 15:
        frame = ending()
    else:
        key = {2: "retake", 3: "choose", 4: "cardboard", 5: "prep",
               6: "no_guess", 8: "food", 9: "battery", 10: "hindi",
               13: "sample"}[index]
        focus_x = 675 if index in (2, 4, 5, 6, 8, 9, 10, 13) else 640
        frame = product_screen(assets[key], t, duration, focus_x)
    caption(frame, index)
    return frame


def render_at(seconds: float, starts: list[float], durations: list[float],
              assets: dict[str, Image.Image]) -> Image.Image:
    index = max(0, min(15, bisect_right(starts, seconds) - 1))
    local = seconds - starts[index]
    current = render_scene(index, local, durations[index], assets)
    if index and local < TRANSITION:
        previous = render_scene(index - 1, seconds - starts[index - 1],
                                durations[index - 1], assets)
        blank = Image.new("RGB", (W, H), DEEP)
        if local < TRANSITION / 2:
            return Image.blend(previous, blank, ease(local / (TRANSITION / 2)))
        return Image.blend(blank, current,
                           ease((local - TRANSITION / 2) / (TRANSITION / 2)))
    return current


def soundtrack(durations: list[float], starts: list[float],
               voices: list[np.ndarray], rate: int) -> Path:
    total = starts[-1] + durations[-1]
    clock = np.arange(round(total * rate), dtype=np.float32) / rate
    mix = np.zeros(len(clock), dtype=np.float32)
    # Quiet sustained tones support the narration without competing with it.
    for frequency, amplitude in ((130.81, 0.004), (164.81, 0.0025),
                                 (196.0, 0.0015)):
        mix += amplitude * np.sin(2 * np.pi * frequency * clock) * (
            0.82 + 0.18 * np.sin(2 * np.pi * 0.13 * clock))
    for index, voice in enumerate(voices):
        start = round((starts[index] + 0.56) * rate)
        timeline = np.arange(len(voice), dtype=np.float32) / rate
        envelope = np.minimum(1, timeline / 0.04) * np.minimum(
            1, (len(voice) / rate - timeline) / 0.08)
        mix[start:start + len(voice)] += voice * envelope * 0.88
    fade = np.minimum(1, clock / 0.8) * np.minimum(1, (total - clock) / 1.0)
    pcm = (np.clip(mix * fade, -0.98, 0.98) * 32767).astype("<i2")
    target = ROOT.parent.parent / "work" / "cinematic-audio.wav"
    with wave.open(str(target), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())
    return target


def main() -> None:
    durations, voices, rate = load_voice()
    starts = scene_starts(durations)
    total = starts[-1] + durations[-1]
    assets = load_assets()
    audio = soundtrack(durations, starts, voices, rate)
    render_scene(0, 2.0, durations[0], assets).save(
        MEDIA / "binwise-cinematic-demo-poster.png")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    command = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo",
               "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS),
               "-i", "-", "-i", str(audio), "-c:v", "libx264", "-preset",
               "veryfast", "-crf", "19", "-pix_fmt", "yuv420p", "-c:a",
               "aac", "-b:a", "128k", "-shortest", str(OUT)]
    process = subprocess.Popen(command, stdin=subprocess.PIPE)
    try:
        assert process.stdin is not None
        last_scene = -1
        for frame_number in range(round(total * FPS)):
            seconds = frame_number / FPS
            scene = max(0, min(15, bisect_right(starts, seconds) - 1))
            if scene != last_scene:
                print(f"Rendering scene {scene + 1}/16", flush=True)
                last_scene = scene
            process.stdin.write(render_at(seconds, starts, durations, assets).tobytes())
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg failed")
    finally:
        if process.poll() is None:
            process.kill()
    print(f"Saved {OUT} ({total:.1f}s)")


if __name__ == "__main__":
    main()
