"""
Cartographie EMPIRIQUE des modes de pièce à partir d'un vrai fichier
`.liveproject` (pas de calcul théorique à partir des dimensions de la
pièce : Steve a fait remarquer à juste titre que les 13 vraies positions
de micro mesurées DANS la pièce constituent déjà une cartographie réelle,
supérieure à un modèle théorique de pièce rectangulaire vide qui ignore
meubles, ouvertures et modes non-axiaux).

Principe utilisé, en deux étapes :

1. **Cohérence spatiale** (`find_recurring_anomalies`) : un creux/pic
   détecté sur une seule position de micro peut être un artefact local ;
   un creux/pic retrouvé à la même fréquence sur la MAJORITÉ des 13
   positions est plus probablement un vrai phénomène de pièce. Réutilise
   `diagnostic_engine.detect_anomalies` (déjà testé/validé) pour chaque
   position individuellement, puis regroupe par fréquence arrondie.

2. **Corrélation croisée entre enceintes/caissons** (`correlation_matrix`) :
   à une fréquence donnée, si le PROFIL spatial (le motif des 13 niveaux
   relatifs selon la position du micro) est quasi identique pour deux
   canaux mesurés par des enceintes différentes, la cause ne peut pas être
   propre à un seul haut-parleur : c'est la pièce (le mode de pièce) qui
   domine la réponse, pas la source. Une corrélation de Pearson proche de
   +1 (même profil) ou -1 (profil en opposition, même mode mais positions
   de pic/creux inversées) entre deux `slot_index` différents est donc un
   bien meilleur indice de "vrai mode de pièce" qu'un calcul théorique de
   modes axiaux. [Acoustique générale] pour le principe (domaine en
   dessous de la fréquence de Schroeder dominé par les modes propres,
   déjà documenté dans knowledge_base.SCHROEDER_TRANSITION_CONCEPT) ;
   la méthode de corrélation croisée elle-même est une construction de ce
   script, pas une règle sourcée externe — à traiter comme un indice
   statistique, pas une preuve absolue.

⚠️ Limites héritées de `liveproject_reader.py`, toujours valables ici :
- `slot_index` 0-5 = canaux large bande, correspondance précise avec l'un
  des 7 noms d'enceintes (Front Left, Center, Front Right, Surround
  Right/Back Right/Back Left/Left) NON établie avec certitude (7 noms
  pour 6 slots, incohérence non résolue).
- `slot_index` 6 et 7 = les 2 subwoofers, identifiés avec une confiance
  nettement meilleure (filtre passe-bas net dans le spectre + durée de
  sweep raccourcie dans l'audio), mais sans certitude sur lequel des deux
  est "Subwoofer 1" vs "Subwoofer 2".
- Les magnitudes sont en dB SPL absolu du fichier brut, pas les dB
  relatifs affichés par le logiciel Dirac Live. Cela n'empêche PAS la
  comparaison relative entre positions ou entre slots faite ici (même
  méthode de mesure, même normalisation pour tous les blocs d'un même
  fichier), mais une valeur affichée ici ne doit jamais être lue comme
  "le niveau en dB tel qu'affiché dans Dirac".
- L'ordre des 13 positions de micro (quelle position = quel siège
  physique) n'est pas documenté dans le fichier : seul Steve, qui a
  déplacé le micro lui-même, peut faire cette correspondance.
- **Ce module trouve des FRÉQUENCES de résonance probables, jamais les
  DIMENSIONS physiques de la pièce** (question explicite de Steve,
  03/10) : le fichier `.liveproject` n'encode nulle part une longueur/
  largeur/hauteur. Tenter l'inversion (partir d'une fréquence de mode
  mesurée pour en déduire LA dimension responsable) est mathématiquement
  ambigu sans contrainte supplémentaire : une même fréquence peut
  correspondre à plusieurs dimensions différentes (pour des ordres n
  différents : f = n·c/(2·L)), à plusieurs axes (longueur, largeur OU
  hauteur), ou à un mode tangentiel/oblique combinant 2-3 dimensions à
  la fois — `axial_room_modes` (diagnostic_engine.py) ne fonctionne que
  dans le sens INVERSE (dimensions connues -> fréquences prédites), pas
  l'inverse. Seule une correspondance partielle redevient possible SI le
  client fournit en plus les vraies dimensions (RoomInfo, niveau
  Approfondi) : on peut alors CONFIRMER qu'une fréquence mesurée
  correspond à un mode axial calculé, pas la DÉCOUVRIR sans cette donnée.

Usage : `python3 cartographie_modale.py "<chemin vers un .liveproject>"`
"""

from __future__ import annotations

import statistics
import sys
from collections import defaultdict
from dataclasses import dataclass

import knowledge_base as kb
from liveproject_reader import MeasurementBlock, read_measurement_blocks
from models import MeasurementPoint, Role, Speaker, SpeakerMeasurement
from diagnostic_engine import detect_anomalies

DEFAULT_FREQ_MIN_HZ = 15.0
DEFAULT_FREQ_MAX_HZ = 500.0
SUBWOOFER_SLOTS = (6, 7)
"""Confirmé par 2 méthodes indépendantes (décodage audio + forme spectrale
passe-bas), voir docstring de `liveproject_reader.py`."""


def _group_by_slot(blocks: list[MeasurementBlock]) -> dict[int, list[MeasurementBlock]]:
    by_slot: dict[int, list[MeasurementBlock]] = defaultdict(list)
    for b in blocks:
        if b.slot_index >= 0:
            by_slot[b.slot_index].append(b)
    return by_slot


def _level_at(block: MeasurementBlock, f_target: float) -> float:
    freqs = block.frequencies_hz
    best_i = min(range(len(freqs)), key=lambda i: abs(freqs[i] - f_target))
    return block.magnitudes_db[best_i]


def _as_measurement(block: MeasurementBlock, f_min: float, f_max: float) -> SpeakerMeasurement:
    pts = [
        MeasurementPoint(f, m)
        for f, m in zip(block.frequencies_hz, block.magnitudes_db)
        if f_min <= f <= f_max
    ]
    dummy = Speaker(name=f"slot{block.slot_index}", role=Role.LFE, freq_min_hz=20.0)
    return SpeakerMeasurement(speaker=dummy, points=pts)


@dataclass
class RecurringAnomaly:
    slot_index: int
    freq_bucket_hz: float
    kind: str  # "creux" ou "pic"
    n_positions: int
    n_total_positions: int
    mean_amplitude_db: float
    min_amplitude_db: float
    max_amplitude_db: float


def find_recurring_anomalies(
    by_slot: dict[int, list[MeasurementBlock]],
    f_min: float = DEFAULT_FREQ_MIN_HZ,
    f_max: float = DEFAULT_FREQ_MAX_HZ,
    threshold_db: float = 4.0,
    freq_bucket_hz: float = 5.0,
    min_position_ratio: float = 0.5,
) -> list[RecurringAnomaly]:
    """Pour chaque slot, détecte les anomalies position par position (sur
    les 13 mesures), puis ne garde que celles qui reviennent à peu près à
    la même fréquence sur au moins `min_position_ratio` des positions —
    le critère de cohérence spatiale qui distingue un vrai phénomène de
    pièce d'un artefact local à une seule position."""
    results: list[RecurringAnomaly] = []
    for slot, blocks in sorted(by_slot.items()):
        n_total = len(blocks)
        occurrences: dict[tuple[float, str], list[float]] = defaultdict(list)
        for block in blocks:
            meas = _as_measurement(block, f_min, f_max)
            for anomaly in detect_anomalies(meas, threshold_db=threshold_db):
                bucket = round(anomaly.freq_hz / freq_bucket_hz) * freq_bucket_hz
                occurrences[(bucket, anomaly.kind)].append(anomaly.amplitude_db)

        min_count = max(1, round(min_position_ratio * n_total))
        for (bucket, kind), amplitudes in sorted(occurrences.items()):
            if len(amplitudes) >= min_count:
                results.append(
                    RecurringAnomaly(
                        slot_index=slot,
                        freq_bucket_hz=bucket,
                        kind=kind,
                        n_positions=len(amplitudes),
                        n_total_positions=n_total,
                        mean_amplitude_db=statistics.mean(amplitudes),
                        min_amplitude_db=min(amplitudes),
                        max_amplitude_db=max(amplitudes),
                    )
                )
    return results


def _pearson(a: list[float], b: list[float]) -> float:
    n = len(a)
    ma, mb = statistics.mean(a), statistics.mean(b)
    cov = sum((a[i] - ma) * (b[i] - mb) for i in range(n))
    sa = sum((x - ma) ** 2 for x in a) ** 0.5
    sb = sum((x - mb) ** 2 for x in b) ** 0.5
    if sa == 0 or sb == 0:
        return 0.0
    return cov / (sa * sb)


def correlation_matrix(
    by_slot: dict[int, list[MeasurementBlock]], freq_hz: float
) -> dict[tuple[int, int], float]:
    """Corrélation de Pearson du profil spatial (niveau par position de
    micro) entre chaque paire de slots, à une fréquence donnée. Une
    corrélation marquée (positive ou négative) entre deux slots DIFFÉRENTS
    indique que le même mode de pièce domine leur réponse à cette
    fréquence, indépendamment de la source : voir docstring de module."""
    vectors = {
        slot: [_level_at(b, freq_hz) for b in blocks]
        for slot, blocks in by_slot.items()
    }
    matrix: dict[tuple[int, int], float] = {}
    slots = sorted(vectors)
    for s1 in slots:
        for s2 in slots:
            matrix[(s1, s2)] = _pearson(vectors[s1], vectors[s2])
    return matrix


@dataclass
class FrequencyCluster:
    anomalies: list[RecurringAnomaly]

    @property
    def slots(self) -> list[int]:
        return sorted({a.slot_index for a in self.anomalies})

    @property
    def freq_range_hz(self) -> tuple[float, float]:
        freqs = [a.freq_bucket_hz for a in self.anomalies]
        return (min(freqs), max(freqs))

    @property
    def is_shared(self) -> bool:
        """Critère strict de 'mode de pièce confirmé' : au moins 2 SLOTS
        DIFFÉRENTS montrent une anomalie DÉTECTÉE (pas une simple
        similarité globale de courbe, voir avertissement ci-dessous) dans
        ce cluster de fréquence. Un seul slot présent = pas de preuve de
        partage à cette fréquence précise."""
        return len(self.slots) >= 2

    @property
    def is_modal_region(self) -> bool:
        return self.freq_range_hz[1] < kb.MODAL_REGION_UPPER_BOUND_HZ


def cluster_anomalies_by_frequency(
    anomalies: list[RecurringAnomaly], window_hz: float = 10.0
) -> list[FrequencyCluster]:
    """Regroupe les anomalies récurrentes dont les fréquences sont proches
    (fenêtre glissante `window_hz`), tous slots confondus. Nécessaire car
    un même phénomène physique peut être détecté à un bucket de fréquence
    légèrement différent selon le canal (bruit de mesure, `freq_bucket_hz`
    de `find_recurring_anomalies` trop fin pour capter ce décalage) : sans
    ce regroupement, deux slots touchés par le même mode à quelques Hz
    d'écart seraient classés à tort comme deux anomalies isolées
    distinctes plutôt qu'un seul mode partagé.

    ⚠️ Ce regroupement par seule proximité fréquentielle reste une
    heuristique : il ne vérifie pas que les slots du cluster partagent
    effectivement la même nature (creux/pic) ni la même signature spatiale
    (contrairement à `correlation_matrix`, qui reste le bon outil pour
    vérifier un cluster suspect au cas par cas)."""
    anomalies_sorted = sorted(anomalies, key=lambda a: a.freq_bucket_hz)
    clusters: list[list[RecurringAnomaly]] = []
    for a in anomalies_sorted:
        if clusters and abs(a.freq_bucket_hz - clusters[-1][-1].freq_bucket_hz) <= window_hz:
            clusters[-1].append(a)
        else:
            clusters.append([a])
    return [FrequencyCluster(c) for c in clusters]


def describe_clusters(clusters: list[FrequencyCluster]) -> str:
    lines = []
    ordered = sorted(clusters, key=lambda c: -len(c.slots))
    for c in ordered:
        fmin, fmax = c.freq_range_hz
        zone = "modale (<300Hz)" if c.is_modal_region else "HORS zone modale (>=300Hz)"
        status = (
            f"PARTAGÉ sur {len(c.slots)} canaux (mode de pièce confirmé)"
            if c.is_shared else "canal UNIQUE (pas de preuve de partage à cette fréquence)"
        )
        lines.append(f"[{fmin:.0f}-{fmax:.0f} Hz] zone {zone} — {status} (slots: {c.slots})")
        for a in sorted(c.anomalies, key=lambda a: a.slot_index):
            lines.append(
                f"    S{a.slot_index}: {a.kind} à {a.freq_bucket_hz:.0f}Hz, "
                f"{a.n_positions}/{a.n_total_positions} positions, "
                f"ampl moy={a.mean_amplitude_db:.1f}dB "
                f"(min={a.min_amplitude_db:.1f}, max={a.max_amplitude_db:.1f})"
            )
    return "\n".join(lines)


def describe_recurring_anomalies(anomalies: list[RecurringAnomaly]) -> str:
    lines = []
    by_slot: dict[int, list[RecurringAnomaly]] = defaultdict(list)
    for a in anomalies:
        by_slot[a.slot_index].append(a)
    for slot in sorted(by_slot):
        label = "SUBWOOFER (confiance haute)" if slot in SUBWOOFER_SLOTS else \
            "canal large bande (correspondance enceinte non confirmée)"
        lines.append(f"--- Slot {slot} [{label}] ---")
        if not by_slot[slot]:
            lines.append("  Aucune anomalie récurrente.")
            continue
        for a in by_slot[slot]:
            lines.append(
                f"  {a.kind.upper():6s} ~{a.freq_bucket_hz:4.0f} Hz : "
                f"{a.n_positions}/{a.n_total_positions} positions, "
                f"amplitude moy={a.mean_amplitude_db:.1f} dB "
                f"(min={a.min_amplitude_db:.1f}, max={a.max_amplitude_db:.1f})"
            )
    return "\n".join(lines)


def describe_correlation(matrix: dict[tuple[int, int], float], freq_hz: float) -> str:
    slots = sorted({s for s, _ in matrix})
    lines = [f"Corrélation du profil spatial (13 positions) à {freq_hz:.0f} Hz :"]
    header = "       " + "  ".join(f"S{s}" for s in slots)
    lines.append(header)
    for s1 in slots:
        row = "  ".join(f"{matrix[(s1, s2)]:+.2f}" for s2 in slots)
        lines.append(f"S{s1:<3d} | {row}")
    return "\n".join(lines)


def main() -> None:
    if len(sys.argv) != 2:
        print("Usage: python3 cartographie_modale.py <chemin_vers_fichier.liveproject>")
        sys.exit(1)

    with open(sys.argv[1], "rb") as f:
        data = f.read()

    blocks = read_measurement_blocks(data)
    by_slot = _group_by_slot(blocks)

    print(f"{len(blocks)} blocs de mesure, {len(by_slot)} slots, "
          f"{len(next(iter(by_slot.values())))} positions de micro par slot.\n")

    anomalies = find_recurring_anomalies(by_slot)
    print(describe_recurring_anomalies(anomalies))

    print("\n" + "=" * 70)
    print("CLASSEMENT PAR CLUSTER DE FRÉQUENCE (fenêtre +/-10Hz) :")
    print("PARTAGÉ = >=2 slots différents montrent une anomalie DÉTECTÉE à "
          "cette fréquence (critère strict, pas une simple similarité de "
          "courbe globale).")
    print("=" * 70)
    clusters = cluster_anomalies_by_frequency(anomalies)
    print(describe_clusters(clusters))

    # Fréquences distinctes où une anomalie récurrente a été trouvée sur
    # au moins 2 slots différents : ce sont les meilleures candidates pour
    # vérifier la corrélation croisée (indice de mode de pièce partagé).
    freq_by_bucket: dict[float, set[int]] = defaultdict(set)
    for a in anomalies:
        freq_by_bucket[a.freq_bucket_hz].add(a.slot_index)
    shared_freqs = sorted(f for f, slots in freq_by_bucket.items() if len(slots) >= 2)

    print("\n" + "=" * 70)
    print("CORRÉLATION CROISÉE (complément informatif, voir avertissement "
          "dans la docstring de cluster_anomalies_by_frequency) :")
    print("=" * 70)
    for fz in shared_freqs:
        print()
        matrix = correlation_matrix(by_slot, fz)
        print(describe_correlation(matrix, fz))


if __name__ == "__main__":
    main()
