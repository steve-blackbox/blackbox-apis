"""
Base de connaissances du moteur de calibrage Dirac Live ART / StormAudio.

⚠️ LIGNE ROUGE RESPECTÉE DANS CE FICHIER (voir PROJETS_FUTURS.md, alerte de
Claude sur le droit d'auteur) : aucune règle ci-dessous ne vient d'un livre
protégé (ex. Anthony Grimani), d'un manuel constructeur spécifique au client,
ou d'une documentation Dirac/StormAudio reproduite telle quelle. Chaque
constante cite sa source réelle :

  - [StormAudio] = reformulation avec nos propres mots des fiches techniques
    publiques "ART — Advanced guidelines & tips" et de l'article de
    vulgarisation ce-sphere.com, déjà vérifiées par recherche web dans la
    conversation Claude source (PROJETS_FUTURS.md, messages 39-40/52).
    Sources : https://support-stormaudio.atlassian.net/wiki/spaces/SUP/pages/359923716/ART+-+Advanced+guidelines+tips
              https://www.ce-sphere.com/home/setting-up-dirac-live-art-with-stormaudio-isr-fusion-20-44824441
  - [Acoustique générale] = physique du son / psychoacoustique de base,
    savoir scientifique public (pas une œuvre soumise à droit d'auteur) :
    modes propres d'une pièce rectangulaire, effet de précédence (Haas),
    perception des graves peu directionnelle sous ~80-120 Hz, masquage
    fréquentiel, seuil de détection d'un écart de niveau (~1 dB).
  - [Steve] = règles empiriques déjà rapportées par Steve dans la
    conversation source, explicitement marquées "à valider" tant qu'aucun
    test en aveugle n'a été fait (voir README.md).
  - [Hypothèse] = indice trouvé sur un forum par Claude, présenté comme
    "un indice, pas une preuve" — jamais utilisé seul pour une
    recommandation ferme, seulement en complément.

Aucune "mémorisation" de documents entiers n'est simulée ici : c'est
exactement le piège que Claude avait signalé dans la conversation source
(un LLM ne retient pas un livre sur simple demande). Ce fichier assume
plutôt un rôle de règles explicites, courtes, et traçables — recommandation
de Claude reprise telle quelle (message 36 : "un socle de règles écrit par
vous, court et ordonné... rédigé avec vos mots, c'est votre propriété").
"""

from __future__ import annotations

from models import CitedStudy, EvidenceLevel, Role

# ---------------------------------------------------------------------------
# 1. Domaine de fonctionnement d'ART vs Dirac Live classique [StormAudio]
# ---------------------------------------------------------------------------
ART_UPPER_BOUND_HZ = 150.0
"""En dessous de cette fréquence, ART corrige le trajet direct ET une partie
des réflexions de la pièce avec l'aide d'autres enceintes (traitement
multi-enceintes). Au-dessus, c'est la correction Dirac Live classique
(mono-enceinte). Ce n'est ni un filtre de croisement ni une gestion de
graves traditionnelle. [StormAudio]"""

DIRAC_DEFAULT_LOW_FLOOR_HZ = 50.0
"""Dirac ne propose pas de borne basse sous cette valeur par défaut — déjà
trop bas pour certaines petites enceintes. [StormAudio]"""

RECOMMENDED_OVERLAP_HZ = 30.0
"""Chevauchement de plage recommandé entre une enceinte et son/ses
caisson(s) de support, plutôt qu'une bande stricte confiée à un seul
groupe — trop contraindre la plage empêche ART d'obtenir une réponse
lisse. [StormAudio]"""

MAX_FULL_RANGE_SUPPORT_HZ = 150.0
"""Une enceinte capable de descendre suffisamment peut servir de support
jusqu'à cette fréquence. [StormAudio]"""

# ---------------------------------------------------------------------------
# 2. Niveaux de support : une limite de liberté, pas un réglage 1:1 [StormAudio]
# ---------------------------------------------------------------------------
SUPPORT_LEVEL_DEFAULT_DB = -18.0
SUPPORT_LEVEL_MIN_DB = -24.0   # augmente l'usage du groupe par ART
SUPPORT_LEVEL_MAX_DB = -6.0    # réduit l'usage du groupe par ART
SUPPORT_LEVEL_STEP_DB = 0.5
"""Dirac accepte un pas de 0,5 dB (confirmé empiriquement par Steve sur son
système [Steve]). ⚠️ Claude reste prudent : le seuil d'audibilité d'un écart
de niveau est généralement cité autour de ~1 dB [Acoustique générale] — un
réglage à 0,5 dB près n'a donc d'effet garanti que sur les filtres calculés,
pas forcément à l'oreille. À ne proposer que si un déclencheur ci-dessous
est rempli, jamais comme réglage systématique."""

SUPPORT_LEVEL_TRIGGERS = [
    "réponses très différentes entre enceintes équivalentes (ex. surround "
    "gauche/droite)",
    "une enceinte ou un caisson visiblement sursollicité comme support",
    "écart important visible sur le graphique de dispersion",
    "direction sonore perceptible dans les graves (le caisson de support "
    "se localise, alors qu'il ne devrait pas)",
]
"""[Steve] — déclencheurs concrets proposés pour juger qu'un réglage fin du
niveau de support est "nécessaire", plutôt que de l'appliquer par défaut."""

# ---------------------------------------------------------------------------
# 3. Hiérarchie de support par rôle [StormAudio]
# ---------------------------------------------------------------------------
STORM_AUDIO_SUPPORT_HIERARCHY: dict[Role, list[str]] = {
    Role.LFE: [
        "autres caissons (meilleur support)",
        "façade (si caissons insuffisants)",
        "enceintes arrière (dernier recours)",
    ],
    Role.FRONT_LEFT: ["caissons (LFE)", "l'autre enceinte de façade"],
    Role.FRONT_RIGHT: ["caissons (LFE)", "l'autre enceinte de façade"],
    Role.CENTER: [
        "⚠️ à éviter comme support : porte déjà beaucoup de signal (dialogues)",
    ],
    Role.SURROUND_LEFT: ["caissons d'abord", "puis enceintes à hauteur d'oreille"],
    Role.SURROUND_RIGHT: ["caissons d'abord", "puis enceintes à hauteur d'oreille"],
    Role.SURROUND_BACK_LEFT: ["caissons d'abord", "puis enceintes à hauteur d'oreille"],
    Role.SURROUND_BACK_RIGHT: ["caissons d'abord", "puis enceintes à hauteur d'oreille"],
    Role.HEIGHT_FRONT_LEFT: ["façade (support de l'avant)"],
    Role.HEIGHT_FRONT_RIGHT: ["façade (support de l'avant)"],
    Role.HEIGHT_REAR_LEFT: ["surrounds (support de l'arrière)"],
    Role.HEIGHT_REAR_RIGHT: ["surrounds (support de l'arrière)"],
}

SEPARATE_GROUPS_FOR_DIFFERENT_CAPABILITIES = True
"""StormAudio recommande de séparer les enceintes de capacités différentes
(surtout les caissons) en groupes individuels, au prix d'une configuration
plus lourde — un groupe partage courbe cible + groupes de support +
réglages, mais chaque enceinte garde ses propres filtres. [StormAudio]"""

# ---------------------------------------------------------------------------
# 4. Courbes cibles connues — noms publics de l'industrie, déjà en
#    possession de Steve (fichiers .targetcurve réels sur son poste, voir
#    PROJETS_FUTURS.md suite 9). Ce ne sont QUE des noms de standards
#    publiquement documentés et débattus dans l'industrie audio (pas un
#    contenu protégé reproduit). [Acoustique générale] / [StormAudio]
# ---------------------------------------------------------------------------
TARGET_CURVES_BY_ROLE: dict[str, list[str]] = {
    "façade (G/D/centre)": [
        "Harman +4 dB bass gain (référence neutre très documentée)",
        "LCR Cinema Target StormAudio (si profil cinéma assumé)",
    ],
    "caisson(s) / LFE": [
        "Subwoofer Cinema Target StormAudio",
        "Harman +6 dB ou +8 dB bass gain (si le client veut plus d'impact)",
    ],
    "surround / hauteur": [
        "Surround Cinema Target StormAudio",
    ],
    "courbe personnalisée": [
        "'courbe maison' — à construire avec le client selon son goût, "
        "jamais recommandée sans une première mesure de référence",
    ],
}

TARGET_CURVE_COHERENCE_RULE = (
    "Garder la façade (gauche/droite/centre) alignée sur la même courbe "
    "cible ; réserver les écarts marqués (plus de gain de graves, cible "
    "différente) aux enceintes dont la situation le justifie clairement "
    "(surrounds, hauteurs, caisson dédié). Une courbe cible différente par "
    "enceinte mal appliquée casse la cohérence de timbre entre enceintes."
)
"""[Steve] — risque identifié pour le levier n°1 (courbes cibles
individuelles par enceinte), à respecter dans toute recommandation."""

# ---------------------------------------------------------------------------
# 5. Diagnostic différentiel des anomalies de courbe [Acoustique générale]
#    + [StormAudio] pour la conséquence pratique sur l'égalisation
# ---------------------------------------------------------------------------
MODAL_REGION_UPPER_BOUND_HZ = 300.0
"""Au-dessus de cette fréquence approximative, une anomalie de courbe est
plus probablement due au haut-parleur ou à une réflexion locale qu'à un
mode propre de la pièce entière. Seuil indicatif, pas une limite stricte."""

DIP_PROBABLE_CAUSES = [
    "mode de la pièce (annulation/addition liée aux dimensions)",
    "annulation par proximité d'un mur ou d'un meuble proche de l'enceinte",
    "problème de phase entre l'enceinte et un caisson de support",
]
"""[Acoustique générale] — un creux peut avoir plusieurs causes distinctes,
qui appellent chacune une action différente (voir diagnostic_engine.py).
Un creux dû à une pure annulation physique NE SE CORRIGE PAS par
l'égalisation : il faut déplacer l'enceinte ou le caisson en cause."""

PEAK_PROBABLE_CAUSES = [
    "mode de la pièce (addition liée aux dimensions)",
    "réflexion précoce renforçant une bande de fréquence (surface dure proche)",
]

# ---------------------------------------------------------------------------
# 6. Les cinq facteurs mesurables de l'immersion [StormAudio + Acoustique
#    générale] — décomposition déjà validée dans la conversation source
#    (message 32/52) de la promesse commerciale "faire croire que la scène
#    se passe dans la pièce du client" en éléments concrets et priorisables.
# ---------------------------------------------------------------------------
IMMERSION_FACTORS = [
    (
        "Réponse en fréquence (surtout les graves)",
        "Ce que Dirac Live / ART corrige le mieux.",
    ),
    (
        "Alignement temporel enceintes/caissons (distances, phase)",
        "Donne la cohérence de l'image sonore ; vérifiable par mesure.",
    ),
    (
        "Localisation et enveloppement (angles/hauteurs, Atmos)",
        "Surtout une question de placement physique — l'égalisation seule "
        "ne la corrige pas.",
    ),
    (
        "Premières réflexions et durée de réverbération de la pièce",
        "Dépendent des matériaux ; l'égalisation ne corrige que "
        "partiellement — traitement acoustique recommandé en complément.",
    ),
    (
        "Niveaux et dynamique entre enceintes",
        "Un volume cohérent entre toutes les enceintes, condition de base.",
    ),
]

PRIORITY_ORDER = [
    "1. Placement physique des enceintes et caissons",
    "2. Traitement acoustique de base (premières réflexions, coins pour "
    "les graves)",
    "3. Réglages logiciels ART (groupes de support, courbes cibles, "
    "niveaux)",
]
"""[StormAudio + Acoustique générale] — rappel explicite (déjà noté dans la
conversation source) : la correction logicielle ne remplace pas un bon
placement ; un algorithme qui ne ferait que régler Dirac plafonnerait vite.
Le rapport généré doit toujours présenter les recommandations dans cet
ordre de priorité, pas seulement les réglages ART."""

# ---------------------------------------------------------------------------
# 7. Prérequis techniques à vérifier avant toute recommandation [StormAudio]
# ---------------------------------------------------------------------------
TECHNICAL_PREREQUISITES = [
    "Firmware du processeur à jour",
    "Logiciel Dirac Live à jour",
    "Licence ART active (incluse de base sur les processeurs StormAudio "
    "commandés après le 1er janvier 2023, à vérifier sinon)",
    "Connexion internet active lors du calcul (les filtres ART sont "
    "calculés sur les serveurs Dirac, pas localement)",
    "Idéalement 9 positions de mesure pour un home cinéma (StormAudio "
    "recommande ce nombre ; ART profite particulièrement des points "
    "supplémentaires)",
]

# ---------------------------------------------------------------------------
# 8. Garde-fous commerciaux et de sécurité — à inclure dans CHAQUE rapport
# ---------------------------------------------------------------------------
MANDATORY_DISCLAIMERS = [
    "Ce rapport propose des réglages à appliquer vous-même dans votre "
    "logiciel Dirac Live / StormAudio ART. Aucun fichier .liveproject "
    "n'est généré ni injecté : cette voie a été testée et s'est révélée "
    "bloquée par la protection du format (voir PROJETS_FUTURS.md).",
    "Les plages de fréquence recommandées doivent toujours être vérifiées "
    "contre la fiche technique de chaque enceinte avant application : une "
    "plage trop basse mal choisie peut endommager du matériel.",
    "L'immersion sonore reste subjective et dépend de votre pièce : ce "
    "rapport propose un processus et des points de mesure avant/après, "
    "pas un résultat garanti.",
    "Ce service n'est pas affilié à Dirac ni à StormAudio ; il propose des "
    "réglages 'pour Dirac Live ART', sans lien officiel avec l'éditeur.",
]

# ---------------------------------------------------------------------------
# 9. Études de référence (psychoacoustique, acoustique des salles, matériaux)
# ---------------------------------------------------------------------------
# Demande explicite de Steve : "cherche aussi toutes les dernières etudes
# acoustiques dispo et celle sur l'interpretation du son par la cerveau,
# les etudes sur l'effet des materiaux sur le son". Chaque entrée ci-dessous
# a été retrouvée par une vraie recherche web (navigateur, pages Bing lues
# et décodées), PAS par mémorisation. Deux niveaux de vérification existent
# et sont indiqués honnêtement dans le champ `verification` :
#   - "titre/auteurs/revue/DOI confirmés" = la référence existe bel et bien
#     (page de résultats ou métadonnées lues), mais le texte intégral n'a
#     pas pu être ouvert (paywall éditeur : PNAS, JASA, ScienceDirect, MDPI
#     renvoient une erreur d'accès direct) — le `takeaway` reste donc
#     général et prudent.
#   - "résumé/introduction lus" = le contenu a été réellement ouvert et lu
#     (cas d'arXiv, en libre accès), le `takeaway` peut être plus précis.
# Objectif : no invention. Si une étude ne peut pas être vérifiée, elle
# n'apparaît pas ici plutôt que d'être approximée.

CITED_STUDIES: list[CitedStudy] = [
    # --- Psychoacoustique / comment le cerveau interprète le son ---
    CitedStudy(
        domain="psychoacoustique",
        title="Statistics of natural reverberation enable perceptual "
        "separation of sound and space",
        venue_or_authors="Traer C. & McDermott J.H., laboratoire "
        "d'audition du MIT",
        year="2016",
        source_url="https://doi.org/10.1073/pnas.1612524113 (PNAS)",
        verification="titre/auteurs/revue/DOI confirmés par recherche web ; "
        "texte intégral non ouvert (PNAS bloque l'accès direct, erreur "
        "403)",
        takeaway="Papier de référence en neurosciences auditives : le "
        "cerveau s'appuie sur les régularités statistiques de la "
        "réverbération naturelle pour séparer ce qui vient de la source "
        "sonore de ce qui vient de l'espace. Cohérent avec l'objectif "
        "formulé par Steve ('faire croire au cerveau que la scène du "
        "film est réelle') : une réverbération qui respecte ces "
        "régularités statistiques naturelles serait plus crédible pour "
        "le cerveau qu'une réverbération simplement 'plate' ou "
        "sur-corrigée. À creuser avant d'en faire une règle numérique.",
    ),
    CitedStudy(
        domain="psychoacoustique",
        title="Early reflections and spatial perception (effet sur "
        "l'intelligibilité, l'enveloppement et la perception de largeur/"
        "distance de la source)",
        venue_or_authors="Introduction sourcée (références [7],[8]) d'un "
        "article sur l'estimation des premières réflexions (FF-PHALCOR)",
        year="2023",
        source_url="https://arxiv.org/abs/2312.13707",
        verification="résumé/introduction lus directement (arXiv, accès "
        "libre)",
        takeaway="Confirme un principe déjà présent dans la conversation "
        "source : les premières réflexions ne sont pas qu'un défaut à "
        "supprimer, elles contribuent à l'intelligibilité de la parole, "
        "au sentiment d'enveloppement et à l'évaluation de la largeur, "
        "du volume perçu et de la distance de la source. Un traitement "
        "acoustique qui éliminerait toutes les premières réflexions "
        "pourrait donc nuire à l'immersion plutôt que l'améliorer — "
        "argument pour favoriser la diffusion plutôt que l'absorption "
        "totale sur certaines surfaces (point déjà noté comme "
        "[Acoustique générale] dans ce fichier).",
    ),
    CitedStudy(
        domain="acoustique des salles",
        title="Perception of reverberation in small rooms: a literature "
        "study",
        venue_or_authors="Kaplanis N. et al.",
        year="non confirmé précisément (article de synthèse, cité dans "
        "la littérature AES)",
        source_url="ResearchGate (page de publication trouvée par "
        "recherche web, PDF non ouvert)",
        verification="titre/auteurs confirmés par recherche web ; contenu "
        "non ouvert",
        takeaway="Pertinent en priorité pour le home cinéma car porte "
        "spécifiquement sur les petites pièces (contrairement à la "
        "plupart des études d'acoustique de salle, pensées pour des "
        "salles de concert). À rouvrir en priorité si une V2 approfondit "
        "la partie théorique du rapport.",
    ),
    CitedStudy(
        domain="acoustique des salles",
        title="Spatial Hearing in Rooms and Effects of Reverberation "
        "(chapitre d'ouvrage)",
        venue_or_authors="Springer, collection sur l'audition spatiale",
        year="2020",
        source_url="https://doi.org/10.1007/978-3-030-57100-9_9",
        verification="titre/éditeur/DOI confirmés par recherche web ; "
        "contenu non ouvert",
        takeaway="Référence académique à vérifier plus tard si besoin "
        "d'approfondir la théorie ; non utilisée pour une règle précise "
        "dans la V1 du moteur faute d'avoir pu lire le contenu.",
    ),
    # --- Effet des matériaux sur le son ---
    CitedStudy(
        domain="matériaux",
        title="Acoustic metamaterials for sound absorption and "
        "insulation in buildings",
        venue_or_authors="MDPI (revue à comité de lecture, open access)",
        year="2022",
        source_url="https://www.mdpi.com/2076-3417/12/9/4446",
        verification="titre/revue confirmés par recherche web ; page "
        "bloquée à l'ouverture directe (erreur 403) malgré le statut "
        "open access affiché",
        takeaway="Illustre une approche récente (métamatériaux) qui va "
        "au-delà des mousses/laines classiques pour absorber les basses "
        "fréquences dans un volume réduit — pertinent pour les petites "
        "pièces de home cinéma où l'espace de traitement est limité. "
        "Reste un indice de tendance, pas une spécification exploitable "
        "telle quelle.",
    ),
    CitedStudy(
        domain="matériaux",
        title="A review on innovative measures for improving sound "
        "absorption performance",
        venue_or_authors="ScienceDirect (revue de littérature)",
        year="2024",
        source_url="https://www.sciencedirect.com/science/article/pii/"
        "S0360132324000921",
        verification="titre/revue confirmés par recherche web ; page "
        "bloquée à l'ouverture directe",
        takeaway="Confirme qu'il existe une littérature scientifique "
        "active et récente (2024) sur l'optimisation des matériaux "
        "absorbants — à rouvrir si la V2 du service veut recommander des "
        "matériaux précis plutôt que de simples catégories ('panneaux "
        "absorbants dans les coins', 'diffuseurs en zone de première "
        "réflexion').",
    ),
    CitedStudy(
        domain="matériaux",
        title="Analysis and Optimization of the Noise Reduction "
        "Performance of Sound-Absorbing Materials in Complex "
        "Environments",
        venue_or_authors="ResearchGate",
        year="2024-2025",
        source_url="https://www.researchgate.net/publication/385910458",
        verification="titre confirmé par recherche web ; contenu non "
        "ouvert",
        takeaway="Étude la plus récente trouvée sur ce domaine lors de "
        "cette recherche ; signale que le sujet reste actif en 2024-2025, "
        "mais son contenu précis reste à vérifier avant toute "
        "exploitation dans une recommandation.",
    ),
]
"""Important : cette liste est un point de départ documentaire, pas une
base scientifique validée. Aucune valeur numérique du moteur
(diagnostic_engine.py) ne repose sur ces études tant que leur contenu
complet n'a pas été lu et confirmé — voir README.md, section Limites."""
