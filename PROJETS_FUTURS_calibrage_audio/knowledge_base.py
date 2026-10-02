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

from models import CitedPatent, CitedStudy, EvidenceLevel, Role

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
#     La seule source technique "interne" légitime ici est un VRAI brevet
#     déposé par Dirac Research AB, document de divulgation publique
#     complète (c'est la contrepartie légale de la protection par brevet),
#     fourni en PDF par Steve lui-même et lu en texte intégral (extraction
#     réelle du texte, pas une supposition). Référence complète dans
#     CITED_PATENTS ci-dessous. Un deuxième fichier PDF fourni par Steve au
#     même moment (US9415102) s'est avéré être un brevet pharmaceutique
#     d'Alexion Pharmaceuticals sur des anticorps anti-C5, sans aucun
#     rapport avec l'audio ou Dirac — vérifié par lecture réelle du texte,
#     signalé honnêtement plutôt qu'ignoré, et non utilisé ici.
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
]
"""Piste identifiée mais NON encore lue en texte intégral (donc non
ajoutée à CITED_PATENTS) : le brevet US8213637B2 / EP2257083B1 "Sound
field control in multiple listening regions", même inventeur principal
(Lars-Johan Brannmark), déposé 2009, antérieur à celui-ci — porterait
spécifiquement sur le contrôle à PLUSIEURS positions d'écoute
simultanées (potentiellement pertinent pour les 13 positions de mesure
de Steve), mais seul le titre et un extrait court ont été vus via l'API
de recherche Google Patents. À lire en texte intégral avant de lui
attribuer le moindre fait précis, même chose pour US9426600B2 (Adrian
Bahne, variante 'pairwise loudspeaker channel') si Steve souhaite
approfondir davantage cette piste."""
