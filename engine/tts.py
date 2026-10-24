"""Génère la voix off (Kokoro TTS) de chaque scène des reels. Tourne sur GitHub Actions."""
import json, os, soundfile as sf
from kokoro_onnx import Kokoro
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data = json.load(open(os.path.join(ROOT, "content/reels.json"), encoding="utf-8"))
k = Kokoro("kokoro-v1.0.onnx", "voices-v1.0.bin")
out = {}
for acc in ("kobi", "dari"):
    voice = data["voices"][acc]
    for r in data[acc]:
        d = os.path.join(ROOT, "audio", acc, r["id"]); os.makedirs(d, exist_ok=True)
        durs = []
        for i, s in enumerate(r["scenes"]):
            samples, sr = k.create(s["say"], voice=voice, speed=1.05, lang="en-us")
            p = os.path.join(d, f"{i:02d}.wav"); sf.write(p, samples, sr)
            durs.append(round(len(samples) / sr, 3))
        out[f"{acc}/{r['id']}"] = durs
        print(acc, r["id"], durs)
json.dump(out, open(os.path.join(ROOT, "audio/durations.json"), "w"), indent=1)
