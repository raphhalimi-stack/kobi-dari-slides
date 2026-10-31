# Suspension des reels programmés — 31/10/2026

Décision du PDG (Raphael), 31/10/2026 : suspendre tous les reels Kobi et Dari encore en attente.
Réversible, aucune suppression, publications déjà en ligne non touchées.

- Les 18 éléments en attente (31/10 au 08/11) ont été déplacés de `queue.json` vers `queue_suspended.json`, à l'identique.
- `publish.py` ne lit que `queue.json` : plus rien n'est dû, il répond « Rien à publier maintenant. ».
- Fichiers vidéo et épisodes : inchangés.

Pour reprendre (uniquement sur autorisation du PDG) : recopier `items` de `queue_suspended.json` à la fin de `queue.json`, en ajustant les dates `not_before` si besoin.
