# Prototype — Moteur de diagnostic Dirac Live ART / StormAudio

Prototype Python, écrit dans cette session à la demande de Steve ("si toi
aussi tu es en mesure de creer cet algorithme à partir de ces elements fait
le"), à partir des éléments déjà documentés dans
`../PROJETS_FUTURS.md` (conversation Claude.ai partagée sur le calibrage
audio home cinéma Dirac Live ART / StormAudio).

## Ce que c'est — et ce que ce n'est pas

C'est un **moteur de règles traçable** : il lit des courbes de mesure et des
informations de système, puis produit un rapport texte de recommandations,
en citant pour chaque recommandation sa source réelle.

Ce n'est **pas** :
- un outil qui génère ou modifie un fichier `.liveproject` (cette voie a
  été testée par Steve et s'est heurtée à la protection du format —
  `liveproject_reader.py` ne fait que *lire* ce format, jamais l'écrire
  ni le modifier, voir plus bas) ;
- une reproduction d'un livre ou d'une documentation protégée : chaque
  règle de `knowledge_base.py` cite sa source réelle (directive StormAudio
  publique, principe acoustique de domaine public, retour d'expérience de
  Steve marqué « à valider », ou simple indice de forum jamais utilisé
  seul). Voir l'alerte sur le droit d'auteur déjà documentée dans
  `../PROJETS_FUTURS.md`.

## Structure des fichiers

| Fichier | Rôle |
|---|---|
| `models.py` | Structures de données (enceintes, mesures, pièce, recommandations, anomalies, rapport, études citées). |
| `knowledge_base.py` | Toutes les règles et sources (directives StormAudio ART, hiérarchie de support, courbes cibles, diagnostic différentiel, 5 facteurs d'immersion, prérequis techniques, disclaimers obligatoires, études scientifiques citées). |
| `diagnostic_engine.py` | Détection d'anomalies sur les courbes, calcul des modes propres de la pièce, diagnostic différentiel, génération des recommandations. |
| `report_generator.py` | Transforme un `DiagnosticReport` en rapport texte livrable au client. |
| `image_reader.py` | Lit automatiquement les courbes depuis une capture d'écran Dirac Live (calibration d'axes + détection de la couleur de la courbe, méthode de digitalisation de graphique) — remplace la saisie manuelle des points fréquence/dB. |
| `liveproject_reader.py` | Rétro-ingénierie du fichier binaire propriétaire `.liveproject` généré par Dirac Live : lit les métadonnées, décode les 13 flux audio de mesure (Ogg Vorbis) et les 104 blocs de mesure fréquence/magnitude bruts. Lecture seule — voir docstring d'en-tête pour la carte complète du format et ses limites. |
| `example_run.py` | Démonstration complète sur un système 5.1.4 fictif (2 niveaux de service). |
| `tests/test_diagnostic_engine.py` | Tests unitaires (`unittest`, bibliothèque standard uniquement). |

## Comment l'exécuter

Aucune dépendance externe pour le moteur de diagnostic (pas de numpy, pas
de pytest) — seulement Python 3. `image_reader.py` nécessite Pillow,
`liveproject_reader.py` ne nécessite que la bibliothèque standard (le
décodage audio optionnel des flux Ogg s'appuie sur `imageio-ffmpeg`).

```bash
cd 01_LA_SOUTE_A_CASH/PROJETS_FUTURS_calibrage_audio

# Démonstration complète (2 rapports : niveau Essentiel et Approfondi)
python3 example_run.py

# Tests unitaires
python3 -m unittest discover -s tests -t . -v

# Lecture d'un fichier .liveproject réel (résumé en console)
python3 liveproject_reader.py "/chemin/vers/fichier.liveproject"
```

## Les deux niveaux de service (repris de la conversation source)

- **Essentiel** : le client fournit les courbes mesurées (captures Dirac
  lues à l'œil et saisies, ou export si l'outil le permet) et la liste du
  matériel. Le diagnostic reste parfois ouvert (plusieurs causes possibles)
  faute de dimensions de pièce.
- **Approfondi** : ajoute les dimensions de la pièce et le placement des
  enceintes (`RoomInfo`). Permet de calculer les modes propres et de
  trancher si une anomalie mesurée correspond à un mode de pièce probable.

## Limites honnêtes (à ne pas vendre comme réglé)

- **Lecture d'image calibrée sur un seul jeu de captures.** `image_reader.py`
  fait bien de la digitalisation de graphique automatique (calibration
  d'axes + détection de couleur de courbe), mais la calibration des axes
  en pixels a été validée sur les 8 captures fournies par Steve le
  29/09/2026 (résolution 2794x1538, interface Dirac Live en français) —
  une résolution ou une version d'interface différente demande de
  revérifier les repères pixel → valeur avant de faire confiance au
  résultat.
- **`liveproject_reader.py` ne lit que ce qui est en clair.** Le fichier
  `.liveproject` contient une zone chiffrée (~25-60 % du fichier selon la
  taille, entropie mesurée à 8,00 bits/octet) qui contient probablement
  les filtres de correction finaux (FIR/IIR) — volontairement non
  explorée (limite éthique assumée, pas technique : la déchiffrer serait
  un contournement de protection). Par ailleurs, la correspondance exacte
  "quel bloc de mesure (0-7) correspond à quelle enceinte précisément"
  n'a pas pu être établie avec certitude (voir docstring du module).
- **Modes de pièce : axiaux uniquement.** Les modes tangentiels et obliques
  (plus faibles, plus nombreux) sont volontairement ignorés pour un MVP
  lisible. Une anomalie qui ne correspond à aucun mode axial calculé n'est
  pas forcément « sans cause liée à la pièce » pour autant.
- **Détection d'anomalies simple.** `detect_anomalies` compare chaque point
  à une tendance de référence calculée en anneau autour de lui (voir
  commentaire de `_ring_baseline` dans `diagnostic_engine.py` pour le
  détail et l'historique du bug corrigé). Ce n'est pas un analyseur de
  courbes certifié ; les seuils (`threshold_db=4.0`, rayons de l'anneau)
  sont des choix de prototype, pas des valeurs validées sur de vraies
  mesures de terrain.
- **Pas de garantie de résultat perceptif.** Les études citées dans
  `knowledge_base.CITED_STUDIES` ont été trouvées par une vraie recherche
  web (navigateur), mais la plupart n'ont pu être vérifiées que par leur
  titre/auteurs/revue/DOI — la plupart des éditeurs académiques (PNAS,
  JASA, ScienceDirect, MDPI) bloquent l'accès direct au texte intégral
  depuis cet environnement. Seul l'article arXiv (accès libre) a été lu
  en détail. Aucune valeur numérique du moteur ne repose sur une étude
  dont le contenu complet n'a pas été vérifié.
- **"La pièce génère ~50 % du rendu sonore"** (retour d'expérience de Steve,
  voir `../PROJETS_FUTURS.md`) n'est pas encore sourcé par une étude
  indépendante ; traité comme `EvidenceLevel.RETOUR_EXPERIENCE_STEVE`,
  pas comme un fait établi.
- **Aucun lien officiel avec Dirac ou StormAudio.** Voir
  `knowledge_base.MANDATORY_DISCLAIMERS`, inclus dans chaque rapport généré.

## Pistes V2 (non commencées)

- Modes tangentiels/obliques en plus des axiaux.
- Relier `image_reader.py`/`liveproject_reader.py` au moteur de diagnostic
  (`diagnostic_engine.py`) pour passer directement d'une capture d'écran
  ou d'un fichier `.liveproject` à un rapport, sans étape manuelle entre
  les deux.
- Vérifier le contenu complet des études listées dans `CITED_STUDIES`
  (accès bibliothèque universitaire ou version préprint/auteur) avant
  d'en tirer des règles numériques.
- Base de données de fiches techniques d'enceintes courantes pour éviter
  la saisie manuelle des plages de fréquence constructeur.
- Base de connaissances comparative entre fichiers `.liveproject`
  analysés (plusieurs mesures/pièces), dans la lignée de ce que Steve
  avait fait faire à Gemini (voir `../PROJETS_FUTURS.md`, "suite 10" à
  "suite 13") — mais à partir de données réellement extraites et
  vérifiables plutôt que d'une mémoire de modèle IA non sauvegardée.
