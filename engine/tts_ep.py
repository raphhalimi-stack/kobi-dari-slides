"""Voix des épisodes (Kokoro). Une piste par scène, voix selon le personnage."""
import glob, json, os, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
for p in sorted(glob.glob(os.path.join(ROOT, "content/episodes/*.json"))):
    ep = json.load(open(p, encoding="utf-8"))
    d = os.path.join(ROOT, "audio/episodes", ep["id"])
    if os.path.exists(os.path.join(d, "durations.json")):
        continue
    os.makedirs(d, exist_ok=True)
    durs = []
    for i, s in enumerate(ep["scenes"]):
        speed = 1.08 if s["who"] == "mina" else 1.02
        a, sr = k.create(s["text"], voice=ep["voices"][s["who"]], speed=speed, lang="en-us")
        sf.write(os.path.join(d, f"{i:02d}.wav"), a, sr); durs.append(round(len(a) / sr, 3))
    json.dump(durs, open(os.path.join(d, "durations.json"), "w"))
    print(ep["id"], durs)
