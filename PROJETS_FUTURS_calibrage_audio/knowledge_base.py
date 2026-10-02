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
  - [Marantz/Dirac officiel] = reformulation avec nos propres mots (jamais
    de copie du texte original) de FAITS lus directement dans le manuel
    en ligne officiel du Marantz CINEMA 30 et du manuel dédié "Dirac Live"
    de Marantz — le modèle d'ampli réellement utilisé par Steve. Seuls des
    faits non soumis au droit d'auteur sont repris (valeurs numériques,
    existence d'une fonction, plage de réglage) ; aucune phrase du manuel
    n'est reproduite telle quelle, conformément à la ligne rouge ci-dessus.
    Sources : https://manuals.marantz.com/CINEMA30/EU/EN/index.php
              https://manuals.marantz.com/DiracLive/ALL/EN/index.php
  - [Brevet Dirac Research] = faits techniques reformulés avec nos propres
    mots, lus en texte intégral dans un vrai brevet déposé par Dirac
    Research AB (document PDF fourni par Steve, texte extrait et vérifié,
    pas une décompilation du logiciel — un brevet accordé est un document
    de divulgation publique obligatoire, voir section 11 pour le détail
    et les limites). AUCUNE tentative de rétro-ingénierie ou de
    décompilation du logiciel Dirac Live lui-même n'a été faite ou ne
    sera faite : ligne rouge absolue, le brevet est la SEULE source
    technique "interne" légitime utilisée ici.
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

from models import (
    ArtCompatibleDevice,
    CitedPatent,
    CitedStudy,
    DeviceType,
    EvidenceLevel,
    ManufacturerSpecSheet,
    Role,
)

# ---------------------------------------------------------------------------
# 1. Domaine de fonctionnement d'ART vs Dirac Live classique [StormAudio]
# ---------------------------------------------------------------------------
ART_UPPER_BOUND_HZ = 150.0
"""En dessous de cette fréquence, ART corrige le trajet direct ET une partie
des réflexions de la pièce avec l'aide d'autres enceintes (traitement
multi-enceintes). Au-dessus, c'est la correction Dirac Live classique
(mono-enceinte). Ce n'est ni un filtre de croisement ni une gestion de
graves traditionnelle. [StormAudio]

Confirmé et précisé par [Marantz/Dirac officiel] (FAQ "About Dirac Live
Active Room Treatment" du manuel Dirac Live dédié) : la borne haute
officiellement documentée est bien 150 Hz, voir ART_LOWER_BOUND_HZ
ci-dessous pour la borne basse, absente de la documentation StormAudio
consultée initialement."""

ART_LOWER_BOUND_HZ = 20.0
"""Borne basse officielle de la plage de fonctionnement d'ART, absente de
la documentation StormAudio consultée initialement — ajoutée après lecture
du manuel Dirac Live dédié de Marantz, qui indique une plage de
fonctionnement allant de 20 Hz à 150 Hz. [Marantz/Dirac officiel]"""

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

ART_REPLACES_MANUAL_CROSSOVER = True
"""Fait confirmé par lecture directe du manuel Dirac Live (FAQ) : une fois
qu'un filtre ART est actif, il n'est plus possible de régler une fréquence
de croisement (crossover) classique dans le menu de l'ampli — ART calcule
et applique ses propres paramètres à la place, par enceinte ou groupe
d'enceintes. [Marantz/Dirac officiel]"""

ART_NO_MANUAL_TUNING_NEEDED_BY_DEFAULT = True
"""Fait confirmé par lecture directe du manuel Dirac Live (page "Measuring
with Dirac Live software") : le logiciel attribue automatiquement la
valeur optimale de chaque paramètre ART d'après les résultats de mesure ;
aucun réglage manuel n'est nécessaire pour un résultat correct. Un réglage
manuel des paramètres ART reste possible (via le guide du support Dirac)
mais n'est présenté par l'éditeur que comme une option avancée, jamais
comme une étape requise. [Marantz/Dirac officiel]"""

ART_MIN_SPEAKER_COUNT = 2
"""Système minimal documenté pour utiliser ART : deux enceintes ou plus
(stéréo au minimum, pas d'utilisation mono-enceinte). [Marantz/Dirac
officiel]"""

ART_IDEAL_ROOM_AREA_M2 = (12.0, 100.0)
"""Plage de surface de pièce pour laquelle ART est documenté comme
fonctionnant de façon optimale (environ 130 à 1100 pieds carrés), incluant
salons, home cinémas dédiés et régies de studio. Donnée indicative, pas
une limite stricte. [Marantz/Dirac officiel]"""

MANUAL_CROSSOVER_FREQUENCIES_HZ = [
    40, 60, 70, 80, 90, 100, 110, 120, 150, 180, 200, 250,
]
"""Valeurs de fréquence de croisement sélectionnables dans le menu Setup
manuel du Marantz CINEMA 30 (hors ART, ou avant d'activer un filtre ART).
Par défaut, les enceintes Front sont réglées en 'Full Range' (pleine
bande, pas de croisement) et toutes les autres enceintes à 80 Hz. Cette
liste reste pertinente même avec ART : Dirac ne mesure pas automatiquement
le croisement, il doit être réglé manuellement dans ce menu avant ou après
la mesure, pour les enceintes non couvertes par un filtre ART.
[Marantz/Dirac officiel]"""

MANUAL_CROSSOVER_DEFAULT_FRONT = "Full Range"
MANUAL_CROSSOVER_DEFAULT_OTHERS_HZ = 80.0
"""Valeurs par défaut d'usine du Marantz CINEMA 30. [Marantz/Dirac
officiel]"""

ART_LICENSE_TIERS = [
    "Dirac Live Room Correction (seule, sans option)",
    "Dirac Live Room Correction + Bass Control (nécessite un ou plusieurs "
    "caissons déclarés)",
    "Dirac Live Room Correction + Bass Control + ART (palier le plus "
    "complet, celui qui s'applique à un système avec caisson(s) comme "
    "celui de Steve)",
]
"""Paliers de licence Dirac Live documentés officiellement : sans caisson,
seules 'Room Correction' et 'Room Correction + ART' existent ; avec un ou
plusieurs caissons déclarés, un palier intermédiaire 'Bass Control' existe
avant le palier complet avec ART. [Marantz/Dirac officiel]"""

OFFICIAL_RECOMMENDED_MIC = "miniDSP UMIK-1 (ou équivalent USB)"
"""Microphone de mesure explicitement cité par le manuel Marantz pour la
calibration via l'application mobile Dirac Live (le micro intégré du
téléphone n'est pas accepté dans ce cas) — celui déjà utilisé par Steve.
[Marantz/Dirac officiel]"""

DIRAC_FILTERS_DELETED_ON_LAYOUT_CHANGE = True
"""Piège opérationnel confirmé par le manuel : modifier le "Speaker
Layout" de l'ampli après une calibration Dirac supprime automatiquement
le ou les filtres Dirac déjà stockés sur l'ampli. Un filtre existant ne
fonctionne que pour la configuration d'enceintes avec laquelle il a été
calculé. [Marantz/Dirac officiel]"""

MENU_LABEL_STILL_SAYS_AUDYSSEY = True
"""Point de confusion possible dans l'interface du CINEMA 30 : l'entrée de
menu pour lancer la calibration automatique (quel que soit le moteur
réellement utilisé) reste intitulée "Audyssey® Setup" dans le manuel et
probablement dans le menu à l'écran, même lorsque Dirac Live est le moteur
réellement actif sur l'appareil. Ne pas confondre avec une calibration
Audyssey réelle. [Marantz/Dirac officiel]"""

DIRAC_MAX_FILTER_SLOTS = 3
"""Nombre maximum de filtres Dirac Live pouvant être stockés simultanément
sur l'ampli (Slot 1 à 3, sélectionnables depuis le menu Audio - Dirac
Live). Chaque filtre mémorise non seulement la correction acoustique
(réponse en fréquence et temporelle) mais aussi le niveau de sortie et la
distance de chaque enceinte au moment de l'export depuis le logiciel
Dirac Live ; ces réglages sont conservés séparément par source d'entrée.
[Marantz/Dirac officiel]"""

DIRAC_FILTER_BYPASSED_IN_DIRECT_MODES = True
"""En mode d'écoute 'Direct' ou 'Pure Direct', seuls les Distances et
Levels mémorisés par le filtre Dirac Live actif sont appliqués ; le filtre
acoustique (correction de fréquence/temporelle, et donc ART) ne l'est
plus. [Marantz/Dirac officiel]"""

ART_REQUIRES_FULL_BANDWIDTH_LICENSE = True
"""La licence Active Room Treatment ne peut être combinée qu'avec la
licence Dirac Live Room Correction 'Full Bandwidth' ; elle est
incompatible avec la licence Room Correction à bande limitée ('Limited
Bandwidth'). Précision apportée à ART_LICENSE_TIERS ci-dessus.
[Marantz/Dirac officiel]"""

ART_LICENSE_CHECK_METHOD = (
    "Se vérifie uniquement dans le logiciel Dirac Live sur ordinateur "
    "(page 'Filter Design'), jamais depuis l'écran de l'ampli/TV."
)
"""[Marantz/Dirac officiel] — point opérationnel utile pour éviter une
fausse alerte si un client ne voit aucune mention de licence sur l'écran
de l'ampli : l'absence d'indication à l'écran ne veut pas dire que la
licence ART est absente ou inactive."""

ART_LOCKED_SETTINGS_WHEN_ACTIVE = [
    "Speaker Layout - Subwoofer Mode",
    "Speaker Layout - Subwoofer Layout",
    "Advanced - Low Frequency Effects",
    "Audio - Subwoofer Level Adjust",
    "Audio - IMAX Audio Settings (forcé sur 'Auto')",
    "Dialog Enhancer (menu Options)",
    "Tone (menu Options)",
    "Channel Level Adjust (menu Options) — verrouillé spécifiquement par "
    "ART, pas par Bass Control/Bass Management seuls",
]
"""Réglages verrouillés dans le menu de l'ampli dès qu'un filtre Dirac
Live avec Bass Management, Bass Control ou ART est actif (la dernière
ligne ne concerne qu'ART spécifiquement). Pour débloquer ces réglages :
désactiver Dirac Live ou sélectionner un filtre où seul Room Correction
est appliqué. [Marantz/Dirac officiel]"""

DIRAC_DISABLED_WITH_HEADPHONES = True
"""Dirac Live (donc ART) se désactive automatiquement dès qu'un casque
est branché/sélectionné sur l'ampli. [Marantz/Dirac officiel]"""

GRAPHIC_EQ_UNAVAILABLE_WITH_DIRAC = True
"""Le Graphic EQ natif de l'ampli ne peut pas être réglé tant que Dirac
Live est actif (quel que soit le filtre sélectionné). [Marantz/Dirac
officiel]"""

ART_VS_PASSIVE_TREATMENT_PRINCIPLE = (
    "Contrairement aux traitements acoustiques passifs (pièges à basses, "
    "diffuseurs), qui absorbent ou dispersent l'énergie sonore existante, "
    "ART utilise activement les enceintes déjà en place pour réduire les "
    "résonances induites par la pièce, permettant un contrôle du champ "
    "sonore aux très basses fréquences qu'un traitement passif ne peut "
    "pratiquement pas atteindre."
)
"""[Marantz/Dirac officiel] — reformulation du principe de fonctionnement
d'ART par opposition aux solutions passives ; utile pour expliquer à un
client pourquoi ART ne remplace pas un traitement acoustique mais agit de
façon complémentaire, pas concurrente. Rejoint ABSORPTION_GENERAL_PRINCIPLE
(section 10), qui couvre le côté traitement passif."""

# ---------------------------------------------------------------------------
# 2. Niveaux de support : une limite de liberté, pas un réglage 1:1 [StormAudio]
# ---------------------------------------------------------------------------
SUPPORT_LEVEL_DEFAULT_DB = -18.0
SUPPORT_LEVEL_MIN_DB = -24.0   # augmente l'usage du groupe par ART
SUPPORT_LEVEL_MAX_DB = -1.0    # réduit l'usage du groupe par ART
"""⚠️ CORRECTION (03/10, suite 32) : la borne -6.0 initialement notée ici
était une valeur arrondie donnée à titre d'EXEMPLE par le Helpdesk Dirac
dans un autre article ('How-to: ART Channel Group and Support Settings'),
pas la vraie borne du curseur. La section 17 de ce fichier
(ART_PARAMETER_SUPPORT_LEVEL_OFFICIAL_TABLE), trouvée plus tard dans la
même session via l'article 'Dirac Live Active Room Treatment Setup
Guide', confirme la plage légale EXACTE du paramètre : -24 dB à -1 dB.
Corrigé ici pour que les calculs (voir diagnostic_engine.py) utilisent
la vraie limite officielle, pas l'ancienne approximation."""
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
mode propre de la pièce entière. Seuil indicatif, pas une limite stricte.

Ce seuil correspond à ce que la littérature acoustique appelle la zone de
transition autour de la « fréquence de Schroeder » (voir
SCHROEDER_TRANSITION_CONCEPT, section 10 de ce fichier) : en dessous, les
modes propres de la pièce dominent ; au-dessus, le comportement devient
statistique/diffus. 300 Hz reste une valeur fixe de prototype — la vraie
fréquence de Schroeder dépend du volume de la pièce et de son RT60, deux
informations que `RoomInfo` ne collecte pas encore (voir piste V2).
[Acoustique générale]"""

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
    CitedStudy(
        domain="psychoacoustique",
        title="Precedence effect (effet de précédence, dit aussi "
        "'effet Haas')",
        venue_or_authors="Wallach H., Newman E.B. & Rosenzweig M.R. "
        "(description/nommage de l'effet de précédence) ; Helmut Haas "
        "(étude sur la parole, thèse de doctorat datée 1949 par la page, "
        "mais la même page cite aussi 'un article de 1951 de Helmut "
        "Haas' — incohérence interne à la source, non résolue ici)",
        year="1949 (Wallach et al. ; thèse de Haas selon une partie de "
        "la page) et/ou 1951 (article de Haas selon une autre partie de "
        "la même page) — Claude avait indiqué '1951' de mémoire, ce qui "
        "est au moins partiellement confirmé mais incomplet",
        source_url="https://en.wikipedia.org/wiki/Precedence_effect",
        verification="page Wikipedia lue directement en entier "
        "(sections historique + conditions d'occurrence)",
        takeaway="Seuils numériques exploitables pour une future règle "
        "de diagnostic temporel : (1) une réflexion arrivant après "
        "1 ms augmente le niveau perçu et l'ampleur spatiale sans créer "
        "un second évènement auditif ; (2) une réflexion unique arrivant "
        "entre 5 et 30 ms peut être jusqu'à 10 dB plus forte que le son "
        "direct sans être perçue comme un écho distinct ; (3) la fenêtre "
        "de l'effet de précédence va de 2 ms à environ 50 ms pour la "
        "parole, et peut s'étendre jusqu'à ~100 ms pour la musique ; "
        "(4) si le son arrivant en second dépasse le premier d'au moins "
        "15 dB, l'effet de précédence s'effondre (recherche de Langmuir "
        "et al., citée par Wallach et al.). Non câblé dans "
        "diagnostic_engine.py pour l'instant : ces seuils concernent "
        "l'alignement temporel inter-enceintes/caissons, pas la réponse "
        "en fréquence pure, donc une intégration éventuelle toucherait "
        "une logique différente de celle existante (DIP/PEAK_PROBABLE_"
        "CAUSES).",
    ),
]
"""Important : cette liste est un point de départ documentaire, pas une
base scientifique validée. Aucune valeur numérique du moteur
(diagnostic_engine.py) ne repose sur ces études tant que leur contenu
complet n'a pas été lu et confirmé — voir README.md, section Limites."""

# ---------------------------------------------------------------------------
# 10. Fondamentaux home cinéma (apprentissage de fond demandé par Steve :
#     "je pense qu'il faut que tu apprenne comment fonctionne un système
#     home cinéma"). Sources encyclopédiques/constructeur de référence,
#     lues directement (Wikipedia, dolby.com via ses propres archives),
#     PAS des études à vérifier comme la section 9 — tous ces faits sont
#     reproductibles et publics. Classés [Acoustique générale]. Rien ici
#     n'est encore câblé dans diagnostic_engine.py : c'est un socle de
#     référence, à mobiliser au cas par cas plus tard (voir pistes V2).
# ---------------------------------------------------------------------------
SCHROEDER_TRANSITION_CONCEPT = (
    "Le comportement du son dans une pièce se découpe en 4 zones "
    "fréquentielles : (1) en dessous de la fréquence dont la demi-longueur "
    "d'onde égale la plus grande dimension de la pièce, le son se comporte "
    "comme une variation de pression statique ; (2) au-dessus, les modes "
    "propres de la pièce dominent (résonances, ondes stationnaires) ; "
    "(3) une zone de transition d'environ 2 octaves ; (4) en haute "
    "fréquence, le son se comporte statistiquement comme des rayons qui "
    "rebondissent. La frontière entre les zones (2) et (3)/(4) est "
    "appelée 'fréquence de Schroeder' (ou 'crossover frequency') : "
    "au-dessus, les fréquences hautes et moyennes dominent sur les modes "
    "de pièce isolés."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Room_acoustics
(section sur les 4 zones fréquentielles et la fréquence de Schroeder,
nommée d'après Manfred R. Schroeder). Volontairement SANS formule
numérique : la page source ne donne pas de formule chiffrée de cette
fréquence de transition (seulement sa définition conceptuelle et les
formules des modes propres, déjà implémentées dans
diagnostic_engine.axial_room_modes). Ne pas coder une formule du type
'2000 * sqrt(RT60/V)' tant qu'elle n'a pas été vérifiée sur une source
réellement consultée — voir la règle 'no invention' de la section 9."""

EQUAL_LOUDNESS_PRINCIPLE = (
    "La sensibilité de l'oreille humaine au volume n'est pas plate sur le "
    "spectre : elle est maximale entre environ 1 kHz et 5 kHz (bande où "
    "se trouvent l'essentiel des dialogues et consonnes), et diminue vers "
    "les graves et les aigus extrêmes. Les courbes isosoniques (equal-"
    "loudness contours, popularisées par Fletcher et Munson) montrent "
    "qu'à bas volume d'écoute, les graves et aigus perçus s'affaiblissent "
    "plus vite que le médium — d'où les fonctions 'loudness' des "
    "amplificateurs, qui ne sont PAS la même chose qu'une courbe cible de "
    "calibrage Dirac/Audyssey (celle-ci vise une réponse en fréquence "
    "stable quel que soit le volume, pas une compensation dynamique)."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Psychoacoustics .
Pertinent pour expliquer à un client pourquoi 'monter le son' ne suffit
pas à corriger un déséquilibre perçu dans les graves ou les dialogues,
et pour ne pas confondre une fonction loudness de l'ampli avec un
réglage de courbe cible Dirac."""

LFE_VS_SUBWOOFER_CHANNEL_DISTINCTION = (
    "Le canal LFE (Low-Frequency Effects) d'une piste Dolby Digital/DTS "
    "est un canal de MIX, limité à la bande 20-120 Hz et amplifié de "
    "+10 dB par convention à la lecture — ce n'est pas un synonyme du "
    "'canal subwoofer' de l'ampli. En pratique, le processeur additionne "
    "dans le(s) caisson(s) à la fois le LFE et les graves renvoyées par "
    "le bass management des autres canaux (voir ci-dessous) : ce que "
    "Dirac/Audyssey mesurent et corrigent sur le(s) caisson(s) est donc "
    "déjà un signal composite, pas le LFE brut seul."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Dolby_Digital
et https://en.wikipedia.org/wiki/Bass_management . Confirme et précise ce
qui avait été déduit empiriquement du fichier .liveproject de Steve (voir
liveproject_reader.py) : les 2 derniers slots de mesure, probablement les
subwoofers, montrent une bande passante réduite après 200-250 Hz,
cohérente avec cette bande LFE 20-120 Hz (+ marge de mesure)."""

BASS_MANAGEMENT_CROSSOVER_PRINCIPLE = (
    "Le 'bass management' sépare un signal en deux à une fréquence de "
    "croisement : un filtre passe-haut (typiquement 12 dB/octave, "
    "Butterworth) retire les graves des enceintes principales, et un "
    "filtre passe-bas (typiquement 24 dB/octave, Linkwitz-Riley) envoie "
    "ces graves vers le(s) caisson(s). L'alignement Linkwitz-Riley "
    "4e ordre (-6 dB au point de croisement pour chaque filtre) est le "
    "standard qui permet une somme plate à la fréquence de croisement. "
    "80 Hz est la fréquence de croisement la plus citée par défaut, dans "
    "une plage usuelle de 40 à 120 Hz selon la capacité des enceintes "
    "principales."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Bass_management .
Cohérent avec MANUAL_CROSSOVER_FREQUENCIES_HZ et
MANUAL_CROSSOVER_DEFAULT_OTHERS_HZ (= 80.0) déjà documentés en section 1
à partir du manuel Marantz — cette entrée ajoute le POURQUOI acoustique
(ordre de filtre, type d'alignement) derrière ces valeurs déjà connues du
manuel constructeur, utile pour expliquer une recommandation à un client
qui demande pourquoi 80 Hz plutôt qu'une autre valeur."""

DOLBY_ATMOS_RENDERING_VS_ROOM_CORRECTION = (
    "Dolby Atmos encode jusqu'à 128 'objets' audio (118 objets dynamiques "
    "+ 10 'beds', canaux fixes de référence), et un moteur de rendu "
    "('renderer') Dolby mixe ces objets en temps réel pour les adapter à "
    "la configuration réelle des enceintes installées (jusqu'à 24.1.10 "
    "canaux en home cinéma). Ce rendu spatial se fait EN AMONT de Dirac "
    "Live ART ou d'Audyssey : ces derniers ne connaissent pas la notion "
    "d'objet Atmos, ils reçoivent le signal déjà mixé par canal physique "
    "et appliquent seulement une correction acoustique (réponse en "
    "fréquence et temporelle) sur ce signal. Ce sont deux couches de "
    "traitement indépendantes dans la chaîne : la correction Dirac/"
    "Audyssey ne peut ni améliorer ni dégrader le placement spatial des "
    "objets Atmos, seulement la fidélité de restitution de chaque "
    "enceinte prise isolément."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Dolby_Atmos .
Utile pour répondre à un client qui demanderait si Dirac 'gère' Atmos :
réponse nuancée, ni oui ni non — Dirac corrige les enceintes sur
lesquelles Atmos a déjà été rendu, sans interagir avec le rendu lui-même."""

DOLBY_OFFICIAL_SUPPORTED_SPEAKER_LAYOUTS = [
    "2.1", "3.1", "4.1", "4.1.2", "4.1.4", "5.1", "5.1.2", "5.1.4",
    "7.1", "7.1.2", "7.1.4", "7.1.6", "9.1", "9.1.2", "9.1.4", "9.1.6",
    "11.1.8",
]
"""[Documentation constructeur publique] — source : guides officiels
'Speaker setup guides' de dolby.com (liste vérifiée via les archives
Wayback Machine du 27/09/2026, le site live bloquant les requêtes
automatisées au moment de cette recherche). Chaque configuration a sa
propre page de placement d'enceintes (angles, hauteur), mais ces pages
utilisent un visualiseur interactif (JS) dont le détail numérique des
angles n'a pas pu être extrait par ce canal — seule la liste des
configurations supportées et le principe général (enceintes à hauteur
d'oreille assise, sauf indication contraire pour les surrounds/hauteurs)
ont pu être confirmés. Le système de Steve (9 canaux : 7 enceintes +
2 caissons, voir liveproject_reader.py) correspond à une configuration
7.1.x standard de cette liste."""

ABSORPTION_GENERAL_PRINCIPLE = (
    "Un matériau absorbant transforme une partie de l'énergie sonore "
    "incidente en chaleur plutôt que de la réfléchir ; le coefficient "
    "d'absorption (entre 0 et 1, parfois >1 en mesure de laboratoire) "
    "dépend à la fois du matériau ET de la fréquence — un même panneau "
    "absorbe généralement beaucoup mieux en haute fréquence qu'en basse "
    "fréquence, car l'épaisseur nécessaire pour absorber efficacement une "
    "longueur d'onde est proportionnelle à cette longueur d'onde (les "
    "graves ont des longueurs d'onde de plusieurs mètres). C'est pourquoi "
    "les pièges à basses ('bass traps') dans les coins sont une approche "
    "différente des panneaux absorbants muraux classiques, plus efficaces "
    "en médium/aigu."
)
"""[Acoustique générale] — source : https://en.wikipedia.org/wiki/Absorption_(acoustics) .
Volontairement qualitatif, SANS tableau de coefficients chiffrés par
matériau : le tableau de la page source s'est révélé mal exploitable via
l'extraction automatique (colonnes de valeurs sans alignement fiable avec
les noms de matériaux) — risque de mal attribuer un chiffre à un
matériau. Cohérent avec IMMERSION_FACTORS (facteur 4, premières
réflexions/réverbération) : ce principe justifie pourquoi un traitement
acoustique de coin (graves) est un geste différent d'un traitement de
première réflexion murale (médium/aigu), déjà distingués en section 6."""

CINEMA_REFERENCE_LEVEL_PRINCIPLE = (
    "Le cinéma professionnel utilise un standard international de "
    "'niveau de référence' qui fait correspondre un niveau de signal sur "
    "la console de mixage à un SPL précis en salle : 20 dB sous le clip "
    "(0 dBFS) correspond à 85 dB SPL pour chaque enceinte L/C/R, 85 dB "
    "SPL pour les canaux surround combinés, et 95 dB SPL pour le(s) "
    "caisson(s) — soit +10 dB par rapport aux L/C/R, cohérent avec le "
    "gain de lecture +10 dB du canal LFE déjà documenté (voir "
    "LFE_VS_SUBWOOFER_CHANNEL_DISTINCTION). Le SPL de crête total "
    "théorique qui en résulte avoisine 115-120 dB, atteint rarement et "
    "brièvement en pratique. Un processeur correctement calibré affiche "
    "'0 dB' au niveau de référence ; un client qui écoute à '-10 dB' "
    "écoute donc 10 dB sous ce standard."
)
"""[Acoustique générale, source professionnelle non académique] — source :
Anthony Grimani (président de Grimani Systems / PMI Engineering /
Dimension4 Acoustics), article « Check Your References », Residential
Systems, 18/08/2021 : https://www.residentialsystems.com/features/home-
theater/check-your-references . Lu en entier directement. Auteur reconnu
dans l'industrie professionnelle du home cinéma, mais ceci reste un
article de magazine professionnel, PAS une étude académique
peer-reviewed : à traiter comme une pratique de l'industrie plutôt que
comme un fait scientifique établi."""

LISTENING_BELOW_REFERENCE_LEVEL_EFFECT = (
    "Selon Anthony Grimani (même source que CINEMA_REFERENCE_LEVEL_"
    "PRINCIPLE), écouter significativement (environ 10 dB) sous le "
    "niveau de référence cinéma dégrade la perception du mixage : le "
    "détail de bas niveau se perd dans le bruit de fond (surtout en "
    "surround/hauteur), les dialogues deviennent plus difficiles à "
    "comprendre, et les graves paraissent plus 'maigres'/moins présents. "
    "Son conseil pratique (opinion professionnelle, pas une règle "
    "chiffrée validée) pour un client qui écoute systématiquement sous le "
    "niveau de référence : envisager un léger renfort du surround et des "
    "graves, et une correction de 'clarté' sur le canal central."
)
"""[Avis d'expert, PAS une étude académique] — même source que
CINEMA_REFERENCE_LEVEL_PRINCIPLE. Intéressant pour expliquer à un client
pourquoi deux systèmes identiques calibrés à des volumes d'écoute très
différents 'ne sonnent pas pareil', mais ne doit PAS être codé comme un
seuil de correction automatique dans diagnostic_engine.py sans validation
supplémentaire (c'est une recommandation d'un professionnel, pas un seuil
mesuré par une étude contrôlée)."""

# ---------------------------------------------------------------------------
# 11. Fondements brevetés d'ART (demande de Steve : "analyse l'intégralité
#     du code de Dirac pour nos connaissances personnelles"). Ligne rouge
#     rappelée : le LOGICIEL Dirac Live est propriétaire et fermé — aucune
#     décompilation ni rétro-ingénierie n'a été tentée ou ne sera tentée.
#     Les seules sources techniques "internes" légitimes ici sont trois
#     VRAIS brevets déposés par Dirac Research AB, documents de divulgation
#     publique complète (c'est la contrepartie légale de la protection par
#     brevet), lus en texte intégral (extraction réelle du texte, pas une
#     supposition) : le premier (US9781510B2) a été fourni en PDF par Steve
#     lui-même ; le second (US8213637B2, famille EP2257083B1) et le
#     troisième (US9426600B2) ont été identifiés via les pages Google
#     Patents que Steve a partagées dans son navigateur, puis téléchargés
#     directement depuis le stockage PDF public officiel de Google Patents
#     (même source finale que si Steve les avait fournis directement —
#     aucun contenu tiers ou résumé non vérifié). Référence complète dans
#     CITED_PATENTS ci-dessous. Un quatrième fichier PDF fourni par Steve
#     au même moment que le premier (US9415102) s'est avéré être un brevet
#     pharmaceutique d'Alexion Pharmaceuticals sur des anticorps anti-C5,
#     sans aucun rapport avec l'audio ou Dirac — vérifié par lecture
#     réelle du texte, signalé honnêtement plutôt qu'ignoré, et non
#     utilisé ici.
# ---------------------------------------------------------------------------
ART_PRIMARY_SUPPORT_MECHANISM = (
    "Le brevet US9781510B2 définit formellement le mécanisme que le "
    "produit commercial appelle 'ART' : pour chaque canal d'entrée, on "
    "désigne UNE enceinte 'primaire' (celle dont on veut améliorer la "
    "réponse) et un sous-ensemble d'autres enceintes 'de support' (de 1 à "
    "N-1 enceintes, N étant le nombre total d'enceintes du système) qui "
    "contribuent au signal pour aider l'enceinte primaire à se rapprocher "
    "de sa cible à TOUTES les positions de mesure simultanément — "
    "l'enceinte primaire elle-même ne fait jamais partie de son propre "
    "sous-ensemble de support. Le brevet précise explicitement que, selon "
    "les réglages trouvés par l'optimisation, le filtre peut parfaitement "
    "décider de sortie nulle sur certaines enceintes de support "
    "candidates si leur usage n'aide pas (revendication 4) — le fait "
    "qu'une enceinte soit déclarée 'candidate au support' ne garantit "
    "donc pas qu'elle sera effectivement utilisée à chaque fréquence."
)
"""[Brevet Dirac Research] — US9781510B2 "Audio precompensation
controller design using a variable set of support loudspeakers",
inventeurs Lars-Johan Brannmark, Anders Ahlén, Adrian Bahne (Uppsala,
Suède), déposé 22/03/2012, accordé 03/10/2017, assigné à Dirac Research
AB. Texte intégral lu (PDF fourni par Steve, 30 pages, extraction de
texte réelle via PyMuPDF, pas un résumé). Revendication 1 (indépendante)
et revendication 3 citées quasi mot pour mot sur le mécanisme central.
Limite à garder en tête : ce brevet date de 2012 et décrit un MÉCANISME
MATHÉMATIQUE GÉNÉRAL, pas nécessairement les paramètres exacts du produit
'Dirac Live ART' commercialisé dans les versions récentes (~2021+) —
le nom commercial 'ART' n'apparaît d'ailleurs jamais dans ce brevet."""

ART_NOT_LIMITED_TO_LOW_FREQUENCY = (
    "Le brevet compare explicitement sa méthode à deux approches "
    "antérieures qu'il juge limitées : (1) un simple ajustement du signal "
    "de caisson en dessous de 150 Hz, qualifié de 'très primitif' ; "
    "(2) l''égalisation modale' (références académiques Mäkivirta et al. "
    "2003), qui identifie explicitement les fréquences centrales et "
    "temps de décroissance de CHAQUE mode de pièce pris séparément, mais "
    "qui est limitée en pratique à moins de 200 Hz (zone où les modes "
    "sont supposés distincts et bien séparés en fréquence). Le brevet "
    "revendique au contraire une 'flexibilité plus élevée, où les "
    "améliorations de performance ne sont pas contraintes aux basses "
    "fréquences' (Summary of the Invention). C'est cohérent avec ce que "
    "Dirac Live ART affiche en pratique (ART reste disponible sur une "
    "plage qui dépasse largement 200 Hz), mais ce principe de brevet ne "
    "dit pas où ART s'arrête concrètement dans l'interface actuelle — "
    "voir section 1 pour les limites déjà connues sur ce point."
)
"""[Brevet Dirac Research] — même brevet US9781510B2, section 'Background
of the Invention' et 'Summary of the Invention'. Texte intégral lu."""

ART_ADAPTIVE_SMOOTHING_PRINCIPLE = (
    "Point le plus directement utile pour anticiper l'interprétation que "
    "Dirac fait d'un fichier de mesure brut : le brevet décrit une étape "
    "de design finale où, pour approcher la cible 'en moyenne RMS sur "
    "toutes les positions de mesure', un 'lissage en fraction d'octave "
    "VARIABLE, basé sur les variations spatiales de la réponse' est "
    "appliqué, explicitement 'afin de ne pas sur-compenser une région de "
    "fréquence particulière'. En clair : plus une anomalie de courbe "
    "varie d'une position de mesure à l'autre (forte variance spatiale), "
    "plus elle est lissée avant correction (car elle est probablement "
    "due à une interférence locale, pas un vrai défaut systématique) ; "
    "plus une anomalie est stable/cohérente à travers les positions "
    "(faible variance spatiale), moins elle est lissée (car elle est "
    "probablement un vrai phénomène systématique — défaut d'enceinte ou "
    "mode de pièce dominant). C'est EXACTEMENT le principe que "
    "cartographie_modale.cluster_anomalies_by_frequency applique déjà "
    "(une anomalie n'est classée 'PARTAGÉE'/mode de pièce confirmé que "
    "si elle est détectée à la même fréquence sur au moins 2 slots de "
    "mesure différents) : ce brevet ne prouve pas que notre seuillage "
    "précis (±10Hz, 2 slots minimum) soit identique à celui de Dirac "
    "(qui reste un paramètre non public), mais confirme que le PRINCIPE "
    "général de notre méthode (distinguer 'cohérent entre positions' de "
    "'isolé à une position') est le même principe que celui revendiqué "
    "par Dirac Research pour son propre algorithme. Limite honnête : la "
    "valeur numérique exacte du lissage ('1/3 octave', '1/6 octave', ou "
    "une largeur vraiment variable selon un calcul propriétaire) n'est "
    "PAS donnée dans le brevet — seul le principe qualitatif l'est."
)
"""[Brevet Dirac Research] — même brevet US9781510B2, section 'Detailed
Description', paragraphe suivant la conception du filtre à phase
minimale ('A final design step is therefore preferably added after the
criterion minimization...'). Texte intégral lu. Recoupé avec le test
empirique réalisé en segment précédent (lissage 1/3 octave appliqué au
vrai fichier de Steve, voir PROJETS_FUTURS.md) : les deux pointent dans
la même direction (le lissage réduit fortement le nombre d'anomalies
jugées significatives), mais le test empirique a utilisé une largeur de
lissage FIXE (1/3 octave) alors que le brevet décrit une largeur
VARIABLE — donc nos deux résultats convergent sur le principe, pas sur
le paramétrage exact."""

ART_OPTIMIZATION_METHOD_LQG = (
    "Le brevet précise que le calcul des paramètres du filtre repose sur "
    "une optimisation de type 'Linear Quadratic Gaussian' (LQG), méthode "
    "connue de la théorie du contrôle optimal, pour concevoir un "
    "contrôleur 'feedforward' multivariable stable, linéaire et causal. "
    "La fonction de critère optimisée est une somme pondérée des carrés "
    "des écarts entre les réponses impulsionnelles compensées estimées "
    "et les réponses impulsionnelles cibles, sur TOUTES les positions de "
    "mesure à la fois (pas position par position), sous contrainte de "
    "stabilité du filtre résultant. La cible elle-même a un délai de "
    "propagation acoustique qui dépend de la DISTANCE réelle entre "
    "l'enceinte primaire et chaque position de mesure — donc la cible "
    "n'est pas purement une courbe de gain en fonction de la fréquence, "
    "elle intègre aussi un alignement temporel physique. Le brevet ajoute "
    "que la fonction de critère peut inclure des 'termes de pénalité' qui "
    "contraignent le niveau de signal (magnitude) envoyé à un "
    "sous-ensemble choisi des enceintes de support, pour des bandes de "
    "fréquence données — mécanisme qui correspond vraisemblablement (mais "
    "ce rapprochement n'est pas confirmé par une source officielle "
    "distincte) à ce que l'interface Dirac Live affiche comme 'niveau de "
    "support' : moins de pénalité laisse les enceintes de support "
    "contribuer plus fort, plus de pénalité les contraint à rester "
    "discrètes."
)
"""[Brevet Dirac Research] — même brevet US9781510B2, section 'Detailed
Description'. Texte intégral lu, y compris le formalisme mathématique
(matrices de fonctions de transfert, modèle MIMO). Le brevet cite lui-
même des références académiques établies sur lesquelles il s'appuie :
Miyoshi & Kaneda 1988 (inversion de la réponse acoustique d'une pièce),
Neely & Allen 1979 (inversibilité d'une réponse impulsionnelle de
pièce), et plusieurs travaux de M. Sternad et A. Ahlén (dont le
co-inventeur Anders Ahlén est lui-même l'auteur académique) sur le
contrôle LQ et le filtrage robuste face aux erreurs de modèle. Limite :
le rapprochement entre 'termes de pénalité par bande de fréquence' et
le curseur commercial 'niveau de support' est une inférence raisonnable
de notre part, PAS un fait confirmé par une source distincte qui ferait
explicitement ce lien."""

ART_PATENT_EXPERIMENTAL_EXAMPLE = (
    "Le brevet documente un exemple expérimental concret et vérifiable : "
    "un haut-parleur de monitoring de studio ATC SCM16 (référence "
    "commerciale réelle) mesuré à 64 positions dans une pièce. Comparé à "
    "un design mono-canal classique, le design multicanal de l'exemple "
    "utilise l'enceinte ATC comme primaire et 15 enceintes "
    "supplémentaires comme support, positionnées à des hauteurs et "
    "distances variées tout autour de la zone d'écoute. Les figures du "
    "brevet (réponses en fréquence et déclin spectral cumulatif/"
    "'waterfall') montrent une dispersion bien plus resserrée entre les "
    "64 positions après le design multicanal qu'après le design "
    "mono-canal — mais le brevet ne donne pas de valeur chiffrée de "
    "réduction de variance ou de dB exploitable telle quelle (seulement "
    "des graphiques)."
)
"""[Brevet Dirac Research] — même brevet US9781510B2, section 'An
Illustrative Example'. Texte intégral lu. Sert uniquement à illustrer
l'ordre de grandeur du nombre d'enceintes de support utilisé par Dirac
Research dans ses propres essais (16 enceintes au total dans cet
exemple) — PAS une recommandation de dimensionnement pour le système 7.2
de Steve, qui n'a que 9 enceintes au total."""

# ---------------------------------------------------------------------------
# 12. Deuxième brevet Dirac Research (US8213637B2, antérieur, 2009) —
#     cherche à répondre spécifiquement à la question de Steve sur le
#     fonctionnement interne d'ART/Dirac Live avec PLUSIEURS positions de
#     mesure. Porte sur un mécanisme plus large que le premier brevet :
#     pas seulement "primaire + support" pour une enceinte à la fois, mais
#     une résolution JOINTE de l'égalisation, du crossover, du délai/
#     niveau et de l'up-mixing pour émuler des "sources sonores
#     virtuelles" sur plusieurs zones d'écoute.
# ---------------------------------------------------------------------------
SFC_UNIFIED_OPTIMIZATION_MECHANISM = (
    "Le brevet US8213637B2 décrit un mécanisme plus large que le premier "
    "brevet (US9781510B2) : au lieu de traiter séparément et "
    "séquentiellement l'égalisation de chaque enceinte, la conception du "
    "filtre de recouvrement (crossover), le réglage du délai et du "
    "niveau de chaque canal, puis l'up-mixing — ce que le brevet décrit "
    "comme le processus de réglage traditionnel d'un système audio de "
    "voiture en plusieurs étapes — l'invention résout ces 5 problèmes "
    "('equalizer design, crossover design, delay and level calibration, "
    "sum-response optimization, up-mixing') en UNE SEULE optimisation "
    "mathématique jointe. Limite honnête à signaler : ce brevet décrit "
    "une CAPACITÉ mathématique générale de l'algorithme, pas "
    "nécessairement ce que fait le produit Marantz CINEMA 30 de Steve en "
    "pratique — on sait déjà par la documentation officielle Marantz que "
    "le crossover (MANUAL_CROSSOVER_FREQUENCIES_HZ) reste un réglage "
    "manuel séparé sur cet appareil, non recalculé automatiquement par "
    "ART. Il y a donc une tension réelle entre la capacité théorique "
    "unifiée revendiquée par le brevet et le réglage manuel du crossover "
    "effectivement documenté sur le CINEMA 30 — à ne pas gommer."
)
"""[Brevet Dirac Research] — US8213637B2 "Sound field control in
multiple listening regions", inventeurs Lars-Johan Brännmark, Mikael
Sternad, Mathias Johansson (Uppsala, Suède), déposé 28/05/2009, accordé
03/07/2012, assigné à Dirac Research AB. Famille de brevet incluant
EP2257083B1 (demande européenne correspondante EP09007142, citée en
page de garde du brevet US lui-même). Texte intégral lu (PDF officiel
téléchargé directement depuis le stockage public Google Patents, 20
pages : abstract, background, summary, detailed description sections 1
à 5, revendications 1 à 20) via extraction réelle PyMuPDF. Section
'Background of the Invention' et 'Summary of the Invention'."""

SFC_TARGET_STAGE_RICHER_THAN_CURVE = (
    "Point potentiellement important pour comprendre pourquoi la 'courbe "
    "cible' visible dans l'interface Dirac Live peut sembler insuffisante "
    "pour tout expliquer : le brevet définit un 'target stage' qui n'est "
    "PAS qu'une simple courbe de gain en fonction de la fréquence, mais "
    "un jeu complet de réponses impulsionnelles cibles (une par position "
    "de mesure) représentant une pièce D'ÉCOUTE DE RÉFÉRENCE virtuelle — "
    "avec des paramètres ajustables explicitement cités : angles et "
    "distances des enceintes virtuelles, taille de la pièce virtuelle, "
    "force et diffusion des premières réflexions. Le brevet précise que "
    "ce 'target stage' peut être MESURÉ dans une vraie pièce de "
    "référence ou SIMULÉ. Limite honnête : rien ne confirme, dans ce "
    "brevet ni ailleurs dans nos sources, quelle part de cette richesse "
    "(réflexions, pièce virtuelle) est réellement exposée ou utilisée "
    "dans le produit Dirac Live ART commercialisé sur le CINEMA 30 — la "
    "courbe cible visible dans l'interface pourrait n'être qu'une "
    "projection simplifiée (gain vs fréquence) de ce modèle plus riche, "
    "sans que cela soit confirmé par une source officielle distincte."
)
"""[Brevet Dirac Research] — même brevet US8213637B2, section 'Detailed
Description', sous-section '2. Acoustic Modelling and Target Stage
Definition'. Texte intégral lu."""

SFC_DISJOINT_REGIONS_CRITERION = (
    "Le brevet définit un critère géométrique précis pour qu'un jeu de "
    "positions de mesure soit traité comme PLUSIEURS zones d'écoute "
    "distinctes plutôt qu'une seule : au moins 2 zones, au moins 4 "
    "positions de mesure par zone, et une distance entre zones "
    "supérieure à la plus grande distance entre positions adjacentes à "
    "l'intérieur d'une même zone (une revendication dépendante précise "
    "même 'au moins deux fois supérieure'). L'exemple chiffré du brevet "
    "est un habitacle de voiture à 4 sièges : 64 positions au total, "
    "réparties en 4 zones de 16 positions (4x4) centrées sur chaque "
    "siège. Limite honnête et importante : nous ne savons PAS, faute "
    "d'une description sourcée de la disposition exacte des 13 positions "
    "de mesure de Steve (TOP CALIB BASE.liveproject), si elles "
    "correspondent à une seule zone d'écoute (cas le plus probable pour "
    "un home cinéma à un seul rang de sièges) ou à plusieurs zones "
    "disjointes au sens de ce brevet (ex: canapé principal + un fauteuil "
    "éloigné) — ce point mériterait d'être vérifié avec Steve avant de "
    "lui attribuer une conclusion précise sur son propre système."
)
"""[Brevet Dirac Research] — même brevet US8213637B2, revendications 1
et 5, et section 'Detailed Description' sous-section 2 (exemple de la
Fig. 3, voiture à 4 sièges). Texte intégral lu."""

SFC_MATHIAS_JOHANSSON_CONFIRMED_COINVENTOR = (
    "Ce brevet confirme, par une source primaire vérifiable (le brevet "
    "lui-même, pas une thèse tierce), que Mathias Johansson est bien "
    "co-inventeur chez Dirac Research AB, aux côtés de Lars-Johan "
    "Brännmark et Mikael Sternad — ce qui renforce (sans le prouver "
    "définitivement) la piste de recherche identifiée précédemment via "
    "la thèse 2024 de Viktor Gunnarsson, qui remerciait un 'Mathias "
    "Johansson' comme initiateur de projet. Les deux noms Brännmark et "
    "Sternad apparaissent également dans les références académiques "
    "citées par l'autre brevet (US9781510B2), ce qui dessine un noyau "
    "académique stable (Uppsala University / Dirac Research AB) commun "
    "aux deux brevets."
)
"""[Brevet Dirac Research] — US8213637B2, page de garde (liste des
inventeurs). Recoupement avec le travail de recherche académique du
segment précédent (checkpoint sur la thèse de Viktor Gunnarsson)."""

# ---------------------------------------------------------------------------
# 13. Troisième brevet Dirac Research : la symétrie de PAIRE d'enceintes
#     (ex : front gauche/droite, surround gauche/droite). Identifié comme
#     piste ouverte à la fin de la section 12 (US9426600B2, jamais lu à
#     l'époque), puis explicitement demandé par Steve ("télécharge le
#     brevet que tu as laissé en piste ouverte"). Texte intégral téléchargé
#     depuis le stockage PDF public officiel de Google Patents (même
#     méthode que pour US8213637B2) et lu en entier (29 pages : abstract,
#     background, summary, detailed description, modélisation
#     mathématique complète du critère LQG, exemple expérimental chiffré,
#     revendications 1 à 22).
# ---------------------------------------------------------------------------
PLS_SYMMETRY_NOT_AUTOMATIC_FROM_EQUALIZATION = (
    "Point de départ du brevet, qui explique pourquoi un simple réglage "
    "ART 'par enceinte' ne suffit pas forcément à garantir une bonne "
    "image stéréo/surround : la similarité entre les réponses de salle "
    "(RTF) de deux enceintes symétriques (front gauche/droite, surround "
    "gauche/droite) est décrite comme une 'exigence de base' pour une "
    "reproduction sonore correcte. Le brevet souligne qu'égaliser "
    "séparément chaque enceinte vers LA MÊME cible n'obtient cette "
    "similarité 'que comme sous-produit, idéalement' — et seulement SI "
    "la pièce est parfaitement symétrique par rapport à la paire "
    "d'enceintes ET que les enceintes sont identiques. Le brevet affirme "
    "explicitement que ce n'est 'pas un résultat réaliste' dans un salon "
    "ordinaire (asymétries dues au mobilier, aux murs, aux ouvertures). "
    "D'où l'idée centrale des inventeurs : il faut un critère "
    "d'optimisation qui exige EXPLICITEMENT cette symétrie, en plus de "
    "l'égalisation de chaque canal vers sa cible — et la placer dans la "
    "MÊME optimisation plutôt que de la traiter après coup."
)
"""[Brevet Dirac Research] — US9426600B2 "Audio precompensation
controller design with pairwise loudspeaker channel similarity",
inventeurs Adrian Bahne, Lars-Johan Brännmark, Anders Ählén (Uppsala,
Suède), demande PCT déposée 20/06/2013 (priorité provisoire 06/07/2012),
accordé 23/08/2016, assigné à Dirac Research AB. Sections 'Background of
the Invention' et 'Summary of the Invention'. Texte intégral lu."""

PLS_CRITERION_FUNCTION_MECHANISM = (
    "Mécanisme technique précis (revendication 1, indépendante) : la "
    "fonction de critère optimisée par le contrôleur combine DEUX termes "
    "en même temps, sous la même contrainte de stabilité : (1) une somme "
    "pondérée des écarts entre les réponses impulsionnelles compensées "
    "et les réponses cibles à chaque position de mesure (l'égalisation "
    "classique, déjà connue des deux autres brevets) ; (2) une somme "
    "pondérée et PERMUTÉE des écarts entre les réponses égalisées d'AU "
    "MOINS UNE PAIRE d'enceintes symétriques — une matrice de "
    "permutation réarrange les positions de mesure d'un canal pour les "
    "aligner avec les positions miroir symétriques de l'autre canal de "
    "la paire. Les deux termes sont résolus ENSEMBLE via la même méthode "
    "d'optimisation LQG (Linear Quadratic Gaussian) que les deux autres "
    "brevets Dirac déjà intégrés ici — confirmation supplémentaire que "
    "LQG est le socle mathématique commun et récurrent des 3 brevets "
    "Dirac Research lus à ce jour, pas une coïncidence isolée."
)
"""[Brevet Dirac Research] — même brevet US9426600B2, revendication 1 et
section 'Detailed Description' (équations (11) et (17), définition de la
matrice de permutation P). Texte intégral lu."""

PLS_EXPERIMENTAL_PROOF_SUPPORT_VS_SYMMETRY = (
    "Preuve chiffrée donnée par le brevet lui-même (section 'An "
    "Illustrative Example', FIG. 13, mesures réelles sur 64 positions) : "
    "'la corrélation croisée pour une conception de précompensateur avec "
    "similarité [de paire] pour SIX enceintes [de support] est plus "
    "élevée que la corrélation croisée pour une conception sans "
    "similarité avec SEIZE enceintes [de support]' (traduction littérale "
    "d'une phrase du brevet). Autrement dit, selon cette expérience des "
    "inventeurs eux-mêmes, activer le critère de symétrie explicite avec "
    "seulement 6 enceintes de support bat, en qualité d'image stéréo, le "
    "fait d'ajouter 16 enceintes de support SANS ce critère. Dans le "
    "même exemple, un seul point de contrôle de similarité suffit déjà à "
    "rendre les réponses en fréquence des deux canaux (gauche/droite) "
    "'presque identiques' dans la bande 70-800 Hz. Limite honnête : ceci "
    "est l'exemple expérimental du brevet (preuve de concept des "
    "inventeurs), pas une mesure indépendante, et rien ne garantit que "
    "le produit commercial Dirac Live ART utilise exactement ces mêmes "
    "proportions sur le système réel de Steve."
)
"""[Brevet Dirac Research] — même brevet US9426600B2, section 'An
Illustrative Example', description de la FIG. 13. Texte intégral lu."""

PLS_MEASUREMENT_POSITIONS_RECOMMENDATION = (
    "Recommandation générale explicite du brevet, directement comparable "
    "au protocole de mesure de Steve : 'il est recommandé que le nombre "
    "de positions de mesure M soit supérieur au nombre d'enceintes N' "
    "(section 'Acoustic Modeling'). Avec 13 positions de mesure pour un "
    "système 7.2 de 9 enceintes au total (7 enceintes + 2 caissons), "
    "Steve respecte déjà ce ratio M > N recommandé par le brevet. "
    "Limite honnête : le brevet ne donne pas de ratio minimal "
    "chiffré (ex : '1.5x' ou '2x') au-delà de cette inégalité stricte "
    "M > N, donc on ne peut pas en tirer une conclusion plus précise sur "
    "le caractère 'optimal' ou non du nombre exact 13."
)
"""[Brevet Dirac Research] — même brevet US9426600B2, section 'Detailed
Description', sous-section 'Acoustic Modeling'. Texte intégral lu."""

CITED_PATENTS: list[CitedPatent] = [
    CitedPatent(
        patent_number="US9781510B2",
        title="Audio precompensation controller design using a variable "
        "set of support loudspeakers",
        inventors="Lars-Johan Brannmark, Anders Ahlén, Adrian Bahne "
        "(Uppsala, Suède)",
        assignee="Dirac Research AB",
        priority_date="2012-03-22 (accordé 2017-10-03)",
        source_url="https://patents.google.com/patent/US9781510B2/en "
        "(PDF texte intégral fourni directement par Steve)",
        verification="Texte intégral lu (30 pages : abstract, background, "
        "summary, detailed description, revendications 1 à 27, liste des "
        "références académiques citées) via extraction réelle du PDF, "
        "pas un résumé de tiers.",
        takeaway="Brevet fondateur du mécanisme 'primaire + enceintes de "
        "support' qui sous-tend ART : voir ART_PRIMARY_SUPPORT_MECHANISM, "
        "ART_NOT_LIMITED_TO_LOW_FREQUENCY, ART_ADAPTIVE_SMOOTHING_"
        "PRINCIPLE, ART_OPTIMIZATION_METHOD_LQG et ART_PATENT_"
        "EXPERIMENTAL_EXAMPLE ci-dessus pour le détail. Ne décrit pas le "
        "nom commercial 'ART' ni les réglages exacts de l'interface "
        "actuelle, seulement le principe mathématique sous-jacent.",
    ),
    CitedPatent(
        patent_number="US8213637B2",
        title="Sound field control in multiple listening regions",
        inventors="Lars-Johan Brännmark, Mikael Sternad, Mathias "
        "Johansson (Uppsala, Suède)",
        assignee="Dirac Research AB",
        priority_date="2009-05-28 (accordé 2012-07-03)",
        source_url="https://patents.google.com/patent/US8213637B2/en "
        "(PDF officiel téléchargé depuis le stockage public Google "
        "Patents ; famille EP2257083B1, demande correspondante "
        "EP09007142)",
        verification="Texte intégral lu (20 pages : abstract, "
        "background, summary, detailed description sections 1 à 5, "
        "revendications 1 à 20) via extraction réelle du PDF, pas un "
        "résumé de tiers.",
        takeaway="Brevet antérieur et plus large que US9781510B2 : "
        "décrit la résolution JOINTE de l'égalisation, du crossover, du "
        "délai/niveau et de l'up-mixing pour émuler des 'sources "
        "sonores virtuelles' sur plusieurs zones d'écoute. Voir "
        "SFC_UNIFIED_OPTIMIZATION_MECHANISM, SFC_TARGET_STAGE_RICHER_"
        "THAN_CURVE, SFC_DISJOINT_REGIONS_CRITERION et SFC_MATHIAS_"
        "JOHANSSON_CONFIRMED_COINVENTOR ci-dessus. Ne décrit pas non "
        "plus le nom commercial 'ART'.",
    ),
    CitedPatent(
        patent_number="US9426600B2",
        title="Audio precompensation controller design with pairwise "
        "loudspeaker channel similarity",
        inventors="Adrian Bahne, Lars-Johan Brännmark, Anders Ählén "
        "(Uppsala, Suède)",
        assignee="Dirac Research AB",
        priority_date="2012-07-06 provisoire, PCT déposé 2013-06-20 "
        "(accordé 2016-08-23)",
        source_url="https://patents.google.com/patent/US9426600B2/en "
        "(PDF officiel téléchargé depuis le stockage public Google "
        "Patents)",
        verification="Texte intégral lu (29 pages : abstract, "
        "background, summary, detailed description, modélisation "
        "mathématique complète du critère LQG, exemple expérimental "
        "chiffré, revendications 1 à 22) via extraction réelle du PDF, "
        "pas un résumé de tiers.",
        takeaway="Brevet complémentaire (pas concurrent) aux deux "
        "autres : il traite spécifiquement de la SYMÉTRIE entre une "
        "PAIRE d'enceintes (ex : front gauche/droite), en ajoutant un "
        "terme de similarité explicite à la fonction de critère "
        "optimisée. Voir PLS_SYMMETRY_NOT_AUTOMATIC_FROM_EQUALIZATION, "
        "PLS_CRITERION_FUNCTION_MECHANISM, PLS_EXPERIMENTAL_PROOF_"
        "SUPPORT_VS_SYMMETRY et PLS_MEASUREMENT_POSITIONS_"
        "RECOMMENDATION ci-dessus. Ne décrit pas non plus le nom "
        "commercial 'ART'.",
    ),
]
"""Les trois brevets Dirac Research identifiés à ce jour ont maintenant
tous été lus en texte intégral et intégrés ci-dessus. Aucune piste de
brevet Dirac Research connue ne reste ouverte à ce stade ; un
approfondissement supplémentaire nécessiterait une nouvelle recherche
(ex : Google Patents, requête 'assignee:Dirac Research AB') que Steve
n'a pas demandée pour l'instant."""

# ---------------------------------------------------------------------------
# 14. Limite physique de toute correction DSP linéaire (ART/Dirac, Audyssey,
#     etc.) : la distorsion NON-LINÉAIRE des haut-parleurs. Question de
#     Steve ("as-tu besoin d'autres informations pour une compréhension
#     globale d'un système home cinéma ?") : après bilan honnête du
#     contenu existant (sections 1 à 13, toutes centrées sur la réponse
#     LINÉAIRE amplitude/phase), ce point est identifié comme le trou le
#     plus directement utile à combler en premier — les 3 brevets Dirac
#     déjà lus (sections 11 à 13) décrivent tous un contrôleur LQG, c'est
#     à dire un filtre LINÉAIRE, causal et stable. Sources encyclopédiques
#     lues directement (même méthode que la section 10), classées
#     [Acoustique générale].
# ---------------------------------------------------------------------------
LINEAR_EQ_CANNOT_FIX_NONLINEAR_DISTORTION = (
    "Distinction fondamentale de théorie du signal, établie en combinant "
    "deux faits séparément sourcés ci-dessous : un égaliseur/correcteur "
    "(dont Dirac ART, d'après les 3 brevets lus en sections 11 à 13, qui "
    "décrivent tous un contrôleur LQG linéaire, causal et stable) ne "
    "fait qu'ajuster l'amplitude et la phase du signal à CHAQUE "
    "fréquence, de façon linéaire. La distorsion harmonique (THD) et la "
    "distorsion d'intermodulation (IMD) d'un haut-parleur sont, par "
    "définition, le produit d'un système NON-LINÉAIRE : elles créent du "
    "contenu fréquentiel NOUVEAU (harmoniques à 2x/3x la fréquence "
    "d'origine, ou produits de combinaison entre deux fréquences "
    "distinctes) qui n'existait pas dans le signal d'entrée. Un filtre "
    "linéaire placé en amont du haut-parleur (ce que fait Dirac) ne peut "
    "structurellement pas empêcher ce phénomène non-linéaire de se "
    "produire DANS le haut-parleur lui-même : il peut seulement changer "
    "l'amplitude et la phase du signal qu'il reçoit, pas la façon dont "
    "ce haut-parleur particulier le transforme physiquement. Conséquence "
    "pratique directe pour un client : une calibration ART parfaite ne "
    "rendra jamais une enceinte de mauvaise qualité, ou poussée au-delà "
    "de ses capacités, aussi propre qu'une meilleure enceinte bien "
    "dimensionnée — ce sont deux problèmes de nature différente, pas un "
    "seul que la calibration pourrait entièrement résoudre."
)
"""[Acoustique générale] — synthèse de deux pages Wikipedia lues
directement : https://en.wikipedia.org/wiki/Total_harmonic_distortion
('When a sinusoidal signal of frequency ω passes through a non-ideal,
non-linear device, additional content is added at integer multiples nω
(harmonics)... we start with an ideal system where the transfer function
is linear and time-invariant') et
https://en.wikipedia.org/wiki/Audio_system_measurements, section
'Intermodulation distortion (IMD)' ('This effect results from
non-linearities in the system'). Le rapprochement entre ces deux faits
(équaliseur = système linéaire ; distorsion = produit d'un système
non-linéaire) est un raisonnement logique explicite de notre part, pas
une phrase unique citée telle quelle — à ne pas présenter comme une
citation directe d'une seule source."""

LOUDSPEAKER_DISTORTION_MAGNITUDE_VS_ELECTRONICS = (
    "Ordres de grandeur chiffrés et sourcés, utiles pour expliquer "
    "concrètement pourquoi le haut-parleur reste le maillon faible : "
    "l'électronique haute-fidélité (amplis, lecteurs CD) atteint "
    "typiquement MOINS de 1 % de distorsion harmonique, alors que les "
    "haut-parleurs ('éléments mécaniques') ont 'des niveaux plus élevés "
    "inévitables' — 1 à 5 % de distorsion à un niveau d'écoute modérément "
    "fort n'est 'pas rare', et jusqu'à 10 % est jugé acceptable dans les "
    "graves en lecture forte (l'oreille humaine étant moins sensible à "
    "la distorsion dans cette zone). Une source dédiée à la mesure des "
    "haut-parleurs chiffre la distorsion typique autour de 3 % "
    "('distortion residue' pondéré 468), correspondant à 1-2 % de THD, "
    "et précise qu'au-dessus de 100 dB SPL 'presque tous les systèmes de "
    "haut-parleurs domestiques distordent fortement' (les moniteurs "
    "professionnels tenant un niveau de distorsion modeste jusqu'à "
    "environ 110 dB SPL à 1 m)."
)
"""[Acoustique générale] — https://en.wikipedia.org/wiki/Audio_system_
measurements, section 'Total harmonic distortion (THD)' ('Essentially,
all loudspeakers produce more distortion than electronics, and 1-5%
distortion is not unheard of at moderately loud listening levels...
levels are usually expected to be under 10% at loud playback [in the
bass]') et https://en.wikipedia.org/wiki/Loudspeaker_measurement,
section 'Distortion measurement' ('Most speakers give around 3%
distortion measured 468-weighted distortion residue... almost all
domestic speaker systems distort badly above 100 dB SPL. Professional
monitors may maintain modest distortion up to around 110 dB SPL at
1 m')."""

INTERMODULATION_DISTORTION_AND_CROSSOVER_LINK = (
    "Précision importante qui relie ce sujet à ce qui est déjà documenté "
    "sur le crossover (voir BASS_MANAGEMENT_CROSSOVER_PRINCIPLE, section "
    "10) : la distorsion d'intermodulation (IMD) d'un haut-parleur "
    "'augmente avec l'excursion du cône' (donc avec le niveau sonore "
    "demandé à ce haut-parleur) et 'réduire la bande passante d'un "
    "haut-parleur réduit directement l'IMD'. C'est exactement ce que "
    "fait un crossover (séparer la bande de fréquences en plusieurs "
    "haut-parleurs spécialisés) : au-delà de la justification déjà "
    "connue (sommation plate au point de croisement, alignement "
    "Linkwitz-Riley), le crossover a donc une seconde justification "
    "acoustique indépendante — limiter l'excursion et la largeur de "
    "bande de chaque haut-parleur réduit sa distorsion d'intermodulation "
    "intrinsèque, un bénéfice qu'aucun réglage DSP linéaire en amont "
    "(ART ou autre) ne peut apporter à lui seul."
)
"""[Acoustique générale] — même source que ci-dessus,
https://en.wikipedia.org/wiki/Audio_system_measurements, section
'Intermodulation distortion (IMD)' ('IMD increases with cone excursion.
Reducing a driver's bandwidth directly reduces IMD. This is achieved by
splitting the desired frequency range into separate bands with an audio
crossover and employing separate drivers for each band of
frequencies')."""

LOUDSPEAKER_COLOURATION_RESONANCE_CONCEPT = (
    "Un phénomène physique distinct de la distorsion harmonique/IMD, "
    "appelé 'coloration' : la tendance du cône, de sa suspension, du "
    "caisson et de l'air qu'il enferme à CONTINUER de vibrer quand le "
    "signal électrique s'arrête, par stockage d'énergie dans des "
    "résonances mécaniques (d'autant plus audibles que leur facteur de "
    "qualité, le 'Q', est élevé — une résonance étroite et prolongée). "
    "C'est ce phénomène, pas la distorsion harmonique, que mesurent les "
    "graphiques en cascade temps/fréquence ('waterfall' ou "
    "spectrogramme) déjà mentionnés en section 11 à propos du lissage "
    "adaptatif de Dirac. Nuance importante pour ne pas sur-simplifier : "
    "une correction DSP qui agit sur l'amplitude ET la phase (ce que "
    "revendiquent les 3 brevets Dirac, via leur 'target impulse "
    "response') peut atténuer une partie de l'effet perçu d'une "
    "résonance en la rééquilibrant en amplitude, mais n'élimine pas le "
    "stockage d'énergie mécanique lui-même à sa source — la frontière "
    "entre 'ce qu'ART peut corriger' et 'ce qui reste un défaut physique "
    "du haut-parleur' n'est donc pas parfaitement nette et mériterait, "
    "si besoin, une source allant plus loin que cette synthèse "
    "encyclopédique générale."
)
"""[Acoustique générale] — https://en.wikipedia.org/wiki/Loudspeaker_
measurement, section 'Colouration analysis' ('Loudspeakers differ from
most other items of audio equipment in suffering from colouration, the
tendency of various parts of the speaker—the cone, its surround, the
cabinet, the enclosed space—to carry on moving when the signal
ceases... resonances with high Q factor are especially audible... FFT
measuring equipment was introduced in order to measure the delayed
output from speakers and display it as a time vs. frequency waterfall
plot')."""

# ---------------------------------------------------------------------------
# 15. Fiches techniques officielles du matériel RÉEL de Steve (demande
#     explicite : "il faut que tu sois en mesure de récupérer les manuels
#     constructeurs des éléments d'un système home cinéma"). MÉTHODE
#     découverte ici, généralisable à tout futur matériel : quand un site
#     constructeur moderne (Wix, React, etc.) ne rend pas ses fiches
#     techniques en HTML statique, le fetcher texte (`web_fetch`) échoue
#     même si la page existe (c'est ce qui avait fait échouer la
#     recherche Elipson en suite 15 — voir PROJETS_FUTURS.md). Le
#     NAVIGATEUR INTÉGRÉ (`navigatePage` + `readPage` + `clickElement`),
#     qui exécute réellement le JavaScript de la page, réussit là où
#     `web_fetch` échoue : la méthode qui a fonctionné ici est (1) trouver
#     l'URL exacte du produit par une recherche Google via le navigateur
#     (le nom commercial exact peut différer de celui utilisé à l'oral —
#     ex: Steve disait 'Facet 2.0', le nom officiel est 'Facet II'), (2)
#     `readPage` pour repérer un onglet/lien "Specifications"/"Détails
#     techniques"/"Datasheet" dans le snapshot d'accessibilité, (3)
#     `clickElement` dessus pour révéler le tableau de specs cliqué (ce
#     contenu n'existe pas encore dans le DOM avant le clic sur certains
#     sites), (4) relire le nouveau snapshot retourné par `clickElement`.
#     Fiches classées [Fiche constructeur officielle].
# ---------------------------------------------------------------------------
CITED_MANUFACTURER_SPECS: list[ManufacturerSpecSheet] = [
    ManufacturerSpecSheet(
        brand="Elipson",
        model="Legacy 3220",
        role_in_system="Façades gauche/droite du système 7.2 de Steve",
        source_url="https://en.elipson.com/product-page/legacy-3220",
        specs={
            "Type": "2 1/2 voies, colonne, bass-reflex",
            "Tweeter": "AMT (Air Motion Transformer)",
            "Médium/Grave": "2x 165mm, membrane aluminium/céramique",
            "Puissance RMS admissible": "150 W",
            "Réponse en fréquence": "35 Hz - 30 kHz",
            "Sensibilité": "89 dB",
            "Impédance": "6 ohms",
            "Dimensions (L x H x P)": "1105 x 276 x 360 mm",
            "Poids (chacune)": "32,8 kg",
        },
        verification="Page produit lue via le navigateur intégré "
        "(readPage), onglet 'SPECIFICATIONS' cliqué (clickElement) pour "
        "révéler le tableau de mesures — remplace l'estimation prudente "
        "non vérifiée utilisée avant le 03/10 (45 Hz) par la vraie "
        "valeur officielle (35 Hz).",
    ),
    ManufacturerSpecSheet(
        brand="Elipson",
        model="Prestige Facet II 14C (dénommée 'Facet 2.0 14C' par Steve "
        "à l'oral — nom commercial officiel confirmé : 'Facet II')",
        role_in_system="Centrale du système 7.2 de Steve",
        source_url="https://www.elipson.com/product-page/prestige-facet-ii-14c",
        specs={
            "Type": "Enceinte centrale, 2 voies, bass-reflex laminaire",
            "Puissance": "150 W RMS, amplification recommandée 40-200 W",
            "Tweeter": "25 mm, dôme souple",
            "Grave-médium": "2x 170 mm avec ogive centrale",
            "Réponse en fréquence": "43 Hz - 25 kHz (±3dB)",
            "Sensibilité": "93 dB (1W/1m)",
            "Filtre": "3000 Hz, 18 dB/octave",
            "Impédance nominale": "6 ohms",
            "Impédance minimale": "4,5 ohms @ 180 Hz",
            "Fréquence d'accord bass-reflex": "57 Hz",
            "Dimensions produit": "600 x 207 x 250 mm",
            "Poids net": "12,7 kg",
        },
        verification="Page produit lue via le navigateur intégré "
        "(readPage), onglet 'Détails techniques' cliqué (clickElement) "
        "— remplace l'estimation prudente non vérifiée utilisée avant le "
        "03/10 (65 Hz) par la vraie valeur officielle (43 Hz ±3dB).",
    ),
    ManufacturerSpecSheet(
        brand="Elipson",
        model="Prestige Facet II 14LCR (dénommée 'Facet 2.0 LCR' par "
        "Steve à l'oral)",
        role_in_system="Surround + Surround Back (x4) du système 7.2 de "
        "Steve",
        source_url="https://www.elipson.com/product-page/prestige-facet-ii-14lcr",
        specs={
            "Type": "Enceinte principale/centrale/surround, 2 voies "
            "bass-reflex",
            "Puissance": "150 W RMS, amplification recommandée 40-200 W",
            "Tweeter": "25 mm",
            "Grave-médiums": "2x 170 mm",
            "Réponse en fréquence": "53 Hz - 25 kHz (±3dB)",
            "Sensibilité": "93 dB (1W/1m)",
            "Filtre répartiteur": "3200 Hz, 18 dB/18 dB",
            "Impédance nominale": "6 ohms",
            "Impédance minimale": "4,6 ohms @ 202 Hz",
            "Fréquence d'accord bass-reflex": "54 Hz",
            "Dimensions": "650 x 280 x 170 mm",
            "Poids": "13,3 kg",
        },
        verification="Page produit lue via le navigateur intégré "
        "(readPage), onglet 'Détails techniques' cliqué (clickElement) "
        "— remplace l'estimation prudente non vérifiée utilisée avant le "
        "03/10 (70 Hz) par la vraie valeur officielle (53 Hz ±3dB).",
    ),
    ManufacturerSpecSheet(
        brand="Buckeye Amps (modules Hypex NCOREx)",
        model="NCx252MP 8-Channel",
        role_in_system="Ampli de puissance du système de Steve, piloté "
        "en pré-ampli par le Marantz CINEMA 30 (7 canaux utilisés sur 8 "
        "en config 7.2 — le fabricant confirme explicitement qu'un canal "
        "inutilisé sur un bloc 8 canaux ne pose aucun problème de "
        "performance)",
        source_url="https://www.buckeyeamp.com/shop/amplifiers/hypex/"
        "ncx252mp/8_channel",
        specs={
            "Modules": "4x Hypex NCx252MP (2 canaux chacun)",
            "Puissance par canal (1kHz, 1% THD)": "150W@8Ω / 250W@4Ω / "
            "180W@2Ω",
            "THD": "0,0007 % (125W, 4 ohms, 10Hz-20kHz)",
            "Rapport signal/bruit (S/N)": "120 dB",
            "Réponse en fréquence": "10 Hz - 50 kHz",
            "Impédance d'entrée": "47 kOhms",
            "Sensibilité d'entrée": "1,6 Vrms (4 ohms) / 1,8 Vrms (8 ohms)",
            "Gain en tension": "26 dB",
            "Courant de sortie": "18 A par canal",
            "Efficacité": "92 %",
            "Consommation veille": "0,5 W",
            "Dimensions": "17 x 13 x 4 pouces, 16 lbs",
        },
        verification="Page produit lue directement via le navigateur "
        "intégré (readPage), tableau 'Power'/'Fidelity'/'Specifications' "
        "déjà présent dans le DOM sans clic nécessaire sur cette page.",
    ),
    ManufacturerSpecSheet(
        brand="Buckeye Amps",
        model="Câbles RCA(M) à XLR(M)",
        role_in_system="Liaison entre les pré-sorties du Marantz CINEMA "
        "30 (RCA) et les entrées de l'ampli Buckeye NCx252MP (XLR) — "
        "confirmé utilisé par Steve",
        source_url="https://www.buckeyeamp.com/shop/amplifiers/options/"
        "cables",
        specs={
            "Câble": "Canare L-4E6S Star Quad",
            "Connecteurs": "Neutrik XLR + Neutrik/Rean RCA",
            "Schéma de câblage": "Schéma exact recommandé par Purifi et "
            "Hypex pour la conversion RCA->XLR, conçu pour éviter le "
            "bruit de fond ou le ronflement de masse (ground hum)",
            "Longueurs disponibles": "0,5 m / 1 m / 2 m",
        },
        verification="Page produit lue directement via le navigateur "
        "intégré (readPage). Pertinent pour le risque de bruit de fond/"
        "ronflement de masse mentionné en section 14 (Audio System "
        "Measurements, 'Noise'/'Crosstalk'/'Common-mode rejection "
        "ratio') : ce choix de câble écarte spécifiquement ce risque, "
        "confirmé par le fabricant d'ampli lui-même, pas par Steve ou "
        "par nous.",
    ),
]
"""Ces 5 fiches remplacent les estimations prudentes ('ESTIMATION NON
VÉRIFIÉE') utilisées dans exemple_systeme_steve.py avant le 03/10 (suite
22) pour les 3 modèles Elipson, et ajoutent deux éléments de la chaîne
électrique (ampli, câblage) jamais documentés avant. Les caissons SVS
3000 Micro R|Evolution restent sourcés séparément (déjà confirmés en
suite 15, voir PROJETS_FUTURS.md) et ne sont pas dupliqués ici. Le
manuel Marantz CINEMA 30 reste sourcé séparément sous
EvidenceLevel.MARANTZ_DIRAC_OFFICIEL (section 1) : cette liste couvre
le matériel qui n'avait PAS encore de source officielle."""

# ---------------------------------------------------------------------------
# 16. Confirmations officielles directes dirac.com + stormaudio.com (demande
#     de Steve : "prend en compte toutes les notes sur le site de dirac et
#     de storm"). Navigateur intégré utilisé (web_fetch avait échoué sur
#     dirac.com par le passé, erreur 429 — voir suite 15). Pages lues :
#     dirac.com/products/art (+ 3 accordéons et 6 "features" cliqués),
#     dirac.com/resources/quickstart, dirac.com/brands (liste complète),
#     dirac.com/brands/marantz, dirac.com/products/marantz-cinema-30,
#     stormaudio.com/room-calibration/. [Documentation officielle Dirac] /
#     [Documentation officielle StormAudio]
# ---------------------------------------------------------------------------
ART_OFFICIAL_MECHANISM_CANCELLATION_SIGNALS = (
    "Formulation officielle exacte de dirac.com/products/art, qui confirme "
    "en langage produit (pas juste brevet) le mécanisme primaire+support "
    "déjà déduit des brevets : 'ART configures your system to generate "
    "cancellation signals using all available speakers. These signals are "
    "applied in real time during playback.' Et dans 'What it does' : "
    "'It uses the strengths of each speaker to create an ideal sound "
    "field, where negative effects like resonances are blocked before "
    "they even occur.' Sur la page produit spécifique au CINEMA 30 "
    "(dirac.com/products/marantz-cinema-30), ART est décrit comme "
    "'Speaker cooperation add-on' avec 3 bénéfices listés : 'Coordinates "
    "speakers to work together', 'Delivers the ultimate immersive "
    "sound', 'Tames resonances and decay times'."
)
"""[Documentation officielle Dirac] — dirac.com/products/art, sections
'What it does' et accordéon 'How to calibrate and set it up' cliqué ;
dirac.com/products/marantz-cinema-30, liste de caractéristiques du
produit '03 ART' spécifique à ce modèle. Lu directement via le
navigateur intégré (readPage + clickElement)."""

ART_OFFICIAL_DECAY_TIME_AND_BASS_FOCUS = (
    "Point concret et actionnable confirmé par DEUX sources officielles "
    "indépendantes (Dirac ET StormAudio) : ART ne corrige pas qu'une "
    "courbe de gain en fréquence, il agit explicitement sur le TEMPS DE "
    "DÉCROISSANCE du son dans la pièce, avec un focus particulier sur "
    "les graves qui 'traînent'. Dirac (feature 'Decay Time Management') : "
    "'ART ensures sound doesn't linger for as long in your room, "
    "improving clarity and preventing muddiness.' StormAudio (plus "
    "explicite encore) : ART 'uses each speaker's strengths to reduce "
    "room decay time, efficiently canceling out **lingering bass**, "
    "leading to unmatched clarity.' Cohérent avec les 3 zones de modes "
    "de pièce confirmées empiriquement sur le système réel de Steve "
    "(toutes situées dans les graves/bas-médium, 45-255 Hz) : c'est "
    "précisément la zone où ART est sensé être le plus utile selon ces "
    "deux sources officielles."
)
"""[Documentation officielle Dirac + StormAudio] — dirac.com/products/art,
feature 'Decay Time Management' cliquée ; stormaudio.com/room-
calibration/, section 'Dirac Live Active Room Treatment'. Lu directement
via le navigateur intégré."""

ART_REUSES_EXISTING_MEASUREMENTS = (
    "Information pratique officielle StormAudio, utile si Steve "
    "réactive/reconfigure ART plus tard : passer de Room Correction/Bass "
    "Control à ART 'will maintain your existing configurations and audio "
    "profiles... If sufficient measurements were previously taken, they "
    "can be used to activate Dirac ART quickly' — pas besoin de "
    "systématiquement tout re-mesurer depuis zéro si les mesures "
    "existantes sont jugées suffisantes par le logiciel."
)
"""[Documentation officielle StormAudio] — stormaudio.com/room-
calibration/, section 'Dirac Live Active Room Treatment', 2e
paragraphe."""

STORMAUDIO_EXPERT_BASS_MANAGEMENT_NOT_CONFIRMED_ON_MARANTZ = (
    "⚠️ Point de vigilance important, à ne pas confondre : StormAudio "
    "annonce sur son propre site un système 'Expert Bass Management' "
    "EXCLUSIF à sa gamme de processeurs ('we have also created our own "
    "exclusive Expert Bass Management system'), gérant jusqu'à 6 zones de "
    "graves indépendantes avec routage par canal. Cette fonctionnalité "
    "est présentée comme un AJOUT PROPRIÉTAIRE StormAudio, EN PLUS de "
    "Dirac Live Bass Control — rien ne confirme qu'elle existe sur le "
    "Marantz CINEMA 30 de Steve, qui utilise Dirac Live Bass Control "
    "'nu' (sans la couche StormAudio). Ne pas recommander cette "
    "fonctionnalité à 6 zones à Steve sans vérifier d'abord si elle "
    "existe réellement dans le menu de son CINEMA 30 : toutes les "
    "règles de cette base de connaissances héritées de la documentation "
    "StormAudio (sections 1 à 9, hiérarchie de support, niveaux de "
    "support) viennent de pages décrivant le fonctionnement GÉNÉRIQUE "
    "d'ART sous licence Dirac (applicable à Marantz), mais celle-ci "
    "semble spécifiquement présentée comme un plus StormAudio."
)
"""[Documentation officielle StormAudio] — stormaudio.com/room-
calibration/, section 'Expert Bass Management'. Contradiction
secondaire notée : la même page affirme aussi 'StormAudio products
range is for now the only brand including this technology [ART]',
alors que dirac.com/brands/marantz confirme ART 'Available' sur
plusieurs modèles Marantz dont le CINEMA 30 — probablement une
affirmation marketing StormAudio devenue obsolète (ART étendu à
d'autres marques depuis), signalée ici honnêtement plutôt que
silencieusement ignorée."""

DIRAC_COMPATIBLE_BRANDS_LIST = [
    "ARCAM", "AudioControl", "Bluesound", "BRYSTON", "Datasat", "Denon",
    "Dynaudio", "Emotiva", "FOCAL", "Integra", "JBL", "JBL Synthesis",
    "Klipsch", "Lexicon", "Marantz", "McIntosh", "miniDSP", "Monoprice",
    "NAD", "Onkyo", "Pioneer", "Pioneer/Elite", "Primare", "Rotel",
    "Sonoro", "StormAudio", "Theta Digital", "Tonewinner", "Model M1",
]
"""[Documentation officielle Dirac] — dirac.com/brands, liste complète
des 29 marques listées comme ayant au moins un appareil compatible
Dirac Live (lue directement). Buckeye (l'ampli de puissance de Steve)
n'y figure pas — cohérent : c'est un ampli de puissance externe piloté
en analogique (XLR) par le CINEMA 30, pas un appareil qui exécute
lui-même Dirac Live."""

# ---------------------------------------------------------------------------
# 17. Guide officiel COMPLET des réglages ART (demande de Steve : "recupere
#     un maximum d'infos", puis "le faq aussi", sur le Helpdesk Dirac
#     officiel). Deux articles lus en entier via le navigateur intégré :
#     "How-to: ART Channel Group and Support Settings" (PDF téléchargeable
#     à https://mavenoidfiles.com/rhn76fg119p6goal115hjddgu67f7k8u8vd6,
#     lu en HTML) et "Dirac Live Active Room Treatment Setup Guide"
#     (incluant son tableau "Detailed Description of Parameters"), tous
#     deux sur helpdesk.dirac.com. C'est la source la plus précise et la
#     plus directement actionnable de toute cette base de connaissances
#     pour répondre à "quels réglages appliquer dans Dirac" — à utiliser
#     en priorité sur les sections 1-9 (qui dataient de documentation
#     StormAudio plus générale, partiellement recoupée ici).
# ---------------------------------------------------------------------------
ART_FOUR_CUSTOMIZATION_SETTINGS = (
    "Au-delà de la courbe cible, Dirac documente officiellement 4 "
    "réglages de personnalisation d'ART, listés dans cet ordre logique "
    "d'intervention : (1) Channel grouping (regroupement des canaux en "
    "groupes ART/principaux et groupes de support) ; (2) Group Support "
    "enable/disable (activer/désactiver qu'un groupe donné supporte un "
    "autre) ; (3) Group Support Range (la plage de fréquence sur "
    "laquelle ce support agit) ; (4) Group Support Level (l'intensité de "
    "ce support, en dB). Ces 4 réglages sont à n'explorer manuellement "
    "que si le résultat par défaut ne convainc pas totalement : ART "
    "fonctionne avec des réglages par défaut automatiquement détectés à "
    "partir des mesures."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'How-to: ART
Channel Group and Support Settings', section 'Problem formulation'."""

ART_PARAMETER_FSISO_OFFICIAL = (
    "Paramètre officiel nommé 'Fsiso', réglé par groupe ART (principal) : "
    "'agit comme une fréquence de crossover dans un système à gestion de "
    "graves. Le but est de trouver la valeur Fsiso la PLUS HAUTE pour "
    "votre système qui donne encore un bon résultat. Des valeurs Fsiso "
    "plus basses sont plus robustes mais offrent moins de bénéfice, des "
    "valeurs plus hautes offrent plus de bénéfice mais peuvent "
    "RÉVÉLER les enceintes de support dans le résultat final' "
    "(traduction). Valeur par défaut : 150 Hz. Plage légale : 50 à "
    "150 Hz. C'est la définition précise et chiffrée de la borne haute "
    "de la plage 20-150 Hz déjà connue : 150 Hz n'est pas une limite "
    "fixe absolue mais la valeur par défaut d'un paramètre réglable "
    "entre 50 et 150 Hz. Méthode de réglage conseillée par Dirac : "
    "partir de 150 Hz et descendre progressivement seulement si une "
    "enceinte de support devient localisable/audible individuellement."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'Dirac Live
Active Room Treatment Setup Guide', section 'ART Parameters', tableau
détaillé du paramètre 'Fsiso'."""

ART_OFFICIAL_FIGURES_1_2_3_CONFIRMED = (
    "Les 3 figures officielles de l'article 'How-to: ART Channel Group "
    "and Support Settings' ont été capturées visuellement (le navigateur "
    "intégré ne restitue que le texte/accessibilité, pas les images "
    "elles-mêmes — `screenshotPage` ciblé sur chaque conteneur d'image a "
    "permis de les voir). Elles confirment ET précisent le texte déjà "
    "lu : **Figure 1** montre le groupement DE BASE (Group 1 = Left "
    "Front + Right Front ENSEMBLE ; Group 2 = Center Front seul ; "
    "Group 3 = Left Surround + Right Surround ENSEMBLE ; Group 4 = LFE/"
    "caisson(s)), avec une flèche indiquant où décocher le support d'un "
    "groupe vers le LFE. **Figure 2** montre la variante AVANCÉE décrite "
    "en texte ('Direction of arrival') : Left Front, Right Front, Left "
    "Surround et Right Surround sont ici TOUS SÉPARÉS en 5 groupes "
    "individuels distincts (Group 1 à 5), avec 2 flèches illustrant "
    "l'asymétrie volontaire des plages de support entre Left Front et "
    "Right Surround. **Figure 3** revient au groupement de base (comme "
    "Figure 1) et montre où cliquer ('...') pour ouvrir les paramètres "
    "avancés du groupe LFE. **Point clé pour Steve** : sa configuration "
    "actuelle réelle (chaque enceinte dans son propre groupe, voir "
    "section 15/22) correspond exactement au cas AVANCÉ de la Figure 2 "
    "(tout séparé), pas au cas de base de la Figure 1/3 (paires "
    "groupées) — cohérent avec de l'intentionnel si sa position d'écoute "
    "est effectivement asymétrique par rapport à une paire, mais à "
    "confirmer avec lui plutôt qu'à supposer automatiquement."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'How-to: ART
Channel Group and Support Settings', Figures 1, 2 et 3, captées
visuellement via `screenshotPage` (le texte seul, déjà lu en section 17,
ne permettait pas de voir leur contenu visuel précis)."""

ART_PARAMETER_SUPPORT_LEVEL_OFFICIAL_TABLE = (
    "Paramètre officiel 'Support Level' (par relation groupe de support "
    "-> groupe principal) : 'détermine à quel point un haut-parleur est "
    "utilisé par l'algorithme. Pour équilibrer l'usage des enceintes et "
    "éviter la distorsion, changez les valeurs de Support Level selon la "
    "position des enceintes dans la pièce' (traduction). Valeur par "
    "défaut : -18 dB. Plage légale exacte : -24 dB (contribution "
    "MAXIMALE) à -1 dB (contribution MINIMALE) -- plage officielle plus "
    "précise que les 'valeurs rondes pratiques' -6/-18/-24 dB données "
    "ailleurs dans le même centre d'aide (article 'How-to: ART Channel "
    "Group and Support Settings') à titre d'exemples arrondis, pas comme "
    "les bornes réelles du curseur. Lien direct avec la section 14 de "
    "cette base (distorsion non-linéaire) : Dirac affirme explicitement "
    "que ce réglage sert à 'éviter de surcharger des enceintes "
    "spécifiques', donc à prévenir la distorsion par excursion excessive "
    "d'un haut-parleur trop sollicité comme support."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'Dirac Live
Active Room Treatment Setup Guide', tableau détaillé du paramètre
'Support level' ; et article 'How-to: ART Channel Group and Support
Settings', section 'Subwoofer rated capability' (valeurs arrondies
-6/-18/-24 dB)."""

ART_PARAMETER_F_SUPPORT_LOW_HIGH_OFFICIAL = (
    "Paramètres officiels 'F-support Low' et 'F-support High' (par "
    "relation groupe de support -> groupe principal), ensemble "
    "équivalents au 'Support Range' : F-support Low 'définit la "
    "fréquence la plus basse à laquelle une enceinte peut en supporter "
    "une autre... évite que de petites enceintes soient surchargées avec "
    "des graves qu'elles ne sont pas conçues pour gérer' — plage légale "
    "20 Hz à Fsiso, valeur par défaut détectée automatiquement depuis "
    "les mesures (PAS une valeur fixe). F-support High 'fixe la "
    "fréquence la plus haute... pour un caisson, agit comme un filtre "
    "passe-bas appliqué au signal d'entrée ; pour une enceinte "
    "large-bande, ce paramètre peut être ajusté selon la position de "
    "l'enceinte pour éviter de révéler les enceintes de support dans le "
    "résultat final' — plage légale F-support Low à Fsiso. Fait "
    "important confirmé explicitement : 'la plage de Support par défaut "
    "pour les enceintes NON-caisson ne descendra jamais sous 50 Hz' "
    "(section 'Active Room Treatment Filter Design' du même guide) — "
    "contrairement aux caissons, qui peuvent descendre jusqu'à 20 Hz."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'Dirac Live
Active Room Treatment Setup Guide', tableaux détaillés des paramètres
'F-support Low' et 'F-support High', et section 'Active Room Treatment
Filter Design' (règle des 50 Hz minimum pour les non-caissons)."""

ART_LFE_MAIN_CHANNEL_OFFICIAL_RULE = (
    "Règle officielle précise sur le canal LFE, directement actionnable "
    "pour le système de Steve : Dirac Live EXIGE qu'un appareil "
    "configuré avec un canal LFE déclare UNE enceinte comme 'enceinte "
    "principale' pour ce canal (cette enceinte sert de référence pour "
    "la correction de réponse impulsionnelle ART à toutes les positions "
    "de micro mesurées ; son groupe de canal porte aussi la courbe "
    "cible associée). LFE est officiellement défini (source Wikipedia "
    "citée par Dirac lui-même) comme produisant du contenu EN DESSOUS DE "
    "120 Hz, ce qui le fait rentrer entièrement dans la plage ART "
    "(<150 Hz). RÈGLE GÉNÉRALE DE BASE donnée par Dirac : 'ne laisser "
    "QUE les caissons et les grandes enceintes large-bande supporter le "
    "canal LFE' — il faut désactiver le support des PETITES enceintes "
    "vers le groupe LFE (décocher leur case de support). Appliqué au "
    "système réel de Steve : parmi ses enceintes, seules les façades "
    "Elipson Legacy 3220 (colonnes 2,5 voies, 35 Hz) sont de bons "
    "candidats 'grande enceinte large-bande' pour supporter le LFE — la "
    "centrale (Facet II 14C, 43 Hz) et les 4 surrounds (Facet II 14LCR, "
    "53 Hz) sont plus proches du profil 'petite enceinte' que ce "
    "principe recommande d'exclure du support LFE, sauf validation "
    "contraire par les mesures réelles."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'How-to: ART
Channel Group and Support Settings', section 'LFE main channel'."""

ART_SUBWOOFER_GROUPING_WALL_POSITION_RULE = (
    "Précision officielle sur le regroupement des caissons, allant "
    "au-delà de la règle déjà connue (séparer les caissons de capacités "
    "différentes) : Dirac recommande AUSSI de séparer en groupes "
    "distincts deux caissons qui n'ont pas le même soutien des murs "
    "environnants (ex : un caisson près d'une ouverture vers une pièce "
    "voisine a MOINS de soutien qu'un caisson dans un angle de la pièce "
    "d'écoute), car 'les murs de soutien affectent significativement la "
    "performance d'un caisson dans une pièce' (traduction). Donc la "
    "position géométrique des 2 caissons de Steve (SVS 3000 Micro "
    "R|Evolution) par rapport aux murs/coins de sa pièce devrait être "
    "vérifiée avant de décider s'ils doivent rester dans le même groupe "
    "ART ou être séparés — information non encore disponible dans ce "
    "projet (aucune donnée géométrique précise sur leur emplacement "
    "relatif aux murs n'a été collectée)."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'How-to: ART
Channel Group and Support Settings', section 'Subwoofer rated
capability', 2e paragraphe."""

ART_SUPPORT_SPEAKERS_NO_OWN_TARGET_CURVE = (
    "Point méthodologique à ne pas négliger en répondant à 'quelle "
    "courbe cible pour chaque enceinte' : dans Dirac Live ART, SEULS les "
    "groupes PRINCIPAUX (ART groups / main groups) ont une courbe cible "
    "qui leur est propre. Un haut-parleur placé en PUR groupe de "
    "support (séparé du groupe principal qu'il soutient) N'A PAS sa "
    "propre courbe cible : il contribue uniquement à aider le groupe "
    "principal qu'il supporte à atteindre LA cible DE CE GROUPE "
    "principal. Donc la question 'quelle courbe cible pour l'enceinte X' "
    "n'a de sens que si X est elle-même désignée comme canal principal "
    "d'un groupe ART, pas si elle n'est que support d'un autre groupe."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'How-to: ART
Channel Group and Support Settings', section 'Support speakers don't
have specific target curves'."""

ART_MINIMUM_MEASUREMENTS_OFFICIAL = (
    "Deux seuils chiffrés officiels distincts sur le nombre de mesures, "
    "à ne pas confondre : (1) il faut AU MOINS 3 mesures valides, dont "
    "le point d'écoute principal ('sweetspot'), pour que l'option ART "
    "soit seulement sélectionnable dans le logiciel (en dessous, "
    "l'option reste grisée) ; (2) il faut AU MOINS 9 positions de micro "
    "déjà capturées, ET une configuration système inchangée depuis, "
    "pour pouvoir réutiliser un projet Dirac existant SANS re-mesurer "
    "(sinon il faut re-mesurer). Avec ses 13 positions de micro (fichier "
    "TOP CALIB BASE.liveproject), Steve dépasse largement les deux "
    "seuils."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'Dirac Live
Active Room Treatment Setup Guide', sections 'Setting up Dirac Live' et
'Active Room Treatment Filter Design'."""

ART_GROUPING_EXAMPLE_OFFICIAL = (
    "Exemple officiel de regroupement donné par Dirac pour un système "
    "2.2 (2 façades + 2 caissons), transposable au raisonnement pour un "
    "système plus grand comme celui de Steve (7.2) : 'Deux groupes : "
    "Façade Gauche et Droite ensemble dans un groupe, les 2 caissons "
    "ensemble dans un second groupe, si on veut utiliser les caissons "
    "de la même façon. Trois groupes : Façade Gauche et Droite "
    "ensemble, et CHAQUE caisson dans son PROPRE groupe séparé si on "
    "veut contrôler leur interaction avec les façades indépendamment' "
    "(traduction). Règle générale pour les grands systèmes : 'grouper "
    "les enceintes selon leur usage et leur position, en pensant à "
    "l'impact de la position de l'enceinte sur des réglages comme Fsiso "
    "et F-support High. Choisir les groupes qui ont le plus de sens "
    "pour votre système et votre position d'écoute' (traduction)."
)
"""[Documentation officielle Dirac] — Helpdesk, article 'Dirac Live
Active Room Treatment Setup Guide', section 'Comment on Grouping'."""

ART_VS_RC_SPATIAL_CONSISTENCY_OFFICIAL = (
    "Différence officielle précise entre Room Correction (RC) seul et "
    "ART, cruciale pour comprendre ce qu'ART apporte concrètement en "
    "plus : 'RC améliore la performance dans la zone mesurée avec "
    "l'objectif d'atteindre la réponse cible EN MOYENNE, ce qui veut "
    "dire qu'une mesure ponctuelle donnée (après calibration) peut "
    "montrer un léger écart par rapport à la courbe cible. ART, grâce à "
    "son contrôle du champ sonore utilisant toutes les enceintes, a une "
    "performance significativement plus forte pour réduire la variation "
    "spatiale et reproduire fidèlement la courbe cible À N'IMPORTE "
    "QUELLE position mesurée' (traduction). Autrement dit : RC vise une "
    "bonne moyenne sur l'ensemble des positions, ART vise une bonne "
    "cohérence à CHAQUE position individuellement -- bénéfice direct "
    "pour un salon avec plusieurs places assises."
)
"""[Documentation officielle Dirac] — Helpdesk, 'Dirac Live Active Room
Treatment (ART) FAQ', question sur la différence entre RC et ART sur
la variation spatiale. Confirme et précise, en langage produit, le
concept de 'target stage' du brevet US8213637B2 (section 12)."""

ART_OFFICIAL_MIMO_AND_ROOM_SIZE = (
    "Confirmations officielles supplémentaires de la FAQ ART : 'ART "
    "utilise une technologie MIMO brevetée pour coordonner toutes les "
    "enceintes, optimisant leur interaction pour gérer les résonances "
    "induites par la pièce, particulièrement dans la plage critique de "
    "graves 20-150 Hz' -- confirmation du terme officiel 'MIMO' "
    "(Multiple-Input Multiple-Output), cohérent avec le modèle MIMO des "
    "brevets lus (sections 11-13). Plage de pièce optimale confirmée "
    "identique à celle déjà connue : environ 12 à 100 m². Config "
    "minimale : système stéréo (2 enceintes). Prérequis matériel "
    "explicites : AVR/récepteur certifié ART, licence Dirac Live avec "
    "add-on ART, application Dirac Live sur Windows/macOS (PAS iOS/"
    "Android pour Bass Control et ART), microphone de mesure "
    "omnidirectionnel, licence Bass Control si un ou plusieurs caissons "
    "sont utilisés."
)
"""[Documentation officielle Dirac] — Helpdesk, 'Dirac Live Active Room
Treatment (ART) FAQ' ; dirac.com/resources/downloads (note OS)."""

# ---------------------------------------------------------------------------
# 18. Valeur ajoutée du service par rapport à l'automatique Dirac (demande
#     de Steve : lister précisément ce qui différencie notre approche d'un
#     simple clic sur "Calculate" avec les réglages par défaut). Inclut
#     HRTF (nouveau sujet, jamais traité ici), le retour d'expérience de
#     Steve sur les paliers de réglage de l'automatique, et son exemple
#     concret de groupement croisé.
# ---------------------------------------------------------------------------
HRTF_CONCEPT_AND_LIMIT_FOR_MULTICHANNEL = (
    "La HRTF (Head-Related Transfer Function) est la façon dont la "
    "taille/forme de la tête, des oreilles (pavillon), du conduit "
    "auditif et du torse d'UNE personne filtre un son selon sa position "
    "dans l'espace avant qu'il n'atteigne le tympan — boost général "
    "autour de 2-5 kHz, résonance principale type +17 dB vers 2700 Hz, "
    "mais très variable d'une personne à l'autre. Elle aide le cerveau à "
    "lever 'le cône de confusion' (positions différentes qui donnent les "
    "mêmes indices de différence de temps/niveau entre les 2 oreilles, "
    "ITD/ILD) grâce aux indices spectraux propres au pavillon de chaque "
    "individu. ⚠️ Point de prudence important, à ne pas confondre : la "
    "HRTF est typiquement appliquée comme un FILTRE ARTIFICIEL pour "
    "SIMULER une position de source sur un rendu BINAURAL (casque, 2 "
    "canaux). Sur un système multicanal de haut-parleurs PHYSIQUES réels "
    "(le cas de Steve), chaque enceinte est déjà à sa vraie position "
    "dans l'espace : c'est la HRTF NATURELLE et propre de l'auditeur "
    "(son vrai corps, en temps réel) qui s'applique directement, sans "
    "qu'aucun filtre logiciel n'ait besoin de la simuler. Rien dans les "
    "3 brevets Dirac lus (sections 11-13) ni dans la documentation "
    "officielle (sections 16-17) ne mentionne de traitement HRTF/"
    "binaural : le lien pertinent et déjà documenté est plutôt indirect "
    "— la qualité de localisation naturelle du cerveau dépend de la "
    "PRÉCISION des indices ITD/ILD réels reçus par les 2 oreilles, donc "
    "de la fidélité de CHAQUE enceinte prise isolément (mécanisme de "
    "symétrie de paire, brevet US9426600B2) et de l'absence d'enceinte "
    "de support 'révélée'/localisable individuellement (paramètre "
    "F-support High, section 17) — PAS d'un filtre HRTF explicite que "
    "Dirac appliquerait."
)
"""[Acoustique générale] — https://en.wikipedia.org/wiki/
Head-related_transfer_function. Le paragraphe de mise en garde est un
raisonnement de rapprochement avec les sources déjà citées de ce
fichier, pas une citation directe d'une source qui ferait ce lien."""

DIRAC_AUTOMATIC_COARSE_STEPS_STEVE_FEEDBACK = (
    "Retour d'expérience de Steve (non encore vérifié par une source "
    "officielle indépendante) : le réglage automatique de Dirac en mode "
    "'Calculate' par défaut n'offrirait, en pratique, qu'un choix par "
    "GROS PALIERS (de l'ordre de 6 dB) pour le niveau de support, plutôt "
    "qu'un réglage fin continu. Nuance à garder : le tableau OFFICIEL "
    "déjà documenté (ART_PARAMETER_SUPPORT_LEVEL_OFFICIAL_TABLE, section "
    "17) montre une plage légale CONTINUE de -24 à -1 dB sur le curseur "
    "manuel — donc le curseur LUI-MÊME n'est pas limité à des paliers de "
    "6 dB. La remarque de Steve porte donc plus probablement sur ce que "
    "l'algorithme AUTOMATIQUE choisit par défaut sans intervention "
    "(peut-être un pas de calcul interne grossier, ou le fait que les "
    "'rough numbers' -6/-18/-24 dB donnés en exemple dans la doc "
    "(section 17) sont les seules valeurs que l'automatique explore "
    "réellement) plutôt que sur une vraie limite de l'interface "
    "elle-même. Non confirmé officiellement : à vérifier en pratique "
    "sur le système de Steve plutôt qu'à présenter comme un fait Dirac "
    "établi. **Confirmation directe de Steve sur SA méthode** (distincte "
    "de l'automatique) : il règle lui-même le Support Level "
    "manuellement 'sans utiliser les paliers de 6 dB', donc bien sur la "
    "plage continue du curseur — cohérent avec l'hypothèse ci-dessus que "
    "la limite par paliers concerne l'algorithme automatique, pas "
    "l'interface manuelle elle-même."
)
"""[Retour d'expérience Steve] — affirmation de Steve sur le comportement
observé de l'algorithme automatique Dirac, en tension avec le tableau
officiel de la section 17 qui documente une plage continue sur le
curseur manuel. Les deux faits ne sont pas forcément contradictoires
(l'un décrit le curseur manuel, l'autre le comportement de l'auto)."""

STEVE_CROSSED_GROUPING_EXAMPLE = (
    "Exemple concret donné par Steve de son propre réglage manuel sur "
    "son système réel : il a regroupé Surround Back Right avec Surround "
    "Right, avec des réglages de support CROISÉS entre eux. Ceci est "
    "cohérent avec le cas d'usage 'Directional bass'/groupement "
    "personnalisé déjà documenté officiellement (section 17, "
    "ART_GROUPING_EXAMPLE_OFFICIAL et le concept de Figure 2 de l'article "
    "'How-to: ART Channel Group and Support Settings', "
    "ART_OFFICIAL_FIGURES_1_2_3_CONFIRMED) : regrouper deux enceintes "
    "censées être proches dans l'espace (Surround Right et Surround Back "
    "Right sont toutes deux du côté droit de la pièce) permet de leur "
    "faire partager un support mutuel plus marqué qu'avec les enceintes "
    "du côté gauche, renforçant la cohérence spatiale de ce côté — un "
    "exemple réel et personnalisé que l'automatique par défaut "
    "n'explore pas de lui-même (voir ART_FOUR_CUSTOMIZATION_SETTINGS, "
    "qui précise que le groupement par défaut n'est révisé que "
    "manuellement)."
)
"""[Retour d'expérience Steve] — réglage réel appliqué par Steve sur son
propre système, rapporté tel quel."""

SERVICE_VALUE_PROPOSITION_VS_AUTOMATIC = (
    "Synthèse de la valeur ajoutée du service par rapport à un simple "
    "clic sur 'Calculate' avec les réglages par défaut d'ART, telle "
    "qu'énoncée explicitement par Steve : (1) ajustement INDIVIDUEL de "
    "la courbe de réponse de chaque enceinte à partir de SES propres "
    "mesures réelles, plutôt qu'un gabarit de courbe cible générique ; "
    "(2) compréhension approfondie du mécanisme ART (3 brevets lus en "
    "texte intégral + documentation officielle complète, sections 11 à "
    "17) appliquée en respectant les limites physiques réelles du "
    "matériel (fiches techniques vérifiées, section 15, et limite de "
    "distorsion non-linéaire, section 14) plutôt que des réglages à "
    "l'aveugle ; (3) prise en compte des caractéristiques des matériaux "
    "de la pièce d'écoute (absorption/diffusion, section 10) ; (4) "
    "niveaux de support ajustés sur mesure plutôt que par les paliers "
    "grossiers de l'automatique (DIRAC_AUTOMATIC_COARSE_STEPS_STEVE_"
    "FEEDBACK, à vérifier) ; (5) plages de fréquence de support (F-"
    "support Low/High) ajustées sur mesure selon la fiche technique "
    "réelle de chaque enceinte plutôt que la détection automatique "
    "générique ; (6) groupes d'enceintes choisis pour leur pertinence "
    "géométrique/acoustique réelle (voir STEVE_CROSSED_GROUPING_EXAMPLE) "
    "plutôt que le groupement par défaut. Limite honnête : ces leviers "
    "sont une synthèse de ce que permet l'interface ART documentée "
    "officiellement (section 17), pas une promesse de résultat garanti "
    "— leur efficacité réelle dépend de chaque système et reste à "
    "valider par la mesure avant/après, comme le reste de cette base de "
    "connaissances le rappelle systématiquement."
)
"""[Steve] — proposition de valeur du service, formulée explicitement
par Steve, recoupée avec les sections déjà sourcées de ce fichier."""

# ---------------------------------------------------------------------------
# 19. Standards professionnels des VRAIS cinémas (demande de Steve :
#     "fais des recherches pour savoir comment sont les reglages des
#     courbes dans les vrais cinemas", puis précision : "le rendu des
#     voix du cinema c'est ce que j'aimerais avoir chez moi"). Sources
#     lues directement via le navigateur intégré (web_fetch bloqué sur
#     Google comme d'habitude) : article technique mkpereport.com
#     ("X-Curve Is Not An EQ Curve"), confirmé par plusieurs sources
#     indépendantes convergentes sur les valeurs chiffrées (Lafont Audio,
#     francis.audio, Elliott Sound Products/sound-au.com, fils AVS
#     Forum). [Acoustique générale] / [Standard professionnel cinéma]
# ---------------------------------------------------------------------------
X_CURVE_IS_NOT_AN_EQ_CURVE = (
    "Mise en garde professionnelle essentielle, à ne jamais perdre de "
    "vue : la 'X-Curve' (standard SMPTE ST202 / ISO 2969) utilisée dans "
    "les VRAIS cinémas commerciaux N'EST PAS une courbe d'égalisation à "
    "reproduire — c'est une FENÊTRE DE MESURE conçue pour permettre à un "
    "technicien, avec un analyseur de spectre standard, de retrouver "
    "approximativement ce qu'entendait le réalisateur dans sa salle de "
    "mixage, EN COMPENSANT les effets de la réverbération de la GRANDE "
    "salle et l'absorption atmosphérique sur de longues distances "
    "(jusqu'à -5 dB à 10 kHz sur 30 mètres, selon température/"
    "conditions). La source elle-même (un ingénieur spécialisé cinéma, "
    "mkpereport.com) signale que la méprise la plus commune est "
    "justement de traiter la X-Curve comme une 'cible à atteindre "
    "exactement', ce qui mène à une SUR-ÉGALISATION et pas "
    "nécessairement au meilleur son. Conséquence directe pour Steve : "
    "copier la X-Curve des grandes salles telle quelle chez lui serait "
    "une erreur reconnue par les professionnels eux-mêmes — sa pièce "
    "n'a ni les dizaines de mètres de distance d'écoute, ni l'écran "
    "perforé, ni la réverbération d'une salle de centaines de places."
)
"""[Acoustique générale / standard professionnel] — mkpereport.com,
'X-Curve Is Not An EQ Curve' (2012), article technique signé par un
ingénieur spécialisé en son de cinéma (blog mkpeReport, couverture
cinéma numérique/3D/HFR). Lu en entier via le navigateur intégré."""

X_CURVE_STANDARD_VALUES = (
    "Valeurs chiffrées de la X-Curve STANDARD (grandes salles de cinéma "
    "commerciales), confirmées par plusieurs discussions techniques "
    "indépendantes (AVS Forum, Gearspace) : la courbe reste plate "
    "jusqu'à 2 kHz, puis descend à 3 dB par octave au-dessus — soit "
    "environ -6 dB à 8 kHz et -9 dB à 16 kHz par rapport au niveau de "
    "référence à 2 kHz. Cette pente compense spécifiquement "
    "l'atténuation de l'air sur de grandes distances (voir "
    "X_CURVE_IS_NOT_AN_EQ_CURVE) : plus la salle est grande, plus "
    "l'atténuation naturelle de l'aigu par l'air est importante, donc "
    "plus il faut 'pré-booster' l'aigu à la source (dans le mixage "
    "studio) pour qu'il survive au trajet jusqu'au fond de la salle — "
    "la X-Curve en salle de mixage est donc l'INVERSE compensatoire de "
    "ce qui sera réellement perdu en salle de projection."
)
"""[Acoustique générale / standard professionnel] — discussions
techniques recoupées : AVS Forum ('Pro Cinema Speakers, the X-Curve,
and other Target Curves at Home', fil de 2014) et Gearspace ('Those
mixing on near/midfields for theater: X-curve?'). Valeurs non
officielles du texte intégral SMPTE ST202 (document payant, non
consulté), mais cohérentes entre elles sur 2 sources indépendantes."""

SMALL_ROOM_X_CURVE_VALUES = (
    "Point le plus directement pertinent pour Steve : le standard "
    "lui-même prévoit une VARIANTE 'small room X-curve' pour les salles "
    "de PETITE taille (moins de 150 m³ selon une source), avec une "
    "pente BEAUCOUP PLUS DOUCE : 1,5 dB par octave au-dessus de 2 kHz "
    "(au lieu de 3 dB/octave pour la grande salle) — soit environ "
    "-3 dB à 8 kHz et -4,5 dB à 16 kHz. Cette variante existe "
    "précisément parce que l'atténuation atmosphérique de l'aigu, "
    "proportionnelle à la distance, est beaucoup plus faible sur "
    "quelques mètres (salle de petite taille/salon) que sur 30+ mètres "
    "(grande salle de cinéma) : la correction nécessaire est donc "
    "logiquement moins marquée. **Comparaison chiffrée avec 'courbe "
    "maison.targetcurve' de Steve** (créée directement sur son CINEMA "
    "30, voir note de prudence ci-dessous) : à 17723 Hz, la small-room "
    "X-curve prédit mathématiquement -4,72 dB (en prenant 2 kHz comme "
    "point de départ), contre -5,00 dB mesurés dans le fichier de Steve "
    "— quasi identique. À 6060 Hz, la prédiction donne -2,40 dB contre "
    "-3,83 dB observés — du même ordre de grandeur, un peu plus marqué. "
    "Hypothèse plausible (NON confirmée par Steve) : son ajustement "
    "pourrait s'inspirer de cette 'small-room X-curve', le standard "
    "professionnel le plus proche de son cas d'usage réel (home cinéma, "
    "petite salle), plutôt qu'être une courbe arbitraire."
)
"""[Acoustique générale / standard professionnel] — 4 sources
indépendantes convergentes sur la valeur 1,5 dB/octave à partir de
2 kHz : lafontaudio.com/courbe-X.htm (français), francis.audio (site
francophone, page '7.2 Quelle courbe de réponse cible ?'),
sound-au.com/articles/cinema-sound.htm (Elliott Sound Products,
référence technique reconnue), fil AVS Forum 2014 cité ci-dessus.
Calcul de comparaison avec 'courbe maison.targetcurve' effectué par
nous-mêmes (formule : -1,5 × log2(f/2000) dB au-dessus de 2 kHz), pas
une affirmation directe d'une des sources."""

CINEMA_DIALOGUE_RENDERING_CAVEAT = (
    "⚠️ Limite honnête importante avant de conclure quoi que ce soit sur "
    "le rendu des VOIX spécifiquement (la demande précise de Steve) : "
    "aucune des sources lues dans cette section ne traite spécifiquement "
    "du traitement du canal CENTRAL/dialogue en cinéma professionnel — "
    "la X-Curve et sa variante 'small room' sont des courbes de "
    "calibration GLOBALES de la salle (toutes enceintes), pas des "
    "ajustements ciblés sur les dialogues. Le rendu des voix au cinéma "
    "dépend de bien d'autres facteurs non couverts ici : le niveau de "
    "référence (déjà documenté, CINEMA_REFERENCE_LEVEL_PRINCIPLE, "
    "section 10), la qualité du mixage lui-même (hors de notre contrôle "
    "une fois le film produit), la directivité du haut-parleur central "
    "et son intégration avec l'écran (non applicable à un vrai écran "
    "acoustiquement transparent chez Steve), et la clarté apportée par "
    "ART via la réduction du temps de décroissance (section 18, déjà "
    "documentée). Ne pas présenter la 'small-room X-curve' comme LA "
    "solution du rendu voix cinéma : c'est une piste cohérente et "
    "sourcée, pas une certitude validée pour ce cas d'usage précis."
)
"""Synthèse de prudence rédigée par nous-mêmes à partir des limites
identifiées dans les sources ci-dessus — pas une citation directe."""

# ---------------------------------------------------------------------------
# 20. Article écrit d'Anthony Grimani sur le canal centre/dialogue (piste de
#     repli honnête : Steve a partagé un live YouTube avec Grimani que
#     nous ne pouvons pas analyser — pas de transcription disponible pour
#     cette vidéo, et contrairement à Gemini, cet environnement n'a pas de
#     capacité native d'analyse audio/vidéo multimodale directe. Un
#     article ÉCRIT du même expert, sur le même sujet précis demandé par
#     Steve — rendu des voix/dialogue — a été trouvé et lu en entier à la
#     place). [Avis d'expert professionnel, pas une étude académique]
# ---------------------------------------------------------------------------
GRIMANI_CENTER_CHANNEL_ENERGY_DISTRIBUTION = (
    "Données chiffrées mesurées par Grimani lui-même sur 10 films "
    "d'action (moyenne) : le canal Centre porte le PLUS d'énergie de "
    "tout le système ('is right in the middle of all the picture "
    "action... film directors and sound designers naturally put the "
    "majority of the sound elements there'). Par rapport au Centre : "
    "Gauche/Droite = -3 dB (moitié de la puissance), canaux latéraux "
    "(Sides) = encore -3 dB de moins, canaux arrière (Backs) = encore "
    "-3 dB de moins. Conclusion de l'auteur : 'il est donc logique "
    "d'être particulièrement attentif à la qualité, la clarté, la "
    "bande passante et la dynamique de l'enceinte Centre' — cohérent "
    "avec l'importance que Steve accorde lui-même au rendu de sa "
    "centrale."
)
"""[Avis d'expert professionnel] — Anthony Grimani, 'Get Centered',
Residential Systems (residentialsystems.com/features/get-centered),
auteur confirmé (lien direct vers son profil). Lu en entier via le
navigateur intégré."""

GRIMANI_PHANTOM_CENTER_EQ_RECOMMENDATION = (
    "⚠️ Donnée chiffrée précise de Grimani, MAIS pour un contexte "
    "différent de celui de Steve — à ne pas appliquer telle quelle sans "
    "cette réserve : pour un système SANS enceinte centrale physique "
    "(image centrale 'fantôme' reconstituée par les enceintes Gauche/"
    "Droite seules), Grimani recommande : déclarer le Centre 'Small' au "
    "décodeur surround, router les sorties L/C/R vers un égaliseur DSP "
    "avec fonction de mixage, et '**ajouter environ 6 dB, sur une "
    "largeur d'un octave, centré à 1500 Hz**' pour compenser la perte "
    "d'énergie dans le médium inhérente à une image centrale fantôme "
    "(causée par le 'crosstalk inter-auriculaire' : l'effet d'ombre de "
    "la tête quand le même signal arrive de 2 enceintes séparées d'un "
    "angle horizontal d'environ 45°). Puis mélanger ce Centre recalculé "
    "dans Gauche/Droite à "
    "-3 dB — procédé que Grimani nomme 'Phantom+™'. **Steve a une "
    "VRAIE enceinte centrale physique (Elipson Prestige Facet II 14C)**, "
    "donc ce correctif spécifique au phénomène de crosstalk d'une "
    "fausse image centrale ne s'applique PAS directement à son cas — "
    "mais la fréquence citée (1500 Hz, zone de présence/intelligibilité "
    "des consonnes) reste une donnée précise et sourcée, potentiellement "
    "une piste à considérer avec prudence, pas une prescription "
    "directement transposable."
)
"""[Avis d'expert professionnel] — Anthony Grimani, 'Get Centered',
Residential Systems. Même source que ci-dessus. Section centrale de
l'article décrivant le procédé 'Phantom+™'."""

GRIMANI_SUBWOOFER_LOCALIZATION_THRESHOLD_120HZ = (
    "Seuil chiffré précis donné par Grimani dans ce même article : "
    "'120 Hz is the frequency at which the average listener can start "
    "to detect that the speaker and subwoofer are not in the same "
    "place' — argument qu'il utilise pour insister sur le fait de "
    "garder TOUS les caissons près de l'écran/façade (pas dispersés "
    "ailleurs dans la pièce) si l'enceinte centrale ne descend pas en "
    "dessous de cette fréquence. Complémentaire aux seuils déjà "
    "documentés sur le bass management (section 10) et la direction "
    "d'arrivée en dessous de 80 Hz (section 17, brevet US9426600B2) — "
    "ces 2 seuils (80 Hz non-audible, 120 Hz audible) ne sont pas "
    "contradictoires : ils viennent de 2 sources différentes et "
    "encadrent une zone de transition plausible entre 80 et 120 Hz, "
    "sans qu'une valeur unique et consensuelle ne soit établie ici."
)
"""[Avis d'expert professionnel] — Anthony Grimani, 'Get Centered',
Residential Systems. Même source que ci-dessus."""

# ---------------------------------------------------------------------------
# 21. Articles Audioholics sur Dirac Live (demande de Steve : explorer
#     Audioholics pour toute information utile, en excluant Audyssey).
#     Source journalistique spécialisée reconnue dans l'industrie, avec
#     CITATIONS DIRECTES ATTRIBUÉES à des dirigeants/scientifiques Dirac
#     Research eux-mêmes (pas une reformulation tierce). [Journalisme
#     spécialisé audio, citations officielles directes]
# ---------------------------------------------------------------------------
DIRAC_COO_JOHANSSON_BASS_DECAY_QUOTE = (
    "Citation officielle directe de Mathias Johansson (Chief Product "
    "Officer de Dirac — déjà identifié comme co-inventeur du brevet "
    "US8213637B2, section 12), rapportée par Audioholics lors de "
    "l'annonce d'ART (printemps 2023) : 'Dirac pioneered digital room "
    "correction through our impulse response optimization technology "
    "found in our acclaimed Dirac Live Room Correction feature. Now, "
    "with Active Room Treatment we are moving beyond traditional room "
    "correction to actually reduce bass decay times digitally, without "
    "needing bass traps or thick layers of wall absorption.' Confirme, "
    "par une citation NOMMÉE et attribuée (pas une reformulation "
    "marketing anonyme), exactement ce que le Helpdesk officiel disait "
    "déjà (section 18) sur la réduction du temps de décroissance des "
    "graves ('lingering bass')."
)
"""[Journalisme spécialisé, citation officielle directe] —
audioholics.com/audio-technologies/dirac-live-active-room-treatment-
dsp-room-eq-spring-201823, 'Dirac Live Active Room Treatment: One Giant
Leap for Room EQ, Coming Spring '23' (Wayde Robson, 2022/2023). Lu en
entier via le navigateur intégré."""

DIRAC_SIMO_VS_MIMO_HISTORICAL_DISTINCTION = (
    "Précision historique et technique importante, confirmée par cet "
    "article : avant ART, 'Dirac Live Room Correction' (RC) classique "
    "reposait sur un système **SIMO** (Single-Input Multiple-Output) : "
    "une correction qui ne pouvait traiter qu'UNE enceinte à la fois, "
    "séquentiellement. ART introduit pour la première fois un vrai "
    "système **MIMO** (Multiple-Input Multiple-Output) : le microphone "
    "de calibration lit le son de TOUTES les enceintes SIMULTANÉMENT, "
    "'en utilisant plusieurs microphones dans des zones d'écoute clés à "
    "travers la pièce', permettant pour la première fois un véritable "
    "contrôle SPATIAL (pas juste par-enceinte). Cohérent avec le terme "
    "'MIMO' déjà confirmé officiellement par la FAQ Dirac (section 18), "
    "mais cette source ajoute la distinction historique AVANT/APRÈS qui "
    "manquait : RC seul = SIMO (limité), ART = MIMO (le vrai saut "
    "technologique)."
)
"""[Journalisme spécialisé] — même article Audioholics que ci-dessus."""

DIRAC_SCIENTIST_BRANNMARK_CO_OPTIMIZATION_QUOTE = (
    "Citation officielle directe du Dr. Lars-Johan Brännmark (Research "
    "Fellow et Chief Scientist chez Dirac — déjà identifié comme "
    "co-inventeur des 3 brevets lus en texte intégral, sections 11 à "
    "13), rapportée par Audioholics : il nomme ce mécanisme "
    "'**Loudspeaker Co-Optimization**' — 'the process that allows "
    "Dirac Live Active Room Treatment to apply room-correction to each "
    "speaker in your multi-channel system simultaneously as they work "
    "together to create equal results across the spatial plane.' "
    "Terme officiel supplémentaire, attribué nommément à l'un des "
    "inventeurs réels des brevets déjà analysés — renforce la "
    "cohérence entre le langage marketing/presse et les mécanismes "
    "mathématiques déjà documentés à partir des brevets eux-mêmes. "
    "L'article emploie aussi une métaphore pédagogique utile pour "
    "expliquer le concept aux clients : 'one hand (or one speaker) "
    "washes the other' (comme un bruiteur actif/Active Noise "
    "Cancelling qui annule les fréquences sur-représentées dues aux "
    "réflexions et interactions entre plusieurs enceintes jouant en "
    "même temps)."
)
"""[Journalisme spécialisé, citation officielle directe] — même article
Audioholics que ci-dessus."""

STORMAUDIO_FIRST_ART_PARTNER_TIMELINE = (
    "Clarification historique importante qui résout la 'tension' notée "
    "en section 16 (StormAudio affirmant être 'la seule marque' à "
    "inclure ART) : cet article (printemps 2023) confirme que "
    "StormAudio a bien été le TOUT PREMIER partenaire à recevoir ART, "
    "via une mise à jour firmware gratuite pour tout achat d'un "
    "processeur/AVR StormAudio à partir du 1er janvier 2023 (ou "
    "199-299$ de licence pour les achats antérieurs). La déclaration "
    "StormAudio 'seule marque' n'était donc pas une erreur marketing "
    "mais un FAIT RÉEL au moment où elle a été écrite (ART n'existait "
    "alors que sur StormAudio) — elle est simplement devenue obsolète "
    "une fois ART étendu à d'autres marques (dont Marantz, confirmé "
    "disponible sur le CINEMA 30 de Steve, section 16) sans que la page "
    "StormAudio ne soit mise à jour depuis."
)
"""[Journalisme spécialisé] — même article Audioholics que ci-dessus,
section 'Practical Testing Availability'."""

DIRAC_THREE_PRODUCT_TIERS_SIMO_VS_MIMO = (
    "Clarification IMPORTANTE issue d'un 2e article Audioholics (2022, "
    "antérieur à ART), à prendre avec prudence car il distingue des "
    "produits Dirac qui pourraient prêter à confusion avec ART : "
    "l'article liste 3 types de correction Dirac déployés ou prévus "
    "chez Denon/Marantz : "
    "(1) 'Basic Dirac Live' — 'the original version, its SIMO "
    "[Single-Input Multiple-Output] and has no bass management of its "
    "own' ; "
    "(2) 'Dirac Live with Bass Control' (version mono-caisson ou "
    "multi-caisson) — reste SIMO : 'it doesn't cancel the modes, it is "
    "simply exciting modes more evenly amongst the 2-4 LF sources' "
    "(ne fait qu'exciter les modes plus uniformément entre 2 à 4 "
    "caissons, ne les annule PAS) ; "
    "(3) 'Dirac Spatial Correction' (anciennement nommé 'Unison') — "
    "vrai MIMO, mais l'article précise explicitement (en 2022) que "
    "'it is not something that exists on any consumer products for "
    "the home. It is used in some cars, like the noted Volvo.' "
    "ATTENTION : il n'est PAS certain que 'Dirac Spatial "
    "Correction'/Unison (orienté automobile) soit le MÊME produit que "
    "'Active Room Treatment' (ART, lancé printemps 2023 pour le grand "
    "public, section 21 ci-dessus) — les deux emploient MIMO mais "
    "semblent être des gammes de produits distinctes développées par "
    "Dirac Research pour des marchés différents (auto vs home "
    "cinema). Cette distinction mérite d'être gardée à l'esprit : le "
    "'MIMO'/'Loudspeaker Co-Optimization' documenté pour ART (section "
    "21) est a priori bien ART, et non ce produit automobile, mais "
    "aucune source officielle Dirac trouvée à ce jour ne clarifie "
    "formellement la relation exacte entre 'Unison' et 'ART'."
)
"""[Journalisme spécialisé, à vérifier] — audioholics.com/editorials/
dirac-road-map-denon-marantz-2022, 'Dirac Roadmap for 2022 Denon &
Marantz AV Products' (Gene DellaSala, 2022). Lu en entier via le
navigateur intégré."""

DENON_MARANTZ_OFFICIAL_DIRAC_QA_2022 = (
    "Q&A officiel (réponses attribuées à Sound United/Denon/Marantz "
    "dans l'article) sur le déploiement de Dirac Live chez Denon et "
    "Marantz, utile pour comprendre le contexte matériel du CINEMA 30 "
    "de Steve : "
    "(1) Firmware supportant Dirac Live (versions limited ET full "
    "bandwidth) déployé 'AFTER the firmware update in March 2023' ; "
    "Bass Control prévu '2024 - TBD' (pas encore commencé à l'époque) ; "
    "Spatial correction : 'too early to commit anything new' (pas de "
    "date). "
    "(2) Les modèles Denon/Marantz ANTÉRIEURS à 2022 (ex. AVR-X8500H, "
    "SR7015/8015, AV7706, AV8805) NE PEUVENT PAS être mis à jour pour "
    "supporter Dirac Live — nécessite un nouveau DSP/matériel présent "
    "uniquement à partir du millésime 2022. Le CINEMA 30 de Steve "
    "étant un modèle plus récent (2023+), il fait partie de la "
    "nouvelle génération compatible nativement. "
    "(3) Dirac Live est un 'optional upgrade (upcharge)' : licence à "
    "acheter séparément sur dirac.com/denon ou dirac.com/marantz, prix "
    "exact non communiqué ('Final pricing is under Dirac's control and "
    "may change in the future'). "
    "(4) Dirac et Audyssey sont des calibrations strictement SÉPARÉES "
    "— impossible de combiner une fonction Audyssey (ex. Dynamic "
    "Volume/Dynamic EQ) avec Dirac Live. Un microphone de calibration "
    "DÉDIÉ est nécessaire pour Dirac (type MiniDSP UMIK-1, déjà "
    "documenté comme celui utilisé par Steve) — le micro Audyssey "
    "fourni avec l'ampli ne fonctionne QUE pour Audyssey. "
    "(5) La fonction 'Speaker Preset' permet de stocker 2 calibrations "
    "sur l'AVR et de basculer entre elles (ex. Preset 1 = Audyssey, "
    "Preset 2 = Dirac Live) — utile pour comparer en A/B. "
    "(6) Sound United NE supporte PAS de PEQ manuel indépendant : tout "
    "ajustement EQ doit passer par le logiciel Dirac Live ou par "
    "l'app/logiciel Audyssey MultEQ — cohérent avec la pratique de "
    "Steve qui ajuste ses courbes cibles directement dans Dirac Live "
    "(points de contrôle), pas via un PEQ tiers."
)
"""[Confirmation officielle via journalisme spécialisé] — même article
Audioholics que ci-dessus (Q&A attribué à Sound United/Denon/Marantz)."""

# ---------------------------------------------------------------------------
# 22. Anthony Grimani — placement d'enceintes et traitement de pièce
#     (live YouTube avec la chaîne Youthman, demandé par Steve, non
#     accessible directement par l'assistant — ni transcription ni
#     capacité d'analyse vidéo native). Steve a transmis un RÉSUMÉ produit
#     par Gemini (IA tierce) à partir de cette vidéo.
#     NIVEAU DE PREUVE À TRAITER AVEC PRUDENCE SUPPLÉMENTAIRE : ce n'est
#     PAS une lecture directe d'une source primaire par l'assistant, mais
#     un résumé secondaire produit par un autre système d'IA, non
#     vérifiable formellement ici (risque résiduel d'erreur/d'extrapolation
#     de la part de Gemini). Le niveau de confiance intrinsèque sur
#     l'identité et l'expertise de Grimani reste élevé : il s'agit du même
#     expert déjà cité en section 20 (article écrit 'Get Centered', lu
#     directement par l'assistant), confirmé par Steve comme étant
#     l'intervenant du live. [Avis d'expert professionnel, rapporté par
#     IA tierce — à corroborer si possible avec une source écrite directe]
# ---------------------------------------------------------------------------
GRIMANI_ROOM_LAYOUT_AND_SEATING = (
    "Règles de disposition de la pièce et du siège d'écoute rapportées "
    "par Grimani (via résumé Gemini) : "
    "(1) concevoir la pièce pour la 'zone verte' (places principales), "
    "sans compromis acoustique pour les sièges d'appoint occasionnels ; "
    "(2) le centre de l'écran/téléviseur doit être proche du niveau des "
    "yeux des spectateurs assis (erreur fréquente : écran trop haut) ; "
    "(3) ne JAMAIS placer le siège d'écoute en plein milieu de la pièce, "
    "ni exactement au 1/4 ou aux 3/4 de la longueur — ce sont des zones "
    "de nœuds/ventres d'ondes stationnaires qui annulent certaines "
    "fréquences et détruisent l'impact des basses ; "
    "(4) règle dite 'des 38%' : bon point de départ pour la rangée de "
    "sièges principale = la positionner à 38% de la longueur totale de "
    "la pièce depuis le mur avant, pour éviter les pires pics/creux. "
    "RÉSERVE : les dimensions exactes de la pièce de Steve et la "
    "position précise de son siège d'écoute par rapport à ces repères "
    "ne sont pas connues de l'assistant à ce jour — cette règle ne peut "
    "donc PAS être vérifiée comme respectée ou non pour son installation "
    "réelle sans ces mesures complémentaires."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — Anthony
Grimani, live YouTube avec la chaîne Youthman (https://www.youtube.com/
watch?v=THlvJ_lolmE), résumé transmis par Steve via Gemini."""

GRIMANI_SPEAKER_PLACEMENT_ANGLES = (
    "Règles de placement des enceintes rapportées par Grimani : "
    "(1) triangle frontal : Front Left/Right à un angle de 45° par "
    "rapport à la position d'écoute principale ; la centrale à la même "
    "hauteur que les frontales pour une transition fluide des sons à "
    "l'écran — DIRECTEMENT APPLICABLE à la config 7.2 de Steve (Front "
    "Left, Center, Front Right) ; "
    "(2) 'Psychoacoustic Reversal' (inversion psychoacoustique) : erreur "
    "fréquente qui consiste à trop écarter la paire Surround Back l'une "
    "de l'autre (ex. 140-150° par rapport à l'auditeur au lieu de "
    "165°). Au-delà d'un écart de ~30° entre les deux enceintes "
    "arrière, le cerveau peut, à cause de la forme de l'oreille externe, "
    "interpréter un son venant de l'arrière comme venant de l'AVANT de "
    "la pièce. Conseil : resserrer la paire Surround Back à un angle "
    "d'environ 165° par rapport à l'auditeur (soit ~30° d'écart entre "
    "elles) — DIRECTEMENT PERTINENT pour Steve qui possède bien un "
    "canal Surround Back Left et Surround Back Right dans sa config "
    "7.2 (confirmé par les métadonnées du fichier .liveproject) ; la "
    "vérification de l'angle RÉEL de ses enceintes arrière nécessite "
    "toutefois une mesure physique que l'assistant n'a pas ; "
    "(3) enceintes 'Wide' à 45° de la position d'écoute pour combler le "
    "vide entre frontales et surrounds latérales — NON APPLICABLE à la "
    "configuration active de Steve (7.2, aucun canal Wide dans sa "
    "liste de 7 enceintes) ; "
    "(4) effet SBIR (Speaker Boundary Interference Response) : la "
    "proximité immédiate d'une enceinte à un mur crée des annulations/"
    "renforcements de fréquences par interférence ; se corrige en "
    "décollant physiquement l'enceinte du mur. Point IMPORTANT : SBIR "
    "crée typiquement des creux étroits et profonds qu'il est difficile "
    "de corriger uniquement par EQ/DSP (nécessiterait un boost très "
    "important, souvent peu souhaitable) — cohérent avec la prudence "
    "déjà documentée en section 14 sur les limites physiques de la "
    "correction numérique : un problème d'interférence physique de "
    "proximité au mur se traite d'abord par le placement, pas par "
    "Dirac ART seul."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — même live
Grimani/Youthman que ci-dessus."""

GRIMANI_ATMOS_HEIGHT_NOTE = (
    "Recommandations Grimani sur les canaux de hauteur (Dolby Atmos) : "
    "éviter 4-6 enceintes au plafond dans une petite pièce ('Mush', "
    "nuage de réflexions incontrôlable) et préférer UNE SEULE paire, "
    "légèrement en avant des spectateurs, alignée en ligne droite à "
    "mi-chemin entre la centrale et les frontales ('parapluie de son'). "
    "RÉSERVE IMPORTANTE : la configuration ACTIVE de Steve est un 7.2 "
    "SANS hauteurs Atmos actives (confirmé dans exemple_systeme_steve.py "
    "et les métadonnées du fichier .liveproject, qui ne listent que 7 "
    "enceintes + 2 caissons, aucun canal de hauteur). Cette recommandation "
    "n'est donc PAS applicable à son installation actuelle telle que "
    "documentée ; elle n'est conservée ici que pour information, au cas "
    "où Steve envisagerait une évolution future de son système."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — même live
Grimani/Youthman que ci-dessus."""

GRIMANI_ROOM_TREATMENT_BALANCE = (
    "Recommandations Grimani sur le traitement acoustique physique : "
    "(1) ne PAS sur-amortir (éviter de recouvrir tous les murs de mousse "
    "absorbante, ce qui rend la pièce 'morte') ; "
    "(2) 'absorption asymétrique' : placer un panneau absorbant sur un "
    "mur latéral et, juste en face sur le mur opposé, un panneau de "
    "diffusion plutôt qu'un second panneau absorbant — casse les échos "
    "flottants tout en gardant une sensation d'espace ; "
    "(3) l'objectif recherché est un temps de décroissance du son "
    "(Decay Time / RT60) ÉQUILIBRÉ entre graves, médiums et aigus, pas "
    "une élimination totale des réflexions. "
    "CONVERGENCE NOTABLE avec la section 21 : cet objectif de RT60 "
    "équilibré par des moyens PHYSIQUES (absorption/diffusion) est "
    "exactement le même objectif que celui cité par Mathias Johansson "
    "(CPO Dirac) pour justifier Active Room Treatment par des moyens "
    "NUMÉRIQUES ('reduce bass decay times digitally, without needing "
    "bass traps or thick layers of wall absorption') — les deux "
    "approches (traitement physique de Grimani, DSP ART de Dirac) "
    "visent la même grandeur acoustique (le temps de décroissance), "
    "par des leviers différents et complémentaires."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — même live
Grimani/Youthman que ci-dessus."""

GRIMANI_MULTI_SUBWOOFER_METHOD = (
    "Méthode des caissons multiples selon Grimani : le problème n°1 en "
    "home cinéma est l'onde stationnaire (basses très fortes à un "
    "endroit, quasi absentes 50cm plus loin) ; sa solution de référence "
    "est l'installation de 4 caissons de basses, un dans CHACUN des 4 "
    "coins de la pièce, qui 's'équilibrent mutuellement' et annulent "
    "en grande partie les résonances architecturales, pour des basses "
    "homogènes à toutes les places. "
    "RÉSERVE IMPORTANTE : Steve possède 2 caissons (Subwoofer 1 et "
    "Subwoofer 2), pas 4 — sa configuration réelle ne correspond pas à "
    "la méthode optimale décrite par Grimani. Cette information n'est "
    "PAS une invitation à recommander l'achat de 2 caissons "
    "supplémentaires (hors sujet de la mission de réglages logiciels), "
    "mais elle explique en partie, de façon cohérente, pourquoi les 3 "
    "modes de pièce déjà confirmés empiriquement par double méthode "
    "indépendante (~60Hz, ~110-135Hz, ~235-255Hz — cf. analyse du "
    "fichier .liveproject et cartographie_modale.py) ne peuvent être "
    "qu'ATTÉNUÉS par le DSP (Dirac Bass Control / ART) et non éliminés "
    "aussi efficacement qu'avec 4 caissons correctement positionnés : "
    "avec seulement 2 sources de graves, il reste structurellement "
    "moins de degrés de liberté spatiaux pour 'bombarder' la pièce "
    "et annuler ses résonances que ce que permettrait une 4e paire de "
    "coins actifs — le rôle du DSP est alors de compenser, autant que "
    "la physique le permet, ce manque de degrés de liberté spatiaux."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — même live
Grimani/Youthman que ci-dessus."""

# ---------------------------------------------------------------------------
# 23. Anthony Grimani — compléments psychoacoustique (vidéo Youthman) et
#     architecture matérielle Grimani Systems / Sonatus (vidéo avec Shane
#     Lee, https://www.youtube.com/live/Qy2bjBBOgIA). Toujours via résumé
#     Gemini transmis par Steve — même réserve de prudence qu'en section 22
#     (source secondaire non vérifiée directement par l'assistant).
#     [Avis d'expert professionnel, rapporté par IA tierce]
# ---------------------------------------------------------------------------
GRIMANI_PSYCHOACOUSTIC_REVERSAL_MECHANISM = (
    "Complément sur le mécanisme physiologique derrière le "
    "'Psychoacoustic Reversal' déjà documenté (section 22) : Grimani "
    "explique que l'évolution humaine a conformé l'oreille pour capter "
    "les menaces venant principalement de l'AVANT et des CÔTÉS ; "
    "l'acuité auditive à l'arrière est naturellement très faible. Les "
    "fourchettes d'angle données varient légèrement selon la prise "
    "(130-140° ou 140-150° à éviter ; 165° à 170° recommandé, soit "
    "~30° d'écart max entre les deux Surround Back) — à traiter comme "
    "un ordre de grandeur ('resserrer autour de 165-170°'), pas une "
    "valeur unique au degré près. Reste directement pertinent pour la "
    "paire Surround Back Left/Right de Steve."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — Anthony
Grimani, live YouTube avec la chaîne Youthman (https://www.youtube.com/
watch?v=THlvJ_lolmE), résumé transmis par Steve via Gemini."""

GRIMANI_SONATUS_ACOUSTIC_TREATMENT_METHOD = (
    "Contenu nouveau (vidéo avec Shane Lee) : Grimani présente Sonatus, "
    "sa filiale de traitement acoustique résidentiel. Méthode en 3 "
    "composants, dans un ratio strict calculé selon le VOLUME de la "
    "pièce (le ratio exact n'est pas chiffré dans le résumé transmis) : "
    "(1) absorption contrôlée, pour stabiliser le temps de réverbération "
    "global (RT60) — cohérent avec la section 22 ; "
    "(2) diffusion/dispersion, pour disperser l'énergie sans l'éteindre "
    "et donner une sensation d'espace ('les murs reculent') ; "
    "(3) gestion des basses (Bass Trapping) par panneaux denses dans "
    "les angles de la pièce, où l'énergie grave s'accumule "
    "naturellement. Image donnée par Grimani : 'l'acoustique, c'est "
    "comme le sel et les épices dans un plat : il en faut, mais si vous "
    "en mettez trop, c'est immangeable' — une mousse acoustique bas de "
    "gamme détruit les aigus SANS toucher aux graves, rendant la pièce "
    "sourde et déséquilibrée plutôt qu'équilibrée. "
    "Précision sur l'asymétrie déjà documentée (section 22) : au lieu "
    "d'une seule paire absorbant/diffusant fixe, Grimani propose "
    "d'ALTERNER (absorbant à gauche/diffusant à droite sur un point de "
    "réflexion, puis diffusant à gauche/absorbant à droite sur le point "
    "de réflexion suivant) pour éviter les échos flottants sans détruire "
    "la dynamique globale de la pièce."
)
"""[Avis d'expert professionnel, rapporté par IA tierce] — Anthony
Grimani avec Shane Lee, discussion sur Sonatus."""

GRIMANI_SYSTEMS_PROPRIETARY_HARDWARE_RESERVE = (
    "Contenu nouveau sur l'architecture matérielle propriétaire de "
    "Grimani Systems (sa marque d'enceintes, distincte de Sonatus) : "
    "(1) technologie brevetée 'CSA' (Conic Section Array), un guide "
    "d'onde élargissant la directivité horizontale à 70-80°, pour un "
    "'sweet spot' qui englobe toute la pièce au lieu d'une zone étroite ; "
    "(2) enceintes TOUT-ACTIF tri-amplifiées : chaque haut-parleur "
    "(grave/médium/aigu) a son propre canal d'amplification dédié dans "
    "un rack externe, avec filtrage numérique géré en amont par un DSP "
    "propriétaire (pas de filtre passif interne), permettant une "
    "correction de phase en temps réel ; "
    "(3) séparation des caissons de basse PAR RÔLE DE FRÉQUENCE : des "
    "caissons d'angle de 18 pouces (aux 4 coins) gèrent la zone de "
    "transition 40-80Hz, tandis qu'un caisson d'infrastructure de 21 "
    "pouces (à l'avant) est dédié exclusivement à l'infrasonique "
    "15-40Hz (impact physique des basses fréquences). "
    "RÉSERVE MÉTHODOLOGIQUE IMPORTANTE : cette architecture décrit le "
    "matériel PROPRIÉTAIRE de la marque Grimani Systems, structurellement "
    "différente du système réel de Steve : ses enceintes Elipson sont "
    "PASSIVES (pas tri-amplifiées actives, pas de DSP par haut-parleur), "
    "amplifiées par un ampli externe générique (Buckeye NCx252MP, pas "
    "un rack Grimani Systems), et ses 2 caissons SVS 3000 Micro "
    "R|Evolution sont IDENTIQUES entre eux (pas une paire '18 pouces "
    "d'angle' + un '21 pouces infrasonique' avec répartition de rôle "
    "par fréquence). Les valeurs chiffrées 15-40Hz / 40-80Hz décrivent "
    "un CROSSOVER MATÉRIEL FIXE entre deux types de caissons différents "
    "chez Grimani Systems — ce ne sont PAS des paramètres Dirac F-support "
    "Low/High génériques à reproduire tels quels dans les réglages de "
    "Steve, dont le Bass Management repose sur Dirac Live (logiciel) "
    "appliqué à 2 caissons de même modèle, pas sur une séparation "
    "matérielle figée par construction."
)
"""[Avis d'expert professionnel, rapporté par IA tierce — architecture
matérielle d'une marque tierce, À NE PAS transposer directement aux
réglages logiciels de Steve] — Anthony Grimani avec Shane Lee,
discussion sur Grimani Systems (grimanisystems.com)."""

# ---------------------------------------------------------------------------
# 24. Synthèse — rôle fonctionnel de chaque canal dans un mix cinéma 7.1,
#     appliqué à la config réelle de Steve (demande de Steve : vérifier
#     que le rôle de chaque enceinte dans la retranscription d'une bande
#     son de film est bien compris). Ceci consolide en un seul endroit
#     des faits déjà sourcés séparément (sections 10, 17, 20-23) plutôt
#     que d'introduire une nouvelle source externe — les rôles de canaux
#     eux-mêmes (trio frontal porteur d'image, surrounds d'ambiance, LFE
#     discret) sont une convention standard de l'industrie du cinéma
#     numérique (ITU-R BS.775, documentation Dolby/DTS grand public),
#     donc du domaine public. [Principe acoustique général / convention
#     d'industrie, domaine public — synthèse interne croisant des
#     sources déjà citées individuellement]
# ---------------------------------------------------------------------------
FILM_MIX_CHANNEL_ROLES_SYNTHESIS = (
    "Rôle fonctionnel standard de chaque canal dans un mix cinéma, "
    "appliqué à la config 7.2 réelle de Steve : "
    "(1) TRIO FRONTAL, porteur de l'image sonore ancrée à l'écran — "
    "Centrale : canal quasi-exclusif du dialogue, ancre la source "
    "sonore sur l'écran indépendamment de la position d'écoute (sans "
    "quoi une image reconstituée par L/R seuls se déplacerait avec le "
    "siège, cf. GRIMANI_PHANTOM_CENTER_EQ_RECOMMENDATION, section 20) ; "
    "porte le PLUS d'énergie de tout le système (référence 0dB, "
    "GRIMANI_CENTER_CHANNEL_ENERGY_DISTRIBUTION). Façades Gauche/Droite : "
    "musique et effets qui suivent visuellement l'action latérale à "
    "l'écran, -3dB sous le Centre. "
    "(2) CANAUX PÉRIPHÉRIQUES, immersion sans ancrage visuel — Surround "
    "Gauche/Droite (latéraux) : ambiance venant des côtés de la salle "
    "(pas de l'écran), -6dB sous le Centre. Surround Back Gauche/Droite "
    "(arrière) : enveloppement à 360°, -9dB sous le Centre (le niveau "
    "le plus faible du système) ; soumis à la contrainte psychoacoustique "
    "du 'Psychoacoustic Reversal' (GRIMANI_PSYCHOACOUSTIC_REVERSAL_"
    "MECHANISM, section 23) — au-delà de ~30° d'écart entre les deux "
    "enceintes arrière, le cerveau peut percevoir le son comme venant "
    "de l'avant plutôt que de l'arrière. "
    "(3) CANAL(AUX) DE GRAVES — ni purement 'LFE' ni purement "
    "'subwoofer' : le signal réellement reproduit par les 2 caissons de "
    "Steve est un COMPOSITE du canal LFE discret du mix (effets "
    "ponctuels encodés séparément, 20-120Hz, +10dB conventionnel) et des "
    "graves de TOUTES les 7 autres enceintes redirigées par le bass "
    "management/crossover (LFE_VS_SUBWOOFER_CHANNEL_DISTINCTION et "
    "BASS_MANAGEMENT_CROSSOVER_PRINCIPLE, section 10) — jamais le LFE "
    "brut seul. "
    "(4) TRAITEMENT GLOBAL PAR LE DSP — contrairement à un traitement "
    "canal par canal indépendant, Dirac Live ART traite ces 9 canaux "
    "SIMULTANÉMENT en connaissant leurs rôles respectifs et leurs "
    "interactions spatiales ('Loudspeaker Co-Optimization', section 21), "
    "ce qui est fondamentalement différent d'une égalisation appliquée "
    "séparément à chaque enceinte sans tenir compte des autres."
)
"""[Principe acoustique général / convention d'industrie, domaine public
— synthèse croisant des sources déjà citées] — rôles de canaux standard
(ITU-R BS.775, documentation Dolby/DTS) ; faits chiffrés spécifiques
cross-référencés vers les constantes déjà sourcées individuellement
dans ce fichier (sections 10, 17, 20, 21, 23)."""

# ---------------------------------------------------------------------------
# 25. Liste officielle des appareils compatibles Dirac Live ART (demande de
#     Steve : "enregistrer la liste des produits compatibles dirac art pour
#     les amplificateurs intégrés et processeurs-préamplis", en 1re étape
#     de sa méthodologie de diagnostic — "pour gagner du temps et préserver
#     les enceintes"). Liste lue directement dans le configurateur d'achat
#     officiel (dirac.com/products/art, menu déroulant "Select for price &
#     license options"), PAS une page marketing générale : ce sont les
#     appareils pour lesquels une licence ART est RÉELLEMENT en vente au
#     moment de l'observation. [Confirmation officielle Dirac — à re-
#     vérifier périodiquement, cette liste peut s'allonger dans le temps]
# ---------------------------------------------------------------------------
ART_COMPATIBLE_DEVICES_OBSERVATION_DATE = "2026-10-02"
ART_COMPATIBLE_DEVICES_SOURCE_URL = "https://www.dirac.com/products/art"

ART_COMPATIBLE_DEVICES: list[ArtCompatibleDevice] = [
    # ARCAM — confirmé via hifi-quimper.fr + Audio Science Review (ASR
    # Forum) : "AVA35 : haut de gamme Radia AV... AVP45 : processeur AV
    # (sans amplification)" — AVA = ampli intégré, AVP = processeur pur.
    ArtCompatibleDevice("ARCAM", "AVA15", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("ARCAM", "AVA25", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("ARCAM", "AVA35", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("ARCAM", "AVP45", DeviceType.PROCESSEUR_PREAMPLI),
    # AudioControl — nomenclature "APR-16" non confirmée avec certitude
    # depuis une fiche officielle dans le temps disponible ; une annonce
    # commerciale tierce (habitech.co.uk) mentionne un "bundle" avec
    # amplificateur 7 ou 11 canaux EN OPTION, ce qui suggère que l'APR-16
    # pourrait être un processeur central plutôt qu'un ampli intégré,
    # mais ce n'est PAS confirmé par une source officielle — laissé en
    # INCERTAIN par prudence plutôt que de deviner.
    ArtCompatibleDevice("AudioControl", "Hyperion APR-16", DeviceType.INCERTAIN),
    # Denon — nomenclature officielle bien connue et déjà confirmée dans
    # ce fichier (section 16/21) : AVR-xxxxH = AV Receiver AVEC ampli
    # intégré ; AVC-xxxxH = même châssis SANS les étages de puissance
    # (version "pre/pro" pour installateurs utilisant un ampli externe).
    ArtCompatibleDevice("Denon", "AVR-A10H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-A10H", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Denon", "AVR-A1H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-A1H", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Denon", "AVR-X3800H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-X3800H", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Denon", "AVR-X3900H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-X3900H", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Denon", "AVR-X4800H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-X4800H", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Denon", "AVR-X6800H", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Denon", "AVC-X6800H", DeviceType.PROCESSEUR_PREAMPLI),
    # JBL Synthesis — nomenclature industrie bien établie : SDP = Surround
    # Decoder/Sound Processor (pre/pro pur) ; SDR = Surround Decoder
    # Receiver (avec ampli intégré).
    ArtCompatibleDevice("JBL Synthesis", "SDP-60", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("JBL Synthesis", "SDR-40", DeviceType.AMPLI_INTEGRE),
    # Marantz — confirmé par la structure produit officielle elle-même
    # (dirac.com affiche "Marantz CINEMA 30" comme appareil par défaut
    # pour Steve) : la série "AV xx" est un processeur pur (lancée pour
    # concurrencer StormAudio/JBL Synthesis en pre/pro haut de gamme),
    # la série "CINEMA xx" (dont le CINEMA 30 de Steve) a des étages de
    # puissance internes natifs, même si Steve les ignore en pratique au
    # profit de son ampli externe Buckeye NCx252MP.
    ArtCompatibleDevice("Marantz", "AV 10", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Marantz", "AV 20", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("Marantz", "AV 30", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice(
        "Marantz", "CINEMA 30", DeviceType.AMPLI_INTEGRE, price_usd="$299",
        notes="Appareil de Steve — confirmé par défaut sur le configurateur officiel.",
    ),
    ArtCompatibleDevice("Marantz", "CINEMA 40", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Marantz", "CINEMA 50", DeviceType.AMPLI_INTEGRE),
    ArtCompatibleDevice("Marantz", "CINEMA 50 SERIES 2", DeviceType.AMPLI_INTEGRE),
    # Monoprice — le HTP-1 Monolith est un pre/pro pur largement documenté
    # dans la presse spécialisée (AVS Forum, Audioholics), jamais vendu
    # avec un ampli intégré.
    ArtCompatibleDevice("Monoprice", "HTP-1 Monolith", DeviceType.PROCESSEUR_PREAMPLI),
    # StormAudio — déjà confirmé section 16 : TOUJOURS un processeur pur
    # (ISP = Immersive Sound Processor), jamais d'ampli intégré, toujours
    # utilisé avec un ampli externe (comme le Buckeye de Steve).
    ArtCompatibleDevice("StormAudio", "I.ISP 16.12", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("StormAudio", "ISP Core 16", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("StormAudio", "ISP Elite MK1", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("StormAudio", "ISP Elite MK2", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("StormAudio", "ISP Elite MK3", DeviceType.PROCESSEUR_PREAMPLI),
    ArtCompatibleDevice("StormAudio", "ISP Master", DeviceType.PROCESSEUR_PREAMPLI),
    # Tonewinner — type non confirmé avec certitude dans le temps
    # disponible (marque moins documentée en sources occidentales) ;
    # laissé en INCERTAIN par prudence plutôt que de deviner.
    ArtCompatibleDevice("Tonewinner", "AT-600", DeviceType.INCERTAIN),
]

ART_REQUIRES_RC_AND_BASS_CONTROL = (
    "Confirmation officielle lue directement sur la fiche produit ART "
    "(dirac.com/products/art) : 'Requires Room Correction. Bass Control "
    "required if using one or more subs.' — ART n'est PAS un produit "
    "autonome, c'est un add-on qui a deux prérequis stricts : (1) Room "
    "Correction (RC) doit déjà être actif, et (2) Bass Control (BC) est "
    "EXIGÉ dès qu'un ou plusieurs caissons sont utilisés dans le système. "
    "**Conséquence directe pour Steve** : ayant 2 caissons (SVS 3000 "
    "Micro R|Evolution), Bass Control n'est pas optionnel dans son cas — "
    "c'est un prérequis obligatoire pour que ART fonctionne correctement "
    "sur l'ensemble de son système 7.2, pas seulement une amélioration "
    "facultative. Tarifs observés (Marantz, 02/10/2026) : ART seul $299 ; "
    "bundle complet RC+BC+ART $799 (au lieu de $947 à l'unité) ; bundle "
    "BC+ART $549 (au lieu de $598)."
)
"""[Confirmation officielle Dirac] — dirac.com/products/art, lu en direct
via le navigateur intégré, section liste à puces sous le titre '03 ART'."""


def is_art_compatible(brand: str, model: str) -> ArtCompatibleDevice | None:
    """Recherche insensible à la casse dans ART_COMPATIBLE_DEVICES.
    Retourne l'appareil trouvé (avec son DeviceType) ou None si le
    matériel du client n'apparaît pas dans la liste observée le
    03/10/2026 — ce qui NE PROUVE PAS que ce matériel est incompatible
    (la liste évolue), seulement qu'il n'y était pas à cette date."""

    brand_norm = brand.strip().casefold()
    model_norm = model.strip().casefold()
    for device in ART_COMPATIBLE_DEVICES:
        if device.brand.casefold() == brand_norm and device.model.casefold() == model_norm:
            return device
    return None

# ---------------------------------------------------------------------------
# 26. Mécanique exacte de l'éditeur de courbe cible et du Bass Control
#     (demande de Steve : connaître précisément "ce que Dirac permet de
#     régler manuellement" avant de calculer des valeurs chiffrées de
#     réglage). Lu en entier sur le Helpdesk officiel Dirac.
#     [Confirmation officielle Dirac — Helpdesk]
# ---------------------------------------------------------------------------
TARGET_CURVE_EDITOR_MECHANICS = (
    "Confirmé noir sur blanc sur le Helpdesk Dirac (page 'Filter Design | "
    "Dirac Live Bass Control') : la courbe cible s'édite par GLISSER-"
    "DÉPOSER libre sur le graphique ('Drag the target-points on the "
    "target curve'), PAS par saisie numérique directe d'une valeur. On "
    "ajoute un nouveau point par clic droit sur la courbe puis 'Add "
    "control point to'. Conséquence méthodologique importante : "
    "CONTRAIREMENT au Support Level qui a un pas CONFIRMÉ et chiffré de "
    "0,5 dB (SUPPORT_LEVEL_STEP_DB), aucun pas fixe en dB ou en Hz n'est "
    "documenté officiellement pour les points de courbe cible — "
    "l'édition est continue, limitée seulement par la précision de la "
    "souris/du geste de l'utilisateur. Une recommandation 'placez un "
    "point à X Hz / Y dB' doit donc être comprise comme une CIBLE à "
    "viser du mieux possible, pas une valeur que l'interface imposerait "
    "au dixième de dB près."
)
"""[Confirmation officielle Dirac] — helpdesk.dirac.com/en/dirac-bass-
control/Filter-Design-c592, lu en entier via le navigateur intégré."""

BASS_CONTROL_TARGET_CURVE_TWO_PART_STRUCTURE = (
    "Découverte officielle majeure, avec impact direct sur toute "
    "recommandation de courbe cible pour Steve (qui utilise Bass Control, "
    "obligatoire avec ses 2 caissons — voir ART_REQUIRES_RC_AND_BASS_"
    "CONTROL) : 'In Dirac Live 2 the target curve setting the sound "
    "colouration was unique to the speaker group. For Dirac Live Bass "
    "Control, however, the lower frequencies are highly correlated "
    "between speakers, and a better compensation is achieved by "
    "separating the target curve into a low-frequency part common to "
    "the system and a higher-frequencies part unique to the speaker "
    "group.' Concrètement, la courbe cible visible pour CHAQUE groupe "
    "se compose de 2 segments avec des règles différentes : "
    "(A) la partie BASSE fréquence (sous le point de croisement du "
    "groupe) est PARTAGÉE/COMMUNE À TOUT LE SYSTÈME — modifier cette "
    "partie sur UN groupe affecte la colouration des graves de TOUS les "
    "groupes simultanément ; "
    "(B) la partie HAUTE fréquence (au-dessus du croisement du groupe) "
    "est PROPRE à ce groupe, réglable indépendamment des autres. "
    "Chaque groupe a en plus SON PROPRE point de croisement individuel "
    "('each speaker group has their own individual crossover "
    "frequency'), ajustable en faisant glisser la barre de croisement "
    "sur le graphique des réponses moyennes. "
    "**Conséquence pour l'algorithme de recommandation** : il est "
    "incohérent de recommander un ajustement de courbe DIFFÉRENT entre "
    "plusieurs enceintes dans leur partie grave commune — seule la "
    "partie au-dessus du croisement de CHAQUE groupe peut être "
    "personnalisée enceinte par enceinte (ou groupe par groupe)."
)
"""[Confirmation officielle Dirac] — même page Helpdesk que ci-dessus."""

BASS_CONTROL_OFFICIAL_MOVIE_BOOST_CONFIRMATION = (
    "Confirmation OFFICIELLE directe de la pratique de Steve (booster le "
    "niveau des caissons pour le cinéma) : 'Increasing the volume of the "
    "subwoofers can be achieved by raising the part of the target curve "
    "under 100 Hz by a few dB... This is often wanted when watching "
    "movies.' Dirac recommande lui-même explicitement de relever la "
    "courbe cible sous 100 Hz de 'quelques dB' pour un rendu cinéma — "
    "ni une fréquence de pivot unique ni une valeur chiffrée précise "
    "n'est donnée ('a few dB'), mais le PRINCIPE et la ZONE (sous "
    "100 Hz) sont désormais une confirmation officielle, pas seulement "
    "un retour d'expérience de Steve ou un conseil d'expert tiers "
    "(Grimani)."
)
"""[Confirmation officielle Dirac] — même page Helpdesk que ci-dessus."""

BASS_CONTROL_VS_BASS_MANAGEMENT_MODE_DISTINCTION = (
    "Distinction officielle entre les 2 modes proposés en plus de "
    "'Off' : 'Bass management' — gain de chaque caisson simplement mis "
    "à l'échelle par 1/(nombre de caissons) pour correspondre à la "
    "courbe cible (répartition égale, pas de filtre sur mesure) ; "
    "'Bass Control' — harmonise caissons ET enceintes non-caisson dans "
    "les basses fréquences via des filtres de phase, délais et gains "
    "SUR MESURE pour chaque canal ('tailor made phase filters, delays "
    "and gains'). C'est ce 2e mode (plus avancé QUE 'Bass management' "
    "seul) qu'ART exige en prérequis ('Bass Control required if using "
    "one or more subs', section 25). "
    "⚠️ PRÉCISION DE STEVE, IMPORTANTE POUR NE PAS CONFONDRE LA "
    "HIÉRARCHIE : Bass Control reste un module MOINS PERFECTIONNÉ "
    "qu'ART lui-même — la hiérarchie réelle à 3 niveaux est 'Bass "
    "management' (le plus basique, répartition égale) < 'Bass Control' "
    "(SIMO avancé : filtres sur mesure par canal mais toujours sans "
    "co-optimisation spatiale entre enceintes, cohérent avec "
    "DIRAC_THREE_PRODUCT_TIERS_SIMO_VS_MIMO, section 21) < 'ART' (vrai "
    "MIMO, 'Loudspeaker Co-Optimization', qui coordonne TOUTES les "
    "enceintes simultanément, section 21). Bass Control est un "
    "PRÉREQUIS TECHNIQUE d'ART (le module de gestion des caissons "
    "qu'ART vient ensuite compléter/coordonner avec le reste du "
    "système), pas un concurrent ni un équivalent d'ART."
)
"""[Confirmation officielle Dirac + précision de Steve] — même page
Helpdesk que ci-dessus pour le mécanisme ; hiérarchie de sophistication
clarifiée par Steve et cross-référencée à la section 21 (SIMO vs MIMO)."""

# ---------------------------------------------------------------------------
# 27. Headroom de mesure et gain d'entrée XLR/RCA (demande de Steve :
#     "quel niveau de gain des subwoofers il doit viser au moment de la
#     prise de mesure initiale... pour exploiter le headroom de la pièce
#     et les niveaux max de gain en sortie de ses connexions XLR ou
#     RCA"). Combine une confirmation officielle Dirac (headroom) et des
#     principes d'ingénierie audio analogique de domaine public (niveaux
#     de référence XLR/RCA), appliqués avec prudence au matériel réel de
#     Steve (fiches déjà sourcées section 15).
# ---------------------------------------------------------------------------
DIRAC_OFFICIAL_HEADROOM_EXPLANATION = (
    "Confirmation officielle directe du Helpdesk Dirac sur le headroom : "
    "'Properly executed EQs, including Dirac Live, require headroom to "
    "boost certain frequencies without exceeding 0dBFS and causing "
    "digital clipping. The output level is attenuated to provide "
    "headroom, and you may need to increase the volume higher than "
    "usual... Ensure the measurement volume is the same or slightly "
    "higher than the listening volume.' Traduction du principe : Dirac "
    "a besoin de marge numérique pour pouvoir BOOSTER certaines "
    "fréquences sans écrêter à 0dBFS ; il réduit donc automatiquement le "
    "niveau de sortie global pour se garder cette marge — d'où un volume "
    "perçu plus faible après application du filtre, à compenser en "
    "augmentant le volume d'écoute habituel. **Conseil officiel "
    "actionnable pour la prise de mesure** : régler le niveau de mesure "
    "à peu près égal, ou légèrement SUPÉRIEUR, au niveau d'écoute "
    "habituel réel de Steve — pas un niveau de mesure arbitrairement "
    "haut ou bas déconnecté de son usage réel."
)
"""[Confirmation officielle Dirac] — helpdesk.dirac.com/en/dirac-live/
Why-does-the-volume-decrease-significantly-when-applying-the-finished-
filter-f49c, lu en entier via le navigateur intégré."""

XLR_VS_RCA_REFERENCE_LEVEL_PRINCIPLE = (
    "Principe d'ingénierie audio analogique de domaine public (pas "
    "spécifique à Dirac) : les connexions RCA (asymétriques) suivent "
    "conventionnellement un niveau de référence 'consumer' de -10 dBV "
    "(≈0,316 Vrms), tandis que les connexions XLR (symétriques) suivent "
    "un niveau de référence 'professionnel' de +4 dBu (≈1,228 Vrms) — un "
    "écart théorique d'environ 11,8 dB entre les deux standards. "
    "**Point de vigilance pour Steve** : sa liaison Marantz CINEMA 30 → "
    "ampli Buckeye NCx252MP passe par un câble ADAPTATEUR RCA(M) vers "
    "XLR(M) (section 15) — ce type de câble change le CONNECTEUR "
    "physique mais ne convertit PAS électriquement un niveau -10dBV en "
    "+4dBu (ce n'est pas un amplificateur de ligne actif, juste un "
    "câblage passif avec un brochage adapté). Le niveau électrique "
    "réellement transmis dépend donc du réglage de gain de sortie par "
    "canal du CINEMA 30 (menu calibration des niveaux d'enceintes), pas "
    "du simple choix de connecteur."
)
"""[Principe d'ingénierie audio générale, domaine public] — standards
AES/EBU de niveaux de référence professionnel vs consumer, largement
documentés dans l'industrie (pas une règle Dirac)."""

BUCKEYE_INPUT_SENSITIVITY_VS_HEADROOM_CALCULATION = (
    "Calcul combinant les fiches déjà sourcées (section 15) : l'ampli "
    "Buckeye NCx252MP a une sensibilité d'entrée confirmée de 1,6 Vrms "
    "(charge 4 ohms) à 1,8 Vrms (charge 8 ohms) pour atteindre sa "
    "PLEINE puissance nominale (150-250W selon canal/impédance), avec "
    "un gain de tension de 26 dB et une impédance d'entrée de 47 kOhms. "
    "Pour exploiter pleinement la puissance disponible de cet ampli "
    "(et donc le headroom réel du système), le niveau de sortie du "
    "CINEMA 30 par canal devrait s'approcher de cette sensibilité "
    "d'entrée (1,6-1,8 Vrms) sans la dépasser au point d'écrêter la "
    "sortie du processeur lui-même. "
    "⚠️ **Limite honnête** : le niveau de sortie MAXIMAL en Vrms du "
    "Marantz CINEMA 30 (avant son propre écrêtage) n'a pas été retrouvé "
    "dans les fiches déjà collectées — cette valeur précise manque pour "
    "donner un pourcentage ou un réglage de gain de sortie exact et "
    "garanti. Le principe reste valable (viser à exploiter la "
    "sensibilité d'entrée du Buckeye sans écrêter le CINEMA 30), mais "
    "la valeur numérique finale ne peut pas être affirmée sans cette "
    "donnée manquante ou sans une mesure directe au voltmètre/analyseur "
    "sur l'installation réelle de Steve."
)
"""[Calcul combinant 2 fiches déjà sourcées, section 15] — Buckeye
NCx252MP (sensibilité d'entrée, gain) ; limite signalée explicitement
plutôt que comblée par une valeur inventée pour le CINEMA 30."""

# ---------------------------------------------------------------------------
# 28. Caractéristiques des composants (drivers) des enceintes réelles de
#     Steve (demande de Steve : "connaissance des caractéristiques des
#     composants"). Complète les fiches déjà sourcées section 15, qui ne
#     couvraient que les specs globales (plage de fréquence, impédance,
#     sensibilité, puissance) sans descendre au niveau du TYPE de driver.
#     Re-consultation des mêmes 3 pages produit Elipson, recherche ciblée
#     sur les paragraphes descriptifs (pas seulement le tableau de specs).
#     [Fiche constructeur officielle]
# ---------------------------------------------------------------------------
ELIPSON_DRIVER_COMPONENTS_BY_MODEL = (
    "Détails de composants (type de driver) relus directement sur les "
    "pages produit officielles elipson.com, paragraphes descriptifs : "
    "**Façades (Legacy 3220)** — '2 1/2 way floorstanding loudspeaker "
    "with two 16.5 cm mid-woofers for the bass and midrange frequencies, "
    "topped with a wide dispersion AMT tweeter' : 2 médium-graves de "
    "16,5 cm + 1 tweeter **AMT** (Air Motion Transformer, parfois appelé "
    "'ruban plissé') à large dispersion — technologie différente d'un "
    "dôme classique, réputée pour une excellente réponse transitoire. "
    "Matériau de la membrane confirmé PAR AILLEURS dans l'onglet "
    "'SPECIFICATIONS' de la même page (CITED_MANUFACTURER_SPECS, section "
    "15, déjà sourcé avant cette relecture) : aluminium/céramique. "
    "**Centrale (Prestige Facet II 14C)** — 'architecture à 2 voies avec "
    "deux haut-parleurs grave-médium de 170 mm, disposés symétriquement "
    "autour d'un tweeter de 25 mm à dôme souple' : configuration "
    "symétrique dite MTM (Médium-Tweeter-Médium), tweeter à **dôme "
    "souple** (soft dome, PAS un AMT). "
    "**Surrounds + Surrounds Back (Prestige Facet II 14LCR, x4)** — "
    "'deux médium-graves de 17 cm' + 'tweeter à dôme souple de 25 mm' : "
    "MÊME famille de tweeter que la centrale (dôme souple 25mm). "
    "⚠️ Pour la centrale ET les surrounds (contrairement aux façades), le "
    "matériau exact des membranes des médium-graves (papier, "
    "polypropylène, fibre...) n'est précisé NI dans le paragraphe "
    "descriptif NI dans l'onglet 'Détails techniques' déjà consulté pour "
    "ces 2 modèles (section 15) — volontairement non deviné, à "
    "distinguer de la Legacy 3220 où cette info existe bien (ci-dessus)."
)
"""[Fiche constructeur officielle] — en.elipson.com/product-page/
legacy-3220, elipson.com/product-page/prestige-facet-ii-14c et
prestige-facet-ii-14lcr, paragraphes descriptifs relus via le navigateur
intégré, croisés avec les tableaux de specs déjà extraits en section 15
(CITED_MANUFACTURER_SPECS) pour ne pas déclarer manquante une info en
réalité déjà présente ailleurs dans ce fichier."""


ELIPSON_TWEETER_HETEROGENEITY_IMPLICATION = (
    "Conséquence directe de la découverte ci-dessus, avec un impact "
    "réel sur ce que Dirac ART peut ou ne peut pas harmoniser : le "
    "système de Steve utilise 2 FAMILLES DE TWEETER DIFFÉRENTES — "
    "tweeter AMT (façades, gamme 'Legacy') vs tweeter à dôme souple "
    "(centrale + 4 surrounds, gamme 'Prestige Facet II'). Cohérence "
    "TIMBRALE forte entre centrale et les 4 surrounds (même famille de "
    "driver), mais hétérogénéité structurelle entre les façades et le "
    "reste du système. **Limite physique à ne pas perdre de vue** : "
    "Dirac ART égalise l'AMPLITUDE en fréquence et optimise la phase/le "
    "temps de décroissance (sections 11-13, 21), mais ne peut PAS "
    "changer la nature physique d'un driver — la DIRECTIVITÉ propre à "
    "un AMT (dispersion large mais motif de rayonnement différent d'un "
    "dôme classique) et la texture/réponse transitoire inhérente au "
    "type de tweeter restent des caractéristiques du matériel, pas du "
    "logiciel. Cohérent avec la limite déjà documentée section 14 "
    "(distorsion non-linéaire = hors de portée d'une correction "
    "linéaire) : ici c'est une 2e limite, différente mais de même "
    "nature (le DSP corrige la réponse en fréquence/temps, pas la "
    "signature physique d'un transducteur)."
)
"""[Déduction logique à partir de 2 faits constructeur officiels déjà
sourcés ci-dessus] — assemblage par nous-mêmes, cohérent avec la
nuance méthodologique déjà appliquée en section 14."""

# ---------------------------------------------------------------------------
# 29. Électronique des amplificateurs — fondamentaux généraux + specs
#     réelles du module Hypex NCx252MP de Steve (demande de Steve :
#     "connaissances solides sur l'électronique pour mieux comprendre et
#     optimiser leur fonctionnement en les respectant" + "sur
#     l'électronique aussi de manière générale"). Comble un des "trous
#     identifiés mais non comblés" du README (électronique de
#     l'amplificateur). [Principe électronique général, domaine public
#     (Wikipedia) + Fiche constructeur officielle pour le matériel réel]
# ---------------------------------------------------------------------------
CLASS_D_AMPLIFIER_PRINCIPLE = (
    "Principe général des amplificateurs Class D (switching amplifiers), "
    "technologie du Buckeye NCx252MP de Steve : les transistors "
    "amplificateurs (MOSFETs) fonctionnent comme des interrupteurs "
    "tout-ou-rien (ON/OFF), PAS comme des dispositifs à gain linéaire "
    "(contrairement aux classes A/AB traditionnelles). La modulation "
    "(PWM ou PDM) encode le signal audio dans un train d'impulsions ; un "
    "filtre passe-bas en sortie retire ensuite le résidu de commutation "
    "haute fréquence pour ne laisser que le signal audio analogique "
    "final vers le haut-parleur. Comme les transistors sont presque "
    "toujours soit totalement ouverts soit totalement fermés, très peu "
    "d'énergie est dissipée en chaleur dans les transistors eux-mêmes : "
    "le rendement peut dépasser 90% (contre ~50-60% pour une Class AB "
    "classique) — c'est ce qui permet à un module aussi compact que le "
    "NCx252MP de délivrer 150-250W/canal sans dissipateur thermique "
    "massif."
)
"""[Principe électronique général, domaine public] —
en.wikipedia.org/wiki/Class-D_amplifier"""

DAMPING_FACTOR_PRINCIPLE = (
    "Principe général du 'facteur d'amortissement' (damping factor) : "
    "ratio entre l'impédance nominale du haut-parleur (souvent 8 ohms "
    "par convention) et l'impédance de SORTIE de l'amplificateur "
    "(incluant l'impédance du câble de liaison ampli→enceinte). Plus ce "
    "facteur est ÉLEVÉ (= impédance de sortie de l'ampli très faible), "
    "mieux l'ampli peut électriquement 'freiner' les mouvements "
    "résiduels du cône du haut-parleur après l'arrêt du signal "
    "électrique (contrôle mécanique du woofer, évite un rendu de "
    "basses 'floues'/non amorties). Les amplis à transistors modernes "
    "ont généralement un damping factor BIEN supérieur à celui des "
    "amplis à tubes (jugé 'indésirable' pour ces derniers par la source "
    "elle-même). Point important : ce facteur VARIE avec la fréquence "
    "(souvent maximal en basse fréquence, décroît en aigu pour les "
    "amplis solid-state) — pertinent pour le réglage des caissons de "
    "Steve, zone où un bon contrôle du woofer importe le plus."
)
"""[Principe électronique général, domaine public] —
en.wikipedia.org/wiki/Damping_factor"""

HYPEX_NCX252MP_TECHNICAL_ARCHITECTURE = (
    "Fiche technique officielle du MODULE ampli exact utilisé par "
    "Buckeye dans le NCx252MP de Steve (fabricant du module : Hypex, "
    "Pays-Bas — Buckeye intègre 4 de ces modules dans son châssis "
    "8 canaux) : technologie 'NCOREx® Class D', avec alimentation à "
    "découpage intégrée ('high efficiency switch mode power supply', "
    "conforme à la norme européenne de consommation en veille '2013 ERP "
    "Lot 6', <0,5W en veille). "
    "Explication officielle du principe NCOREx : 'builds on the proven "
    "NCORE® architecture with a redesigned loop filter that increases "
    "loop gain across the audio band. This results in over 60 dB of "
    "error correction, further reducing distortion, improving "
    "linearity, and lowering output impedance' — un GAIN DE BOUCLE DE "
    "CONTRE-RÉACTION élevé (>60dB de correction d'erreur) sur toute la "
    "bande audio, qui réduit la distorsion ET abaisse l'impédance de "
    "sortie (donc AUGMENTE le damping factor, cohérent avec le THD "
    "'very low, frequency independent' déjà confirmé en section 15). "
    "Conçu explicitement pour 'stable operation across varying load "
    "impedances' — pertinent car les 3 modèles Elipson de Steve ont "
    "tous une impédance minimale sous leur valeur nominale à certaines "
    "fréquences (4,5-4,6 ohms min, déjà documenté section 15). "
    "**Protections listées officiellement** (pour 'respecter' "
    "l'électronique comme demandé par Steve) : surintensité avancée, "
    "protection DC (offset continu en sortie, dangereux pour les "
    "haut-parleurs), surchauffe, court-circuit — plus une 'indication "
    "d'écrêtage' (clip indication) EXPLOITABLE PENDANT LA CALIBRATION : "
    "un signal visuel qui permet de savoir en temps réel si le niveau "
    "de mesure choisi (section 27, headroom) fait déjà écrêter l'ampli, "
    "AVANT même de lancer la mesure Dirac."
)
"""[Fiche constructeur officielle] — hypex.nl/products/amplifier-
families/mains-powered-ncorex-family/ncx252mp, lu en entier via le
navigateur intégré (le module exact intégré par Buckeye dans le
NCx252MP 8 canaux de Steve, déjà sourcé section 15)."""

# ---------------------------------------------------------------------------
# 30. Paramètres de calcul de l'algorithme intégré (diagnostic_engine.py) —
#     choix de PROTOTYPE explicitement motivés, pas des valeurs officielles
#     Dirac/StormAudio. Séparés du reste pour qu'ils restent faciles à
#     retrouver et à ajuster si un vrai retour de terrain les contredit.
# ---------------------------------------------------------------------------
ROOM_MODE_TARGET_REDUCTION_FACTOR = 0.7
"""Pour un PIC confirmé comme mode de pièce (jamais pour un creux, voir
LINEAR_EQ_CANNOT_FIX_NONLINEAR_DISTORTION et la logique déjà présente
dans diagnose_anomaly : combler un creux de mode nécessiterait un boost
disproportionné et risqué), le point de contrôle de courbe cible calculé
vise à réduire SEULEMENT 70% de l'écart mesuré, pas 100%. Justification :
(1) un mode de pièce n'a pas la même amplitude à toutes les positions de
micro (section empirique, cartographie_modale.py) — viser 100% sur la
position la plus affectée risquerait de créer un creux ailleurs dans la
pièce ; (2) cohérent avec la prudence déjà appliquée pour le Support
Level (section 17 : laisser ART co-optimiser plutôt que forcer une
correction totale). ⚠️ Choix de PROTOTYPE motivé par cette logique, PAS
une valeur officielle Dirac/StormAudio ni une étude scientifique — à
ajuster si un vrai retour de terrain (plusieurs clients, plusieurs
pièces) suggère une meilleure fraction."""

SUPPORT_LEVEL_INTERPOLATION_WINDOW_HZ = 10.0
"""Fenêtre (± Hz autour de la fréquence de croisement déclarée) utilisée
pour moyenner les points de mesure lors du calcul d'un niveau de support
précis (voir calculate_precise_support_level_db) — choix de prototype
pour lisser le bruit de mesure ponctuel, pas une valeur officielle."""

DEFAULT_FSISO_HZ = 150.0
"""Valeur par défaut officielle du paramètre Fsiso (ART_PARAMETER_
FSISO_OFFICIAL, section 17) réutilisée comme borne haute par défaut de
F-support High tant qu'aucune valeur personnalisée n'est fournie — pas un
nouveau choix de prototype, une vraie valeur par défaut Dirac."""
