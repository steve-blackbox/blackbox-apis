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
| `models.py` | Structures de données (enceintes, mesures, pièce, recommandations, anomalies, rapport, études citées, brevets cités). |
| `knowledge_base.py` | Toutes les règles et sources (directives StormAudio ART, hiérarchie de support, courbes cibles, diagnostic différentiel, 5 facteurs d'immersion, prérequis techniques, disclaimers obligatoires, études scientifiques citées, fondamentaux home cinéma de fond — section 10, trois brevets Dirac Research lus en texte intégral — sections 11 à 13, limite physique de la correction linéaire face à la distorsion non-linéaire des haut-parleurs — section 14, fiches techniques officielles du matériel réel de Steve — section 15). |
| `diagnostic_engine.py` | Détection d'anomalies sur les courbes, calcul des modes propres de la pièce, diagnostic différentiel, génération des recommandations **et calculs précis chiffrés** (niveau de Support Level à 0,5 dB près à partir de l'écart RÉELLEMENT mesuré entre 2 enceintes groupées — y compris un groupage personnalisé/croisé déclaré via `support_group_assignments`, plage F-support Low/High par enceinte, points de contrôle de courbe cible pour les pics confirmés comme modes de pièce — jamais pour un creux, limite physique). 100% générique : s'adapte à n'importe quelle configuration cliente, aucune valeur codée en dur pour un système particulier. |
| `report_generator.py` | Transforme un `DiagnosticReport` en rapport texte livrable au client. |
| `image_reader.py` | Lit automatiquement les courbes depuis une capture d'écran Dirac Live (calibration d'axes + détection de la couleur de la courbe, méthode de digitalisation de graphique) — remplace la saisie manuelle des points fréquence/dB. |
| `liveproject_reader.py` | Rétro-ingénierie du fichier binaire propriétaire `.liveproject` généré par Dirac Live : lit les métadonnées, décode les 13 flux audio de mesure (Ogg Vorbis) et les 104 blocs de mesure fréquence/magnitude bruts. Lecture seule — voir docstring d'en-tête pour la carte complète du format et ses limites. |
| `cartographie_modale.py` | Cartographie EMPIRIQUE des modes de pièce à partir d'un vrai `.liveproject` : cohérence spatiale des anomalies sur les 13 positions de micro + corrélation croisée entre enceintes/caissons (sans calcul théorique de dimensions de pièce). Voir docstring d'en-tête pour la méthode et ses limites. |
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
- **Section 10 de `knowledge_base.py` (fondamentaux home cinéma) est un
  socle de référence, pas encore câblée dans `diagnostic_engine.py`.**
  Apprentissage de fond fait à la demande de Steve (psychoacoustique,
  zones fréquentielles d'une pièce/fréquence de Schroeder, bass
  management, distinction rendu Atmos vs correction Dirac/Audyssey,
  absorption), sourcé sur Wikipedia et les guides officiels dolby.com
  (via leurs archives Wayback Machine, le site live ayant bloqué les
  requêtes automatisées pendant cette recherche). Volontairement sans
  formule numérique inventée quand la source ne la donnait pas (ex. pas
  de valeur chiffrée de fréquence de Schroeder) ni de tableau de
  coefficients d'absorption mal extrait d'une page source.
- **Sections 11 à 13 de `knowledge_base.py` (fondements brevetés d'ART)
  décrivent un mécanisme mathématique général lu dans trois vrais
  brevets Dirac Research (US9781510B2, US8213637B2, US9426600B2, textes
  intégraux), pas les réglages exacts du produit commercial actuel.**
  Aucune décompilation ni rétro-ingénierie du logiciel Dirac Live n'a
  été faite ou ne sera faite : seule la lecture de documents de
  divulgation publique (brevets accordés) est utilisée comme source
  "interne". Pas encore câblées dans `diagnostic_engine.py`.
- **Section 14 de `knowledge_base.py` (limite physique de la correction
  linéaire face à la distorsion non-linéaire des haut-parleurs) est un
  raisonnement logique assemblé à partir de deux pages Wikipedia lues
  séparément, pas une citation unique d'une source qui l'énoncerait
  telle quelle.** Voir la docstring de `LINEAR_EQ_CANNOT_FIX_NONLINEAR_
  DISTORTION` pour le détail de cette nuance. Pas encore câblée dans
  `diagnostic_engine.py`.

## Pistes V2 (non commencées)

- Modes tangentiels/obliques en plus des axiaux.
- Calculer une vraie fréquence de Schroeder par pièce (au lieu du seuil
  fixe `MODAL_REGION_UPPER_BOUND_HZ = 300.0`) si `RoomInfo` collecte un
  jour le RT60 ou une estimation de celui-ci — voir
  `knowledge_base.SCHROEDER_TRANSITION_CONCEPT`.
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
- **Trous identifiés (03/10, bilan de compréhension globale demandé par
  Steve) mais non comblés par manque de priorisation explicite** :
  directivité/dispersion du haut-parleur selon le type de driver,
  diffusion acoustique (3e pilier à côté de l'absorption et des modes,
  diffuseurs Schroeder/QRD), RT60 réellement mesuré (pas seulement le
  concept de fréquence de Schroeder), électronique de l'amplificateur
  (puissance, impédance de charge, headroom, écrêtage), câblage et
  alimentation électrique (bruit de fond, mise à la terre), chaîne
  numérique en amont (codecs, HDMI eARC, gigue/jitter). À reprendre si
  Steve en fait la demande, avec la même méthode de recherche sourcée.

