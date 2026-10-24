#!/usr/bin/env python3
"""Publication Instagram (API officielle, Instagram Login) depuis la file queue.json.

Chaque exécution publie, pour chaque compte, le prochain élément dont l'heure est passée
(un seul par compte et par exécution : le rythme vient du cron toutes les 30 min).
Les stories (kind=story) d'un même lot partent ensemble.

  python publish.py                 # mode file d'attente (cron)
  python publish.py --check         # vérifie les tokens
  python publish.py --dry-run       # montre ce qui partirait maintenant
  python publish.py --key kobi:c:00_launch   # force un élément précis
Secrets : IG_TOKEN_KOBI, IG_TOKEN_DARI. État : state2.json (commité par le workflow).
"""
import argparse, datetime, json, os, sys, time, urllib.error, urllib.parse, urllib.request

GRAPH = "https://graph.instagram.com/v23.0"
REPO = "raphhalimi-stack/kobi-dari-slides"
ROOT = os.path.dirname(os.path.abspath(__file__))
STATE = os.path.join(ROOT, "state2.json")
SHA = os.environ.get("GITHUB_SHA", "main")


def raw(path):
    return f"https://raw.githubusercontent.com/{REPO}/{SHA}/{path}"


def cdn(path):
    return f"https://cdn.jsdelivr.net/gh/{REPO}@{SHA}/{path}"


def api(method, path, params, token):
    params = dict(params, access_token=token)
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}"
    req = urllib.request.Request(url if method == "POST" else f"{url}?{data.decode()}",
                                 data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=90) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {e.read().decode(errors='replace')}") from None


def token_for(acc):
    t = os.environ.get(f"IG_TOKEN_{acc.upper()}")
    if not t:
        raise RuntimeError(f"secret IG_TOKEN_{acc.upper()} manquant")
    return t


def wait(cid, token, tries=60, delay=5):
    for _ in range(tries):
        r = api("GET", cid, {"fields": "status_code,status"}, token)
        sc = r.get("status_code")
        if sc == "FINISHED":
            return
        if sc in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"conteneur {cid}: {r}")
        time.sleep(delay)
    raise RuntimeError(f"conteneur {cid}: toujours en cours")


def publish_item(it):
    tok = token_for(it["account"])
    kind = it["kind"]
    if kind == "carousel":
        kids = []
        for p in it["media"]:
            r = api("POST", "me/media", {"image_url": raw(p), "is_carousel_item": "true"}, tok)
            kids.append(r["id"])
        for k in kids:
            wait(k, tok, delay=3)
        r = api("POST", "me/media", {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": it["caption"]}, tok)
    elif kind == "reel":
        last = None
        for url in (cdn(it["media"][0]), raw(it["media"][0])):
            try:
                r = api("POST", "me/media", {"media_type": "REELS", "video_url": url, "caption": it["caption"],
                                             "share_to_feed": "true", "thumb_offset": "400"}, tok)
                wait(r["id"], tok, tries=90)
                break
            except Exception as e:
                last = e; print("   essai vidéo échoué:", url, e); r = None
        if r is None:
            raise last
    elif kind == "story":
        r = api("POST", "me/media", {"media_type": "STORIES", "image_url": raw(it["media"][0])}, tok)
        wait(r["id"], tok, delay=3)
    else:
        raise RuntimeError("type inconnu " + kind)
    time.sleep(8)
    for attempt in range(12):
        try:
            pub = api("POST", "me/media_publish", {"creation_id": r["id"]}, tok)
            return pub["id"]
        except RuntimeError as e:
            if "2207027" in str(e) or "9007" in str(e) or "is_transient\":true" in str(e):
                time.sleep(10 + attempt * 5)
                continue
            raise
    raise RuntimeError("media_publish : toujours pas prêt après plusieurs essais")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--key")
    a = ap.parse_args()
    if a.check:
        for acc in ("kobi", "dari"):
            try:
                print(acc, api("GET", "me", {"fields": "user_id,username,account_type,media_count"}, token_for(acc)))
            except Exception as e:
                print(acc, "ERREUR", e)
        return
    q = json.load(open(os.path.join(ROOT, "queue.json"), encoding="utf-8"))
    st = json.load(open(STATE)) if os.path.exists(STATE) else {"posted": {}, "errors": {}}
    now = datetime.datetime.now(datetime.timezone.utc)
    todo = []
    if a.key:
        todo = [it for it in q if it["key"] == a.key]
    else:
        for acc in ("kobi", "dari"):
            due = [it for it in q if it["account"] == acc and it["key"] not in st["posted"]
                   and datetime.datetime.fromisoformat(it["not_before"]) <= now
                   and st["errors"].get(it["key"], 0) < 3]
            if not due:
                continue
            first = due[0]
            if first["kind"] == "story":
                todo += [it for it in due if it["kind"] == "story" and it.get("batch") == first.get("batch")]
                nxt = [it for it in due if it["kind"] != "story"]
                if nxt:
                    todo.append(nxt[0])
            else:
                todo.append(first)
    if not todo:
        print("Rien à publier maintenant.")
        return
    fails = 0
    for it in todo:
        print(f"* {it['account']} {it['kind']} {it['key']}")
        if a.dry_run:
            continue
        try:
            mid = publish_item(it)
            st["posted"][it["key"]] = {"id": mid, "at": now.isoformat()}
            print("  OK", mid)
        except Exception as e:
            fails += 1
            st["errors"][it["key"]] = st["errors"].get(it["key"], 0) + 1
            st.setdefault("last_error", {})[it["key"]] = str(e)[:600]
            print("  ERREUR", e)
        json.dump(st, open(STATE, "w"), indent=1)
        time.sleep(5)
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
