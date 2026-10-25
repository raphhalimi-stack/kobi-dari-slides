#!/usr/bin/env python3
"""10 concepts visuels (1080x1920) pour une série d'épisodes « ingrédient expliqué »."""
import os, sys, io
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import Engine
from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "v2", "concepts"); os.makedirs(OUT, exist_ok=True)

BASE = """<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{font-family:Inter;src:url(fonts/Inter.ttf);font-weight:100 900}
@font-face{font-family:Serif;src:url(fonts/NewsreaderItalic.ttf);font-style:italic;font-weight:200 800}
*{margin:0;padding:0;box-sizing:border-box}
body{width:1080px;height:1920px;overflow:hidden;font-family:Inter;-webkit-font-smoothing:antialiased;position:relative}
.serif{font-family:Serif;font-style:italic;font-weight:400}
.tag{position:absolute;top:120px;left:80px;display:flex;align-items:center;gap:18px;font-size:34px;font-weight:700;letter-spacing:.5px}
.logo{width:56px;height:56px;border-radius:16px;background:#ebc9c6;position:relative}
.logo:after{content:'';position:absolute;right:8px;bottom:8px;width:16px;height:16px;border-radius:50%;background:#181415}
.c{position:absolute;left:80px;right:80px}
.ko{font-family:'Noto Sans CJK KR',sans-serif}
</style></head><body>%s</body></html>"""

TAG = lambda col="#f5f1ec": f'<div class="tag" style="color:{col}"><div class="logo"></div>INGREDIENT EXPLAINED · EP.01</div>'

C = []

# 1. Carte de collection (stats)
C.append(("Carte ingrédient", f"""
<div style="position:absolute;inset:0;background:radial-gradient(900px 900px at 50% 35%,#3b2a2e,#141011)"></div>
{TAG()}
<div class="c" style="top:300px;height:1240px;border-radius:56px;background:linear-gradient(160deg,#f6d9d5,#e9b9b4);box-shadow:0 40px 90px rgba(0,0,0,.5);padding:56px;color:#181415">
 <div style="display:flex;justify-content:space-between;font-weight:800;font-size:40px"><span>NIACINAMIDE</span><span>#01</span></div>
 <div style="height:520px;margin:30px 0;border-radius:36px;background:#fff8f5;display:flex;align-items:center;justify-content:center;font-size:260px;font-weight:900;color:#e9a7a2">B3</div>
 <div class="serif" style="font-size:52px;margin-bottom:30px">The one almost everyone can use.</div>
 {''.join(f'<div style="display:flex;align-items:center;gap:24px;margin:22px 0;font-size:40px;font-weight:700"><span style="width:300px">{n}</span><div style="flex:1;height:26px;border-radius:13px;background:rgba(0,0,0,.12)"><div style="width:{v}%;height:100%;border-radius:13px;background:#181415"></div></div></div>' for n, v in [("Brightening", 80), ("Oil control", 70), ("Calming", 75), ("Gentleness", 90)])}
</div>
<div class="c" style="top:1600px;text-align:center;color:#f5f1ec;font-size:46px;font-weight:700">Collect them all · follow for ep.02</div>"""))

# 2. Sous le microscope
C.append(("Sous le microscope", f"""
<div style="position:absolute;inset:0;background:#0f1a24"></div>{TAG()}
<div class="c" style="top:260px;color:#fff;font-size:96px;font-weight:900;line-height:1;letter-spacing:-3px">What niacinamide<br><span class="serif" style="color:#9fe3c9;font-weight:400">does inside</span> your skin</div>
<div style="position:absolute;left:140px;top:640px;width:800px;height:800px;border-radius:50%;border:22px solid #e9eef2;overflow:hidden;background:#f4d3c4;box-shadow:0 0 0 14px #0f1a24,0 0 0 24px #e9eef2">
 <div style="position:absolute;left:0;right:0;top:0;height:230px;background:#f9e3d8"></div>
 <div style="position:absolute;left:0;right:0;top:230px;height:16px;background:repeating-linear-gradient(90deg,#e8b5a5 0 60px,#f9e3d8 60px 72px)"></div>
 {''.join(f'<div style="position:absolute;left:{x}px;top:{y}px;width:44px;height:44px;border-radius:50%;background:#7a4b3a"></div>' for x, y in [(150,420),(300,520),(470,440),(600,560),(260,640)])}
 {''.join(f'<div style="position:absolute;left:{x}px;top:{y}px;width:34px;height:34px;border-radius:9px;background:#3ccf97;transform:rotate(45deg);box-shadow:0 0 24px #3ccf97"></div>' for x, y in [(210,360),(390,300),(540,380),(330,460),(660,470)])}
</div>
<div style="position:absolute;left:600px;top:1480px;color:#9fe3c9;font-size:44px;font-weight:800">◆ niacinamide</div>
<div style="position:absolute;left:150px;top:1480px;color:#d9a48e;font-size:44px;font-weight:800">● melanin</div>"""))

# 3. Mythe vs vérité
C.append(("Mythe vs vérité", f"""
<div style="position:absolute;left:0;right:0;top:0;height:960px;background:#e5484d"></div>
<div style="position:absolute;left:0;right:0;top:960px;height:960px;background:#1fa36b"></div>{TAG('#fff')}
<div class="c" style="top:330px;color:#fff"><div style="font-size:60px;font-weight:900;opacity:.85">MYTH</div><div style="font-size:92px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:20px">"Never mix niacinamide with vitamin C."</div></div>
<div style="position:absolute;left:440px;top:890px;width:200px;height:140px;border-radius:70px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:64px;font-weight:900;color:#181415">VS</div>
<div class="c" style="top:1110px;color:#fff"><div style="font-size:60px;font-weight:900;opacity:.85">FACT</div><div style="font-size:92px;font-weight:900;line-height:1.02;letter-spacing:-2px;margin-top:20px">Modern formulas pair them just fine.</div></div>"""))

# 4. Tableau de compatibilité
pairs = [("Hyaluronic acid", "✓", "#1fa36b"), ("Ceramides", "✓", "#1fa36b"), ("Vitamin C", "✓", "#1fa36b"), ("Retinol", "✓", "#1fa36b"), ("Strong acids (same night)", "!", "#f0a33a")]
C.append(("Ça se mélange ?", f"""
<div style="position:absolute;inset:0;background:#fbf4ef"></div>{TAG('#181415')}
<div class="c" style="top:260px;font-size:104px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">Niacinamide<br><span class="serif" style="font-weight:400;color:#c4706b">+ what?</span></div>
<div class="c" style="top:600px">{''.join(f'<div style="display:flex;justify-content:space-between;align-items:center;background:#fff;border-radius:34px;padding:40px 46px;margin-bottom:26px;box-shadow:0 10px 30px rgba(0,0,0,.06)"><span style="font-size:54px;font-weight:800;color:#181415">{n}</span><span style="width:110px;height:110px;border-radius:50%;background:{c};color:#fff;font-size:66px;font-weight:900;display:flex;align-items:center;justify-content:center">{s}</span></div>' for n, s, c in pairs)}</div>"""))

# 5. Élément du tableau périodique
C.append(("Tableau périodique", f"""
<div style="position:absolute;inset:0;background:#181415"></div>{TAG()}
<div style="position:absolute;left:150px;top:380px;width:780px;height:900px;border:10px solid #ebc9c6;border-radius:40px;padding:60px;color:#ebc9c6">
 <div style="display:flex;justify-content:space-between;font-size:60px;font-weight:800"><span>01</span><span>B3</span></div>
 <div style="font-size:400px;font-weight:900;line-height:1.1;color:#f5f1ec;letter-spacing:-10px;margin-top:20px">Nc</div>
 <div style="font-size:76px;font-weight:800;color:#f5f1ec">Niacinamide</div>
 <div class="serif" style="font-size:52px;margin-top:16px">brightens · calms · controls oil</div>
</div>
<div class="c" style="top:1360px;text-align:center;color:#a59e9c;font-size:46px;font-weight:600">The K-beauty periodic table · 01/30</div>"""))

# 6. Conversation (messages)
msgs = [("me", "is niacinamide actually worth it??"), ("k", "yes. it's vitamin B3"), ("k", "evens tone, calms redness, less shine ✨"), ("me", "how much tho"), ("k", "2–5% is plenty. more ≠ better")]
C.append(("Conversation", f"""
<div style="position:absolute;inset:0;background:#ffffff"></div>
<div style="position:absolute;left:0;right:0;top:0;height:230px;background:#f6f6f7;border-bottom:1px solid #e5e5ea;display:flex;align-items:flex-end;justify-content:center;padding-bottom:28px;gap:18px"><div class="logo"></div><span style="font-size:40px;font-weight:700;color:#181415">Kobi</span></div>
<div class="c" style="top:330px">{''.join(f'<div style="display:flex;justify-content:{"flex-end" if w=="me" else "flex-start"};margin-bottom:26px"><div style="max-width:720px;padding:30px 40px;border-radius:44px;font-size:52px;font-weight:500;line-height:1.25;background:{"#0a84ff" if w=="me" else "#e9e9eb"};color:{"#fff" if w=="me" else "#111"}">{t}</div></div>' for w, t in msgs)}</div>
<div class="c" style="top:1500px;text-align:center;font-size:44px;font-weight:800;color:#181415">Niacinamide, explained in 5 texts</div>"""))

# 7. Tier list
tiers = [("S", "#ff7f7f", ["Niacinamide", "SPF"]), ("A", "#ffbf7f", ["Ceramides", "Centella"]), ("B", "#ffdf7f", ["Vitamin C"]), ("C", "#bfff7f", ["Coconut oil"])]
C.append(("Tier list", f"""
<div style="position:absolute;inset:0;background:#1a1a1a"></div>{TAG()}
<div class="c" style="top:250px;color:#fff;font-size:100px;font-weight:900;letter-spacing:-3px">Skincare<br>ingredient tier list</div>
<div class="c" style="top:600px">{''.join(f'<div style="display:flex;margin-bottom:14px;height:200px"><div style="width:200px;background:{c};display:flex;align-items:center;justify-content:center;font-size:110px;font-weight:900;color:#1a1a1a">{t}</div><div style="flex:1;background:#2b2b2b;display:flex;align-items:center;gap:18px;padding:0 24px">{"".join(f"<span style=\'background:#f5f1ec;color:#181415;border-radius:20px;padding:22px 26px;font-size:40px;font-weight:800\'>{x}</span>" for x in items)}</div></div>' for t, c, items in tiers)}</div>"""))

# 8. Expliqué comme à un enfant (personnage)
C.append(("Comme à un enfant", f"""
<div style="position:absolute;inset:0;background:#fff2c9"></div>{TAG('#181415')}
<div class="c" style="top:250px;font-size:96px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">Niacinamide is your<br>skin's <span style="background:#181415;color:#fff2c9;padding:0 16px;border-radius:16px">bodyguard</span></div>
<div style="position:absolute;left:240px;top:660px;width:600px;height:640px">
 <div style="position:absolute;left:150px;top:0;width:300px;height:300px;border-radius:50%;background:#f6cdb4"></div>
 <div style="position:absolute;left:180px;top:110px;width:240px;height:70px;border-radius:35px;background:#181415"></div>
 <div style="position:absolute;left:250px;top:215px;width:100px;height:22px;border-radius:11px;background:#a33"></div>
 <div style="position:absolute;left:60px;top:300px;width:480px;height:360px;border-radius:120px 120px 30px 30px;background:#1f2a44"></div>
 <div style="position:absolute;left:230px;top:330px;width:140px;height:70px;border-radius:12px;background:#fff;font-size:44px;font-weight:900;color:#1f2a44;display:flex;align-items:center;justify-content:center">B3</div>
</div>
<div class="c" style="top:1360px;display:flex;justify-content:space-around;font-size:46px;font-weight:800;color:#181415"><span>🚫 redness</span><span>🚫 shine</span><span>🚫 dark spots</span></div>"""))

# 9. Zoom sur l'étiquette
C.append(("Zoom étiquette", f"""
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#e9e4df,#d8d0c9)"></div>{TAG('#181415')}
<div class="c" style="top:250px;font-size:92px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">Find it on<br>the label.</div>
<div style="position:absolute;left:190px;top:560px;width:700px;height:1080px;border-radius:60px;background:#fff;box-shadow:0 40px 80px rgba(0,0,0,.18);padding:70px;font-size:40px;line-height:1.55;color:#777">
 <div style="font-size:52px;font-weight:900;color:#181415;margin-bottom:30px">INGREDIENTS</div>
 Water, Glycerin, Butylene Glycol, <span style="background:#ffe14d;color:#181415;font-weight:900;padding:2px 10px;border-radius:8px">Niacinamide</span>, Panthenol, Sodium Hyaluronate, Centella Asiatica Extract, Allantoin, Adenosine…
 <div style="margin-top:70px;font-size:170px;font-weight:900;color:#181415;letter-spacing:-6px">5%</div>
 <div class="serif" style="font-size:48px;color:#c4706b">the sweet spot: 2–5%</div>
</div>"""))

# 10. Quiz
C.append(("Quiz", f"""
<div style="position:absolute;inset:0;background:#6b5bd6"></div>{TAG('#fff')}
<div class="c" style="top:360px;color:#fff;font-size:110px;font-weight:900;letter-spacing:-3px;line-height:1.02">Can you use niacinamide with vitamin C?</div>
<div class="c" style="top:1000px;display:flex;gap:40px">
 <div style="flex:1;height:300px;border-radius:50px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:110px;font-weight:900;color:#1fa36b">YES</div>
 <div style="flex:1;height:300px;border-radius:50px;background:#fff;display:flex;align-items:center;justify-content:center;font-size:110px;font-weight:900;color:#e5484d">NO</div></div>
<div class="c" style="top:1390px;text-align:center;color:#fff;font-size:50px;font-weight:700">Answer in 3… 2… 1…</div>"""))


def main():
    eng = Engine()
    pg = eng.br.new_page(viewport={"width": 1080, "height": 1920})
    files = []
    for i, (name, body) in enumerate(C, 1):
        path = os.path.join(ROOT, "engine", f"_concept.html")
        open(path, "w", encoding="utf-8").write(BASE.replace("%s", body))
        pg.goto("file://" + path); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
        f = os.path.join(OUT, f"{i:02d}.jpg"); open(f, "wb").write(pg.screenshot(type="jpeg", quality=92)); files.append((f, name))
    eng.close()
    # planche
    W, H = 360, 640
    sheet = Image.new("RGB", (5 * (W + 20) + 20, 2 * (H + 90) + 20), "white")
    d = ImageDraw.Draw(sheet)
    fnt = ImageFont.truetype(os.path.join(ROOT, "engine/fonts/Inter.ttf"), 34)
    for i, (f, name) in enumerate(files):
        x = 20 + (i % 5) * (W + 20); y = 20 + (i // 5) * (H + 90)
        sheet.paste(Image.open(f).resize((W, H)), (x, y))
        d.text((x, y + H + 14), f"{i+1}. {name}", font=fnt, fill=(24, 20, 21))
    sheet.save(os.path.join(OUT, "planche.jpg"), quality=90)
    print("ok")


if __name__ == "__main__":
    main()
