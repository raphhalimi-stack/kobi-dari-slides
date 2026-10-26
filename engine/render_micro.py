#!/usr/bin/env python3
"""Rend l'épisode « microscope » : python engine/render_micro.py ni01"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Engine, read_wav, resample, music_bed, word_times, chunks  # noqa
from render_ep import sfx_pop, sfx_ding, add  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, SR = 30, 44100
MIN = {"hook": 3.4, "melanocyte": 2.6, "transfer": 3.4, "block": 3.0, "fade": 3.8, "barrier": 3.2, "end": 4.2, "inflame": 3.4, "calm": 3.6, "dry": 3.2, "draw": 3.6, "plump": 3.4, "gaps": 3.4, "fill": 3.6, "seal": 3.2}


def whoosh(n=0.7):
    x = np.arange(int(n * SR)) / SR
    noise = np.random.default_rng(3).standard_normal(len(x))
    env = np.sin(np.pi * x / n) ** 2
    k = np.ones(40) / 40
    return np.convolve(noise, k, mode="same") * env * 0.35


def main(eid, html="micro.html"):
    ep = json.load(open(os.path.join(ROOT, f"content/episodes/{eid}.json"), encoding="utf-8"))
    ad = os.path.join(ROOT, "audio/episodes", eid)
    durs = json.load(open(os.path.join(ad, "durations.json")))
    lead = 0.3
    sd = [max(MIN.get(s["scene"], 2.4), d + lead + 0.6) for s, d in zip(ep["scenes"], durs)]
    total = sum(sd); starts = np.cumsum([0] + sd[:-1])
    voice = np.zeros(int(total * SR) + SR)
    for i, st in enumerate(starts):
        a, r = read_wav(os.path.join(ad, f"{i:02d}.wav")); add(voice, resample(a, r, SR), st + lead)
    voice = voice[: int(total * SR)]; voice /= max(1e-6, np.abs(voice).max()); voice *= 0.9
    fx = np.zeros_like(voice)
    add(fx, whoosh(), starts[0] + 0.9)
    for k in range(1, len(sd) - 1):
        add(fx, sfx_ding() * 0.5, starts[k] + 0.05)
    names = [s["scene"] for s in ep["scenes"]]
    for nm in ("block", "calm", "draw", "fill"):
        if nm in names:
            for i in range(6):
                add(fx, sfx_pop(0.07, 900, 1400) * 0.6, starts[names.index(nm)] + 0.4 + i * 0.12)
    add(fx, whoosh(0.5) * 0.7, starts[-1])
    bed = music_bed(total, SR, "cool")
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = voice + fx * 0.7 + bed * 0.15 * (1 - 0.5 * np.clip(env / 0.05, 0, 1))
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.95
    out = os.path.join(ROOT, "v2/episodes"); os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, f"{eid}.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    mp4 = os.path.join(out, f"{eid}.mp4" if eid.startswith(("k_", "d_")) else f"kobi_{eid}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-x264-params", "aq-mode=3",
                           "-pix_fmt", "yuv420p", "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart",
                           "-shortest", mp4], stdin=subprocess.PIPE)
    eng = Engine(); pg = eng.br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + os.path.join(ROOT, "engine", html)); pg.evaluate("document.fonts.ready")
    pg.evaluate("a=>init(a[0],a[1])", [eng.grain, ep.get("cfg", {})])
    for i, s in enumerate(ep["scenes"]):
        pg.evaluate("a=>setScene(a[0],a[1])", [s["scene"], s.get("head")])
        wt = word_times(s["text"], lead, durs[i]); ch = chunks(wt, 3)
        nf = int(round(sd[i] * FPS)); last = i == len(sd) - 1
        for k in range(nf):
            t = k / FPS
            act = [j for j, w in enumerate(wt) if w[1] <= t < w[2] + 0.04]
            cap = None
            if act or (lead <= t < wt[-1][2] + 0.35):
                ai = act[-1] if act else len(wt) - 1
                grp = next(gp for gp in ch if ai in gp)
                cap = {"words": [wt[j][0] for j in grp], "on": grp.index(ai) if act else -1}
            outv = max(0.0, (t - (sd[i] - 0.15)) / 0.15) if not last else max(0.0, (t - (sd[i] - 0.5)) / 0.5)
            pg.evaluate("o=>frame(o)", {"t": t, "T": float(starts[i] + t), "dur": sd[i], "cap": cap, "out": min(1.0, outv)})
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
        print("scene", s["scene"], f"{sd[i]:.2f}s")
    ff.stdin.close(); ff.wait(); os.remove(wav); eng.close()
    print(mp4, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ni01")
