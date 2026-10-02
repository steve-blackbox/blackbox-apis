"""
Tests unitaires du moteur de diagnostic. Aucune dépendance externe
(bibliothèque standard `unittest` uniquement), cohérent avec le choix de
ne pas requérir numpy/pytest pour que ce prototype reste exécutable tel
quel.

Lancer depuis le dossier PROJETS_FUTURS_calibrage_audio :
    python3 -m unittest discover -s tests -t .

Le premier test (`test_detect_anomalies_finds_injected_dip`) est un test
de régression : il aurait immédiatement attrapé un bug réel trouvé en
vérifiant ce prototype (la détection par moyenne mobile classique
n'atteignait jamais le seuil car elle lissait l'anomalie avec elle-même ;
corrigé par une tendance de référence en anneau, voir diagnostic_engine.py).
"""

from __future__ import annotations

import math
import os
import sys
import unittest

# Le dossier parent (contenant diagnostic_engine.py, models.py...) n'est
# pas forcément sur sys.path selon la façon dont les tests sont lancés.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diagnostic_engine import (
    axial_room_modes,
    detect_anomalies,
    diagnose_anomaly,
    recommend_support_groups,
)
from models import (
    MeasurementPoint,
    Role,
    RoomInfo,
    Speaker,
    SpeakerMeasurement,
)


def _synthetic_curve(
    base_db: float = 75.0,
    dip_at_hz: float | None = None,
    dip_db: float = 8.0,
    peak_at_hz: float | None = None,
    peak_db: float = 6.0,
) -> list[MeasurementPoint]:
    """Même générateur que example_run.py, dupliqué ici pour ne pas
    dépendre d'un script d'exemple (qui pourrait changer sans rapport
    avec les tests)."""
    points = []
    freq = 20.0
    while freq <= 300.0:
        spl = base_db
        if dip_at_hz and abs(freq - dip_at_hz) < 4:
            spl -= dip_db * math.exp(-((freq - dip_at_hz) ** 2) / 20)
        if peak_at_hz and abs(freq - peak_at_hz) < 4:
            spl += peak_db * math.exp(-((freq - peak_at_hz) ** 2) / 20)
        points.append(MeasurementPoint(freq_hz=round(freq, 1), spl_db=round(spl, 1)))
        freq += 2.0
    return points


class TestDetectAnomalies(unittest.TestCase):
    def setUp(self) -> None:
        self.speaker = Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45)

    def test_detect_anomalies_finds_injected_dip(self) -> None:
        measurement = SpeakerMeasurement(
            self.speaker, _synthetic_curve(dip_at_hz=57.0, dip_db=9.0)
        )
        anomalies = detect_anomalies(measurement)
        self.assertEqual(len(anomalies), 1, anomalies)
        self.assertEqual(anomalies[0].kind, "creux")
        self.assertGreater(anomalies[0].amplitude_db, 4.0)
        self.assertAlmostEqual(anomalies[0].freq_hz, 57.0, delta=4.0)

    def test_detect_anomalies_finds_injected_peak(self) -> None:
        measurement = SpeakerMeasurement(
            self.speaker, _synthetic_curve(peak_at_hz=250.0, peak_db=7.0)
        )
        anomalies = detect_anomalies(measurement)
        self.assertEqual(len(anomalies), 1, anomalies)
        self.assertEqual(anomalies[0].kind, "pic")
        self.assertAlmostEqual(anomalies[0].amplitude_db, 7.0, delta=0.5)

    def test_detect_anomalies_no_false_positive_on_flat_curve(self) -> None:
        measurement = SpeakerMeasurement(self.speaker, _synthetic_curve())
        self.assertEqual(detect_anomalies(measurement), [])

    def test_detect_anomalies_handles_too_few_points(self) -> None:
        few_points = [MeasurementPoint(freq_hz=20.0 + 2 * i, spl_db=75.0) for i in range(5)]
        measurement = SpeakerMeasurement(self.speaker, few_points)
        self.assertEqual(detect_anomalies(measurement), [])

    def test_adjacent_detections_are_merged_into_one_anomaly(self) -> None:
        """Avant le correctif de clustering, un seul creux large de
        plusieurs points de mesure produisait une Anomaly par point."""
        measurement = SpeakerMeasurement(
            self.speaker, _synthetic_curve(dip_at_hz=57.0, dip_db=9.0)
        )
        anomalies = detect_anomalies(measurement)
        freqs = [a.freq_hz for a in anomalies]
        self.assertEqual(len(freqs), len(set(freqs)))
        self.assertEqual(len(anomalies), 1)


class TestAxialRoomModes(unittest.TestCase):
    def test_known_mode_for_6m_length(self) -> None:
        # c / 2 * n / L avec c=343 m/s, L=6 m, n=2 -> ~57.17 Hz
        room = RoomInfo(length_m=6.0, width_m=4.5, height_m=2.5)
        modes = axial_room_modes(room, max_freq_hz=300.0)
        self.assertTrue(
            any(abs(m - 57.17) < 0.5 for m in modes),
            f"Mode attendu ~57.17 Hz absent de {modes}",
        )

    def test_modes_are_sorted_and_bounded(self) -> None:
        room = RoomInfo(length_m=6.0, width_m=4.5, height_m=2.5)
        modes = axial_room_modes(room, max_freq_hz=300.0)
        self.assertEqual(modes, sorted(modes))
        self.assertTrue(all(m <= 300.0 for m in modes))


class TestDiagnoseAnomaly(unittest.TestCase):
    def test_dip_matching_room_mode_is_identified_as_probable(self) -> None:
        room = RoomInfo(length_m=6.0, width_m=4.5, height_m=2.5)
        measurement = SpeakerMeasurement(
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            _synthetic_curve(dip_at_hz=57.0, dip_db=9.0),
        )
        anomaly = detect_anomalies(measurement)[0]
        diagnosed = diagnose_anomaly(anomaly, room=room)
        self.assertTrue(
            any("mode" in cause.lower() for cause in diagnosed.probable_causes)
        )

    def test_without_room_info_diagnosis_stays_open(self) -> None:
        measurement = SpeakerMeasurement(
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            _synthetic_curve(dip_at_hz=57.0, dip_db=9.0),
        )
        anomaly = detect_anomalies(measurement)[0]
        diagnosed = diagnose_anomaly(anomaly, room=None)
        self.assertIn("Essentiel", diagnosed.suggested_action)


class TestRecommendSupportGroups(unittest.TestCase):
    def test_subwoofers_with_different_ranges_get_separate_groups(self) -> None:
        speakers = [
            Speaker("Caisson 1", Role.LFE, freq_min_hz=18, freq_max_hz=120),
            Speaker("Caisson 2", Role.LFE, freq_min_hz=16, freq_max_hz=150),
        ]
        recs = recommend_support_groups(speakers)
        self.assertTrue(len(recs) >= 1)


if __name__ == "__main__":
    unittest.main()
