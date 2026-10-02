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
    CitedPatent,
    CitedStudy,
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
