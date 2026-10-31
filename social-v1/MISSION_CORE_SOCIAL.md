# Mission proposée pour RAPHAEL CORE : écran « Social » (à valider par le PDG)

Type : nouvel écran, lecture seule. Aucun secret, aucun appel payant.

Source des données : https://raw.githubusercontent.com/raphhalimi-stack/kobi-dari-slides/main/stats/latest.json
(produit chaque jour à 20 h 47 Séoul par le workflow « Statistiques Instagram » ; format décrit dans stats.py).

Affichage, par compte (@kobiapp.cc, @dariapp.cc) :
1. Abonnés, nombre de publications, heure du dernier relevé (alerte si plus de 26 h).
2. Les 10 dernières publications : titre, date, statut (en_ligne / introuvable / erreur), vues, portée, partages, sauvegardes, lien qui ouvre le post.
3. Médiane des vues sur 7 jours et comparaison avec la semaine précédente (stats/history/).
4. Erreurs de collecte en rouge (droit insights refusé, jeton expiré).
5. Bandeau « Publications suspendues » tant que queue_suspended.json existe et que queue.json n'a rien en attente.

Critères d'acceptation :
- l'écran s'affiche sur Samsung (390 px) et PC ;
- avec un latest.json vide ou absent, l'écran dit « Aucun relevé » sans planter ;
- chaque lien ouvre la bonne publication ;
- aucun jeton ni secret n'est lu ni affiché.

Mise en ligne : selon la charte de CORE (tests verts, vu sur Samsung, retour arrière prêt).
