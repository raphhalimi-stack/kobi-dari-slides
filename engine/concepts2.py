#!/usr/bin/env python3
"""Concepts 11 à 20 (même sujet : niacinamide)."""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import concepts as base
from concepts import TAG

C = []
# 11. Jauge de dosage
C.append(("Dosage", f"""
<div style="position:absolute;inset:0;background:#181415"></div>{TAG()}
<div class="c" style="top:260px;color:#f5f1ec;font-size:100px;font-weight:900;letter-spacing:-3px;line-height:1">How much<br><span class="serif" style="font-weight:400;color:#ebc9c6">niacinamide?</span></div>
<div style="position:absolute;left:140px;top:700px;width:800px;height:400px;border-radius:400px 400px 0 0;background:conic-gradient(from 270deg at 50% 100%,#1fa36b 0deg 90deg,#f0a33a 90deg 140deg,#e5484d 140deg 180deg,transparent 180deg)"></div>
<div style="position:absolute;left:240px;top:800px;width:600px;height:300px;border-radius:300px 300px 0 0;background:#181415"></div>
<div style="position:absolute;left:532px;top:760px;width:16px;height:340px;background:#f5f1ec;border-radius:8px;transform-origin:50% 100%;transform:rotate(-38deg)"></div>
<div style="position:absolute;left:510px;top:1075px;width:60px;height:60px;border-radius:50%;background:#f5f1ec"></div>
<div class="c" style="top:1200px;display:flex;justify-content:space-between;font-size:52px;font-weight:900"><span style="color:#1fa36b">2–5%</span><span style="color:#f0a33a">5–10%</span><span style="color:#e5484d">10%+</span></div>
<div class="c" style="top:1330px;text-align:center;color:#a59e9c;font-size:44px;font-weight:600">More is not better.</div>"""))

# 12. POV Olive Young
C.append(("POV en magasin", f"""
<div style="position:absolute;inset:0;background:linear-gradient(180deg,#e9f4ee,#cfe6da)"></div>{TAG('#181415')}
<div class="c" style="top:250px;font-size:92px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">POV: you finally<br>understand the shelf</div>
{''.join(f'<div style="position:absolute;left:80px;right:80px;top:{y}px;height:22px;background:#fff;border-radius:11px;box-shadow:0 8px 20px rgba(0,0,0,.08)"></div>' for y in (900, 1250))}
{''.join(f'<div style="position:absolute;left:{x}px;top:{y-h}px;width:110px;height:{h}px;border-radius:18px;background:{c}"></div>' for x, y, h, c in [(110,900,200,'#f4b6b0'),(250,900,240,'#ffffff'),(390,900,180,'#d9ccff'),(530,900,230,'#ffd9a8'),(670,900,200,'#bfe6f5'),(810,900,170,'#fff0a8'),(110,1250,220,'#c8e3d6'),(250,1250,190,'#ffd0d0'),(390,1250,240,'#ffffff'),(530,1250,200,'#e4d6ff'),(670,1250,230,'#ffe6b8'),(810,1250,180,'#d0f0ff')])}
<div style="position:absolute;left:520px;top:640px;width:130px;height:300px;border:10px solid #181415;border-radius:26px"></div>
<div style="position:absolute;left:470px;top:560px;background:#181415;color:#fff;font-size:40px;font-weight:800;padding:12px 22px;border-radius:16px">✓ niacinamide 5%</div>
<div class="c" style="top:1400px;text-align:center;font-size:46px;font-weight:800;color:#181415">Shot in Olive Young · scanned with Kobi</div>"""))

# 13. Fiche recette
C.append(("Recette", f"""
<div style="position:absolute;inset:0;background:#fff6e9"></div>{TAG('#181415')}
<div class="c" style="top:250px;font-size:100px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">Recipe:<br><span class="serif" style="font-weight:400;color:#c4706b">even-toned skin</span></div>
<div class="c" style="top:640px;background:#fff;border-radius:40px;padding:56px;box-shadow:0 20px 50px rgba(0,0,0,.08);font-size:50px;color:#181415;line-height:1.7">
<div style="font-weight:900;font-size:40px;letter-spacing:2px;color:#c4706b">INGREDIENTS</div>
• 2–5% niacinamide<br>• 1 hydrating toner<br>• 1 moisturiser<br>• SPF every morning
<div style="font-weight:900;font-size:40px;letter-spacing:2px;color:#c4706b;margin-top:30px">COOKING TIME</div>4 to 8 weeks</div>"""))

# 14. Flash info
C.append(("Flash info", f"""
<div style="position:absolute;inset:0;background:#0b1630"></div>
<div style="position:absolute;left:0;right:0;top:0;height:160px;background:#e5484d;display:flex;align-items:center;padding-left:80px;font-size:62px;font-weight:900;color:#fff;letter-spacing:2px">BREAKING</div>
<div class="c" style="top:300px;color:#fff;font-size:104px;font-weight:900;letter-spacing:-3px;line-height:1.02">Vitamin B3 found in<br>half your skincare</div>
<div style="position:absolute;left:120px;top:780px;width:840px;height:480px;border-radius:30px;background:#1b2a4d;display:flex;align-items:center;justify-content:center;font-size:200px;font-weight:900;color:#ebc9c6">B3</div>
<div style="position:absolute;left:0;right:0;top:1360px;height:110px;background:#f5f1ec;display:flex;align-items:center;font-size:44px;font-weight:800;color:#0b1630;white-space:nowrap;overflow:hidden;padding-left:40px">NIACINAMIDE · brightens · calms · controls oil · 2–5% is enough · NIACINAMIDE ·</div>"""))

# 15. Profil de rencontre
C.append(("Profil de rencontre", f"""
<div style="position:absolute;inset:0;background:linear-gradient(160deg,#ff8aa0,#ff5f7e)"></div>{TAG('#fff')}
<div class="c" style="top:260px;height:1180px;background:#fff;border-radius:50px;overflow:hidden;box-shadow:0 30px 70px rgba(0,0,0,.2)">
 <div style="height:560px;background:linear-gradient(160deg,#f6d9d5,#e9b9b4);display:flex;align-items:center;justify-content:center;font-size:240px;font-weight:900;color:#fff">B3</div>
 <div style="padding:44px;color:#181415"><div style="font-size:70px;font-weight:900">Niacinamide, <span style="font-weight:400">3</span></div>
 <div style="font-size:42px;margin-top:18px;line-height:1.5">💚 Likes: hyaluronic acid, ceramides, SPF<br>🚩 Dealbreaker: anything over 10%<br>✨ Looking for: oily & uneven skin</div></div></div>
<div class="c" style="top:1500px;display:flex;justify-content:center;gap:80px"><div style="width:150px;height:150px;border-radius:50%;background:#fff;font-size:80px;display:flex;align-items:center;justify-content:center">✕</div><div style="width:150px;height:150px;border-radius:50%;background:#fff;font-size:80px;display:flex;align-items:center;justify-content:center;color:#ff5f7e">♥</div></div>"""))

# 16. Notes
C.append(("Bloc-notes", f"""
<div style="position:absolute;inset:0;background:#fffdf5"></div>
<div style="position:absolute;left:0;right:0;top:0;height:200px;display:flex;align-items:flex-end;padding:0 60px 30px;font-size:44px;color:#e0a800;font-weight:600">‹ Notes</div>
<div class="c" style="top:260px;color:#1c1c1e"><div style="font-size:74px;font-weight:800;line-height:1.1">things I wish I knew about niacinamide</div>
<div style="font-size:52px;line-height:1.6;margin-top:50px">- it's just vitamin B3<br>- 2–5% is enough<br>- you CAN use it with vitamin C<br>- results take 4–8 weeks<br>- flushing = too strong for you</div></div>"""))

# 17. Leçon de coréen
C.append(("Leçon de coréen", f"""
<div style="position:absolute;inset:0;background:#ffffff"></div>{TAG('#181415')}
<div class="c" style="top:260px;font-size:64px;font-weight:800;color:#777">How do you say it in Korean?</div>
<div class="c ko" style="top:420px;font-size:150px;font-weight:900;color:#181415;line-height:1.1">나이아신<br>아마이드</div>
<div class="c" style="top:800px;font-size:56px;color:#c4706b" ><span class="serif">na-i-a-sin-a-ma-i-deu</span></div>
<div class="c" style="top:980px;display:flex;flex-direction:column;gap:26px">{''.join(f'<div style="border:6px solid #e5e5e5;border-bottom-width:12px;border-radius:30px;padding:36px 44px;font-size:54px;font-weight:800;color:#181415;{s}">{t}</div>' for t, s in [("Niacinamide", "border-color:#58cc02;background:#d7ffb8"), ("Retinol", ""), ("Centella", "")])}</div>"""))

# 18. Green flag / red flag
C.append(("Green flag / red flag", f"""
<div style="position:absolute;inset:0;background:#141414"></div>{TAG()}
<div class="c" style="top:250px;color:#fff;font-size:96px;font-weight:900;letter-spacing:-3px;line-height:1">Niacinamide serum<br>green & red flags</div>
<div class="c" style="top:640px;display:flex;flex-direction:column;gap:24px">{''.join(f'<div style="display:flex;align-items:center;gap:30px;background:#222;border-radius:30px;padding:34px 40px;font-size:50px;font-weight:700;color:#fff"><span style="font-size:70px">{e}</span>{t}</div>' for e, t in [("🟢", "2–5% on the label"), ("🟢", "fragrance-free"), ("🟢", "with ceramides"), ("🔴", "20% \"for faster results\""), ("🔴", "stings every time")])}</div>"""))

# 19. Combien de temps
C.append(("Combien de temps ?", f"""
<div style="position:absolute;inset:0;background:#f3eefc"></div>{TAG('#181415')}
<div class="c" style="top:250px;font-size:100px;font-weight:900;letter-spacing:-3px;line-height:1;color:#181415">When will I<br>see results?</div>
<div class="c" style="top:700px">{''.join(f'<div style="display:flex;align-items:center;gap:34px;margin-bottom:60px"><div style="width:190px;font-size:56px;font-weight:900;color:#6b5bd6">{w}</div><div style="flex:1"><div style="height:34px;border-radius:17px;background:#ddd5f5"><div style="width:{p}%;height:100%;border-radius:17px;background:#6b5bd6"></div></div><div style="font-size:42px;font-weight:600;color:#181415;margin-top:14px">{t}</div></div></div>' for w, p, t in [("Week 1", 15, "less shine"), ("Week 4", 55, "calmer, more even"), ("Week 8", 100, "spots fading")])}</div>"""))

# 20. Ceci ou cela
C.append(("Ceci ou cela", f"""
<div style="position:absolute;left:0;top:0;width:540px;height:1920px;background:#ebc9c6"></div>
<div style="position:absolute;left:540px;top:0;width:540px;height:1920px;background:#ffd36e"></div>
<div style="position:absolute;left:0;right:0;top:250px;text-align:center;font-size:76px;font-weight:900;color:#181415">Which one is for you?</div>
<div style="position:absolute;left:40px;width:460px;top:700px;text-align:center;color:#181415"><div style="font-size:190px;font-weight:900">B3</div><div style="font-size:60px;font-weight:900">Niacinamide</div><div style="font-size:42px;margin-top:20px;line-height:1.4">oily · redness<br>sensitive OK</div></div>
<div style="position:absolute;left:580px;width:460px;top:700px;text-align:center;color:#181415"><div style="font-size:190px;font-weight:900">C</div><div style="font-size:60px;font-weight:900">Vitamin C</div><div style="font-size:42px;margin-top:20px;line-height:1.4">dull · dark spots<br>morning use</div></div>
<div style="position:absolute;left:440px;top:1300px;width:200px;height:200px;border-radius:50%;background:#181415;color:#fff;font-size:70px;font-weight:900;display:flex;align-items:center;justify-content:center">or</div>"""))


def main():
    from render import Engine
    eng = Engine()
    pg = eng.br.new_page(viewport={"width": 1080, "height": 1920})
    for i, (name, body) in enumerate(C, 11):
        path = os.path.join(base.ROOT, "engine", "_concept.html")
        open(path, "w", encoding="utf-8").write(base.BASE.replace("%s", body))
        pg.goto("file://" + path); pg.evaluate("document.fonts.ready"); pg.wait_for_timeout(120)
        open(os.path.join(base.OUT, f"{i:02d}.jpg"), "wb").write(pg.screenshot(type="jpeg", quality=92))
        print(i, name)
    eng.close()


if __name__ == "__main__":
    main()
