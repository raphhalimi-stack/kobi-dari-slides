#!/usr/bin/env python3
"""Collecte des statistiques Instagram de @kobiapp.cc et @dariapp.cc (lecture seule).

Ne publie rien, ne modifie rien sur Instagram. Lit, pour chaque compte :
  - le profil (abonnés, nombre de publications, type de compte) ;
  - chaque média publié (state2.json) : permalien, date, type, likes, commentaires ;
  - les statistiques de chaque média (insights) : vues, portée, partages, sauvegardes,
    interactions, et pour les reels le temps de visionnage moyen ;
  - la visibilité publique : le média existe encore, a un permalien, et le compte est
    professionnel (un compte professionnel Instagram ne peut pas être privé).

Écrit :
  stats/latest.json             dernier relevé complet (horodaté)
  stats/history/AAAA-MM-JJ.json un relevé par jour
  stats/RAPPORT.md              rapport lisible par le PDG

  python stats.py            # relevé complet
  python stats.py --check    # vérifie les jetons et les droits « insights »
Secrets : IG_TOKEN_KOBI, IG_TOKEN_DARI (jamais affichés).
"""
import argparse, datetime, json, os, sys, urllib.error, urllib.parse, urllib.request

GRAPH = "https://graph.instagram.com/v23.0"
ROOT = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(ROOT, "stats")
KST = datetime.timezone(datetime.timedelta(hours=9))

MEDIA_FIELDS = "id,media_type,media_product_type,permalink,timestamp,like_count,comments_count,caption"
# Métriques demandées par type ; si l'API en refuse une, on la retire et on réessaie.
METRICS = {
    "REELS": ["views", "reach", "saved", "shares", "total_interactions", "ig_reels_avg_watch_time"],
    "FEED": ["views", "reach", "saved", "shares", "total_interactions"],
    "STORY": ["views", "reach", "shares", "total_interactions"],
}


class ApiError(Exception):
    pass


def api(path, params, token):
    q = urllib.parse.urlencode(dict(params, access_token=token))
    try:
        with urllib.request.urlopen(f"{GRAPH}/{path}?{q}", timeout=60) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        # Jamais de jeton dans les messages d'erreur.
        raise ApiError(f"HTTP {e.code}: {body.replace(token, '***')[:400]}") from None


def token_for(acc):
    t = os.environ.get(f"IG_TOKEN_{acc.upper()}")
    if not t:
        raise ApiError(f"secret IG_TOKEN_{acc.upper()} manquant")
    return t


def media_insights(mid, product, token):
    wanted = list(METRICS.get(product, METRICS["FEED"]))
    refused = []
    while wanted:
        try:
            r = api(f"{mid}/insights", {"metric": ",".join(wanted)}, token)
            vals = {m["name"]: (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
                    for m in r.get("data", [])}
            return vals, refused, None
        except ApiError as e:
            msg = str(e)
            bad = next((m for m in wanted if m in msg), None)
            if bad:
                wanted.remove(bad); refused.append(bad); continue
            return {}, refused, msg
    return {}, refused, "aucune métrique acceptée"


def account(acc, posted, now):
    tok = token_for(acc)
    out = {"account": acc, "ok": True, "errors": [], "media": []}
    try:
        me = api("me", {"fields": "user_id,username,account_type,followers_count,follows_count,media_count"}, tok)
        out["profile"] = me
        out["public"] = me.get("account_type") in ("BUSINESS", "MEDIA_CREATOR", "CREATOR")
    except ApiError as e:
        out.update(ok=False, profile=None, public=None); out["errors"].append(f"profil: {e}")
        return out
    for key, info in sorted(posted.items(), key=lambda kv: kv[1].get("at", "")):
        if not key.startswith(acc + ":"):
            continue
        mid = info.get("id") if isinstance(info, dict) else info
        row = {"key": key, "id": mid, "published_at": info.get("at") if isinstance(info, dict) else None}
        if not mid or not str(mid).isdigit():
            row["status"] = "id_invalide"; out["media"].append(row); continue
        try:
            m = api(mid, {"fields": MEDIA_FIELDS}, tok)
            row.update(status="en_ligne", permalink=m.get("permalink"), type=m.get("media_type"),
                       product=m.get("media_product_type"), likes=m.get("like_count"),
                       comments=m.get("comments_count"))
            vals, refused, err = media_insights(mid, m.get("media_product_type", "FEED"), tok)
            row["insights"] = vals
            if refused: row["metrics_refusees"] = refused
            if err: row["insights_erreur"] = err
        except ApiError as e:
            s = str(e)
            row["status"] = "introuvable" if "does not exist" in s or "HTTP 400" in s else "erreur"
            row["erreur"] = s
        out["media"].append(row)
    return out


def rapport(data):
    L = [f"# Statistiques Instagram — relevé du {data['collected_at_kst']}", ""]
    for a in data["accounts"]:
        p = a.get("profile") or {}
        L.append(f"## @{p.get('username', a['account'])}")
        if not a["ok"]:
            L += ["Relevé impossible : " + "; ".join(a["errors"]), ""]; continue
        L.append(f"Abonnés : {p.get('followers_count')} · Publications : {p.get('media_count')} · "
                 f"Compte {p.get('account_type')} ({'public' if a.get('public') else 'visibilité à vérifier'})")
        L += ["", "| Publication | Publié | Statut | Vues | Portée | Partages | Sauv. | Likes | Lien |",
              "|---|---|---|---|---|---|---|---|---|"]
        for m in reversed(a["media"]):
            i = m.get("insights") or {}
            L.append(f"| {m['key']} | {(m.get('published_at') or '')[:10]} | {m['status']} | {i.get('views', '—')} | "
                     f"{i.get('reach', '—')} | {i.get('shares', '—')} | {i.get('saved', '—')} | {m.get('likes', '—')} | "
                     f"{m.get('permalink') or '—'} |")
        vues = [m["insights"].get("views") for m in a["media"] if isinstance(m.get("insights", {}).get("views"), int)]
        if vues:
            s = sorted(vues); med = s[len(s) // 2]
            L.append(f"\nVues : total {sum(vues)}, médiane {med}, max {max(vues)} sur {len(vues)} publications mesurées.")
        else:
            L.append("\nAucune vue mesurable (droit « insights » absent ou publications trop récentes).")
        L.append("")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--check", action="store_true"); a = ap.parse_args()
    if a.check:
        for acc in ("kobi", "dari"):
            try:
                tok = token_for(acc)
                me = api("me", {"fields": "username,account_type,followers_count,media_count"}, tok)
                print(acc, "profil OK :", me.get("username"), me.get("account_type"), "abonnés", me.get("followers_count"))
                try:
                    api("me/insights", {"metric": "reach", "period": "day"}, tok); print(acc, "droit insights : OK")
                except ApiError as e:
                    print(acc, "droit insights : REFUSÉ ->", e)
            except ApiError as e:
                print(acc, "ERREUR", e)
        return
    st = json.load(open(os.path.join(ROOT, "state2.json")))
    now = datetime.datetime.now(datetime.timezone.utc)
    data = {"collected_at": now.isoformat(), "collected_at_kst": now.astimezone(KST).strftime("%d/%m/%Y %H:%M (Séoul)"),
            "accounts": [account(acc, st["posted"], now) for acc in ("kobi", "dari")]}
    os.makedirs(os.path.join(OUT, "history"), exist_ok=True)
    js = json.dumps(data, ensure_ascii=False, indent=1)
    open(os.path.join(OUT, "latest.json"), "w", encoding="utf-8").write(js)
    open(os.path.join(OUT, "history", now.astimezone(KST).strftime("%Y-%m-%d") + ".json"), "w", encoding="utf-8").write(js)
    open(os.path.join(OUT, "RAPPORT.md"), "w", encoding="utf-8").write(rapport(data))
    print(rapport(data))
    sys.exit(0 if all(x["ok"] for x in data["accounts"]) else 1)


if __name__ == "__main__":
    main()
