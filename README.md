# kobi-dari-slides

Slides des carrousels Instagram de @kobiapp.cc et @dariapp.cc, et publication automatique
via l'API officielle Instagram (GitHub Actions, gratuit).

- `slides/<compte>/<deck>/NN.jpg` — 141 slides 1080×1350
- `profile/kobi.png`, `profile/dari.png` — photos de profil
- `schedule.json` — calendrier (un carrousel par compte et par jour, 19h00 Séoul) + légendes
- `publish.py` — le script de publication
- `.github/workflows/publish.yml` — tous les jours à 10:00 UTC (19:00 Séoul) ; lancement manuel possible

## Secrets GitHub à définir (Settings → Secrets and variables → Actions)

- `IG_TOKEN_KOBI` — token longue durée de @kobiapp.cc
- `IG_TOKEN_DARI` — token longue durée de @dariapp.cc

Les tokens expirent après 60 jours.

## Publier tout de suite un lot

Actions → « Publication Instagram » → Run workflow → `decks` = `0-4` (les 5 premiers de chaque compte).
