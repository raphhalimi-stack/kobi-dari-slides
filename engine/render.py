#!/usr/bin/env python3
"""Moteur de rendu v2 : carrousels (1080x1350 JPEG) et reels (1080x1920 MP4) via Chromium.
Usage :
  python engine/render.py carousels [kobi|dari] [deck]
  python engine/render.py reels [kobi|dari] [id]
  python engine/render.py stories
"""
import base64, io, json, math, os, re, subprocess, sys, wave
import numpy as np
from PIL import Image
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENG = os.path.join(ROOT, "engine")
OUTC = os.path.join(ROOT, "v2", "carousels")
OUTR = os.path.join(ROOT, "v2", "reels")
FPS = 30
SITES = {"kobi": "kobiapp.cc", "dari": "dariapp.cc"}


def grain_url():
    rng = np.random.default_rng(7)
    n = (rng.random((256, 256)) * 255).astype(np.uint8)
    im = Image.fromarray(n, "L").convert("RGB")
    b = io.BytesIO(); im.save(b, "PNG")
    return "data:image/png;base64," + base64.b64encode(b.getvalue()).decode()


class Engine:
    def __init__(self):
        self.pw = sync_playwright().start()
        self.br = self.pw.chromium.launch(args=["--force-color-profile=srgb", "--font-render-hinting=none"])
        self.grain = grain_url()

    def page(self, acc, w, h):
        pg = self.br.new_page(viewport={"width": w, "height": h}, device_scale_factor=1)
        pg.goto("file://" + os.path.join(ENG, "page.html"))
        pg.evaluate("document.fonts.ready")
        pg.evaluate("o=>setup(o)", {"acc": acc, "w": w, "h": h, "grain": self.grain, "site": SITES[acc]})
        pg.wait_for_timeout(150)
        return pg

    def shot(self, pg, w, h, q=92):
        return pg.screenshot(type="jpeg", quality=q, clip={"x": 0, "y": 0, "width": w, "height": h})

    def close(self):
        self.br.close(); self.pw.stop()


# ------------------------------------------------------------------ carrousels
def render_carousels(eng, acc, only=None):
    data = json.load(open(os.path.join(ROOT, "content/carousels.json"), encoding="utf-8"))[acc]
    pg = eng.page(acc, 1080, 1350)
    for deck in data:
        if only and deck["id"] != only:
            continue
        d = os.path.join(OUTC, acc, deck["id"]); os.makedirs(d, exist_ok=True)
        specs = [dict(type="cover", swipe=True, **deck["cover"])]
        specs += [dict(type="slide", **s) for s in deck["slides"]]
        specs.append(dict(type="end", **deck["end"]))
        for i, sp in enumerate(specs, 1):
            pg.evaluate("s=>setScene(s,'carousel')", sp)
            pg.evaluate("frame(30,99,true,null)")
            pg.wait_for_timeout(30)
            open(os.path.join(d, f"{i:02d}.jpg"), "wb").write(eng.shot(pg, 1080, 1350, 95))
        print("carousel", acc, deck["id"], len(specs))
    pg.close()


# ------------------------------------------------------------------ reels
def read_wav(p):
    with wave.open(p) as w:
        sr = w.getframerate(); n = w.getnframes(); ch = w.getnchannels(); sw = w.getsampwidth()
        raw = w.readframes(n)
    if sw == 2:
        a = np.frombuffer(raw, np.int16).astype(np.float32) / 32768
    else:
        a = np.frombuffer(raw, np.float32) if sw == 4 else np.frombuffer(raw, np.int16) / 32768
    if ch > 1:
        a = a.reshape(-1, ch).mean(1)
    return a, sr


def resample(a, sr, to=44100):
    if sr == to:
        return a
    x = np.linspace(0, len(a) - 1, int(len(a) * to / sr))
    return np.interp(x, np.arange(len(a)), a)


def music_bed(dur, sr=44100, mood="warm"):
    n = int(dur * sr); t = np.arange(n) / sr
    chords = ([[220.0, 277.18, 329.63], [196.0, 246.94, 293.66], [174.61, 220.0, 261.63], [196.0, 246.94, 329.63]]
              if mood == "warm" else
              [[196.0, 246.94, 293.66], [164.81, 207.65, 246.94], [174.61, 220.0, 261.63], [146.83, 185.0, 220.0]])
    out = np.zeros(n); seg = 2.6
    for ci in range(int(dur / seg) + 2):
        s0 = int(ci * seg * sr)
        if s0 >= n:
            break
        e = min(n, s0 + int((seg + 1.5) * sr)); x = np.arange(e - s0) / sr
        env = np.minimum(1, x / 0.8) * np.exp(-np.maximum(0, x - seg) * 2.5)
        tone = sum(np.sin(2 * np.pi * f * x) + 0.25 * np.sin(2 * np.pi * f * 2.001 * x) for f in chords[ci % 4])
        out[s0:e] += tone * env
    # pulsation douce
    beat = 60 / 92
    for b in np.arange(0, dur, beat):
        s0 = int(b * sr); e = min(n, s0 + int(0.18 * sr)); x = np.arange(e - s0) / sr
        out[s0:e] += np.sin(2 * np.pi * 62 * x) * np.exp(-x * 22) * 1.6
    for b in np.arange(beat / 2, dur, beat):
        s0 = int(b * sr); e = min(n, s0 + int(0.05 * sr)); x = np.arange(e - s0) / sr
        out[s0:e] += (np.random.default_rng(int(b * 100)).random(e - s0) - .5) * np.exp(-x * 90) * 0.5
    out /= max(1e-6, np.abs(out).max())
    f = int(0.8 * sr); out[:f] *= np.linspace(0, 1, f); out[-f:] *= np.linspace(1, 0, f)
    return out


def merge_letters(words):
    out = []
    for w in words:
        core = w.rstrip(".,?!")
        prev = out[-1] if out else ""
        ok_prev = prev.isalpha() and prev.isupper() and len(prev) <= 3 and prev not in ("I",)
        if len(core) == 1 and core.isupper() and ok_prev and (core != "A" or (len(prev) <= 2 and prev != "A")):
            out[-1] = prev + w
        else:
            out.append(w)
    return out


def word_times(say, start, dur):
    words = merge_letters(say.split())
    w = np.array([len(re.sub(r"[^\w]", "", x)) + 2.5 for x in words], float)
    pos = np.concatenate([[0], np.cumsum(w)]) / w.sum()
    return [(words[i], start + pos[i] * dur, start + pos[i + 1] * dur) for i in range(len(words))]


def chunks(words, maxn=4):
    out, cur = [], []
    for i, wd in enumerate(words):
        cur.append(i)
        if len(cur) >= maxn or wd[0].endswith((".", ",", "?", "!")):
            out.append(cur); cur = []
    if cur:
        out.append(cur)
    return out


def render_reel(eng, acc, reel, durs, voice_dir):
    os.makedirs(OUTR, exist_ok=True)
    sr = 44100
    lead = 0.15
    scenes = reel["scenes"]
    sdur = [max(1.9, d + lead + 0.45) for d in durs]
    sdur[-1] += 0.6
    total = sum(sdur)
    # audio : voix + nappe
    voice = np.zeros(int(total * sr) + sr)
    t0 = 0
    for i, d in enumerate(sdur):
        a, s = read_wav(os.path.join(voice_dir, f"{i:02d}.wav"))
        a = resample(a, s, sr)
        st = int((t0 + lead) * sr); voice[st:st + len(a)] += a[: len(voice) - st]
        t0 += d
    voice = voice[: int(total * sr)]
    voice /= max(1e-6, np.abs(voice).max()); voice *= 0.92
    bed = music_bed(total, sr, "warm" if acc == "kobi" else "cool")
    # ducking : la musique baisse sous la voix
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    duck = 1 - 0.55 * np.clip(env / 0.05, 0, 1)
    mix = voice + bed * 0.16 * duck
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.95
    wav = os.path.join(OUTR, f"{acc}_{reel['id']}.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(sr)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    mp4 = os.path.join(OUTR, f"{acc}_{reel['id']}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS),
                           "-c:v", "mjpeg", "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "16",
                           "-x264-params", "aq-mode=3:deblock=-1,-1", "-pix_fmt", "yuv420p", "-profile:v", "high",
                           "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-ar", "44100", "-movflags", "+faststart",
                           "-shortest", mp4], stdin=subprocess.PIPE)
    pg = eng.page(acc, 1080, 1920)
    for si, sc in enumerate(scenes):
        pg.evaluate("s=>setScene(s,'reel')", sc)
        wt = word_times(sc["say"], lead, durs[si])
        ch = chunks(wt)
        last = si == len(scenes) - 1
        nf = int(round(sdur[si] * FPS))
        for k in range(nf):
            t = k / FPS
            cap = None
            act = [i for i, w in enumerate(wt) if w[1] <= t < w[2] + 0.05]
            if act or t < wt[-1][2] + 0.4:
                ai = act[-1] if act else (len(wt) - 1 if t >= wt[-1][2] else 0)
                if t >= lead - 0.05:
                    grp = next(g for g in ch if ai in g)
                    cap = {"words": [wt[i][0] for i in grp], "on": grp.index(ai) if act else -1, "y": 1300, "size": 58}
            pg.evaluate("a=>frame(a[0],a[1],a[2],a[3])", [t, sdur[si], last, cap])
            ff.stdin.write(eng.shot(pg, 1080, 1920, 93))
    pg.close()
    ff.stdin.close(); ff.wait()
    os.remove(wav)
    print("reel", acc, reel["id"], f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")
    return mp4


def render_reels(eng, acc, only=None):
    data = json.load(open(os.path.join(ROOT, "content/reels.json"), encoding="utf-8"))
    durs = json.load(open(os.path.join(ROOT, "audio/durations.json")))
    for r in data[acc]:
        if only and r["id"] != only:
            continue
        render_reel(eng, acc, r, durs[f"{acc}/{r['id']}"], os.path.join(ROOT, "audio", acc, r["id"]))


def render_stories(eng, acc):
    data = json.load(open(os.path.join(ROOT, "content/stories.json"), encoding="utf-8"))[acc]
    d = os.path.join(ROOT, "v2", "stories", acc); os.makedirs(d, exist_ok=True)
    pg = eng.page(acc, 1080, 1920)
    for name, frames in data.items():
        for i, sp in enumerate(frames, 1):
            pg.evaluate("s=>setScene(s,'reel')", sp)
            pg.evaluate("frame(30,99,true,null)")
            pg.wait_for_timeout(30)
            open(os.path.join(d, f"{name}_{i}.jpg"), "wb").write(eng.shot(pg, 1080, 1920, 95))
            print("story", acc, name, i)
    pg.close()


if __name__ == "__main__":
    what = sys.argv[1]
    accs = [sys.argv[2]] if len(sys.argv) > 2 and sys.argv[2] in ("kobi", "dari") else ["kobi", "dari"]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    eng = Engine()
    try:
        for acc in accs:
            if what == "carousels":
                render_carousels(eng, acc, only)
            elif what == "stories":
                render_stories(eng, acc)
            elif what == "reels":
                render_reels(eng, acc, only)
    finally:
        eng.close()
