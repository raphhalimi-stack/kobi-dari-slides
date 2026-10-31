#!/usr/bin/env python3
"""Prépare une file de 3 publications originales par jour et par compte, SANS la programmer.

N'écrit jamais dans queue.json (la file réelle lue par publish.py).
Écrit queue_proposed.json, un brouillon à valider par le PDG.

  python build_slots.py 2026-11-09 14 [1|2|3]
      -> 14 jours à partir du 09/11, 3 créneaux par compte et par jour, formats en rotation.

Règles intégrées :
  - jamais deux fois le même format d'affilée sur un compte ;
  - au moins 2 h entre deux publications d'un même compte ;
  - Kobi et Dari ne publient jamais à la même minute ;
  - chaque créneau attend un épisode original (champ "episode" à remplir par la production).
"""
import datetime, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
KST = datetime.timezone(datetime.timedelta(hours=9))

# Créneaux en heure de Séoul : matin (trajet), midi (pause), soir (pic d'usage).
SLOTS = {"kobi": ["08:40", "12:40", "21:10"], "dari": ["08:10", "13:10", "20:20"]}
FORMATS = {"kobi": ["k_scan", "k_dupe", "k_xray"], "dari": ["d_10k", "d_dont", "d_line"]}


def build(start, days, per_day=3):
    out = []
    d0 = datetime.date.fromisoformat(start)
    for acc in ("kobi", "dari"):
        rot, n = FORMATS[acc], 0
        for day in range(days):
            date = d0 + datetime.timedelta(days=day)
            for hhmm in SLOTS[acc][-per_day:]:
                h, m = map(int, hhmm.split(":"))
                t = datetime.datetime(date.year, date.month, date.day, h, m, tzinfo=KST)
                fmt = rot[n % len(rot)]; n += 1
                out.append({"key": f"{acc}:r:{fmt}_{date:%m%d}_{h:02d}", "account": acc, "kind": "reel",
                            "format": fmt, "episode": None, "media": [], "caption": "",
                            "not_before": t.astimezone(datetime.timezone.utc).isoformat(), "status": "brouillon"})
    out.sort(key=lambda x: x["not_before"])
    return out


def check(items):
    last = {}
    for it in items:
        t = datetime.datetime.fromisoformat(it["not_before"]); acc = it["account"]
        if acc in last:
            pt, pf = last[acc]
            assert (t - pt) >= datetime.timedelta(hours=2), f"moins de 2 h : {it['key']}"
            assert pf != it["format"], f"format répété : {it['key']}"
        last[acc] = (t, it["format"])
    times = [(i["not_before"]) for i in items]
    assert len(times) == len(set(times)), "deux comptes à la même minute"


if __name__ == "__main__":
    start = sys.argv[1] if len(sys.argv) > 1 else "2026-11-09"
    days = int(sys.argv[2]) if len(sys.argv) > 2 else 14
    per_day = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    items = build(start, days, per_day); check(items)
    json.dump({"statut": "BROUILLON — non programmé, à valider par le PDG", "items": items},
              open(os.path.join(ROOT, "queue_proposed.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print(f"{len(items)} créneaux préparés dans queue_proposed.json (queue.json non modifié).")
