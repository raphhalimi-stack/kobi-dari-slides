#!/usr/bin/env python3
"""Rend un épisode des séries Myth or Fact / mot coréen / quiz : python engine/render_series.py k_mf01"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Engine, read_wav, resample, music_bed, word_times, chunks  # noqa
from render_ep import sfx_pop, sfx_ding, add  # noqa
from render_micro import whoosh  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, SR = 30, 44100
MIN = {"myth": 3.6, "verdict": 1.7, "explain": 3.4, "rule": 2.8, "end": 3.4,
       "word": 3.4, "meaning": 3.2, "examples": 3.6, "question": 3.8, "count": 3.0, "answer": 3.6}


def tick():
    x = np.arange(int(0.05 * SR)) / SR
    return np.sin(2 * np.pi * 1200 * x) * np.exp(-x * 80) * 0.5


def thud():
    x = np.arange(int(0.35 * SR)) / SR
    return np.sin(2 * np.pi * 70 * x) * np.exp(-x * 12) * 0.9


def main(eid):
    ep = json.load(open(os.path.join(ROOT, f"content/episodes/{eid}.json"), encoding="utf-8"))
    acc = ep["account"]
    ad = os.path.join(ROOT, "audio/episodes", eid)
    durs = json.load(open(os.path.join(ad, "durations.json")))
    lead = 0.25
    sd = []
    for s, d in zip(ep["scenes"], durs):
        v = max(MIN.get(s["scene"], 2.4), d + lead + 0.5)
        if s["scene"] == "count":
            v = max(3.0, d + lead + 0.3)
        sd.append(v)
    total = sum(sd); starts = np.cumsum([0] + sd[:-1])
    voice = np.zeros(int(total * SR) + SR)
    for i, st in enumerate(starts):
        a, r = read_wav(os.path.join(ad, f"{i:02d}.wav")); add(voice, resample(a, r, SR), st + lead)
    voice = voice[: int(total * SR)]; voice /= max(1e-6, np.abs(voice).max()); voice *= 0.9
    fx = np.zeros_like(voice)
    names = [s["scene"] for s in ep["scenes"]]
    for k, nm in enumerate(names):
        st = starts[k]
        if nm == "verdict":
            add(fx, whoosh(0.3), st); add(fx, thud(), st + 0.3)
        elif nm == "count":
            for j in range(3):
                add(fx, tick(), st + j * sd[k] / 3)
        elif nm in ("rule", "answer", "meaning"):
            add(fx, sfx_ding() * 0.6, st + 0.1)
        elif nm == "examples":
            for j in range(3):
                add(fx, sfx_pop(0.07, 700, 1100) * 0.6, st + 0.3 + j * 0.35)
        elif nm == "end":
            add(fx, whoosh(0.5) * 0.6, st)
    bed = music_bed(total, SR, "warm" if acc == "kobi" else "cool")
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = voice + fx * 0.7 + bed * 0.15 * (1 - 0.5 * np.clip(env / 0.05, 0, 1))
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.95
    out = os.path.join(ROOT, "v2/episodes"); os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, f"{eid}.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    mp4 = os.path.join(out, f"{eid}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-x264-params", "aq-mode=3",
                           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                           "-shortest", mp4], stdin=subprocess.PIPE)
    cfg = {"acc": acc, "template": ep["template"], "series": ep["series"], "ep": ep["ep"], "grain": None}
    first = ep["scenes"][0]
    for k in ("quote", "word", "roman", "q", "a", "b"):
        if k in first:
            cfg[k] = first[k]
    eng = Engine(); cfg["grain"] = eng.grain
    pg = eng.br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + os.path.join(ROOT, "engine/series.html")); pg.evaluate("document.fonts.ready")
    pg.evaluate("c=>init(c)", cfg)
    # warm-up: lay out the first scene once so web fonts are applied before measuring (fixes overlap on scene 1)
    pg.evaluate("a=>setScene(a[0],a[1])", [ep["scenes"][0]["scene"], ep["scenes"][0]]); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(400)
    for i, s in enumerate(ep["scenes"]):
        pg.evaluate("a=>setScene(a[0],a[1])", [s["scene"], s])
        wt = word_times(s["text"], lead, durs[i]); ch = chunks(wt, 3)
        nf = int(round(sd[i] * FPS)); last = i == len(sd) - 1
        for k in range(nf):
            t = k / FPS
            act = [j for j, w in enumerate(wt) if w[1] <= t < w[2] + 0.04]
            cap = None
            if s["scene"] != "count" and (act or (lead <= t < wt[-1][2] + 0.35)):
                ai = act[-1] if act else len(wt) - 1
                grp = next(gp for gp in ch if ai in gp)
                cap = {"words": [wt[j][0] for j in grp], "on": grp.index(ai) if act else -1}
            outv = max(0.0, (t - (sd[i] - 0.15)) / 0.15) if not last else max(0.0, (t - (sd[i] - 0.5)) / 0.5)
            if s["scene"] == "myth" or (i + 1 < len(names) and names[i + 1] == "verdict"):
                outv = 0.0  # enchaînement direct vers le verdict
            pg.evaluate("o=>frame(o)", {"t": t, "dur": sd[i], "cap": cap, "out": min(1.0, outv)})
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
    ff.stdin.close(); ff.wait(); os.remove(wav); eng.close()
    print(mp4, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")


if __name__ == "__main__":
    for e in sys.argv[1:]:
        main(e)
