#!/usr/bin/env python3
"""Publie les carrousels Kobi & Dari sur Instagram via l'API officielle (Instagram Login).

Modes :
  python publish.py --today                 # les posts dont la date = aujourd'hui (Séoul)
  python publish.py --date 2026-10-26       # les posts d'une date précise
  python publish.py --decks 0-4             # publie tout de suite les decks 0..4 des deux comptes
  python publish.py --decks 0-4 --account kobi
  python publish.py --check                 # vérifie les tokens (username de chaque compte)
Ajouter --dry-run pour tout simuler sans rien publier.

Secrets attendus en variables d'environnement :
  IG_TOKEN_KOBI, IG_TOKEN_DARI  (tokens longue durée)
  IG_USER_KOBI, IG_USER_DARI    (identifiants Instagram, optionnels : "me" fonctionne)
L'état (posts déjà publiés) est dans state.json, commité par le workflow pour éviter les doublons.
"""
import argparse, json, os, sys, time, datetime, urllib.request, urllib.parse, urllib.error
from zoneinfo import ZoneInfo

GRAPH = "https://graph.instagram.com/v23.0"
RAW = "https://raw.githubusercontent.com/raphhalimi-stack/kobi-dari-slides/main/slides/"
TZ = ZoneInfo("Asia/Seoul")
ROOT = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(ROOT, "state.json")


def api(method, path, params, token):
    params = dict(params, access_token=token)
    data = urllib.parse.urlencode(params).encode()
    url = f"{GRAPH}/{path}"
    req = urllib.request.Request(url if method == "POST" else f"{url}?{data.decode()}",
                                 data=data if method == "POST" else None, method=method)
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {path} -> HTTP {e.code}: {body}") from None


def creds(account):
    token = os.environ.get(f"IG_TOKEN_{account.upper()}")
    user = os.environ.get(f"IG_USER_{account.upper()}") or "me"
    if not token:
        raise RuntimeError(f"Secret IG_TOKEN_{account.upper()} manquant")
    return token, user


def wait_finished(cid, token, tries=30):
    for _ in range(tries):
        r = api("GET", cid, {"fields": "status_code,status"}, token)
        if r.get("status_code") == "FINISHED":
            return
        if r.get("status_code") in ("ERROR", "EXPIRED"):
            raise RuntimeError(f"Conteneur {cid}: {r}")
        time.sleep(4)
    raise RuntimeError(f"Conteneur {cid}: toujours en cours")


def publish_carousel(post, dry_run=False):
    token, user = creds(post["account"])
    urls = [RAW + s for s in post["slides"]]
    if dry_run:
        print(f"  [dry-run] {post['handle']} {post['deck']} : {len(urls)} slides, légende {len(post['caption'])} car.")
        return "dry-run"
    children = []
    for u in urls:
        r = api("POST", f"{user}/media", {"image_url": u, "is_carousel_item": "true"}, token)
        children.append(r["id"])
    for cid in children:
        wait_finished(cid, token)
    r = api("POST", f"{user}/media", {"media_type": "CAROUSEL", "children": ",".join(children),
                                       "caption": post["caption"]}, token)
    wait_finished(r["id"], token)
    r = api("POST", f"{user}/media_publish", {"creation_id": r["id"]}, token)
    return r["id"]


def load_state():
    return json.load(open(STATE_FILE)) if os.path.exists(STATE_FILE) else {"posted": {}}


def save_state(state):
    json.dump(state, open(STATE_FILE, "w"), indent=2, ensure_ascii=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--today", action="store_true")
    ap.add_argument("--date")
    ap.add_argument("--decks", help="ex. 0-4 ou 3")
    ap.add_argument("--account", choices=["kobi", "dari"])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()

    if a.check:
        for acc in ("kobi", "dari"):
            try:
                token, user = creds(acc)
                print(acc, api("GET", user, {"fields": "id,username,account_type"}, token))
            except Exception as e:
                print(acc, "ERREUR:", e)
        return

    schedule = json.load(open(os.path.join(ROOT, "schedule.json")))
    if a.decks:
        lo, _, hi = a.decks.partition("-")
        lo, hi = int(lo), int(hi or lo)
        sel = [p for p in schedule if lo <= int(p["deck"][:2]) <= hi]
    else:
        date = a.date or datetime.datetime.now(TZ).strftime("%Y-%m-%d")
        sel = [p for p in schedule if p["date"] == date]
    if a.account:
        sel = [p for p in sel if p["account"] == a.account]
    if not sel:
        print("Rien à publier.")
        return

    state = load_state()
    errors = 0
    for post in sel:
        key = f"{post['account']}:{post['deck']}"
        if key in state["posted"] and not a.force:
            print(f"- {key} déjà publié ({state['posted'][key]}), ignoré")
            continue
        print(f"* {post['handle']} {post['deck']} ({len(post['slides'])} slides)")
        try:
            mid = publish_carousel(post, a.dry_run)
            print(f"  OK media id {mid}")
            if not a.dry_run:
                state["posted"][key] = mid
                save_state(state)
                time.sleep(20)  # laisse respirer l'API entre deux posts
        except Exception as e:
            errors += 1
            print(f"  ERREUR: {e}")
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
