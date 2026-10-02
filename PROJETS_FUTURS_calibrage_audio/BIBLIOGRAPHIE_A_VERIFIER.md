# Bibliographie à vérifier avant intégration dans `knowledge_base.py`

## Statut et méthode

Liste fournie par Claude (claude.ai, conversation partagée par Steve), **citée
de mémoire et explicitement non vérifiée par recherche web** — citation
exacte de Claude : *« Je la cite de mémoire, sans vérification en ligne :
contrôle titres, auteurs et années avant de les mettre en base. »*

Ce fichier n'est **pas** une source utilisable telle quelle par le moteur de
diagnostic. C'est un backlog de pistes de recherche, conservé ici pour ne
pas perdre l'information, en attendant vérification réelle référence par
référence (recherche web, confirmation que le titre/auteurs/année/revue
existent bien, puis lecture du contenu si accessible).

Règle du projet (déjà en vigueur pour `knowledge_base.CITED_STUDIES`,
rappelée dans son commentaire d'en-tête) : **si une référence ne peut pas
être vérifiée, elle n'entre pas dans `knowledge_base.py`.** Une fois une
entrée ci-dessous vérifiée, elle doit être déplacée vers
`knowledge_base.CITED_STUDIES` (format `CitedStudy`) ou vers une constante
sourcée appropriée, avec son véritable niveau de vérification honnêtement
indiqué (titre confirmé seulement / résumé lu / texte intégral lu), puis
supprimée d'ici.

Format suggéré par Claude pour la suite, à reprendre une fois une référence
vérifiée : règle ou seuil extrait, source complète, condition d'application,
niveau de confiance (étude contrôlée / recommandation / avis d'expert).

---

## 1. Fondamentaux : perception du son et des salles

- Toole, *Sound Reproduction* (3e éd., 2017) — interaction enceintes/salle,
  perception des résonances, cible en salle, modes graves.
- Toole & Olive (1988), « The modification of timbre by resonances » (JAES)
  — audibilité des résonances (pics plus audibles que creux).
- Toole (2006), « Loudspeakers and Rooms for Sound Reproduction: A
  Scientific Review » (JAES) — réflexions, transition de Schroeder, EQ.
- Olive, Toole, Schuck et al. (1994) — effet de la salle d'écoute sur la
  qualité perçue.
- Olive & Toole (1989), « The detection of reflections in typical rooms »
  (JAES) — seuils d'audibilité des premières réflexions.

## 2. Enceintes : mesure et préférence

- CTA/CEA-2034-A — méthode standard de mesure des enceintes (spinorama).
- Olive (2004), modèle de régression de préférence (AES).
- Olive, Welti & McMullin (2013), cibles de réponse en salle (AES 135) —
  courbe cible de type Harman.
- Fielder & Benjamin (1988), performance des subwoofers (JAES).
- Fryer (1977) et Temme et al. (2014) — audibilité de la distorsion ;
  compléter par Geddes & Lee (2003, AES).

## 3. Graves en petite salle (le cœur d'ART)

- Schroeder (1962 et 1996) — fréquence de transition, densité modale.
  **Le concept lui-même (4 zones fréquentielles, fréquence de Schroeder)
  est déjà sourcé et intégré** dans `knowledge_base.SCHROEDER_TRANSITION_
  CONCEPT`, via https://en.wikipedia.org/wiki/Room_acoustics — vérifié à
  nouveau dans cette passe, aucun delta trouvé. Les papiers originaux de
  Schroeder (1962, 1996) eux-mêmes restent non vérifiés (titres exacts/
  revues à confirmer séparément si besoin de remonter à la source
  primaire plutôt qu'à Wikipedia).
- Bolt (1946), Louden (1971), Bonello (1981), Walker (1996, AES 100) —
  rapports de dimensions de pièce et répartition des modes.
- Allison (1974, JAES) et Allison & Berkovitz (1972) — influence des parois
  sur la puissance rayonnée (SBIR).
- Welti (2002), « How Many Subwoofers Are Enough » (AES 112) et Welti &
  Devantier (2006), « Low-Frequency Optimization Using Multiple
  Subwoofers » (JAES) — nombre et placement des subs.
- Fazenda, Stephenson & Goldberg (2015, JASA) — seuils perceptifs des
  modes selon leur décroissance.
- Fazenda et al. (2012, JAES) — préférence subjective entre méthodes de
  contrôle modal.
- Wankling, Fazenda & Davies (2012) — évaluation subjective des
  paramètres acoustiques graves.
- Karjalainen et al. (2002, JAES) — estimation des paramètres de
  décroissance modale.
- Mäkivirta, Antsalo, Karjalainen & Välimäki (2003, JAES) — égalisation
  modale en graves.
- Celestinos & Nielsen (2008, JAES) — CABS, contrôle actif du grave par
  subs en réseau (le plus proche de l'idée d'ART).

## 4. Correction de salle : théorie

- Neely & Allen (1979) et Mourjopoulos (1985) — invertibilité des réponses
  de salle, limites de l'égalisation.
- Elliott & Nelson (1989, JAES) — égalisation multi-points.
- Hatziantoniou & Mourjopoulos (2000, JAES) — lissage fractionnaire
  d'octave.
- Bharitkar & Kyriakakis, *Immersive Audio Signal Processing* (2006) —
  base d'Audyssey.
- Brännmark et al. (2013, IEEE/ACM TASLP) — compensation MIMO robuste des
  réponses enceintes-salle (à vérifier pour la mention Dirac).
- Nelson & Elliott, *Active Control of Sound* (1992).
- Documentation Dirac : white papers ART, Bass Control, mixed-phase (sur
  dirac.com — contenu non lu par Claude).

## 5. Perception temporelle et spatiale

- Fincham (1985, JAES) et Blauert & Laws (1978, JASA) — audibilité du
  retard de groupe, surtout dans les graves.
- Flanagan, Moore & Stone (2005) — discrimination du retard de groupe.
- ~~Haas (1951) — effet de précédence~~ **VÉRIFIÉ et intégré dans
  `knowledge_base.CITED_STUDIES`** (source : Wikipedia « Precedence
  effect », lu directement). Correction : Claude citait 1951, Wikipedia
  indique 1949 pour Wallach et al. et pour la thèse de Haas, mais aussi
  « un article de 1951 » de Haas plus loin dans la même page —
  incohérence non résolue, les deux dates sont mentionnées dans
  `CITED_STUDIES` avec cette réserve.
- Litovsky et al. (1999, JASA) — effet de précédence, revue de synthèse.
  Reste à vérifier (non trouvé lors de cette passe).
- Blauert, *Spatial Hearing* ; Rumsey, *Spatial Audio* ; Bech & Zacharov,
  *Perceptual Audio Evaluation*.
- Hyunkook Lee — travaux sur la localisation verticale (configurations
  Atmos).

## 6. Normes et recommandations salle / home cinéma

- ITU-R BS.775 (disposition multicanale), BS.2051 (systèmes audio
  avancés, agencements Atmos), BS.1116 (conditions d'écoute, RT60 cible).
- EBU Tech 3276 — salles d'écoute.
- Recommandations Dolby Atmos Home — angles, hauteurs, nombre d'enceintes.
- CEDIA / CTA RP22 et CEB22 — bonnes pratiques d'installation immersive.
- THX — conventions de croisement (~80 Hz) et niveaux. **Partiellement
  vérifié** : le chiffre 80 Hz et le principe (filtre passe-haut 12 dB/
  octave Butterworth, filtre passe-bas 24 dB/octave Linkwitz-Riley,
  alignement -6 dB au croisement, plage usuelle 40-120 Hz) sont déjà
  sourcés et intégrés dans `knowledge_base.BASS_MANAGEMENT_CROSSOVER_
  PRINCIPLE` via https://en.wikipedia.org/wiki/Bass_management — vérifié
  à nouveau dans cette passe, aucun delta trouvé. En revanche, cette
  source attribue le choix de 80 Hz aux directives Dolby et aux AVR bon
  marché à crossover fixe, **pas spécifiquement à une norme THX** — donc
  l'attribution précise "convention THX" reste à vérifier séparément si
  elle doit être citée nommément.
- ISO 3382 — mesure du temps de réverbération (RT60). Existence de la
  norme confirmée (ISO 3382-1 « Acoustics — Measurement of room acoustic
  parameters — Part 1: Performance spaces », https://www.iso.org/
  standard/40979.html, titre uniquement — contenu payant non consulté).

## 7. Mesure

- Farina (2000, AES 108) et Müller & Massarani (2001, JAES) — mesure par
  sweeps logarithmiques (protocole derrière REW et Dirac).
- Documentation REW — waterfall, RT60 par bande, fonction de transfert.

## 8. Ouvrages de référence acoustique

- Everest & Pohlmann, *Master Handbook of Acoustics*.
- Cox & D'Antonio, *Acoustic Absorbers and Diffusers*.
- Kuttruff, *Room Acoustics*.
- Howard & Angus, *Acoustics and Psychoacoustics*.
- Rossing, *Springer Handbook of Acoustics*.

## 9. Matériaux acoustiques : comment ils agissent et se mesurent

(Deuxième liste fournie par Claude, même statut non vérifié que ci-dessus.)

### 9.1 Comment un matériau agit sur l'onde

**Matériaux poreux (laine, mousse, tissus, rideaux, tapis)**
- Delany & Bazley (1970, *Applied Acoustics*) — modèle empirique
  d'absorbants fibreux à partir de la résistivité au passage de l'air.
- Miki (1990, *J. Acoust. Soc. Japan*) — correction du modèle précédent.
- Johnson, Koplik & Dashen (1987, *J. Fluid Mech.*) et Champoux & Allard
  (1991, *J. Appl. Phys.*) — modèle Johnson-Champoux-Allard, base des
  simulateurs modernes.
- Biot (1956, *JASA*) — théorie des milieux poroélastiques.
- Allard & Atalla, *Propagation of Sound in Porous Media*.
- Mechel, *Formulas of Acoustics*.

**Absorbeurs résonants (Helmholtz, panneaux, perforés)**
- Ingard (1953, *JASA*) — plaques perforées.
- Maa (1987 et 1998) — panneaux micro-perforés.
- Fuchs et Kuttruff — absorbeurs à membrane (voir *Room Acoustics*).
- Cox & D'Antonio, *Acoustic Absorbers and Diffusers* — synthèse pratique
  avec les bass traps.

**Diffusion**
- Schroeder (1975, *JASA*) — diffuseurs à résidus quadratiques.
- ISO 17497-1 et -2 — coefficients de diffusion et de dispersion.
- Vorländer & Mommertz (2000, *Applied Acoustics*) — mesure du
  coefficient de diffusion.

**Transmission et isolation (murs, doubles cloisons, vitrages)**
- Loi de masse et fréquence de coïncidence, formalisées par Cremer.
- Sharp (1978) et Davy (2004) — modèles de perte par transmission.
- ISO 10140 et ISO 717 — mesure et indices d'isolation.

### 9.2 Comment on mesure les matériaux

- ISO 354 / ASTM C423 — absorption en chambre réverbérante.
- ISO 10534-2 / ASTM E1050 — tube d'impédance, incidence normale.
- ISO 9053 — résistivité au passage de l'air.
- ISO 11654 — indices d'absorption (αw, NRC).
- Mommertz (1995, *Applied Acoustics*) et ISO 13472 — mesure en place du
  coefficient de réflexion.
- Vorländer & Mommertz — écarts entre absorption en chambre réverbérante
  et valeurs réelles (explique pourquoi un coefficient de fiche technique
  ne se retrouve pas à l'identique chez soi).

### 9.3 Comment un matériau se lit dans une mesure de salle

Tableau fourni par Claude (effet physique → signature dans la mesure →
références), à vérifier avant tout usage :

| Effet physique | Signature dans la mesure | Références citées |
|---|---|---|
| Absorption large bande | Baisse du RT60 et de la queue de réponse | Sabine (1900), Eyring (1930), Millington (1932), ISO 3382 |
| Absorption médiums/aigus (rideaux, tapis, canapé) | RT60 plus court au-dessus de 500 Hz, peu d'effet sous 200 Hz | Cox & D'Antonio, Kuttruff |
| Absorbeur de graves (bass trap, membrane) | Pic modal amorti, décroissance plus rapide à la fréquence ciblée, waterfall plus propre | Fazenda et al., Cox & D'Antonio |
| Réflexion forte (mur nu, vitre) | Pics sur la courbe d'énergie dans le temps (ETC), peigne de filtrage (comb filtering) | Bech (1995 et 1996, JAES), Toole, Olive & Toole (1989) |
| Diffuseur | ETC plus étalée, moins de pics isolés | Schroeder (1975), ISO 17497 |
| Paroi proche d'une enceinte | Creux d'interférence (SBIR) | Allison (1974), Toole |
| Transmission/fuite (cloison légère) | Perte de niveau grave, résonances de paroi | Fahy, Sharp |

Outils d'analyse associés cités : intégration inverse de Schroeder (1965,
pour le RT60), réponse impulsionnelle filtrée par bandes, waterfall,
spectrogrammes. Karjalainen et al. (2002) pour l'estimation de décroissance
par mode ; Fazenda, Stephenson & Goldberg (2015) pour les seuils
d'audibilité associés.

### 9.4 Effets sur la correction (Dirac, Audyssey) — à recouper avec
    `knowledge_base.DIP_PROBABLE_CAUSES` / `PEAK_PROBABLE_CAUSES`

- Un creux causé par une interférence ou une annulation de paroi se
  corrige mal, voire pas du tout, par égalisation (cité : Toole, Neely &
  Allen) — c'est le traitement acoustique qui règle ce cas, pas l'EQ.
- Un pic modal se corrige bien par égalisation. Pour l'allongement de
  décroissance (temps), il faut du contrôle actif (type ART) ou du
  traitement passif.
- Le traitement passif change la mesure de départ : mieux vaut traiter la
  pièce avant de lancer Dirac que l'inverse.

### 9.5 Remarque de Claude sur la suite

Format le plus exploitable selon Claude : table « matériau → plage de
fréquences → effet mesurable → seuil ou critère ». Exemple donné (à
vérifier explicitement, Claude le signale lui-même comme non confirmé) :
« RT60 cible 0,3-0,5 s en salle de cinéma domestique » (ITU-R BS.1116, à
vérifier). Claude précise volontairement ne pas fournir de valeurs
chiffrées d'absorption par matériau (trop variables selon fabricant et
épaisseur) — recommande de se fier aux fiches fabricant ou aux mesures en
tube d'impédance.

## 10. Sources praticiennes (non académiques, magazines/blogs professionnels)

Statut différent des sections 1-9 : ce ne sont pas des études
peer-reviewed mais des articles de professionnels reconnus de
l'industrie du home cinéma. Niveau de preuve à traiter comme « avis
d'expert » / « pratique de l'industrie », jamais comme un fait
scientifique établi.

- **Anthony Grimani** (président de Grimani Systems / PMI Engineering /
  Dimension4 Acoustics), série d'articles sur Residential Systems :
  « Check Your References » (niveau de référence cinéma), « A Fresh
  Perspective on Tuning Reverberant Rooms » (2021), « Get Centered »
  (2023), « Be Ready to Evolve Your Audio » (mai 2026), série « Home
  Theater Week ». Liste complète :
  https://www.residentialsystems.com/author/anthonygrimani
  - ~~« Check Your References »~~ **VÉRIFIÉ et intégré** dans
    `knowledge_base.CINEMA_REFERENCE_LEVEL_PRINCIPLE` et
    `LISTENING_BELOW_REFERENCE_LEVEL_EFFECT` (lu en entier directement,
    18/08/2021). Contenu exploitable : chiffres précis du niveau de
    référence cinéma (85 dB SPL LCR, 85 dB surround, 95 dB caisson à
    -20 dB sous clip), effet perceptif d'une écoute sous ce niveau.
  - Les autres articles de cette liste (Tuning Reverberant Rooms, Get
    Centered, Be Ready to Evolve Your Audio, Home Theater Week) restent
    non vérifiés — à ouvrir un par un si besoin, même URL auteur.
- **Blog technique de PMI, « The Grimani Files »** (diffusion, réglage
  d'une salle, etc.) : https://avspaces-grimani.blogspot.com — non
  vérifié (existence du blog non confirmée lors de cette passe).
- **Cours CEDIA** : « High Performance Home Theater Calibration » et
  « Room Acoustics: Acoustic Treatments ». Claude mentionne un compte
  rendu détaillé par Audioholics, « le plus proche d'un manuel » qu'il
  ait vu — non vérifié (ni l'existence des cours, ni le compte rendu
  Audioholics).
- **Chroniques « Sound Advice »** dans Connected Magazine, par Chase
  Walton (coauteur identifié de l'article Grimani vérifié ci-dessus,
  donc personne réelle confirmée indirectement) — série elle-même non
  vérifiée.
