#!/usr/bin/env python3
"""Ajoute des reels à la file : 1 reel/jour/compte. Kobi 10:00 UTC (19:00 KST), Dari 10:30 UTC.
Usage : python build_week.py 2026-10-26 kobi:k_mf01,k_rl01,... dari:d_mf01,...
Les épisodes déjà dans la file sont ignorés ; les éléments non publiés en pause (2099) sont retirés."""
import datetime, json, os, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HOUR = {"kobi": (10, 0), "dari": (10, 30)}
VIDEO = {"ni01": "v2/episodes/kobi_ni01.mp4"}
CAPFILE = {"ni01": "ni01"}


def trim_tags(cap, n=5):
    lines = cap.rstrip().split("\n")
    if lines and lines[-1].startswith("#"):
        lines[-1] = " ".join(lines[-1].split()[:n])
    return "\n".join(lines)


def main():
    start = datetime.date.fromisoformat(sys.argv[1])
    q = json.load(open(os.path.join(ROOT, "queue.json"), encoding="utf-8"))
    q = [it for it in q if not it["not_before"].startswith("2099")]
    have = {it["key"] for it in q}
    for spec in sys.argv[2:]:
        acc, ids = spec.split(":")
        for d, eid in enumerate(ids.split(",")):
            key = f"{acc}:r:{eid}"
            if key in have:
                continue
            ep = json.load(open(os.path.join(ROOT, f"content/episodes/{CAPFILE.get(eid, eid)}.json"), encoding="utf-8"))
            vid = VIDEO.get(eid, f"v2/episodes/{eid}.mp4")
            assert os.path.exists(os.path.join(ROOT, vid)), vid
            h, m = HOUR[acc]
            when = datetime.datetime.combine(start + datetime.timedelta(days=d), datetime.time(h, m), datetime.timezone.utc)
            q.append({"key": key, "account": acc, "kind": "reel", "media": [vid], "thumb": 1500,
                      "caption": trim_tags(ep["caption"]), "not_before": when.isoformat()})
    q.sort(key=lambda it: it["not_before"])
    json.dump(q, open(os.path.join(ROOT, "queue.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for it in q:
        print(it["not_before"], it["key"])


if __name__ == "__main__":
    main()
