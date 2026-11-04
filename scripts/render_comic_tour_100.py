"""Render the approximately 100-second BinWise comic tour with five GIF creatures.

First run narrate_comic_tour_100.ps1 to create the narration WAV files.
Requires Pillow, NumPy and imageio-ffmpeg for video authoring.
"""

from __future__ import annotations

import math
import subprocess
import wave
from bisect import bisect_right
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import render_comic_tour as short
import segno
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / "media"
VOICE = ROOT.parent.parent / "work" / "comic-voice-100-neural"
OUT = MEDIA / "binwise-comic-tour-100.mp4"
W, H, FPS = short.W, short.H, short.FPS
TRANSITION = 0.45

CAPTIONS = [
    "The bottle has a bin identity crisis.",
    "One clear photo. One visible item.",
    "Blur gremlin says: retake!",
    "Detective Cardboard checks the clue.",
    "A photo suggestion still needs a preparation check.",
    "Empty and clean? Answer before sorting.",
    "Uncertain? You choose the material.",
    "Type or tap. No photo needed.",
    "Food scraps → wet waste stream in the India guide.",
    "Battery gets special-care guidance.",
    "Hindi guidance can be read aloud.",
    "Scan this QR for the official rules source.",
    "Send feedback without a photo or name.",
    "Sample site profiles are demo examples.",
    "Local signs decide the exact handover.",
    "BinWise. Check. Prepare. Sort.",
]

OLD_SCENE = {0: 0, 1: 1, 2: 2, 4: 3, 6: 4, 7: 5,
             9: 6, 10: 7, 12: 9, 14: 10, 15: 11}


def load_voice() -> tuple[list[float], list[np.ndarray], int]:
    parts = []
    rate = 0
    for i in range(16):
        with wave.open(str(VOICE / f"voice-{i:02d}.wav"), "rb") as wav:
            assert wav.getnchannels() == 1 and wav.getsampwidth() == 2
            rate = wav.getframerate()
            parts.append(np.frombuffer(wav.readframes(wav.getnframes()), dtype="<i2").astype(np.float32) / 32768)
    durations = [len(p) / rate + 0.82 + (TRANSITION if i < 15 else 0)
                 for i, p in enumerate(parts)]
    durations[11] += 2.0  # Hold the unobstructed QR long enough to be noticed.
    return durations, parts, rate


def load_assets() -> dict:
    assets = short.load_assets()
    assets["cardboard"] = short.character_frames(
        "cardboard-detective.png", "cardboard-detective.gif", 385
    )
    assets["banana"] = short.character_frames(
        "banana-dancer.png", "banana-dancer.gif", 385
    )
    assets["gremlin"] = short.character_frames(
        "blur-gremlin.png", "blur-gremlin.gif", 385
    )
    assets["new_bg"] = {
        3: short.flat_bg("#FBEACC", "#F1D4A8"),
        5: short.flat_bg("#E4F1F7", "#C6E4EB"),
        8: short.flat_bg("#EEF8C9", "#D6EDA6"),
        11: short.flat_bg("#124B42", "#1C6759"),
        13: short.flat_bg("#E5F1EC", "#C8E2D4"),
    }
    qr_path = MEDIA / "official-rules-qr.png"
    segno.make_qr(
        "https://egazette.gov.in/WriteReadData/2026/269620.pdf", error="m"
    ).save(qr_path, kind="png", scale=8, border=4, dark=short.INK, light="white")
    assets["official_qr"] = Image.open(qr_path).convert("RGBA")
    assets["live_prep"] = Image.open(MEDIA / "demo-prep-panel.png").convert("RGBA").resize(
        (520, 244), Image.Resampling.LANCZOS)
    assets["live_typed"] = Image.open(MEDIA / "demo-typed-panel.png").convert("RGBA").resize(
        (540, 240), Image.Resampling.LANCZOS)
    assets["live_feedback"] = Image.open(MEDIA / "demo-feedback-panel.png").convert("RGBA").resize(
        (555, 151), Image.Resampling.LANCZOS)
    assets["live_food"] = short.screenshot("demo-food.png", (650, 15, 1205, 502), (510, 414))
    assets["live_battery"] = short.screenshot("demo-battery.png", (650, 15, 1205, 510), (495, 407))
    assets["live_hindi"] = short.screenshot("demo-hindi.png", (650, 15, 1205, 525), (478, 444))
    return assets


def draw_new_scene(index: int, t: float, duration: float, assets: dict) -> Image.Image:
    frame = assets["new_bg"][index].copy()
    d = ImageDraw.Draw(frame)
    if index == 3:
        short.burst(frame, 345, 391, t, "#E5B54F", 19, 330)
        short.paste_char(frame, assets["cardboard"], t, 344, 412, 0.87)
        short.panel(frame, (680, 115, 1215, 565), "#FFFDF7")
        short.text(d, (716, 153), "CASE FILE #001", 35, short.GREEN, True)
        short.text(d, (715, 219), "WHAT MATERIAL?", 49, short.INK, True)
        short.box(d, (721, 318, 1172, 387), short.YELLOW, short.INK, r=18)
        short.text(d, (745, 333), "PHOTO = A CLUE", 29, short.INK, True)
        short.text(d, (722, 438), "Look at the actual item.", 27, short.INK)
        # Animated little evidence markers around the magnifying glass.
        for k in range(4):
            x = round(494 + 19 * math.cos(t * 3 + k * 1.57))
            y = round(252 + 19 * math.sin(t * 3 + k * 1.57))
            d.ellipse((x-5, y-5, x+5, y+5), fill=short.CORAL)
    elif index == 5:
        short.text(d, (70, 117), "THE PREP CHECK", 62, short.INK, True)
        short.text(d, (75, 213), "Food stain? Liquid? Still full?", 31, short.GREEN, True)
        short.paste_char(frame, assets["cardboard"], t, 310, 473, 0.58)
        short.panel(frame, (617, 118, 1207, 565), "#FFFFFF")
        short.box(d, (660, 177, 1162, 251), "#E1F5E5", short.GREEN, r=20)
        short.text(d, (686, 194), "EMPTY + CLEAN?", 34, short.INK, True)
        short.box(d, (661, 295, 901, 421), "#CFF0DB", short.GREEN, r=20)
        short.text(d, (704, 315), "YES", 38, short.GREEN, True)
        short.text(d, (692, 369), "Dry guide", 27, short.INK, True)
        short.box(d, (922, 295, 1163, 421), "#FFE1D9", short.CORAL, r=20)
        short.text(d, (943, 315), "NO / ?", 35, "#9B453C", True)
        short.text(d, (937, 369), "Local check", 25, short.INK, True)
        short.text(d, (662, 478), "The bin waits until you answer.", 24, "#5D746B")
        marker_x = 775 if (int(t * 0.7) % 2 == 0) else 1035
        d.ellipse((marker_x-10, 438, marker_x+10, 458), fill=short.YELLOW,
                  outline=short.INK, width=3)
    elif index == 8:
        short.burst(frame, 335, 359, t, "#B6DC76", 22, 327)
        short.paste_char(frame, assets["banana"], t, 338, 405, 0.88)
        short.panel(frame, (671, 117, 1219, 562), "#FFFFFF")
        short.text(d, (709, 154), "BANANA BREAKS IT DOWN", 34, short.GREEN, True)
        short.text(d, (711, 234), "FOOD SCRAPS", 52, short.INK, True)
        short.box(d, (710, 338, 1176, 425), "#DDF2BD", short.GREEN, r=21)
        short.text(d, (735, 357), "WET WASTE STREAM", 32, short.GREEN, True)
        short.text(d, (714, 482), "India guide  •  check local collection", 23, "#607463")
        for k in range(5):
            x = 560 + k * 20
            y = 265 + round(22 * math.sin(t * 3 + k))
            d.ellipse((x, y+16, x+10, y+25), fill=short.GREEN)
            d.line((x+9, y+17, x+9, y-2), fill=short.GREEN, width=3)
            d.line((x+9, y-2, x+17, y+1), fill=short.GREEN, width=3)
    elif index == 11:
        short.text(d, (65, 138), "THE QR CODE", 65, "#FFFFFF", True)
        short.text(d, (70, 229), "IS RIGHT HERE.", 57, short.YELLOW, True)
        short.text(d, (76, 331), "Scan for the official", 29, "#FFFFFF")
        short.text(d, (76, 371), "waste-sorting rules.", 29, "#FFFFFF")
        short.box(d, (70, 463, 686, 548), short.YELLOW, short.INK, r=22)
        short.text(d, (92, 478), "App guide QR needs a", 26, short.INK, True)
        short.text(d, (92, 510), "reachable public link.", 26, short.INK, True)
        short.panel(frame, (751, 107, 1212, 576), "#FFFFFF")
        qr = assets["official_qr"]
        x = 795 + (372 - qr.width) // 2
        y = 127 + (370 - qr.height) // 2
        frame.alpha_composite(qr, (x, y))
        short.text(d, (790, 508), "OFFICIAL SOURCE QR", 27, short.GREEN, True)
    elif index == 13:
        short.text(d, (66, 126), "LOCATION MATTERS", 52, short.INK, True)
        short.text(d, (72, 213), "Rules can change by collection point.", 30, short.GREEN, True)
        short.panel(frame, (626, 115, 1211, 559), "#FFFFFF")
        short.box(d, (662, 183, 1167, 276), "#DDF2E5", short.GREEN, r=19)
        short.text(d, (686, 204), "INDIA-WIDE GUIDE", 30, short.GREEN, True)
        short.box(d, (662, 301, 1167, 395), "#FFECC2", "#B98738", r=19)
        short.text(d, (686, 321), "CAMPUS / OFFICE", 29, "#855B2A", True)
        short.text(d, (688, 360), "EXAMPLE DATA ONLY", 21, "#855B2A", True)
        short.text(d, (668, 467), "Verify the real signs before sorting.", 24, short.INK)
        short.paste_char(frame, assets["bottle"], t, 297, 473, 0.44)
        short.paste_char(frame, assets["banana"], max(0, t-0.15), 448, 498, 0.27)
    return frame


def overlay_gremlin(frame: Image.Image, t: float, assets: dict) -> None:
    # The first video has an illustrative blurred viewfinder; the gremlin owns it here.
    short.paste_char(frame, assets["gremlin"], t, 408, 393, 0.69)
    d = ImageDraw.Draw(frame)
    d.rectangle((135, 502, 618, 561), fill="#FFFFFF")
    short.box(d, (141, 512, 607, 559), short.YELLOW, short.INK, r=15)
    short.text(d, (164, 519), "SORRY, I BLURRED IT!", 22, short.INK, True)


def overlay_caption(frame: Image.Image, index: int, t: float) -> None:
    d = ImageDraw.Draw(frame)
    short.box(d, (30, 624, 1250, 705), short.INK, r=24)
    x = round(60 + (1-short.ease(t/0.3))*36)
    short.text(d, (x, 642), CAPTIONS[index], 27, "#FFFFFF", True)


def render_frame(index: int, t: float, duration: float, assets: dict) -> Image.Image:
    if index in OLD_SCENE:
        frame = short.draw_scene(OLD_SCENE[index], t, duration, assets,
                                 chrome=False, wipe=False).convert("RGBA")
    else:
        frame = draw_new_scene(index, t, duration, assets)
    if index == 2:
        overlay_gremlin(frame, t, assets)
    if index == 5:
        short.panel(frame, (617, 118, 1207, 565), "#FFFFFF")
        d = ImageDraw.Draw(frame)
        short.text(d, (650, 158), "IN THE APP", 28, short.GREEN, True)
        frame.alpha_composite(assets["live_prep"], (650, 220))
        short.text(d, (650, 505), "Answer before BinWise suggests a stream.", 22, short.INK)
    elif index == 7:
        short.panel(frame, (595, 147, 1194, 554), "#FFFFFF")
        d = ImageDraw.Draw(frame)
        short.text(d, (629, 176), "TYPE OR TAP IN THE APP", 27, short.GREEN, True)
        frame.alpha_composite(assets["live_typed"], (625, 238))
        short.text(d, (632, 497), "A no-photo route to the same guide.", 22, short.INK)
    elif index == 8:
        short.panel(frame, (671, 117, 1219, 562), "#FFFFFF")
        frame.alpha_composite(assets["live_food"], (690, 132))
    elif index == 9:
        short.panel(frame, (684, 113, 1216, 555), "#FFFFFF")
        frame.alpha_composite(assets["live_battery"], (702, 131))
    elif index == 10:
        short.panel(frame, (700, 108, 1208, 582), "#FFFFFF")
        frame.alpha_composite(assets["live_hindi"], (713, 124))
    elif index == 12:
        short.panel(frame, (562, 145, 1188, 552), "#FFFFFF")
        d = ImageDraw.Draw(frame)
        short.text(d, (596, 182), "FEEDBACK IN THE APP", 28, short.GREEN, True)
        frame.alpha_composite(assets["live_feedback"], (595, 260))
        short.text(d, (600, 461), "A report stores no photo or name.", 23, short.INK)
    overlay_caption(frame, index, t)
    return frame.convert("RGB")


def scene_starts(durations: list[float]) -> list[float]:
    starts = [0.0]
    for duration in durations[:-1]:
        starts.append(starts[-1] + duration - TRANSITION)
    return starts


def render_at(seconds: float, starts: list[float], durations: list[float],
              assets: dict) -> Image.Image:
    index = max(0, min(15, bisect_right(starts, seconds) - 1))
    local = seconds - starts[index]
    current = render_frame(index, local, durations[index], assets)
    if index and local < TRANSITION:
        previous = render_frame(index - 1, seconds - starts[index - 1],
                                durations[index - 1], assets)
        transition_bg = Image.new("RGB", (W, H), short.CREAM)
        if local < TRANSITION / 2:
            return Image.blend(previous, transition_bg,
                               short.ease(local / (TRANSITION / 2)))
        return Image.blend(transition_bg, current,
                           short.ease((local - TRANSITION / 2) / (TRANSITION / 2)))
    return current


def soundtrack(durations: list[float], starts: list[float],
               voices: list[np.ndarray], rate: int) -> Path:
    total=starts[-1]+durations[-1]
    n=round(total*rate)
    mix=np.zeros(n,dtype=np.float32)
    clock=np.arange(n,dtype=np.float32)/rate
    # Soft harmonics leave the spoken words clear.
    notes=(130.81,164.81,196.0,174.61)
    for tone,amp in ((1.0,0.0045),(1.5,0.0025),(2.0,0.0018)):
        frequency=np.array(notes)[(clock//12).astype(int)%len(notes)]*tone
        phase=2*np.pi*np.cumsum(frequency)/rate
        mix += amp*np.sin(phase)*(0.88+0.12*np.sin(2*np.pi*0.22*clock))
    for i,voice in enumerate(voices):
        start=round((starts[i]+0.48)*rate)
        voice_time=np.arange(len(voice),dtype=np.float32)/rate
        envelope=np.minimum(1,voice_time/0.035)*np.minimum(1,(len(voice)/rate-voice_time)/0.06)
        mix[start:start+len(voice)] += voice*0.84*envelope
        if i in (3,8,9,11,15):
            short.add_sound(mix,rate,starts[i]+0.13,"ding")
    fade=np.minimum(1,clock/0.7)*np.minimum(1,(total-clock)/1.0)
    pcm=(np.clip(mix*fade,-0.98,0.98)*32767).astype("<i2")
    path=ROOT.parent.parent/"work"/"comic-tour-100-audio.wav"
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate)
        wav.writeframes(pcm.tobytes())
    return path


def main() -> None:
    durations, voices, rate=load_voice()
    starts=scene_starts(durations)
    total=starts[-1]+durations[-1]
    assets=load_assets()
    audio=soundtrack(durations,starts,voices,rate)
    render_frame(0,2.0,durations[0],assets).save(MEDIA/"binwise-comic-tour-100-poster.png")
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(audio),
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","128k","-shortest",str(OUT)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        assert process.stdin is not None
        last_scene=-1
        for j in range(round(total*FPS)):
            seconds=j/FPS
            scene=max(0,min(15,bisect_right(starts,seconds)-1))
            if scene!=last_scene:
                print(f"Rendering scene {scene+1}/16",flush=True)
                last_scene=scene
            process.stdin.write(render_at(seconds,starts,durations,assets).tobytes())
        process.stdin.close()
        if process.wait()!=0:
            raise RuntimeError("FFmpeg failed")
    finally:
        if process.poll() is None:
            process.kill()
    print(f"Saved {OUT} ({total:.1f}s)")


if __name__=="__main__":
    main()
