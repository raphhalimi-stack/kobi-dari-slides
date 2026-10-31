# RAPHAEL SOCIAL V1 — LIVRABLE DU 31/10/2026
Légende : [FAIT] vérifié · [PRÊT] préparé, non activé · [ACCORD] attend la validation du PDG

---

## 1. PREUVE DE SUSPENSION [FAIT]

- Commit `825000e` sur `main` du dépôt raphhalimi-stack/kobi-dari-slides, 31/10/2026 15 h 15 (Séoul) :
  https://github.com/raphhalimi-stack/kobi-dari-slides/commit/825000e79542029e9feee0e78868805b339f24d1
- Les 18 reels en attente (31/10 au 08/11) ont été déplacés à l'identique de `queue.json` vers `queue_suspended.json`.
  Kobi : k_qz02, k_mf01b, k_rl02, k_mf03, k_qz03, k_ie03, k_rl03, k_mf04, k_qz04.
  Dari : d_mf03, d_mf01b, d_sk03, d_qz03, d_mf04, d_sk04, d_qz04, d_mf05, d_sk05.
- Vérification sur GitHub après le push : `queue.json` contient 44 éléments, tous déjà publiés ; **0 élément en attente**.
  `publish.py` ne lit que `queue.json` : il répondra « Rien à publier maintenant. ».
- Aucune suppression. Les 44 publications en ligne et les fichiers vidéo ne sont pas touchés.
- Retour arrière : recopier les `items` de `queue_suspended.json` dans `queue.json` (mode d'emploi dans `SUSPENSION.md`).
- Note : le workflow « Publication Instagram » continue de tourner toutes les 30 min, mais à vide. Il n'a pas été désactivé, pour ne rien casser.

---

## 2. DIAGNOSTIC DES STATISTIQUES

État actuel [FAIT]
- Aucune statistique Instagram n'est collectée, nulle part (ni dépôt, ni base de la holding, ni CORE).
- Les jetons IG_TOKEN_KOBI et IG_TOKEN_DARI existent (secrets GitHub) et permettent de publier. Leur droit de lecture des statistiques (« insights ») n'a jamais été testé.
- Supermetrics (Instagram Insights) est installé dans tes connecteurs mais non connecté.

Correctif préparé [PRÊT], sur la branche `social-v1` (rien en production)
- `stats.py` : lecture seule. Pour chaque compte : abonnés, nombre de publications, type de compte ; pour chaque publication : permalien, likes, commentaires, vues, portée, partages, sauvegardes, interactions, temps de visionnage des reels. Si l'API refuse une métrique, il la retire et continue. Aucun jeton n'apparaît jamais dans les journaux.
- Visibilité publique : un média est « en ligne » si l'API le retrouve avec un permalien ; le compte est public s'il est professionnel (un compte professionnel Instagram ne peut pas être privé). Ce qu'aucune API ne montre : une éventuelle réduction de distribution. Elle se lit dans l'app, « Statut du compte ».
- `.github/workflows/stats.yml` : un relevé par jour à 20 h 47 (Séoul), plus un mode « check » manuel qui teste les jetons et le droit insights.
- Sorties : `stats/latest.json`, `stats/history/AAAA-MM-JJ.json`, `stats/RAPPORT.md` (tableau lisible).
- Test : logique vérifiée sur une API simulée (22 publications Kobi, métrique refusée gérée, ID invalide « 20_intro » détecté). Pas encore testé contre Instagram : un workflow ne peut être lancé que depuis `main`.

Supervision dans RAPHAEL CORE [PRÊT]
- Réutilise l'existant : la file de chantier de CORE (exécuteur core-dev-0, `docs/chantier/FILE.md`).
- Mission proposée (fichier `social-v1/MISSION_CORE_SOCIAL.md`) : un écran « Social » dans CORE qui lit `stats/latest.json` (dépôt public, aucun secret nécessaire) et affiche par compte : abonnés, dernières publications avec permalien, vues, partages, sauvegardes, heure du relevé, erreurs, et l'évolution sur 7 jours.

---

## 3. NOUVEAUX FORMATS (prototypes dans `social-v1/proto/`)

Deux identités distinctes, fini le texte sur fond uni :
- **Kobi** : studio crème et rose poudré, encre cacao, serif éditorial en italique, produits mis en scène avec ombres et reflets. Calme, premium, « beauty editor ».
- **Dari** : nuit de Séoul, marine profond et corail, typo capitale très grasse, néons, cartes de métro, tickets. Énergique, urbain.

| Format | Accroche (1re seconde) | Visuel clé | Pourquoi ça peut marcher [HYP] |
|---|---|---|---|
| K1 « Scan it » | « I scanned a viral Korean sunscreen. » + laser qui balaie le produit + prix | Produit réel + score animé + verdict par type de peau | Recherches massives sur les crèmes solaires coréennes ; démontre l'app sans la vendre |
| K2 « ₩ vs ₩₩₩ » | « ₩9,900 vs ₩210,000 » + VS qui claque | Deux produits côte à côte, % d'ingrédients communs | Les « dupes » sont un des sujets beauté les plus partagés |
| K3 « Label X-ray » | « Your toner says this. Do you know what it means? » + loupe sur 진정 | Étiquette coréenne qui se traduit sous la loupe | Utile, très sauvegardable, propre à Kobi |
| D1 « Seoul for ₩10,000 » | Compteur ₩0 → ₩10,000 qui démarre, brochette qui surgit | Ticket de caisse animé, vraie bouffe de rue | Prix concrets = curiosité jusqu'au total |
| D2 « Don't do this » | « Tourists do this on the subway every day. » + tampon ✕ rouge | Scène du métro, siège rose | La peur de mal faire fait commenter et partager |
| D3 « Line 2 secrets » | « Skip Hongdae. Get off here instead. » + ligne 2 qui s'allume | Carte de ligne, 3 arrêts qui s'allument | Contre-pied d'un lieu célèbre, très sauvegardé |

Fichiers : planches 3 écrans par format (`*_planche.png`), images plein format (`*_0/1/2.png`), et 3 aperçus animés de l'accroche (`K1_accroche.mp4`, `D1_accroche.mp4`, `D2_accroche.mp4`). Source unique et paramétrable : `social-v1/formats.html`.

À noter : les chiffres des prototypes (score 92/100, 78 %, prix) sont des exemples de mise en page. En production, chaque chiffre vient d'une source réelle (fiche produit, prix relevé, Kobi lui-même).

---

## 4. MONTÉE EN CHARGE : 3 PUBLICATIONS ORIGINALES PAR JOUR ET PAR COMPTE [PRÊT]

- `build_slots.py` génère `queue_proposed.json` : 3 créneaux par compte et par jour, formats en rotation, sans jamais toucher `queue.json`. Contrôles intégrés : jamais deux fois le même format d'affilée, 2 h minimum entre deux posts d'un compte, jamais Kobi et Dari à la même minute.
- Créneaux (Séoul) : Kobi 08:40 · 12:40 · 21:10 ; Dari 08:10 · 13:10 · 20:20.
- Brouillon généré : 84 créneaux du 09/11 au 22/11, statut « brouillon », aucun programmé.
- Production nécessaire : 6 épisodes originaux par jour (3 par compte). Le moteur de rendu actuel (HTML → Playwright → ffmpeg) sait déjà faire ; les nouveaux gabarits sont dans `formats.html`.

---

## 5. CALENDRIER PROPOSÉ (rien n'est programmé)

Je recommande une montée progressive plutôt que 3 par jour d'un coup, parce que les comptes sont neufs et ont déjà subi une rafale le 25/10.

| Période | Rythme par compte | Contenu | Condition pour passer à l'étape suivante |
|---|---|---|---|
| Dès ton accord | 0 | Activation de la mesure, premier relevé, vérification « Statut du compte » | Relevé qui fonctionne, permaliens ouverts |
| 3 jours | 1 par jour (soir) | Les 3 nouveaux formats, une fois chacun | Statistiques relevées à J+1 sur chaque post |
| 7 jours | 2 par jour (midi, soir) | Rotation des 3 formats | Vues médianes en hausse vs les anciens reels |
| Ensuite | 3 par jour | Rotation, on garde les 2 meilleurs formats, on teste 1 nouveau par semaine | Revue du lundi |

Point à trancher : la consigne 102 (« rien avant la recette du 14/11 ») bloque tout ce calendrier jusqu'au 14/11. Soit tu l'assouplis pour les réseaux, soit le calendrier démarre le 15/11.

---

## 6. CE QUI ATTEND TON ACCORD

1. **Fusionner la branche `social-v1` dans `main`.** Ajoute `stats.py`, `stats.yml`, `build_slots.py`, `queue_proposed.json` et les prototypes. Lecture seule côté Instagram, rien publié.
2. **Lancer une première fois le mode « check »** du workflow Statistiques, pour tester le droit insights des jetons. Si refusé : régénérer les jetons avec ce droit (à faire par toi, dans Meta for Developers).
3. **Activer le relevé quotidien** (20 h 47).
4. **Créer la mission CORE « Écran Social »** dans la file de chantier de RAPHAEL CORE.
5. **Valider les 6 formats** (ou en écarter), et la source des visuels réels : photos de produits et de rues prises par toi ou ta copine, ou images générées par IA (à préciser, coût éventuel).
6. **Décider de la consigne 102** pour les réseaux, et de la date de reprise.
7. **Valider le calendrier** et le rythme de départ (je recommande 1 par jour).
8. **Reprise des publications** : seulement sur ton feu vert explicite.
9. Point d'attention : le dépôt est **public**. Les statistiques et les brouillons y seront visibles par tous. Le passer en privé casserait la publication actuelle (Instagram télécharge les vidéos depuis l'adresse publique du dépôt) : à ne faire qu'avec un autre hébergement des médias.
