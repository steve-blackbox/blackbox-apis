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
    minimum : rôle + plage de fréquence constructeur)."""

    name: str
    role: Role
    freq_min_hz: float          # fréquence basse garantie par le constructeur
    freq_max_hz: float = 20000.0
    is_subwoofer: bool = False

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
    STORMAUDIO_OFFICIEL = "Directive officielle StormAudio (doc ART)"
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
