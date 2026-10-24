#!/usr/bin/env python3
"""Construit queue.json : 1 post toutes les 30 min par compte, puis le reste chaque jour à 19h (Séoul).
Usage : python build_queue.py 2026-10-24T22:00:00+00:00"""
import datetime as dt, glob, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
caps = json.load(open(os.path.join(ROOT, "content/captions.json"), encoding="utf-8"))
reels = json.load(open(os.path.join(ROOT, "content/reels.json"), encoding="utf-8"))
stories = json.load(open(os.path.join(ROOT, "content/stories.json"), encoding="utf-8"))
start = dt.datetime.fromisoformat(sys.argv[1])

PLAN = {
    "kobi": {"now": ["c:00_launch", "r:barrier", "c:01_meet_kobi", "r:label", "c:06_korean_label", "r:uv",
                     "c:03_routine", "r:order", "c:02_skin_types", "r:doublecleanse", "c:07_olive_young",
                     "r:oliveyoung", "c:08_spf"],
             "daily": ["c:04_niacinamide", "c:05_centella", "c:09_am_pm", "c:10_mistakes"]},
    "dari": {"now": ["c:00_launch", "r:trashcans", "c:01_meet_dari", "r:landed", "c:04_apps", "r:koreanage",
                     "c:06_taxi", "r:restaurant", "c:08_etiquette", "r:phrases", "c:09_neighbourhoods",
                     "r:tmoney", "c:02_just_landed"],
             "daily": ["c:03_no_arc", "c:05_tmoney", "c:07_convenience", "c:10_daytrips"]},
}


def item(acc, ref, when):
    kind, name = ref.split(":")
    if kind == "c":
        media = sorted(os.path.relpath(p, ROOT) for p in glob.glob(os.path.join(ROOT, f"v2/carousels/{acc}/{name}/*.jpg")))
        assert media, ref
        return {"key": f"{acc}:{ref}", "account": acc, "kind": "carousel", "media": media,
                "caption": caps[f"{acc}/{name}"], "not_before": when.isoformat()}
    r = next(x for x in reels[acc] if x["id"] == name)
    mp4 = f"v2/reels/{acc}_{name}.mp4"
    assert os.path.exists(os.path.join(ROOT, mp4)), mp4
    return {"key": f"{acc}:{ref}", "account": acc, "kind": "reel", "media": [mp4],
            "caption": r["caption"], "not_before": when.isoformat()}


q = []
for acc, plan in PLAN.items():
    for name, frames in stories[acc].items():
        for i in range(1, len(frames) + 1):
            q.append({"key": f"{acc}:s:{name}_{i}", "account": acc, "kind": "story", "batch": "highlights",
                      "highlight": name, "media": [f"v2/stories/{acc}/{name}_{i}.jpg"], "caption": "",
                      "not_before": start.isoformat()})
    for i, ref in enumerate(plan["now"]):
        q.append(item(acc, ref, start + dt.timedelta(minutes=30 * i)))
    day1 = dt.datetime(2026, 10, 26, 10, 0, tzinfo=dt.timezone.utc)  # 19:00 Séoul
    for i, ref in enumerate(plan["daily"]):
        q.append(item(acc, ref, day1 + dt.timedelta(days=i)))
json.dump(q, open(os.path.join(ROOT, "queue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
for it in q:
    if it["kind"] != "story":
        t = dt.datetime.fromisoformat(it["not_before"]).astimezone(dt.timezone(dt.timedelta(hours=9)))
        print(t.strftime("%a %d %b %H:%M"), it["key"])
