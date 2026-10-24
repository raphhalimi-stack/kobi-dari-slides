#!/usr/bin/env python3
"""Rend les reels Kobi/Dari (1080x1920, 30 fps, H.264 + AAC) au design des carrousels.
Usage : python reels/render.py [kobi|dari] [id]  (sans argument : tout)"""
import json, math, os, subprocess, sys, wave
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

ROOT = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(ROOT)
OUT = os.path.join(ROOT, "out")
W, H, FPS = 1080, 1920, 30
INTER = "/usr/share/fonts/opentype/inter/Inter-{}.otf"
SERIF_IT = "/usr/share/fonts/type1/gsfonts/../../X11/Type1/c0649bt_.pfb"
CJK = "/usr/share/fonts/opentype/noto/NotoSansCJK-{}.ttc"


def font(kind, size):
    if kind == "serif":
        for p in ["/usr/share/fonts/X11/Type1/c0649bt_.pfb",
                  "/usr/share/fonts/truetype/crosextra/Caladea-Italic.ttf",
                  "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"]:
            if os.path.exists(p):
                return ImageFont.truetype(p, size)
    if kind.startswith("cjk"):
        return ImageFont.truetype(CJK.format(kind.split(":")[1]), size, index=1)  # KR
    return ImageFont.truetype(INTER.format(kind), size)


THEMES = {
    "kobi": dict(bg=(24, 20, 21), glow=(70, 52, 54), accent=(235, 201, 198), num=(235, 201, 198),
                 alt=(205, 226, 214), text=(245, 241, 236), sub=(165, 158, 156), desc=(214, 208, 204), handle="@kobiapp.cc",
                 site="kobiapp.cc", logo=("slides/kobi/06_korean_label/01.jpg", (78, 78, 146, 146))),
    "dari": dict(bg=(10, 18, 36), glow=(10, 42, 90), accent=(143, 180, 240), num=(242, 207, 158),
                 alt=(143, 180, 240), text=(244, 246, 250), sub=(150, 163, 186), desc=(200, 210, 228), handle="@dariapp.cc",
                 site="dariapp.cc", logo=("slides/dari/06_taxi/01.jpg", (78, 84, 162, 128))),
}
M = 96  # marge gauche


def background(t):
    img = Image.new("RGB", (W, H), t["bg"])
    glow = Image.new("RGB", (W, H), t["bg"])
    d = ImageDraw.Draw(glow)
    d.ellipse((W * 0.35, -H * 0.05, W * 1.45, H * 0.55), fill=t["glow"])
    glow = glow.filter(ImageFilter.GaussianBlur(260))
    img = Image.blend(img, glow, 0.85)
    return img


def wrap(draw, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        test = (cur + " " + w_).strip()
        if draw.textlength(test, font=f) <= maxw or not cur:
            cur = test
        else:
            lines.append(cur); cur = w_
    if cur:
        lines.append(cur)
    return lines


def ease(x):
    x = max(0.0, min(1.0, x))
    return 1 - (1 - x) ** 3


class Layer:
    """Un élément texte avec apparition (fondu + montée)."""
    def __init__(self, img, x, y, start):
        self.img, self.x, self.y, self.start = img, x, y, start


def text_img(lines, f, color, spacing=1.12):
    asc, desc = f.getmetrics()
    lh = int((asc + desc) * spacing)
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    wmax = max(int(tmp.textlength(l, font=f)) for l in lines) + 20
    im = Image.new("RGBA", (wmax, lh * len(lines) + desc), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for i, l in enumerate(lines):
        d.text((0, i * lh), l, font=f, fill=color)
    return im


def has_hangul(s):
    return any("가" <= c <= "힣" for c in s)


def build_scenes(acc, s, t):
    """Retourne une liste de scènes : (durée, [Layer], label_progress)."""
    tmp = ImageDraw.Draw(Image.new("L", (1, 1)))
    maxw = W - 2 * M - 40
    scenes = []
    # 1. Accroche (visible dès la frame 0)
    fk = font("serif", 84)
    fh = font("Bold", 118)
    kick = text_img(wrap(tmp, s["kicker"], fk, maxw), fk, t["accent"])
    hook_lines = wrap(tmp, s["hook"], fh, maxw)
    hook = text_img(hook_lines, fh, t["text"], 1.08)
    y0 = 620
    layers = [Layer(kick, M, y0, -1), Layer(hook, M, y0 + kick.height + 24, -1)]
    scenes.append((2.6, layers, None))
    n = len(s["points"])
    for i, (tag, title, desc) in enumerate(s["points"]):
        if has_hangul(tag):
            ft = font("cjk:Bold", 104); tagc = t["alt"]
        elif tag in ("Avoid", "Safe"):
            ft = font("serif", 110); tagc = (236, 128, 128) if tag == "Avoid" else (150, 214, 168)
        else:
            ft = font("serif", 150); tagc = t["num"]
        tag_im = text_img([tag], ft, tagc)
        fti = font("Bold", 92 if len(title) < 18 else 76)
        ti = text_img(wrap(tmp, title, fti, maxw), fti, t["text"], 1.08)
        fd = font("Regular", 60)
        de = text_img(wrap(tmp, desc, fd, maxw), fd, t["desc"], 1.3)
        y = 640
        rule = Image.new("RGBA", (88, 6), t["accent"] + (255,))
        ly = [Layer(tag_im, M, y, 0.0)]
        y += tag_im.height + 30
        ly.append(Layer(ti, M, y, 0.12)); y += ti.height + 34
        ly.append(Layer(rule, M + 2, y, 0.22)); y += 6 + 40
        ly.append(Layer(de, M, y, 0.3))
        scenes.append((2.3 if len(desc) < 40 else 2.6, ly, (i + 1, n)))
    if s.get("rule"):
        fr = font("Bold", 96)
        r = text_img(wrap(tmp, s["rule"], fr, maxw), fr, t["accent"], 1.1)
        scenes.append((2.0, [Layer(r, M, 780, 0.0)], None))
    # CTA
    fc = font("Bold", 92)
    cta = text_img(wrap(tmp, s["cta"], fc, maxw), fc, t["text"], 1.1)
    fs = font("serif", 64)
    tag = text_img(["Launching 25 Nov · link in bio"], fs, t["accent"])
    fhd = font("SemiBold", 60)
    hd = text_img([t["handle"]], fhd, t["sub"])
    scenes.append((3.0, [Layer(cta, M, 640, 0.0), Layer(tag, M, 640 + cta.height + 50, 0.25),
                         Layer(hd, M, 640 + cta.height + 50 + tag.height + 30, 0.4)], None))
    return scenes


def chrome(base, t, logo, prog):
    """Logo en haut, site en bas, barre de progression."""
    img = base.copy()
    img.paste(logo, (M, 150), logo if logo.mode == "RGBA" else None)
    d = ImageDraw.Draw(img)
    f = font("Regular", 40)
    if prog:
        i, n = prog
        label = f"{i} / {n}"
        d.text((W - M - d.textlength(label, font=f), 162), label, font=f, fill=t["sub"])
    return img


def render(acc, s):
    t = THEMES[acc]
    os.makedirs(OUT, exist_ok=True)
    base = background(t)
    lp, box = t["logo"]
    logo = Image.open(os.path.join(REPO, lp)).crop(box)
    logo = logo.resize((int(logo.width * 1.5), int(logo.height * 1.5)), Image.LANCZOS)
    scenes = build_scenes(acc, s, t)
    total = sum(d for d, _, _ in scenes)
    nframes = int(total * FPS)
    vid = os.path.join(OUT, f"{acc}_{s['id']}.mp4")
    wav = os.path.join(OUT, f"{acc}_{s['id']}.wav")
    cuts = []
    acc_t = 0
    for d, _, _ in scenes:
        cuts.append(acc_t); acc_t += d
    make_audio(wav, total, cuts)
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
                           "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-", "-i", wav,
                           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
                           "-profile:v", "high", "-c:a", "aac", "-b:a", "128k", "-ar", "44100",
                           "-movflags", "+faststart", "-shortest", vid], stdin=subprocess.PIPE)
    fi = 0
    for si, (dur, layers, prog) in enumerate(scenes):
        frame_base = chrome(base, t, logo, prog)
        sf = int(round(dur * FPS))
        for k in range(sf):
            tt = k / FPS
            img = frame_base.copy()
            for L in layers:
                if L.start < 0:
                    a, dy = 1.0, 0
                    # légère respiration sur l'accroche
                else:
                    p = ease((tt - L.start) / 0.35)
                    a, dy = p, int((1 - p) * 40)
                if a <= 0:
                    continue
                im = L.img
                if a < 1:
                    im = im.copy()
                    alpha = im.getchannel("A").point(lambda v, a=a: int(v * a))
                    im.putalpha(alpha)
                img.paste(im, (L.x, L.y + dy), im)
            # fondu de sortie sur les 4 dernières frames (sauf la dernière scène : boucle)
            if k >= sf - 4 and si < len(scenes) - 1:
                img = Image.blend(img, frame_base, (k - (sf - 4) + 1) / 5)
            ff.stdin.write(img.tobytes())
            fi += 1
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    # couverture (frame de l'accroche)
    cover = chrome(base, t, logo, None)
    for L in scenes[0][1]:
        cover.paste(L.img, (L.x, L.y), L.img)
    cover.save(os.path.join(OUT, f"{acc}_{s['id']}_cover.jpg"), quality=92)
    return vid, total


def make_audio(path, dur, cuts, sr=44100):
    """Nappe douce originale (accords lents) + petit 'tick' à chaque changement de scène."""
    n = int(dur * sr) + sr
    tt = np.arange(n) / sr
    chords = [[220.0, 277.18, 329.63, 440.0], [196.0, 246.94, 293.66, 392.0],
              [174.61, 220.0, 261.63, 349.23], [196.0, 246.94, 329.63, 392.0]]
    out = np.zeros(n)
    seg = 2.4
    for ci in range(int(dur / seg) + 2):
        ch = chords[ci % len(chords)]
        s0 = int(ci * seg * sr)
        L = int((seg + 1.2) * sr)
        e = min(n, s0 + L)
        if s0 >= n:
            break
        x = np.arange(e - s0) / sr
        env = np.minimum(1, x / 0.6) * np.exp(-np.maximum(0, x - seg) * 3)
        tone = sum(np.sin(2 * np.pi * f * x) * (0.5 if i else 0.7) for i, f in enumerate(ch))
        tone += 0.15 * sum(np.sin(2 * np.pi * f * 2 * x) for f in ch)
        out[s0:e] += tone * env * 0.06
    # pulsation légère
    beat = 60 / 96
    for b in np.arange(0, dur, beat):
        s0 = int(b * sr); e = min(n, s0 + int(0.12 * sr))
        x = np.arange(e - s0) / sr
        out[s0:e] += np.sin(2 * np.pi * 70 * x) * np.exp(-x * 40) * 0.18
    for c in cuts[1:]:
        s0 = int(c * sr); e = min(n, s0 + int(0.08 * sr))
        x = np.arange(e - s0) / sr
        out[s0:e] += np.sin(2 * np.pi * 1760 * x) * np.exp(-x * 60) * 0.12
    out = out[: int(dur * sr)]
    fade = int(0.4 * sr)
    out[-fade:] *= np.linspace(1, 0, fade)
    out = out / max(1e-6, np.abs(out).max()) * 0.6
    st = np.stack([out, out], 1)
    data = (st * 32767).astype(np.int16)
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr); w.writeframes(data.tobytes())


if __name__ == "__main__":
    scripts = json.load(open(os.path.join(ROOT, "scripts.json"), encoding="utf-8"))
    accs = [sys.argv[1]] if len(sys.argv) > 1 else ["kobi", "dari"]
    for acc in accs:
        for s in scripts[acc]:
            if len(sys.argv) > 2 and s["id"] != sys.argv[2]:
                continue
            v, d = render(acc, s)
            print(f"{v}  {d:.1f}s  {os.path.getsize(v)//1024} KB")
