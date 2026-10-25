#!/usr/bin/env python3
"""Reel de présentation : python engine/render_intro_reel.py k_in01 d_in01"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import read_wav, resample, music_bed, word_times, chunks  # noqa
from render_ep import sfx_ding, add  # noqa
from render_micro import whoosh  # noqa
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, SR = 30, 44100
MIN = {"logo": 2.8, "tag": 3.0, "series": 4.2, "launch": 4.4}


def main(eid):
    ep = json.load(open(os.path.join(ROOT, f"content/episodes/{eid}.json"), encoding="utf-8"))
    acc = ep["account"]; ad = os.path.join(ROOT, "audio/episodes", eid)
    durs = json.load(open(os.path.join(ad, "durations.json"))); lead = 0.35
    sd = [max(MIN[s["scene"]], d + lead + 0.5) for s, d in zip(ep["scenes"], durs)]
    sd[-1] += 0.8
    total = sum(sd); starts = np.cumsum([0] + sd[:-1])
    voice = np.zeros(int(total * SR) + SR)
    for i, st in enumerate(starts):
        a, r = read_wav(os.path.join(ad, f"{i:02d}.wav")); add(voice, resample(a, r, SR), st + lead)
    voice = voice[: int(total * SR)]; voice /= max(1e-6, np.abs(voice).max()); voice *= 0.9
    fx = np.zeros_like(voice)
    for k, s in enumerate(ep["scenes"]):
        add(fx, whoosh(0.6) * 0.8, starts[k])
        if s["scene"] in ("logo", "launch"):
            add(fx, sfx_ding() * 0.5, starts[k] + 0.9)
    bed = music_bed(total, SR, "warm" if acc == "kobi" else "cool")
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = voice + fx * 0.7 + bed * 0.22 * (1 - 0.5 * np.clip(env / 0.05, 0, 1))
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.95
    out = os.path.join(ROOT, "v2/episodes"); wav = os.path.join(out, f"{eid}.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    mp4 = os.path.join(out, f"{eid}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4], stdin=subprocess.PIPE)
    with sync_playwright() as p:
        b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1920})
        pg.goto("file://" + os.path.join(ROOT, "engine/intro_reel.html")); pg.evaluate("document.fonts.ready")
        pg.evaluate("a=>init(a)", acc)
        for i, s in enumerate(ep["scenes"]):
            pg.evaluate("n=>setScene(n)", s["scene"])
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
                outv = max(0.0, (t - (sd[i] - 0.5)) / 0.5) if last else 0.0
                pg.evaluate("o=>frame(o)", {"t": t, "T": float(starts[i] + t), "cap": cap, "out": min(1.0, outv)})
                ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
        b.close()
    ff.stdin.close(); ff.wait(); os.remove(wav)
    print(mp4, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")


if __name__ == "__main__":
    for e in sys.argv[1:]:
        main(e)
