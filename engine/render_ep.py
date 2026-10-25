#!/usr/bin/env python3
"""Rend un épisode animé (personnages) : python engine/render_ep.py ep1"""
import json, os, subprocess, sys, wave
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Engine, read_wav, resample, music_bed, word_times, chunks  # noqa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FPS, SR = 30, 44100
MIN = {"shelf": 3.4, "morning": 2.8, "kobi_enter": 2.4, "barrier": 3.0, "rule": 3.0, "happy": 2.4, "end": 3.0}


def sfx_pop(n=0.09, f0=900, f1=300):
    x = np.arange(int(n * SR)) / SR
    f = np.linspace(f0, f1, len(x))
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 40) * 0.5


def sfx_boing():
    x = np.arange(int(0.35 * SR)) / SR
    f = 220 + 160 * np.sin(2 * np.pi * 9 * x) * np.exp(-x * 6)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-x * 7) * 0.5


def sfx_ding():
    x = np.arange(int(0.8 * SR)) / SR
    return (np.sin(2 * np.pi * 1318 * x) + .5 * np.sin(2 * np.pi * 1975 * x)) * np.exp(-x * 5) * 0.25


def add(buf, clip, t):
    s = int(t * SR); e = min(len(buf), s + len(clip))
    if s < len(buf):
        buf[s:e] += clip[: e - s]


def main(eid):
    ep = json.load(open(os.path.join(ROOT, f"content/episodes/{eid}.json"), encoding="utf-8"))
    ad = os.path.join(ROOT, "audio/episodes", eid)
    durs = json.load(open(os.path.join(ad, "durations.json")))
    lead = 0.25
    sd = [max(MIN.get(s["scene"], 2.2), d + lead + 0.55) for s, d in zip(ep["scenes"], durs)]
    total = sum(sd)
    voice = np.zeros(int(total * SR) + SR); env_frames = []
    starts = np.cumsum([0] + sd[:-1])
    for i, (s, st) in enumerate(zip(ep["scenes"], starts)):
        a, r = read_wav(os.path.join(ad, f"{i:02d}.wav")); a = resample(a, r, SR)
        vstart = st + (1.2 if s["scene"] == "shelf" and False else lead)
        add(voice, a, vstart)
    voice = voice[: int(total * SR)]
    voice /= max(1e-6, np.abs(voice).max()); voice *= 0.9
    # enveloppe pour la synchro des lèvres
    hop = SR // FPS
    rms = np.array([np.sqrt(np.mean(voice[i * hop:(i + 1) * hop] ** 2)) for i in range(int(total * FPS))])
    talk = np.clip((rms - 0.02) / 0.16, 0, 1)
    talk = np.convolve(talk, [0.25, 0.5, 0.25], mode="same")
    # effets sonores
    fx = np.zeros_like(voice)
    for i in range(7):
        add(fx, sfx_pop(f0=700 + i * 90, f1=300 + i * 40), starts[0] + 0.15 + i * 0.28)
    add(fx, sfx_pop(0.12, 1400, 1800) * 0.8, starts[1] + 0.9)
    add(fx, sfx_boing(), starts[2] + 0.05)
    for i in range(7):
        add(fx, sfx_pop(0.07, 500, 200) * 0.7, starts[3] + 0.3 + i * 0.32 + 0.45)
    for k, f in enumerate([0.15, 0.42, 0.62]):
        add(fx, sfx_ding() * 0.8, starts[4] + f * sd[4])
    add(fx, sfx_ding(), starts[5] + 0.7)
    bed = music_bed(total, SR, "warm")
    env = np.convolve(np.abs(voice), np.ones(4410) / 4410, mode="same")
    mix = voice + fx[: len(voice)] * 0.7 + bed * 0.14 * (1 - 0.5 * np.clip(env / 0.05, 0, 1))
    mix /= max(1e-6, np.abs(mix).max()); mix *= 0.95
    out = os.path.join(ROOT, "v2/episodes"); os.makedirs(out, exist_ok=True)
    wav = os.path.join(out, f"{eid}.wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.stack([mix, mix], 1) * 32767).astype(np.int16).tobytes())
    mp4 = os.path.join(out, f"kobi_{eid}.mp4")
    ff = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", str(FPS), "-c:v", "mjpeg",
                           "-i", "-", "-i", wav, "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
                           "-r", str(FPS), "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", "-shortest", mp4],
                          stdin=subprocess.PIPE)
    eng = Engine()
    pg = eng.br.new_page(viewport={"width": 1080, "height": 1920})
    pg.goto("file://" + os.path.join(ROOT, "engine/ep.html")); pg.evaluate("document.fonts.ready")
    pg.evaluate("g=>init(g)", eng.grain)
    fi = 0
    for i, s in enumerate(ep["scenes"]):
        pg.evaluate("n=>setScene(n)", s["scene"])
        wt = word_times(s["text"], lead, durs[i]); ch = chunks(wt, 3)
        nf = int(round(sd[i] * FPS))
        for k in range(nf):
            t = k / FPS; T = starts[i] + t
            act = [j for j, w in enumerate(wt) if w[1] <= t < w[2] + 0.04]
            cap = None
            if act or (wt and lead <= t < wt[-1][2] + 0.35):
                ai = act[-1] if act else len(wt) - 1
                grp = next(gp for gp in ch if ai in gp)
                cap = {"words": [wt[j][0] for j in grp], "on": grp.index(ai) if act else -1}
            tk = float(talk[min(fi, len(talk) - 1)]) if True else 0
            last = i == len(ep["scenes"]) - 1
            outv = max(0.0, (t - (sd[i] - 0.15)) / 0.15) if not last else max(0.0, (t - (sd[i] - 0.5)) / 0.5)
            pg.evaluate("o=>frame(o)", {"t": t, "T": T, "talk": tk, "dur": sd[i], "top": s.get("top", ""), "cap": cap,
                                        "out": min(1.0, outv)})
            ff.stdin.write(pg.screenshot(type="jpeg", quality=93))
            fi += 1
        print("scene", s["scene"], f"{sd[i]:.2f}s")
    ff.stdin.close(); ff.wait(); os.remove(wav); eng.close()
    print(mp4, f"{total:.1f}s", os.path.getsize(mp4) // 1024, "KB")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "ep1")
