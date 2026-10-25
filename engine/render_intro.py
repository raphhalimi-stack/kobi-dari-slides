#!/usr/bin/env python3
"""Carrousels de présentation (1080x1350) : python engine/render_intro.py"""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def rows(items):
    return "".join(f'<div class="row"><div><div class="t">{t}</div><div class="d">{d}</div></div></div>'
                   for t, d in items)


DECKS = {
    "kobi": [
        dict(html='<div class="k">K-BEAUTY · DECODED</div><div class="big" style="font-size:150px;margin-top:50px">Skincare,<br><span class="serif" style="color:var(--acc)">explained.</span></div>'
                  '<div style="font-size:44px;color:var(--sub);margin-top:50px;line-height:1.35;font-weight:500">Short, honest science about what you put on your skin. One reel every day.</div>',
             fl="Swipe →", fr="Launching 25 Nov"),
        dict(html='<div class="k">WHAT YOU\'LL FIND HERE</div><div style="margin-top:40px">' + rows([
            ("Myth or Fact", "The skincare rules everyone repeats, checked."),
            ("Ingredient Explained", "What an ingredient actually does, under the microscope."),
            ("Read the Label", "The Korean words on your products, translated."),
            ("Skin Quiz", "Answer before the timer ends.")]) + '</div>',
             fl="Every day · 7pm KST", fr="Follow"),
        dict(html='<div class="k">THE APP</div><div class="big" style="font-size:110px;margin-top:40px">Kobi reads the label <span class="serif" style="color:var(--acc)">for you.</span></div><div style="margin-top:40px">' + rows([
            ("Scan", "Any product, in any shop."),
            ("Decode", "Every ingredient, checked against your skin type."),
            ("Build", "A routine made for your skin.")]) + '</div>', fl="kobiapp.cc", fr="25 Nov"),
        dict(html='<div class="k">LAUNCH</div><div class="big" style="font-size:190px;margin-top:40px">25<br>Nov.</div>'
                  '<div style="font-size:44px;color:var(--sub);margin-top:40px;line-height:1.35;font-weight:500">Join the waitlist and be first in.</div><div class="cta">Link in bio</div>',
             fl="@kobiapp.cc", fr="Follow for daily reels"),
    ],
    "dari": [
        dict(html='<div class="k">KOREA · MADE EASY</div><div class="big" style="font-size:150px;margin-top:50px">Korea,<br><span class="serif" style="color:var(--acc)">explained.</span></div>'
                  '<div style="font-size:44px;color:var(--sub);margin-top:50px;line-height:1.35;font-weight:500">For everyone visiting or living in Korea. One reel every day.</div>',
             fl="Swipe →", fr="Launching 25 Nov"),
        dict(html='<div class="k">WHAT YOU\'LL FIND HERE</div><div style="margin-top:40px">' + rows([
            ("Myth or Fact: Korea", "What people get wrong about Korea, checked."),
            ("Say it in Korean", "One useful phrase at a time, with pronunciation."),
            ("Korea Quiz", "Culture, food and etiquette. Answer before the timer ends.")]) + '</div>',
             fl="Every day · 7:30pm KST", fr="Follow"),
        dict(html='<div class="k">THE APP</div><div class="big" style="font-size:110px;margin-top:40px"><span class="ko" style="color:var(--acc)">다리</span> means <span class="serif" style="color:var(--acc)">bridge.</span></div><div style="margin-top:40px">' + rows([
            ("Explore", "Places to eat, walk and see, in your language."),
            ("Settle", "Phone, bank, ARC: the practical side, explained."),
            ("Ask", "A concierge that answers with real addresses.")]) + '</div>', fl="dariapp.cc", fr="25 Nov"),
        dict(html='<div class="k">LAUNCH</div><div class="big" style="font-size:190px;margin-top:40px">25<br>Nov.</div>'
                  '<div style="font-size:44px;color:var(--sub);margin-top:40px;line-height:1.35;font-weight:500">Join the waitlist and be first in.</div><div class="cta">Link in bio</div>',
             fl="@dariapp.cc", fr="Follow for daily reels"),
    ],
}

with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={"width": 1080, "height": 1350})
    pg.goto("file://" + os.path.join(ROOT, "engine/intro.html")); pg.evaluate("document.fonts.ready")
    for acc, slides in DECKS.items():
        d = os.path.join(ROOT, "v2/carousels", acc, "20_intro"); os.makedirs(d, exist_ok=True)
        for i, s in enumerate(slides):
            pg.evaluate("o=>show(o)", dict(s, acc=acc)); pg.wait_for_timeout(100)
            pg.screenshot(path=os.path.join(d, f"{i+1:02d}.jpg"), type="jpeg", quality=94)
        print(acc, len(slides))
    b.close()
