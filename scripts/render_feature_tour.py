"""Render a narrated, illustrated feature tour with app captures and GIF stickers.

Run on Windows after `narrate_feature_tour.ps1` has created WAV files in
../../work/feature-voice. Requires Pillow, numpy, and imageio-ffmpeg.
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
VOICE = ROOT.parent.parent / "work" / "feature-voice"
OUT = MEDIA / "binwise-feature-tour.mp4"
W, H, FPS = 1280, 720, 18
CREAM, DARK, GREEN, MINT = "#F6F7EF", "#123B34", "#267B60", "#DCEFE2"

SCENES = [
    ("BINWISE", "A bottle. Two bins. One tiny crisis.", "Meet the bottle with a bin-dentity crisis.", "scene-1.png"),
    ("SNAP ONE ITEM", "A clear photo starts the sorting step.", "No group selfies for garbage.", "app-home-polished.png"),
    ("SEE A SUGGESTION", "A real cardboard photo from the app.", "Cardboard → dry waste, after prep.", "app-result-polished.png"),
    ("BLUR? RETAKE.", "Dark, tiny, or fuzzy images get another try.", "Even the camera can have an off day.", "illustration"),
    ("UNSURE? YOU CHOOSE.", "Uncertain items need your confirmation.", "No confident match = no automatic bin advice.", "illustration"),
    ("EMPTY AND CLEAN?", "Answer the preparation questions first.", "No or unsure? Check locally before sorting.", "app-result-polished.png"),
    ("NO CAMERA? NO PROBLEM.", "Type an item or tap a common choice.", "The typed route sends no photo.", "illustration"),
    ("BATTERIES ARE SPECIAL", "Special-care waste needs separate handling.", "The battery refuses the regular bin.", "illustration"),
    ("HINDI + READ ALOUD", "Read guidance or listen to it.", "Sorting advice, now with a voice.", "app-hindi-prep-polished.png"),
    ("SHARE THE GUIDE", "Create a QR card for the sourced guide.", "Use a reachable link for other phones.", "illustration"),
    ("SPOT A MISTAKE?", "Report the material or a local-rule difference.", "Feedback stores no photo or name.", "illustration"),
    ("LOCAL RULES FIRST", "India-wide guidance; local handover varies.", "Know where it goes. Check your local signs.", "scene-3.png"),
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(
        str(Path("C:/Windows/Fonts") / ("arialbd.ttf" if bold else "arial.ttf")), size
    )


def ease(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def txt(draw: ImageDraw.ImageDraw, at: tuple[int, int], value: str, size: int,
        color: str = DARK, bold: bool = False) -> None:
    draw.text(at, value, fill=color, font=font(size, bold))


def card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int],
         fill: str = "#FFFFFF", outline: str | None = None, radius: int = 28) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=3)


def fit_image(path: Path, box: tuple[int, int]) -> Image.Image:
    image = Image.open(path).convert("RGB")
    w, h = box
    scale = max(w / image.width, h / image.height)
    image = image.resize((round(image.width * scale), round(image.height * scale)), Image.Resampling.LANCZOS)
    x = (image.width - w) // 2
    y = (image.height - h) // 2
    return image.crop((x, y, x + w, y + h))


def screenshot_card(base: Image.Image, filename: str, crop: tuple[int, int, int, int],
                    label: str) -> None:
    frame = Image.open(MEDIA / filename).convert("RGB").crop(crop)
    frame.thumbnail((450, 463), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (490, 508), (255, 255, 255, 0))
    d = ImageDraw.Draw(canvas)
    card(d, (4, 4, 486, 504), "#FFFFFF", "#CFE5D5")
    canvas.alpha_composite(frame.convert("RGBA"), ((490 - frame.width) // 2, 21))
    d = ImageDraw.Draw(canvas)
    card(d, (24, 458, 466, 490), "#E3F3E8", radius=13)
    txt(d, (38, 464), label, 17, GREEN, True)
    base.alpha_composite(canvas, (744, 103))


def comic_bottle_frame(phase: int) -> Image.Image:
    im = Image.new("RGBA", (210, 255), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    wobble = round(5 * math.sin(phase * math.tau / 16))
    d.ellipse((48 + wobble, 232, 169 + wobble, 250), fill=(33, 71, 57, 35))
    d.rounded_rectangle((71 + wobble, 12, 143 + wobble, 38), radius=7, fill="#1378C3", outline="#0D527E", width=3)
    d.rounded_rectangle((67 + wobble, 31, 148 + wobble, 218), radius=38, fill="#A7E0F0", outline="#2F91B3", width=5)
    d.rounded_rectangle((75 + wobble, 65, 141 + wobble, 195), radius=29, fill="#E3F8F6")
    d.rounded_rectangle((74 + wobble, 126, 142 + wobble, 163), radius=6, fill="#58C6A9")
    d.line((67 + wobble, 130, 27 + wobble, 111 + phase % 3 * 2), fill="#2B7E90", width=6)
    d.line((148 + wobble, 130, 183 + wobble, 105 + phase % 4 * 2), fill="#2B7E90", width=6)
    d.line((80 + wobble, 215, 70 + wobble, 234), fill="#2B7E90", width=6)
    d.line((135 + wobble, 215, 144 + wobble, 234), fill="#2B7E90", width=6)
    d.ellipse((86 + wobble, 86, 99 + wobble, 104), fill=DARK)
    d.ellipse((119 + wobble, 86, 132 + wobble, 104), fill=DARK)
    d.arc((94 + wobble, 101, 126 + wobble, 125), 10, 170, fill=DARK, width=3)
    return im


def comic_battery_frame(phase: int) -> Image.Image:
    im = Image.new("RGBA", (225, 225), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    tilt = round(4 * math.sin(phase * math.tau / 16))
    d.ellipse((35, 197, 196, 220), fill=(33, 71, 57, 35))
    d.rounded_rectangle((48 + tilt, 47, 183 + tilt, 187), radius=23, fill="#F5C65A", outline="#87602C", width=5)
    d.rounded_rectangle((93 + tilt, 28, 139 + tilt, 54), radius=7, fill="#6F6660")
    d.rectangle((54 + tilt, 70, 177 + tilt, 98), fill="#194D43")
    txt(d, (89 + tilt, 66), "+", 29, "#FFFFFF", True)
    d.ellipse((79 + tilt, 111, 94 + tilt, 130), fill=DARK)
    d.ellipse((139 + tilt, 111, 154 + tilt, 130), fill=DARK)
    d.arc((98 + tilt, 121, 137 + tilt, 145), 0, 180, fill=DARK, width=4)
    d.line((50 + tilt, 119, 23 + tilt, 108), fill="#8E612D", width=6)
    d.line((181 + tilt, 119, 210 + tilt, 102), fill="#8E612D", width=6)
    return im


def save_gifs() -> tuple[list[Image.Image], list[Image.Image]]:
    bottle = [comic_bottle_frame(i) for i in range(16)]
    battery = [comic_battery_frame(i) for i in range(16)]
    for frames, filename in ((bottle, "bottle-buddy.gif"), (battery, "battery-buddy.gif")):
        frames[0].save(MEDIA / filename, save_all=True, append_images=frames[1:],
                       duration=85, loop=0, disposal=2, optimize=True)
    return bottle, battery


def base_scene(index: int) -> Image.Image:
    title, detail, joke, source = SCENES[index]
    if source.startswith("scene-"):
        base = fit_image(MEDIA / source, (W, H)).convert("RGBA")
        overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        od = ImageDraw.Draw(overlay)
        card(od, (693, 87, 1232, 585), "#FFFFFF", radius=30)
        base.alpha_composite(overlay)
    else:
        base = Image.new("RGBA", (W, H), CREAM)
        d = ImageDraw.Draw(base)
        d.ellipse((-105, 370, 500, 970), fill="#E2F0E4")
        d.ellipse((970, -255, 1520, 290), fill="#D9EEE6")
        d.rounded_rectangle((700, 83, 1233, 594), radius=32, fill="#FFFFFF", outline="#D6E8D8", width=3)
    d = ImageDraw.Draw(base)
    if source.startswith("scene-"):
        text_x = 725
        text_max = 490
    else:
        text_x = 72
        text_max = 580
    card(d, (text_x, 117, text_x + 158, 152), MINT, radius=17)
    txt(d, (text_x + 16, 124), f"FEATURE {index + 1:02d}/12", 16, GREEN, True)
    title_size = 48 if len(title) < 20 else 41
    if d.textbbox((0, 0), title, font=font(title_size, True))[2] > text_max:
        title_size = 37
    txt(d, (text_x, 186), title, title_size, DARK, True)
    txt(d, (text_x, 266), detail, 23, "#4B6D62")
    if index == 0:
        card(d, (text_x, 366, text_x + 200, 448), "#E8F5E9", radius=22)
        txt(d, (text_x + 19, 388), "Blue? Green?", 22, GREEN, True)
        txt(d, (text_x + 19, 415), "Help!", 22, GREEN, True)
    elif index == 11:
        card(d, (text_x, 317, text_x + 180, 353), "#DCEFE2", radius=16)
        txt(d, (text_x + 13, 324), "INDIA GUIDE", 17, GREEN, True)
        card(d, (text_x + 189, 317, text_x + 463, 353), "#F7E9C9", radius=16)
        txt(d, (text_x + 201, 324), "SAMPLE SITE · DEMO", 17, "#8A5B13", True)
        card(d, (text_x, 366, text_x + 295, 448), "#E8F5E9", radius=22)
        txt(d, (text_x + 20, 391), "Check local signs.", 22, GREEN, True)
    else:
        card(d, (text_x, 366, text_x + text_max, 448), "#E8F5E9", radius=22)
        txt(d, (text_x + 20, 390), joke, 22, GREEN, True)
    if source == "app-result-polished.png":
        screenshot_card(base, source, (630, 64, 1191, 665), "ACTUAL APP CAPTURE · DATASET PHOTO")
    elif source == "app-hindi-prep-polished.png":
        screenshot_card(base, source, (620, 0, 1190, 670), "ACTUAL APP CAPTURE · TYPED ITEM")
    elif source == "app-home-polished.png":
        screenshot_card(base, "app-home-polished.png", (60, 50, 650, 710), "ACTUAL APP CAPTURE · HOME")
    elif source == "illustration":
        draw_illustration(base, index)
    if index == 11:
        txt(d, (730, 512), "Made by Hridya Jain", 25, DARK, True)
    return base


def draw_illustration(base: Image.Image, index: int) -> None:
    d = ImageDraw.Draw(base)
    x, y = 730, 124
    if index == 3:
        card(d, (x + 55, y + 10, x + 425, y + 412), "#183F39", radius=28)
        d.rounded_rectangle((x + 81, y + 45, x + 399, y + 305), radius=18, fill="#6E8984")
        for cx, cy, r in ((170, 144, 50), (260, 215, 60), (325, 125, 45)):
            d.ellipse((x + cx - r, y + cy - r, x + cx + r, y + cy + r), fill="#A1ABA5")
        card(d, (x + 111, y + 333, x + 369, y + 388), "#D9F3E3", radius=22)
        txt(d, (x + 160, y + 347), "RETAKE PHOTO", 23, GREEN, True)
    elif index == 4:
        txt(d, (x + 180, y + 8), "?", 144, "#61AD88", True)
        txt(d, (x + 70, y + 189), "Choose the material:", 28, DARK, True)
        card(d, (x + 50, y + 248, x + 260, y + 312), MINT)
        txt(d, (x + 91, y + 265), "Cardboard", 24, GREEN, True)
        card(d, (x + 270, y + 248, x + 480, y + 312), "#F3F5EE", "#D3E1D3")
        txt(d, (x + 298, y + 265), "Something else", 22, DARK, True)
        txt(d, (x + 97, y + 365), "No guess, no wrong bin.", 23, "#6A8179")
    elif index == 6:
        txt(d, (x + 45, y + 20), "No camera?", 31, DARK, True)
        card(d, (x + 34, y + 100, x + 468, y + 169), "#F5F9F3", "#CFE3D3")
        txt(d, (x + 56, y + 120), "plastic bottle", 25, "#486C5F")
        for k, (label, left) in enumerate((("Plastic bottle", 37), ("Cardboard", 263),
                                           ("Food scraps", 37), ("Battery", 263))):
            yy = y + 208 + (k // 2) * 91
            card(d, (x + left, yy, x + left + 209, yy + 63), MINT, radius=17)
            txt(d, (x + left + 16, yy + 18), label, 21, GREEN, True)
    elif index == 7:
        card(d, (x + 39, y + 307, x + 467, y + 393), "#FBEAC9", radius=23)
        txt(d, (x + 73, y + 329), "SPECIAL-CARE WASTE", 26, "#8A5B13", True)
        txt(d, (x + 72, y + 406), "Ask your local collector.", 20, "#65776C")
    elif index == 9:
        cell = 18
        for row in range(15):
            for col in range(15):
                finder = ((row < 5 and col < 5) or (row < 5 and col > 9)
                          or (row > 9 and col < 5))
                on = finder and (row in (0, 4, 10, 14) or col in (0, 4, 10, 14)
                                 or 1 < row % 10 < 4 and 1 < col % 10 < 4)
                on = on or (not finder and (row * 7 + col * 11 + row * col) % 5 < 2)
                if on:
                    d.rectangle((x + 111 + col * cell, y + 37 + row * cell,
                                 x + 127 + col * cell, y + 53 + row * cell), fill=DARK)
        txt(d, (x + 137, y + 351), "ILLUSTRATED QR CARD", 17, GREEN, True)
        txt(d, (x + 60, y + 401), "Real QR uses a shared guide link.", 20, "#65776C")
    elif index == 10:
        txt(d, (x + 60, y + 30), "Was this advice correct?", 30, DARK, True)
        for i, label in enumerate(("Yes, correct", "Wrong material", "Local rule differs")):
            yy = y + 112 + i * 96
            card(d, (x + 48, yy, x + 455, yy + 72), MINT if i == 0 else "#F5F8F2",
                 "#CDE1D0", radius=17)
            txt(d, (x + 76, yy + 22), label, 24, GREEN if i == 0 else DARK, True)
        txt(d, (x + 105, y + 411), "No photo. No name.", 21, "#65776C")


def lengths() -> tuple[list[float], list[np.ndarray], int]:
    samples = []
    rate = None
    for i in range(len(SCENES)):
        with wave.open(str(VOICE / f"voice-{i:02d}.wav"), "rb") as wav:
            assert wav.getnchannels() == 1 and wav.getsampwidth() == 2
            rate = wav.getframerate()
            samples.append(np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float32) / 32768)
    assert rate is not None
    return [len(s) / rate + 0.7 for s in samples], samples, rate


def make_audio(durations: list[float], samples: list[np.ndarray], rate: int) -> Path:
    total = sum(durations)
    n = round(total * rate)
    mix = np.zeros(n, dtype=np.float32)
    clock = np.arange(n, dtype=np.float32) / rate
    # Original soft, slightly bouncy music loop.
    notes = (261.63, 329.63, 392.00, 493.88, 392.00, 329.63, 293.66, 349.23)
    for start in np.arange(0, total, 0.54):
        ix = round(start * rate)
        count = min(round(rate * 0.45), n - ix)
        tt = np.arange(count, dtype=np.float32) / rate
        f = notes[int(start / 0.54) % len(notes)]
        env = np.exp(-8 * tt) * np.minimum(1.0, 25 * tt)
        mix[ix:ix + count] += (0.024 * np.sin(2 * np.pi * f * tt) * env)
    cursor = 0.0
    for i, voice in enumerate(samples):
        ix = round((cursor + 0.28) * rate)
        end = min(n, ix + len(voice))
        mix[ix:end] += voice[:end - ix] * 0.78
        # Small comic pop at scene transitions.
        count = min(round(rate * 0.14), n - round(cursor * rate))
        tt = np.arange(count, dtype=np.float32) / rate
        pulse = 0.045 * np.sin(2 * np.pi * (310 + 600 * tt) * tt) * np.exp(-25 * tt)
        start = round(cursor * rate)
        mix[start:start + count] += pulse
        cursor += durations[i]
    fade = np.minimum(1.0, clock / 0.35) * np.minimum(1.0, (total - clock) / 0.7)
    audio = (np.clip(mix * fade, -0.97, 0.97) * 32767).astype("<i2")
    path = ROOT.parent.parent / "work" / "feature-tour-audio.wav"
    with wave.open(str(path), "wb") as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(rate)
        wav.writeframes(audio.tobytes())
    return path


def frame_for(index: int, elapsed: float, duration: float, bases: list[Image.Image],
              bottle: list[Image.Image], battery: list[Image.Image]) -> Image.Image:
    frame = bases[index].copy()
    d = ImageDraw.Draw(frame)
    progress = elapsed / duration
    gif_frame = round(elapsed * 12) % 16
    if index == 0:
        frame.alpha_composite(bottle[gif_frame], (992 + round(9 * math.sin(elapsed * 2.5)), 309))
    elif index == 1:
        d.rounded_rectangle((775, 548, 1179, 567), radius=9, fill="#D6E9DA")
        d.rounded_rectangle((775, 548, 775 + round(404 * ease(progress)), 567), radius=9, fill=GREEN)
    elif index == 2:
        if elapsed > duration * 0.45:
            card(d, (765, 507, 1174, 557), "#C7ECD5", radius=17)
            txt(d, (785, 518), "CHECK PREP → DRY WASTE", 21, GREEN, True)
    elif index == 3:
        if int(elapsed * 2.2) % 2 == 0:
            card(d, (810, 337, 1135, 430), "#FCF5E4", "#EECF8B", radius=20)
            txt(d, (852, 360), "PLEASE RETAKE", 29, "#9B691B", True)
    elif index == 4:
        frame.alpha_composite(bottle[gif_frame].resize((108, 131)), (1042, 474))
    elif index == 5:
        if progress > 0.4:
            card(d, (770, 511, 1173, 563), "#D2F0DC", radius=16)
            txt(d, (786, 524), "EMPTY?  CLEAN?  CHECK.", 22, GREEN, True)
    elif index == 6:
        x = 795 + round(235 * ease((progress - 0.25) / 0.5))
        d.ellipse((x - 15, 430, x + 15, 460), fill="#FAAF57", outline="#9F5B24", width=3)
    elif index == 7:
        frame.alpha_composite(battery[gif_frame], (860 + round(7 * math.sin(elapsed * 3)), 195))
    elif index == 8:
        for i in range(4):
            height = 18 + round(17 * abs(math.sin(elapsed * 6 + i * 1.3)))
            d.rounded_rectangle((1010 + i * 19, 508 - height, 1022 + i * 19, 508 + height), radius=6, fill=GREEN)
    elif index == 9:
        d.arc((1129, 380, 1210, 462), 245, 115, fill=GREEN, width=5)
        d.arc((1139, 389, 1201, 453), 245, 115, fill=GREEN, width=4)
    elif index == 10:
        pos = min(2, int(elapsed * 0.65) % 3)
        d.ellipse((1190, 237 + pos * 96, 1210, 257 + pos * 96), fill="#58B782")
    elif index == 11:
        frame.alpha_composite(bottle[gif_frame].resize((105, 128)), (1066, 417))
    # Accessible subtitle strip and a small, persistent disclosure.
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    od.rounded_rectangle((44, 616, 1236, 701), radius=23, fill=(13, 49, 43, 235))
    txt(od, (70, 639), SCENES[index][2], 27, "#FFFFFF", True)
    txt(od, (52, 19), "BINWISE  •  ANIMATED FEATURE TOUR", 19, "#FFFFFF" if SCENES[index][3].startswith("scene-") else GREEN, True)
    if index not in (0, 1, 2, 5, 8, 11):
        txt(od, (958, 24), "ILLUSTRATED UI", 16, GREEN, True)
    frame.alpha_composite(overlay)
    # Soft fade at scene boundaries.
    fade = min(1.0, elapsed / 0.28, (duration - elapsed) / 0.28)
    if fade < 1:
        frame = Image.blend(Image.new("RGBA", (W, H), CREAM), frame, max(0.0, fade))
    return frame.convert("RGB")


def main() -> None:
    MEDIA.mkdir(exist_ok=True)
    durations, voices, rate = lengths()
    audio = make_audio(durations, voices, rate)
    bottle, battery = save_gifs()
    bases = [base_scene(i) for i in range(len(SCENES))]
    preview = frame_for(0, 2.5, durations[0], bases, bottle, battery)
    preview.save(MEDIA / "binwise-feature-tour-preview.png")
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    args = [ffmpeg, "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", str(audio),
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-shortest", str(OUT)]
    process = subprocess.Popen(args, stdin=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for i, duration in enumerate(durations):
            for n in range(round(duration * FPS)):
                process.stdin.write(frame_for(i, n / FPS, duration, bases, bottle, battery).tobytes())
            print(f"Rendered scene {i + 1}/{len(SCENES)}: {SCENES[i][0]}", flush=True)
        process.stdin.close()
        if process.wait() != 0:
            raise RuntimeError("FFmpeg failed to render the feature tour")
    finally:
        if process.poll() is None:
            process.kill()
    print(f"{OUT} ({sum(durations):.1f} seconds)")


if __name__ == "__main__":
    main()
