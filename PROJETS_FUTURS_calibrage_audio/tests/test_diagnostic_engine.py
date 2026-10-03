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
    calculate_precise_support_level_db,
    calculate_room_mode_control_points,
    calculate_support_frequency_range,
    detect_anomalies,
    detect_dangerous_gain_anomalies,
    diagnose_anomaly,
    evaluate_subwoofer_pre_gain_headroom_strategy,
    recommend_support_groups,
    recommend_support_pairings,
    recommend_target_curves,
    run_diagnostic,
)
from models import (
    AmplificationTopology,
    AmplifierChainSpec,
    Anomaly,
    MeasurementPoint,
    Role,
    RoomInfo,
    ServiceLevel,
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


class TestRecommendSupportPairings(unittest.TestCase):
    """Vérifie que le groupage de support est DÉDUIT du système réel du
    client (rôles présents), de façon générique pour N'IMPORTE QUELLE
    configuration (pas seulement celle de Steve) — exigence explicite de
    Steve (03/10) : 'il y aura des configurations totalement différentes
    à la mienne [...] il y a tout un tas d'autres possibilités'."""

    def test_decisive_subwoofer_support_for_every_non_sub_speaker(self) -> None:
        speakers = [
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            Speaker("Façade Droite", Role.FRONT_RIGHT, freq_min_hz=45),
            Speaker("Centrale", Role.CENTER, freq_min_hz=60),
            Speaker("Surround Gauche", Role.SURROUND_LEFT, freq_min_hz=80),
            Speaker("Surround Droite", Role.SURROUND_RIGHT, freq_min_hz=80),
            Speaker("Caisson", Role.LFE, freq_min_hz=20),
        ]
        recs = recommend_support_pairings(speakers)
        decisive = [r for r in recs if r.category == "Groupage de support recommandé"]
        # Une recommandation décisive par enceinte non-caisson, jamais pour
        # le caisson lui-même.
        self.assertEqual(len(decisive), 5)
        for rec in decisive:
            self.assertEqual(rec.action, "Support retenu : Caisson.")

    def test_no_subwoofer_in_system_yields_no_recommendation(self) -> None:
        speakers = [
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            Speaker("Façade Droite", Role.FRONT_RIGHT, freq_min_hz=45),
        ]
        self.assertEqual(recommend_support_pairings(speakers), [])

    def test_center_never_offered_as_an_alternative_support_donor(self) -> None:
        speakers = [
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            Speaker("Façade Droite", Role.FRONT_RIGHT, freq_min_hz=45),
            Speaker("Centrale", Role.CENTER, freq_min_hz=60),
            Speaker("Caisson", Role.LFE, freq_min_hz=20),
        ]
        recs = recommend_support_pairings(speakers)
        alternatives = [
            r for r in recs
            if r.category == "Groupage de support — configuration alternative existante"
        ]
        self.assertTrue(all("Centrale" not in r.action for r in alternatives))

    def test_alternative_mentioned_only_decisive_recommendation_stays_subwoofer(self) -> None:
        """Même quand une configuration croisée alternative existe (ex.
        Surround Back disponible), la recommandation DÉCISIVE reste le
        caisson — jamais une instruction 'testez et changez si besoin'."""
        speakers = [
            Speaker("Surround Gauche", Role.SURROUND_LEFT, freq_min_hz=80),
            Speaker("Surround Back Gauche", Role.SURROUND_BACK_LEFT, freq_min_hz=80),
            Speaker("Caisson", Role.LFE, freq_min_hz=20),
        ]
        recs = recommend_support_pairings(speakers)
        decisive = [
            r for r in recs
            if r.category == "Groupage de support recommandé" and r.target == "Surround Gauche"
        ]
        self.assertEqual(len(decisive), 1)
        self.assertEqual(decisive[0].action, "Support retenu : Caisson.")
        self.assertNotIn("essayez", decisive[0].action.lower())
        self.assertNotIn("si besoin", decisive[0].action.lower())


class TestRecommendTargetCurves(unittest.TestCase):
    """Le choix entre les options de courbe cible façade/caisson relève
    du goût du client, pas d'un calcul physique (voir docstring de
    recommend_target_curves) : sans préférence déclarée, le moteur doit
    rester honnête et lister les options plutôt que d'en inventer une ;
    avec une préférence déclarée, il doit trancher fermement."""

    def setUp(self) -> None:
        self.speakers = [
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            Speaker("Façade Droite", Role.FRONT_RIGHT, freq_min_hz=45),
            Speaker("Centrale", Role.CENTER, freq_min_hz=60),
            Speaker("Caisson 1", Role.LFE, freq_min_hz=18, freq_max_hz=120),
        ]

    def _facade_rec(self, recs):
        return next(r for r in recs if r.target == "façade (gauche/droite/centre)")

    def _sub_rec(self, recs):
        return next(r for r in recs if r.target == "caisson(s) / LFE")

    def test_no_preference_lists_options_for_facade(self) -> None:
        recs = recommend_target_curves(self.speakers)
        facade = self._facade_rec(recs)
        self.assertIn("Options :", facade.action)
        self.assertIn("préférence", facade.detail.lower())

    def test_harman_preference_resolves_facade_to_a_single_choice(self) -> None:
        recs = recommend_target_curves(self.speakers, target_curve_preference="harman")
        facade = self._facade_rec(recs)
        self.assertNotIn("Options :", facade.action)
        self.assertIn("Harman", facade.action)

    def test_cinema_dedie_preference_resolves_facade_to_a_single_choice(self) -> None:
        recs = recommend_target_curves(self.speakers, target_curve_preference="cinema_dedie")
        facade = self._facade_rec(recs)
        self.assertNotIn("Options :", facade.action)
        self.assertIn("Cinema Target", facade.action)

    def test_cinema_dedie_preference_also_resolves_subwoofer_curve(self) -> None:
        recs = recommend_target_curves(self.speakers, target_curve_preference="cinema_dedie")
        sub = self._sub_rec(recs)
        self.assertNotIn("Options :", sub.action)
        self.assertIn("Cinema Target", sub.action)

    def test_harman_preference_leaves_subwoofer_impact_choice_open(self) -> None:
        # Le caisson garde 2 options (6 ou 8 dB) : aucune règle sourcée
        # ne permet de trancher ce dernier point à la place du client.
        recs = recommend_target_curves(self.speakers, target_curve_preference="harman")
        sub = self._sub_rec(recs)
        self.assertIn("Options :", sub.action)

    def test_surround_curve_is_a_firm_recommendation_not_a_menu(self) -> None:
        # Une seule option documentée ici : pas d'ambiguïté de goût à
        # résoudre, donc pas de "menu" d'un seul élément.
        speakers = self.speakers + [
            Speaker("Surround Gauche", Role.SURROUND_LEFT, freq_min_hz=55),
        ]
        recs = recommend_target_curves(speakers)
        surround = next(r for r in recs if r.target == "surround / hauteur")
        self.assertNotIn("Options :", surround.action)
        self.assertIn("Surround Cinema Target StormAudio", surround.action)


class TestCalculatePreciseSupportLevel(unittest.TestCase):
    """Couvre calculate_precise_support_level_db : le calcul chiffré
    demandé par Steve (niveau de support à 0,5 dB près, pas une
    recommandation qualitative seule)."""

    def setUp(self) -> None:
        self.main_speaker = Speaker("Surround Right", Role.SURROUND_RIGHT, freq_min_hz=53)
        self.support_speaker = Speaker(
            "Surround Back Right", Role.SURROUND_BACK_RIGHT, freq_min_hz=53
        )

    def test_computes_exact_gap_rounded_to_half_db_step(self) -> None:
        main_m = SpeakerMeasurement(self.main_speaker, [MeasurementPoint(80, 0.0)])
        # -7.3 dB d'écart doit arrondir à -7.5 dB (pas de 0,5 dB)
        support_m = SpeakerMeasurement(self.support_speaker, [MeasurementPoint(80, -7.3)])
        rec = calculate_precise_support_level_db(main_m, support_m, crossover_hz=80.0)
        self.assertEqual(rec.precise_value_db, -7.5)

    def test_clamps_to_official_min_db(self) -> None:
        main_m = SpeakerMeasurement(self.main_speaker, [MeasurementPoint(80, 0.0)])
        support_m = SpeakerMeasurement(self.support_speaker, [MeasurementPoint(80, -50.0)])
        rec = calculate_precise_support_level_db(main_m, support_m, crossover_hz=80.0)
        self.assertEqual(rec.precise_value_db, -24.0)

    def test_clamps_to_official_max_db(self) -> None:
        main_m = SpeakerMeasurement(self.main_speaker, [MeasurementPoint(80, 0.0)])
        support_m = SpeakerMeasurement(self.support_speaker, [MeasurementPoint(80, 10.0)])
        rec = calculate_precise_support_level_db(main_m, support_m, crossover_hz=80.0)
        self.assertEqual(rec.precise_value_db, -1.0)

    def test_returns_none_precise_value_when_no_point_in_window(self) -> None:
        main_m = SpeakerMeasurement(self.main_speaker, [MeasurementPoint(500, 0.0)])
        support_m = SpeakerMeasurement(self.support_speaker, [MeasurementPoint(500, -7.0)])
        rec = calculate_precise_support_level_db(main_m, support_m, crossover_hz=80.0)
        self.assertIsNone(rec.precise_value_db)


class TestCalculateSupportFrequencyRange(unittest.TestCase):
    """Couvre calculate_support_frequency_range : F-support Low/High,
    génériques pour n'importe quelle enceinte ou caisson."""

    def test_non_subwoofer_floor_is_50hz(self) -> None:
        speaker = Speaker("Petite surround", Role.SURROUND_LEFT, freq_min_hz=35.0)
        rec = calculate_support_frequency_range(speaker)
        self.assertEqual(rec.freq_range_hz, (50.0, 150.0))

    def test_non_subwoofer_uses_manufacturer_value_above_floor(self) -> None:
        speaker = Speaker("Surround", Role.SURROUND_LEFT, freq_min_hz=53.0)
        rec = calculate_support_frequency_range(speaker)
        self.assertEqual(rec.freq_range_hz, (53.0, 150.0))

    def test_subwoofer_floor_is_20hz(self) -> None:
        speaker = Speaker("Caisson", Role.LFE, freq_min_hz=20.0)
        rec = calculate_support_frequency_range(speaker)
        self.assertEqual(rec.freq_range_hz, (20.0, 150.0))

    def test_custom_fsiso_changes_high_bound(self) -> None:
        speaker = Speaker("Surround", Role.SURROUND_LEFT, freq_min_hz=53.0)
        rec = calculate_support_frequency_range(speaker, fsiso_hz=100.0)
        self.assertEqual(rec.freq_range_hz, (53.0, 100.0))


class TestCalculateRoomModeControlPoints(unittest.TestCase):
    """Couvre calculate_room_mode_control_points : le principe de
    prudence est le coeur de cette fonction — jamais de point de boost
    pour combler un creux de mode de pièce (limite physique déjà
    documentée section 14)."""

    def test_confirmed_peak_generates_a_control_point(self) -> None:
        anomalies = [Anomaly("Center", 110.0, "pic", 6.0, is_confirmed_room_mode=True)]
        points = calculate_room_mode_control_points(anomalies)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].freq_hz, 110.0)
        self.assertLess(points[0].gain_db, 0.0)  # toujours une réduction, jamais un boost

    def test_confirmed_dip_generates_a_lowering_control_point_never_a_boost(self) -> None:
        """Le test le plus important de cette classe, mis à jour suite au
        cas réel vécu par Steve (gains jusqu'à 12dB ayant fait chauffer
        son ampli, section 33) : un creux confirmé comme mode GÉNÈRE
        maintenant un point de contrôle, mais celui-ci ABAISSE toujours
        la cible (jamais un boost positif) — c'est précisément ce qui
        empêche Dirac de tenter de combler le creux par un gain massif."""
        anomalies = [Anomaly("Front Left", 60.0, "creux", 9.0, is_confirmed_room_mode=True)]
        points = calculate_room_mode_control_points(anomalies)
        self.assertEqual(len(points), 1)
        self.assertEqual(points[0].freq_hz, 60.0)
        self.assertLess(points[0].gain_db, 0.0)  # invariant de sécurité : jamais un boost
        self.assertIn("ABAISSÉE", points[0].reason)

    def test_unconfirmed_peak_generates_no_control_point(self) -> None:
        anomalies = [Anomaly("Front Left", 200.0, "pic", 5.0, is_confirmed_room_mode=False)]
        points = calculate_room_mode_control_points(anomalies)
        self.assertEqual(points, [])

    def test_unconfirmed_dip_generates_no_control_point(self) -> None:
        anomalies = [Anomaly("Front Left", 200.0, "creux", 5.0, is_confirmed_room_mode=False)]
        points = calculate_room_mode_control_points(anomalies)
        self.assertEqual(points, [])

    def test_reduction_is_a_fraction_not_the_full_measured_amplitude(self) -> None:
        anomalies = [Anomaly("Center", 110.0, "pic", 10.0, is_confirmed_room_mode=True)]
        points = calculate_room_mode_control_points(anomalies)
        self.assertGreater(points[0].gain_db, -10.0)  # pas 100% de réduction
        self.assertLess(points[0].gain_db, 0.0)

    def test_no_control_point_ever_boosts_the_target_curve(self) -> None:
        """Invariant de sécurité global, directement motivé par le cas
        réel de surchauffe vécu par Steve : qu'il s'agisse d'un pic ou
        d'un creux, calculate_room_mode_control_points ne doit JAMAIS
        retourner un gain_db positif."""
        anomalies = [
            Anomaly("A", 60.0, "creux", 15.0, is_confirmed_room_mode=True),
            Anomaly("B", 120.0, "pic", 15.0, is_confirmed_room_mode=True),
        ]
        points = calculate_room_mode_control_points(anomalies)
        self.assertEqual(len(points), 2)
        self.assertTrue(all(p.gain_db < 0.0 for p in points))


class TestDetectDangerousGainAnomalies(unittest.TestCase):
    """Couvre detect_dangerous_gain_anomalies — directement motivé par
    le cas réel vécu par Steve (gains jusqu'à 12dB ayant fait chauffer
    son ampli, section 33)."""

    def test_amplitude_above_threshold_triggers_a_warning(self) -> None:
        anomalies = [Anomaly("Front Left", 60.0, "creux", 12.0, is_confirmed_room_mode=True)]
        warnings = detect_dangerous_gain_anomalies(anomalies)
        self.assertEqual(len(warnings), 1)
        self.assertIn("Front Left", warnings[0])
        self.assertIn("60", warnings[0])

    def test_amplitude_below_threshold_triggers_no_warning(self) -> None:
        anomalies = [Anomaly("Front Left", 60.0, "creux", 4.0, is_confirmed_room_mode=True)]
        self.assertEqual(detect_dangerous_gain_anomalies(anomalies), [])

    def test_applies_even_to_unconfirmed_anomalies(self) -> None:
        """Même un creux non confirmé comme mode de pièce (local,
        proximité mur/meuble) peut inciter Dirac à un gain dangereux."""
        anomalies = [Anomaly("Front Left", 200.0, "creux", 11.0, is_confirmed_room_mode=False)]
        warnings = detect_dangerous_gain_anomalies(anomalies)
        self.assertEqual(len(warnings), 1)


class TestEvaluateSubwooferPreGainHeadroomStrategy(unittest.TestCase):
    """Couvre evaluate_subwoofer_pre_gain_headroom_strategy — généralise
    à n'importe quel client la stratégie de pré-gain caisson rapportée
    par Steve (knowledge_base.py, section 40-41 : Gemini a déterminé son
    +8dB en fonction de sa connectique XLR/RCA Buckeye et des capacités
    du CINEMA 30)."""

    def test_missing_preamp_data_returns_none_but_explains_principle(self) -> None:
        """Cas réel actuel de Steve : le niveau de sortie max du CINEMA
        30 n'a jamais été retrouvé (section 27) — la fonction doit
        rester honnête plutôt que d'inventer un chiffre."""
        chain = AmplifierChainSpec(connector_type="XLR(adaptateur RCA)")
        margin, message = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain, proposed_input_gain_increase_db=8.0
        )
        self.assertIsNone(margin)
        self.assertIn("8.0", message)
        self.assertIn("manque", message)

    def test_missing_baseline_required_output_also_returns_none(self) -> None:
        chain = AmplifierChainSpec(preamp_max_output_vrms=4.0)
        margin, message = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain, proposed_input_gain_increase_db=8.0
        )
        self.assertIsNone(margin)

    def test_complete_data_computes_exact_margin_gain(self) -> None:
        """Avec toutes les données, le gain de marge doit être exactement
        égal au pré-gain appliqué (identité mathématique directe tant
        qu'aucun maillon n'est déjà saturé)."""
        chain = AmplifierChainSpec(preamp_max_output_vrms=4.0)
        margin, message = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain,
            proposed_input_gain_increase_db=8.0,
            baseline_required_output_vrms=1.0,
        )
        self.assertIsNotNone(margin)
        baseline_margin = 20 * math.log10(4.0 / 1.0)
        self.assertAlmostEqual(margin - baseline_margin, 8.0, places=6)
        self.assertIn("12.0", message)  # marge de départ
        self.assertIn("20.0", message)  # marge après pré-gain

    def test_zero_gain_increase_leaves_margin_unchanged(self) -> None:
        chain = AmplifierChainSpec(preamp_max_output_vrms=4.0)
        margin, _ = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain, proposed_input_gain_increase_db=0.0,
            baseline_required_output_vrms=1.0,
        )
        self.assertAlmostEqual(margin, 20 * math.log10(4.0 / 1.0), places=6)

    def test_integrated_amp_topology_adds_extra_caveat_but_still_computes(
        self,
    ) -> None:
        """Remarque explicite de Steve (03/10) : même avec des amplis
        intégrés pour le reste du système, le caisson reste alimenté par
        une sortie ligne LFE dédiée — le calcul reste applicable, mais
        avec un avertissement supplémentaire sur la fiabilité de la
        donnée Vrms."""
        chain = AmplifierChainSpec(
            topology=AmplificationTopology.INTEGRATED_AMP,
            preamp_max_output_vrms=4.0,
        )
        margin, message = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain,
            proposed_input_gain_increase_db=8.0,
            baseline_required_output_vrms=1.0,
        )
        self.assertIsNotNone(margin)
        self.assertIn("INTEGRATED_AMP", message)

    def test_external_power_amp_topology_has_no_extra_caveat(self) -> None:
        chain = AmplifierChainSpec(
            topology=AmplificationTopology.EXTERNAL_POWER_AMP,
            preamp_max_output_vrms=4.0,
        )
        _, message = evaluate_subwoofer_pre_gain_headroom_strategy(
            chain,
            proposed_input_gain_increase_db=8.0,
            baseline_required_output_vrms=1.0,
        )
        self.assertNotIn("INTEGRATED_AMP", message)


class TestRunDiagnosticSupportsCustomGrouping(unittest.TestCase):
    """Vérifie que run_diagnostic s'adapte à N'IMPORTE QUEL schéma de
    groupage déclaré (pas seulement la hiérarchie standard par rôle) —
    exigence explicite de Steve."""

    def test_custom_crossed_grouping_produces_a_precise_level(self) -> None:
        speakers = [
            Speaker("Surround Right", Role.SURROUND_RIGHT, freq_min_hz=53),
            Speaker("Surround Back Right", Role.SURROUND_BACK_RIGHT, freq_min_hz=53),
        ]
        measurements = [
            SpeakerMeasurement(speakers[0], [MeasurementPoint(80, 0.0)]),
            SpeakerMeasurement(speakers[1], [MeasurementPoint(80, -7.0)]),
        ]
        report = run_diagnostic(
            speakers=speakers,
            measurements=measurements,
            service_level=ServiceLevel.ESSENTIEL,
            support_group_assignments=[("Surround Back Right", "Surround Right", 80.0)],
        )
        precise_recs = [r for r in report.recommendations if r.precise_value_db is not None]
        self.assertEqual(len(precise_recs), 1)
        self.assertEqual(precise_recs[0].precise_value_db, -7.0)

    def test_unknown_speaker_name_in_grouping_adds_a_warning_not_a_crash(self) -> None:
        speakers = [Speaker("Surround Right", Role.SURROUND_RIGHT, freq_min_hz=53)]
        measurements = [SpeakerMeasurement(speakers[0], [MeasurementPoint(80, 0.0)])]
        report = run_diagnostic(
            speakers=speakers,
            measurements=measurements,
            service_level=ServiceLevel.ESSENTIEL,
            support_group_assignments=[("Nom Inexistant", "Surround Right", 80.0)],
        )
        self.assertTrue(any("introuvable" in w for w in report.warnings))


class TestRunDiagnosticAutoDeducesSupportLevel(unittest.TestCase):
    """Le niveau de support précis doit être calculé AUTOMATIQUEMENT (pas
    seulement pour un groupage déclaré manuellement) dès qu'un caisson
    existe dans le système — exigence explicite de Steve (03/10) :
    'l'algorithme doit être en mesure de conseiller le client [...] en
    fonction de son système et pas du mien'."""

    def test_every_non_sub_speaker_gets_a_precise_level_without_any_declaration(self) -> None:
        speakers = [
            Speaker("Façade Gauche", Role.FRONT_LEFT, freq_min_hz=45),
            Speaker("Surround Gauche", Role.SURROUND_LEFT, freq_min_hz=80),
            Speaker("Caisson", Role.LFE, freq_min_hz=20),
        ]
        measurements = [
            SpeakerMeasurement(speakers[0], [MeasurementPoint(80, 0.0)]),
            SpeakerMeasurement(speakers[1], [MeasurementPoint(80, -3.0)]),
            SpeakerMeasurement(speakers[2], [MeasurementPoint(80, -5.0)]),
        ]
        report = run_diagnostic(
            speakers=speakers,
            measurements=measurements,
            service_level=ServiceLevel.ESSENTIEL,
            # Aucun support_group_assignments fourni : doit être déduit.
        )
        precise_recs = {
            r.target: r.precise_value_db
            for r in report.recommendations
            if r.precise_value_db is not None
        }
        self.assertEqual(len(precise_recs), 2)
        self.assertEqual(precise_recs["Caisson -> Façade Gauche"], -5.0)
        self.assertEqual(precise_recs["Caisson -> Surround Gauche"], -2.0)

    def test_declared_custom_grouping_is_not_duplicated_by_auto_deduction(self) -> None:
        speakers = [
            Speaker("Surround Right", Role.SURROUND_RIGHT, freq_min_hz=53),
            Speaker("Surround Back Right", Role.SURROUND_BACK_RIGHT, freq_min_hz=53),
            Speaker("Caisson", Role.LFE, freq_min_hz=20),
        ]
        measurements = [
            SpeakerMeasurement(speakers[0], [MeasurementPoint(80, 0.0)]),
            SpeakerMeasurement(speakers[1], [MeasurementPoint(80, -7.0)]),
            SpeakerMeasurement(speakers[2], [MeasurementPoint(80, -2.0)]),
        ]
        report = run_diagnostic(
            speakers=speakers,
            measurements=measurements,
            service_level=ServiceLevel.ESSENTIEL,
            support_group_assignments=[("Surround Back Right", "Surround Right", 80.0)],
        )
        precise_recs = [r for r in report.recommendations if r.precise_value_db is not None]
        main_names = [r.target.split(" -> ")[1] for r in precise_recs]
        # "Surround Right" ne doit apparaître qu'UNE fois comme cible
        # principale (le groupage déclaré), pas une seconde fois via la
        # déduction automatique caisson -> Surround Right.
        self.assertEqual(main_names.count("Surround Right"), 1)
        # Le caisson doit quand même supporter automatiquement l'autre
        # enceinte non couverte par la déclaration (Surround Back Right).
        self.assertIn("Surround Back Right", main_names)


if __name__ == "__main__":
    unittest.main()
