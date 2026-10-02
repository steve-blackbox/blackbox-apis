"""
Structures de données du moteur de diagnostic/calibrage Dirac Live ART.

Ce module ne contient aucune règle métier : uniquement les objets manipulés
par `knowledge_base.py` et `diagnostic_engine.py`. Voir README.md pour le
contexte complet du projet et les sources utilisées.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    """Rôle d'une enceinte dans le système, utilisé pour appliquer les
    règles de groupes/support propres à chaque position (voir
    knowledge_base.STORM_AUDIO_SUPPORT_HIERARCHY)."""

    LFE = "lfe"                      # caisson(s) de graves
    FRONT_LEFT = "front_left"
    FRONT_RIGHT = "front_right"
    CENTER = "center"
    SURROUND_LEFT = "surround_left"
    SURROUND_RIGHT = "surround_right"
    SURROUND_BACK_LEFT = "surround_back_left"
    SURROUND_BACK_RIGHT = "surround_back_right"
    HEIGHT_FRONT_LEFT = "height_front_left"
    HEIGHT_FRONT_RIGHT = "height_front_right"
    HEIGHT_REAR_LEFT = "height_rear_left"
    HEIGHT_REAR_RIGHT = "height_rear_right"


FRONT_ROLES = {Role.FRONT_LEFT, Role.FRONT_RIGHT, Role.CENTER}
SURROUND_ROLES = {
    Role.SURROUND_LEFT, Role.SURROUND_RIGHT,
    Role.SURROUND_BACK_LEFT, Role.SURROUND_BACK_RIGHT,
}
HEIGHT_ROLES = {
    Role.HEIGHT_FRONT_LEFT, Role.HEIGHT_FRONT_RIGHT,
    Role.HEIGHT_REAR_LEFT, Role.HEIGHT_REAR_RIGHT,
}


@dataclass
class Speaker:
    """Une enceinte ou un caisson déclaré par le client (niveau Essentiel
    minimum : rôle + plage de fréquence constructeur). Les trois derniers
    champs sont optionnels : renseignés quand une vraie fiche technique
    constructeur a été récupérée (voir knowledge_base.py, section 15, et
    EvidenceLevel.FICHE_CONSTRUCTEUR_OFFICIELLE), sinon laissés à None
    plutôt que devinés."""

    name: str
    role: Role
    freq_min_hz: float          # fréquence basse garantie par le constructeur
    freq_max_hz: float = 20000.0
    is_subwoofer: bool = False
    impedance_nominal_ohms: float | None = None
    sensitivity_db_1w1m: float | None = None
    power_rms_w: float | None = None

    def __post_init__(self) -> None:
        if self.role == Role.LFE:
            self.is_subwoofer = True


@dataclass
class MeasurementPoint:
    freq_hz: float
    spl_db: float


@dataclass
class SpeakerMeasurement:
    """Courbe mesurée brute pour une enceinte (lue par le client sur sa
    capture d'écran Dirac et saisie point par point, ou exportée si son
    outil de mesure le permet). Le moteur ne lit pas l'image lui-même —
    voir README.md, section Limites."""

    speaker: Speaker
    points: list[MeasurementPoint]


@dataclass
class RoomInfo:
    """Informations optionnelles du niveau 'Approfondi' (formulaire 2 min
    déjà proposé par Claude dans la conversation source, message 34)."""

    length_m: float
    width_m: float
    height_m: float
    speaker_positions: dict[str, tuple[float, float, float]] = field(
        default_factory=dict
    )  # nom d'enceinte -> (x, y, z) en mètres depuis un coin de la pièce
    subwoofer_count: int = 1


class ServiceLevel(str, Enum):
    ESSENTIEL = "essentiel"     # captures de courbes + liste du matériel
    APPROFONDI = "approfondi"   # + dimensions et placement (RoomInfo)


class EvidenceLevel(str, Enum):
    """Niveau de confiance affiché pour CHAQUE recommandation — exigence
    explicite notée dans PROJETS_FUTURS.md : 'citer sa source à chaque
    recommandation' plutôt que produire une réponse à l'aveugle."""

    MARANTZ_DIRAC_OFFICIEL = (
        "Manuel officiel Marantz / Dirac Live (manuals.marantz.com, lu "
        "directement, pas une reformulation tierce)"
    )
    FICHE_CONSTRUCTEUR_OFFICIELLE = (
        "Fiche technique officielle du site du fabricant (ex: elipson.com, "
        "buckeyeamp.com), lue directement via navigation réelle, pas une "
        "reformulation tierce ni une estimation"
    )
    STORMAUDIO_OFFICIEL = "Directive officielle StormAudio (doc ART)"
    BREVET_DIRAC_RESEARCH = (
        "Brevet Dirac Research AB lu en texte intégral (ex: US9781510B2) "
        "— source primaire officielle, mais décrit un mécanisme "
        "mathématique général, pas forcément les paramètres exacts du "
        "produit commercial actuel"
    )
    PRINCIPE_ACOUSTIQUE = "Principe acoustique général (domaine public)"
    RETOUR_EXPERIENCE_STEVE = "Retour d'expérience Steve — à valider par test"
    HYPOTHESE_A_TESTER = "Hypothèse / indice de forum — non prouvé"


@dataclass
class Recommendation:
    category: str                # ex: "Groupes de support", "Plage de fréquence"
    target: str                  # enceinte(s) ou groupe concerné
    action: str                  # ce qu'il faut faire, en une phrase claire
    evidence: EvidenceLevel
    detail: str = ""             # justification plus longue si utile


@dataclass
class Anomaly:
    """Un creux ou un pic jugé significatif sur une courbe mesurée."""

    speaker_name: str
    freq_hz: float
    kind: str            # "creux" ou "pic"
    amplitude_db: float
    probable_causes: list[str] = field(default_factory=list)
    suggested_action: str = ""


@dataclass
class DiagnosticReport:
    service_level: ServiceLevel
    recommendations: list[Recommendation] = field(default_factory=list)
    anomalies: list[Anomaly] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


@dataclass
class CitedStudy:
    """Une référence bibliographique réellement vérifiée par recherche web
    (titre/auteurs/revue/URL confirmés), jamais une référence inventée ou
    'mémorisée' sans fichier fourni — voir knowledge_base.py, section
    Études de référence, pour la méthode et les limites de vérification."""

    domain: str                  # "psychoacoustique" / "acoustique des salles" / "matériaux"
    title: str
    venue_or_authors: str
    year: str
    source_url: str
    verification: str            # ce qui a été réellement vérifié (titre, abstract, texte intégral...)
    takeaway: str                 # ce qu'on en retient pour l'algorithme, formulé prudemment


@dataclass
class CitedPatent:
    """Un brevet réellement lu en texte intégral (PDF fourni par Steve ou
    récupéré via Google Patents), jamais une référence inventée — voir
    knowledge_base.py, section 11, pour le contexte. Un brevet est une
    source de nature différente d'une étude académique (CitedStudy) :
    c'est un document de divulgation technique complète, obligatoire en
    échange de la protection juridique, examiné par un office des
    brevets (pas de peer review scientifique). Son contenu technique est
    public et citable, mais reste la description d'une invention
    protégée, pas une publication scientifique."""

    patent_number: str            # ex: "US9781510B2"
    title: str
    inventors: str
    assignee: str
    priority_date: str            # date de dépôt initiale
    source_url: str
    verification: str             # ce qui a été réellement lu (texte intégral, quelles sections)
    takeaway: str                  # ce qu'on en retient, formulé prudemment


@dataclass
class ManufacturerSpecSheet:
    """Une fiche technique constructeur réellement lue sur le site
    officiel du fabricant (navigation réelle, onglet 'Specifications'/
    'Détails techniques' cliqué), jamais une estimation ni une
    reformulation tierce — voir knowledge_base.py, section 15, pour la
    méthode de récupération et le contexte (demande de Steve : être
    capable de récupérer les manuels constructeurs du matériel réel)."""

    brand: str
    model: str
    role_in_system: str           # ex: "Façades 7.2 de Steve", "Ampli de puissance"
    source_url: str
    specs: dict[str, str]          # ex: {"Fréquence": "35Hz-30kHz", "Impédance": "6 ohms"}
    verification: str              # ce qui a été réellement lu (onglet cliqué, méthode)
