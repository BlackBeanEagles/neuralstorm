"""Render BinWise's faster comic feature tour with animated character GIFs.

Run narrate_comic_tour.ps1 first. This authoring script needs Pillow, NumPy,
and imageio-ffmpeg; the app itself does not need those video authoring tools.
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
VOICE = ROOT.parent.parent / "work" / "comic-voice"
OUT = MEDIA / "binwise-comic-tour.mp4"
W, H, FPS = 1280, 720, 20
INK = "#103C34"
GREEN = "#24785C"
TEAL = "#3DBB96"
YELLOW = "#FFCF57"
CREAM = "#FFF9EC"
CORAL = "#F27665"

CAPTIONS = [
    "One bottle. Two bins. A tiny identity crisis.",
    "One clear photo. One item. Let's sort.",
    "Blurry photo? Even robots need glasses.",
    "Cardboard suggestion → clean check → dry waste guide.",
    "Unsure? You choose. No risky bin guess.",
    "No camera? Type or tap. No photo sent.",
    "Battery: special care, not the regular bin.",
    "Hindi guidance and advice read aloud.",
    "QR sharing works with a reachable guide link.",
    "Spot a mistake? Send a correction.",
    "India-wide guide. Local signs have the final word.",
    "BinWise. Know where it goes."
]


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(Path("C:/Windows/Fonts") /
                                  ("segoeuib.ttf" if bold else "segoeui.ttf")), size)


def ease(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return x * x * (3 - 2 * x)


def spring(x: float) -> float:
    x = min(1.0, max(0.0, x))
    return 1 - math.exp(-8 * x) * math.cos(13 * x)


def text(d: ImageDraw.ImageDraw, xy: tuple[int, int], s: str, size: int,
         fill: str = INK, bold: bool = False, stroke: int = 0) -> None:
    d.text(xy, s, font=font(size, bold), fill=fill, stroke_width=stroke,
           stroke_fill=INK if stroke else None)


def box(d: ImageDraw.ImageDraw, rect: tuple[int, int, int, int], fill: str,
        outline: str | None = None, r: int = 25, width: int = 4) -> None:
    d.rounded_rectangle(rect, radius=r, fill=fill, outline=outline, width=width)


def panel(im: Image.Image, rect: tuple[int, int, int, int], fill: str = "#FFFFFF",
          outline: str = INK, r: int = 27) -> None:
    d = ImageDraw.Draw(im)
    x1, y1, x2, y2 = rect
    box(d, (x1 + 9, y1 + 11, x2 + 9, y2 + 11), "#194C3E", r=r)
    box(d, rect, fill, outline, r=r, width=5)


def cover(path: Path) -> Image.Image:
    im = Image.open(path).convert("RGB")
    scale = max(W / im.width, H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.Resampling.LANCZOS)
    return im.crop(((im.width - W) // 2, (im.height - H) // 2,
                    (im.width + W) // 2, (im.height + H) // 2)).convert("RGBA")


def flat_bg(fill: str, dots: str) -> Image.Image:
    im = Image.new("RGBA", (W, H), fill)
    d = ImageDraw.Draw(im)
    for row in range(13):
        for col in range(24):
            x, y = 19 + col * 55, 16 + row * 55
            r = 2 + (row + col) % 2
            d.ellipse((x-r, y-r, x+r, y+r), fill=dots)
    d.arc((-230, 365, 350, 950), 192, 345, fill=dots, width=18)
    d.arc((950, -250, 1530, 330), 25, 165, fill=dots, width=18)
    return im


def character_frames(filename: str, gif_name: str, height: int) -> list[Image.Image]:
    source = Image.open(MEDIA / filename).convert("RGBA")
    bbox = source.getbbox()
    assert bbox is not None
    source = source.crop(bbox)
    source = source.resize((round(source.width * height / source.height), height),
                           Image.Resampling.LANCZOS)
    frames = []
    for i in range(20):
        phase = 2 * math.pi * i / 20
        squish = 1 + 0.035 * math.sin(phase)
        scaled = source.resize((round(source.width / squish), round(source.height * squish)),
                                Image.Resampling.BICUBIC)
        tilt = 4.5 * math.sin(phase - 0.8)
        rotated = scaled.rotate(tilt, resample=Image.Resampling.BICUBIC, expand=True)
        canvas = Image.new("RGBA", (420, 480), (0, 0, 0, 0))
        x = (420 - rotated.width) // 2
        y = 16 + round(8 * math.sin(phase))
        canvas.alpha_composite(rotated, (x, y))
        frames.append(canvas)
    frames[0].save(MEDIA / gif_name, save_all=True, append_images=frames[1:],
                   duration=70, loop=0, disposal=2, optimize=True)
    return frames


def screenshot(path: str, crop: tuple[int, int, int, int], size: tuple[int, int]) -> Image.Image:
    im = Image.open(MEDIA / path).convert("RGB").crop(crop)
    return im.resize(size, Image.Resampling.LANCZOS).convert("RGBA")


def paste_char(frame: Image.Image, frames: list[Image.Image], t: float, x: int, y: int,
               scale: float = 1.0, entrance: float = 0.5) -> None:
    active = spring(t / entrance)
    image = frames[round(t * 12) % len(frames)]
    sz = max(1, round(420 * scale * active)), max(1, round(480 * scale * active))
    im = image.resize(sz, Image.Resampling.BICUBIC)
    frame.alpha_composite(im, (round(x - sz[0] / 2), round(y - sz[1] / 2)))


def comic_top(frame: Image.Image, index: int, actual: bool = False) -> None:
    d = ImageDraw.Draw(frame)
    box(d, (28, 22, 225, 62), INK, r=15)
    text(d, (47, 29), "BINWISE / 2026", 19, "#FFFFFF", True)
    label = "APP CAPTURE" if actual else "ANIMATED EXPLAINER"
    width = 172 if actual else 246
    box(d, (W - width - 28, 22, W - 28, 62), "#FFFFFF", INK, r=15, width=2)
    text(d, (W - width - 13, 30), label, 17, INK, True)
    # Small segments provide a sense of progress without a static slide number.
    for i in range(12):
        box(d, (28 + i * 25, 76, 46 + i * 25, 83),
            YELLOW if i <= index else "#E0EAE2", r=3)


def caption(frame: Image.Image, index: int, t: float) -> None:
    d = ImageDraw.Draw(frame)
    box(d, (32, 626, 1248, 704), INK, r=23)
    alpha = ease(t / 0.32)
    x = round(61 + (1 - alpha) * 45)
    text(d, (x, 642), CAPTIONS[index], 28, "#FFFFFF", True)


def burst(frame: Image.Image, cx: int, cy: int, t: float, color: str,
          count: int = 18, radius: int = 230) -> None:
    d = ImageDraw.Draw(frame)
    for i in range(count):
        a = 2 * math.pi * i / count + t * 0.05
        inner = radius * 0.52
        outer = radius * (0.85 + 0.08 * math.sin(t * 4 + i))
        d.line((cx + inner * math.cos(a), cy + inner * math.sin(a),
                cx + outer * math.cos(a), cy + outer * math.sin(a)),
               fill=color, width=5 if i % 2 else 3)


def draw_scene(index: int, t: float, duration: float, assets: dict,
               chrome: bool = True, wipe: bool = True) -> Image.Image:
    p = t / duration
    if index in (0, 10, 11):
        frame = assets["scenes"][{0: 0, 10: 1, 11: 2}[index]].copy()
    else:
        frame = assets["backgrounds"][index].copy()
    d = ImageDraw.Draw(frame)

    if index == 0:
        panel(frame, (610, 111, 1230, 580), CREAM)
        burst_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        burst(burst_layer, 1024, 420, t, YELLOW, radius=225)
        frame.alpha_composite(burst_layer.crop((618, 119, 1221, 571)), (618, 119))
        text(d, (650, 149), "WAIT...", 70, INK, True)
        text(d, (650, 233), "WHICH BIN?!", 62, CORAL, True, stroke=2)
        box(d, (649, 337, 918, 408), YELLOW, INK, r=26)
        text(d, (673, 351), "PLOT TWIST:", 30, INK, True)
        paste_char(frame, assets["bottle"], t, 1088, 454, 0.55)
        text(d, (659, 453), "The bottle is", 25, INK, True)
        text(d, (659, 483), "panicking.", 25, INK, True)
    elif index == 1:
        text(d, (65, 146), "SNAP.", 98, INK, True)
        text(d, (73, 266), "One clear item.", 40, GREEN, True)
        text(d, (76, 329), "No rubbish group selfies.", 28, INK)
        panel(frame, (710, 108, 1190, 590), "#FFFFFF")
        shot = assets["home"]
        frame.alpha_composite(shot, (741 + round(5 * math.sin(t * 0.9)), 129))
    elif index == 2:
        panel(frame, (80, 133, 705, 573), "#FFFFFF")
        d.rounded_rectangle((111, 160, 674, 511), radius=20, fill="#7D928D")
        # A blurred photo jiggles in the viewfinder.
        for k, (cx, cy, r) in enumerate(((245, 305, 105), (390, 360, 115), (520, 275, 92))):
            dx = round(8 * math.sin(6*t+k))
            d.ellipse((cx-r+dx,cy-r,cx+r+dx,cy+r),fill="#B5BDB3")
        text(d, (765, 170), "BLURRY?", 68, INK, True)
        text(d, (765, 249), "RETAKE!", 68, CORAL, True)
        box(d, (774, 377, 1170, 478), YELLOW, INK, r=22)
        text(d, (801, 391), "EVEN AI NEEDS", 27, INK, True)
        text(d, (801, 426), "GLASSES.", 27, INK, True)
        if int(t * 5) % 2 == 0:
            d.line((100, 139, 683, 563), fill=CORAL, width=9)
            d.line((683, 139, 100, 563), fill=CORAL, width=9)
    elif index == 3:
        panel(frame, (71, 111, 654, 586), "#FFFFFF")
        frame.alpha_composite(assets["result"], (92, 131))
        text(d, (704, 131), "CARDBOARD!", 56, INK, True)
        text(d, (712, 217), "Photo suggestion", 28, GREEN, True)
        box(d, (706, 298, 1209, 369), "#FFFFFF", GREEN, r=19)
        text(d, (733, 316), "1  CHECK CLEAN", 29, GREEN, True)
        box(d, (706, 390, 1209, 468), YELLOW, INK, r=19)
        text(d, (733, 408), "2  DRY WASTE GUIDE", 28, INK, True)
        # Hand-drawn pulsing arrow between steps.
        yy = 369 + round(8 * abs(math.sin(t*5)))
        d.line((960, yy, 960, 389), fill=GREEN, width=7)
        d.polygon(((949,383),(971,383),(960,399)), fill=GREEN)
        text(d, (725, 520), "Actual app result / dataset photo", 21, "#5A7568")
    elif index == 4:
        text(d, (72, 126), "THE APP SAYS:", 34, GREEN, True)
        text(d, (72, 187), "'I'M NOT SURE.'", 66, INK, True)
        paste_char(frame, assets["bottle"], t, 271, 451, 0.7)
        panel(frame, (603, 137, 1215, 551), "#FFFFFF")
        text(d, (649, 177), "YOU choose the material", 31, INK, True)
        box(d, (650, 259, 917, 331), "#D8F2DF", GREEN, r=19)
        text(d, (684, 275), "Cardboard", 29, GREEN, True)
        box(d, (935, 259, 1177, 331), "#F1F3EC", "#B5C9B8", r=19)
        text(d, (952, 276), "Something else", 24, INK, True)
        box(d, (649, 374, 1178, 446), "#FCE0DC", CORAL, r=19)
        text(d, (682, 390), "NO CONFIDENT GUESS = NO BIN", 24, "#8D3E36", True)
        for k in range(3):
            text(d, (80 + k*75, 337 + round(12*math.sin(t*3+k))), "?", 50, CORAL, True)
    elif index == 5:
        text(d, (72, 122), "CAMERA OFF?", 64, INK, True)
        text(d, (73, 207), "TYPE IT.", 74, GREEN, True)
        panel(frame, (595, 147, 1194, 554), "#FFFFFF")
        text(d, (636, 180), "What is your item?", 26, INK, True)
        box(d, (632, 238, 1153, 313), "#F3F8F0", "#B6D3BD", r=15)
        typed = "plastic bottle"[:max(0, min(14, round((t-0.4)*5)))]
        text(d, (660, 250), typed + ("|" if int(t*3)%2 else ""), 32, INK)
        for k, (label, xx, yy) in enumerate((("Plastic bottle",638,351), ("Cardboard",896,351),
                                              ("Food scraps",638,434), ("Battery",896,434))):
            pop = spring((t-1.1-k*0.18)/0.35)
            if pop > 0.1:
                box(d, (xx, yy, xx+239, yy+60), YELLOW if k == 0 else "#E2F4E7", GREEN, r=16)
                text(d, (xx+17, yy+13), label, 23, INK, True)
        box(d, (73, 372, 493, 463), YELLOW, INK, r=25)
        text(d, (103, 391), "NO PHOTO SENT", 31, INK, True)
    elif index == 6:
        burst(frame, 365, 370, t, CORAL, 22, 330)
        paste_char(frame, assets["battery"], t, 333, 380, 0.9)
        panel(frame, (684, 113, 1216, 555), "#FFFFFF")
        text(d, (726, 158), "I'M SPECIAL!", 59, INK, True)
        text(d, (733, 238), "said the battery.", 28, "#6D7765")
        box(d, (725, 333, 1171, 411), YELLOW, INK, r=22)
        text(d, (747, 350), "SPECIAL-CARE WASTE", 27, INK, True)
        box(d, (725, 442, 1171, 497), "#FCE2DD", CORAL, r=17)
        text(d, (747, 451), "NOT a regular bin guest", 25, "#8C3F37", True)
    elif index == 7:
        text(d, (70, 139), "HINDI?", 74, INK, True)
        text(d, (74, 232), "YES!", 87, GREEN, True)
        text(d, (79, 343), "Press Read advice aloud.", 31, INK)
        panel(frame, (700, 108, 1208, 582), "#FFFFFF")
        frame.alpha_composite(assets["hindi"], (723, 130))
        for j in range(6):
            height = 16 + round(29 * abs(math.sin(t*6+j*0.7)))
            d.rounded_rectangle((90+j*37, 453-height, 111+j*37, 453+height),
                                radius=8, fill=GREEN)
        text(d, (79, 513), "Actual app capture", 21, GREEN, True)
    elif index == 8:
        text(d, (74, 131), "SCAN. SHARE.", 68, "#FFFFFF", True)
        text(d, (79, 222), "SOURCED GUIDE.", 49, YELLOW, True)
        panel(frame, (769, 111, 1188, 561), "#FFFFFF")
        qr = assets["qr"]
        frame.alpha_composite(qr, (824, 155))
        scan_y = 166 + round(310*((t*0.47)%1))
        d.line((832, scan_y, 1127, scan_y), fill=CORAL, width=7)
        text(d, (813, 490), "ILLUSTRATED QR", 23, GREEN, True)
        box(d, (79, 365, 641, 461), YELLOW, INK, r=24)
        text(d, (110, 383), "REACHABLE LINK", 34, INK, True)
        text(d, (110, 421), "REQUIRED", 29, INK, True)
        text(d, (84, 529), "Use a shared app URL for another phone.", 26, "#FFFFFF")
    elif index == 9:
        text(d, (74, 124), "UH-OH.", 84, CORAL, True)
        text(d, (79, 219), "SPOT A MISTAKE?", 52, INK, True)
        panel(frame, (562, 145, 1188, 552), "#FFFFFF")
        text(d, (603, 183), "Was this advice correct?", 32, INK, True)
        for k, label in enumerate(("Yes, correct", "Wrong material", "Local rule differs")):
            yy = 262 + 82*k
            box(d, (603, yy, 1147, yy+64), YELLOW if k == int(t*0.7)%3 else "#E7F5E9",
                GREEN, r=17)
            text(d, (629, yy+11), label, 27, INK, True)
        text(d, (74, 411), "No photo or name", 31, GREEN, True)
        text(d, (74, 449), "stored with feedback.", 31, GREEN, True)
        for k in range(18):
            xx = 30+(k*71)%510
            yy = 100+((k*43+round(t*70))%490)
            d.ellipse((xx,yy,xx+7,yy+7), fill=CORAL if k%2 else YELLOW)
    elif index == 10:
        panel(frame, (639, 107, 1222, 563), CREAM)
        text(d, (678, 146), "LOCAL RULES", 52, INK, True)
        text(d, (679, 215), "GET THE LAST WORD.", 34, GREEN, True)
        box(d, (675, 307, 910, 372), "#D8F2DF", GREEN, r=19)
        text(d, (700, 324), "INDIA GUIDE", 25, GREEN, True)
        box(d, (925, 307, 1190, 372), "#FFEBBE", "#B78937", r=19)
        text(d, (943, 325), "SAMPLE SITE", 24, "#885C25", True)
        text(d, (684, 434), "Check your actual collection signs.", 25, INK)
        paste_char(frame, assets["bottle"], t, 492, 491, 0.27)
    else:
        panel(frame, (600, 103, 1235, 570), CREAM)
        text(d, (650, 137), "BINWISE", 92, INK, True)
        text(d, (656, 258), "KNOW WHERE", 43, GREEN, True)
        text(d, (656, 313), "IT GOES.", 47, GREEN, True)
        paste_char(frame, assets["bottle"], t, 1033, 453, 0.39)
        paste_char(frame, assets["battery"], max(0,t-0.2), 1160, 453, 0.36)
        if p > 0.4:
            for k in range(24):
                x = round(650+(k*37)%550)
                y = round(130+((k*59+int(t*80))%410))
                if y < 480:
                    d.rectangle((x,y,x+9,y+17),fill=CORAL if k%3 else YELLOW)
        box(d, (649, 492, 980, 543), "#FFFFFF", GREEN, r=13, width=2)
        text(d, (667, 501), "Created by Hridya Jain", 21, INK, True)

    if chrome:
        comic_top(frame, index, actual=index in (1, 3, 7))
        caption(frame, index, t)
    if wipe:
        # Preserve the earlier short tour's panel wipe.
        enter = 1-ease(t/0.28)
        leave = ease((t-(duration-0.22))/0.22)
        width = round(W*max(enter, leave))
        if width:
            d = ImageDraw.Draw(frame)
            d.polygon(((W-width,0),(W,0),(W,H),(W-width-110,H)), fill=YELLOW)
            for k in range(5):
                xx = W-width+40+k*30
                d.line((xx,0,xx-110,H),fill=INK,width=4)
    return frame.convert("RGB")


def make_qr_illustration() -> Image.Image:
    im = Image.new("RGBA", (305, 305), (255, 255, 255, 255))
    d = ImageDraw.Draw(im)
    cell = 17
    for row in range(17):
        for col in range(17):
            finder = ((row < 5 and col < 5) or (row < 5 and col > 11)
                      or (row > 11 and col < 5))
            on = finder and (row in (0,4,12,16) or col in (0,4,12,16)
                             or 1 < row%12 < 4 and 1 < col%12 < 4)
            on |= not finder and (row*7 + col*13 + row*col) % 7 < 3
            if on:
                x,y = 8+col*cell,8+row*cell
                d.rectangle((x,y,x+14,y+14),fill=INK)
    return im


def load_assets() -> dict:
    bottle = character_frames("bottle-character-v2.png", "bottle-bounce-v2.gif", 390)
    battery = character_frames("battery-character-v2.png", "battery-diva-v2.gif", 390)
    return {
        "bottle": bottle,
        "battery": battery,
        "scenes": [cover(MEDIA / f"scene-{i}.png") for i in (1,2,3)],
        "backgrounds": {
            i: flat_bg(*{
                1:("#DEF5E9","#C2E8D3"),2:("#FFE7A6","#F7D184"),
                3:("#E7F3E9","#CFE9D8"),4:("#E9EAF8","#D0D5EE"),
                5:("#FFF3DC","#F6DBAF"),6:("#FFD6B8","#F7B293"),
                7:("#E4F4EB","#CAEBDA"),8:("#124B42","#1C6759"),
                9:("#E1F7DE","#C3E9C4")}[i]) for i in range(1,10)},
        "home": screenshot("app-home-polished.png", (63, 20, 654, 712), (413, 434)),
        "result": screenshot("app-result-polished.png", (623, 55, 1210, 683), (540, 435)),
        "hindi": screenshot("app-hindi-prep-polished.png", (620, 0, 1210, 682), (463, 430)),
        "qr": make_qr_illustration(),
    }


def load_voice() -> tuple[list[float], list[np.ndarray], int]:
    parts, rate = [], 0
    for i in range(12):
        with wave.open(str(VOICE / f"voice-{i:02d}.wav"), "rb") as wav:
            assert wav.getnchannels()==1 and wav.getsampwidth()==2
            rate = wav.getframerate()
            parts.append(np.frombuffer(wav.readframes(wav.getnframes()),dtype="<i2").astype(np.float32)/32768)
    return [len(p)/rate+0.72 for p in parts], parts, rate


def add_sound(mix: np.ndarray, rate: int, start: float, kind: str) -> None:
    ix = round(start*rate)
    length = min(round(0.35*rate), len(mix)-ix)
    if length <= 0:
        return
    tt = np.arange(length,dtype=np.float32)/rate
    env = np.exp(-13*tt)
    if kind == "boing":
        sound = np.sin(2*np.pi*(220*tt+520*tt*tt))*env*0.10
    elif kind == "buzz":
        sound = np.sin(2*np.pi*105*tt)*np.sign(np.sin(2*np.pi*35*tt))*env*0.075
    elif kind == "click":
        sound = np.random.default_rng(4).normal(0,1,length).astype(np.float32)*np.exp(-70*tt)*0.11
    elif kind == "ding":
        sound = (np.sin(2*np.pi*660*tt)+0.4*np.sin(2*np.pi*990*tt))*env*0.055
    else:
        sound = np.sin(2*np.pi*(300*tt+1200*tt*tt))*env*0.08
    mix[ix:ix+length] += sound


def audio_track(durations: list[float], voices: list[np.ndarray], rate: int) -> Path:
    total = sum(durations)
    n = round(total*rate)
    mix = np.zeros(n,dtype=np.float32)
    beat = 0.47
    bass_notes = (130.81, 164.81, 196.0, 164.81, 146.83, 174.61, 220.0, 196.0)
    rng = np.random.default_rng(2026)
    for b,start in enumerate(np.arange(0,total,beat)):
        ix = round(start*rate)
        count = min(round(beat*rate), n-ix)
        tt = np.arange(count,dtype=np.float32)/rate
        f = bass_notes[(b//2)%len(bass_notes)]
        bass = (np.sin(2*np.pi*f*tt)+0.25*np.sin(4*np.pi*f*tt))*np.exp(-7*tt)
        mix[ix:ix+count] += 0.026*bass
        if b%2==0:
            kick = np.sin(2*np.pi*(78-35*tt)*tt)*np.exp(-28*tt)
            mix[ix:ix+count] += 0.035*kick
        hat = rng.normal(0,1,count).astype(np.float32)*np.exp(-55*tt)
        mix[ix:ix+count] += 0.012*hat
    kinds = ["boing","click","buzz","ding","boing","click","buzz","ding","click","ding","boing","ding"]
    cursor=0.0
    for i,voice in enumerate(voices):
        start=round((cursor+0.19)*rate)
        mix[start:start+len(voice)] += voice*0.76
        add_sound(mix,rate,cursor+0.02,kinds[i])
        if i in (1,5,9):
            for j in range(3):
                add_sound(mix,rate,cursor+1.0+j*0.23,"click")
        cursor += durations[i]
    clock=np.arange(n,dtype=np.float32)/rate
    fade=np.minimum(1,clock/0.28)*np.minimum(1,(total-clock)/0.7)
    pcm=(np.clip(mix*fade,-0.98,0.98)*32767).astype("<i2")
    path=ROOT.parent.parent/"work"/"comic-tour-audio.wav"
    with wave.open(str(path),"wb") as wav:
        wav.setnchannels(1); wav.setsampwidth(2); wav.setframerate(rate); wav.writeframes(pcm.tobytes())
    return path


def main() -> None:
    durations, voices, rate = load_voice()
    assets=load_assets()
    audio=audio_track(durations,voices,rate)
    draw_scene(0,2.1,durations[0],assets).save(MEDIA/"binwise-comic-tour-poster.png")
    ffmpeg=imageio_ffmpeg.get_ffmpeg_exe()
    cmd=[ffmpeg,"-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24",
         "-s",f"{W}x{H}","-r",str(FPS),"-i","-","-i",str(audio),
         "-c:v","libx264","-preset","veryfast","-crf","20","-pix_fmt","yuv420p",
         "-c:a","aac","-b:a","128k","-shortest",str(OUT)]
    process=subprocess.Popen(cmd,stdin=subprocess.PIPE)
    try:
        assert process.stdin is not None
        for i,duration in enumerate(durations):
            for n in range(round(duration*FPS)):
                process.stdin.write(draw_scene(i,n/FPS,duration,assets).tobytes())
            print(f"Scene {i+1}/12 complete",flush=True)
        process.stdin.close()
        if process.wait()!=0:
            raise RuntimeError("FFmpeg failed")
    finally:
        if process.poll() is None:
            process.kill()
    print(f"Saved {OUT} ({sum(durations):.1f}s)")


if __name__=="__main__":
    main()
