"""
Tests unitaires du ré-échantillonnage linéaire (`curve_resampling.py`).

Lancer depuis le dossier PROJETS_FUTURS_calibrage_audio :
    python3 -m unittest discover -s tests -t .
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from curve_resampling import resample_linear
from models import MeasurementPoint


class ResampleLinearTests(unittest.TestCase):
    def test_exact_grid_point_matches_input(self):
        points = [
            MeasurementPoint(10.0, 0.0),
            MeasurementPoint(20.0, 10.0),
            MeasurementPoint(30.0, 0.0),
        ]
        out = resample_linear(points, step_hz=10.0, f_min=10.0, f_max=30.0)
        by_freq = {p.freq_hz: p.spl_db for p in out}
        self.assertAlmostEqual(by_freq[10.0], 0.0)
        self.assertAlmostEqual(by_freq[20.0], 10.0)
        self.assertAlmostEqual(by_freq[30.0], 0.0)

    def test_midpoint_is_linearly_interpolated(self):
        points = [MeasurementPoint(0.0, 0.0), MeasurementPoint(10.0, 10.0)]
        out = resample_linear(points, step_hz=5.0, f_min=0.0, f_max=10.0)
        by_freq = {p.freq_hz: p.spl_db for p in out}
        self.assertAlmostEqual(by_freq[5.0], 5.0)

    def test_targets_outside_measured_range_are_skipped(self):
        """Pas d'extrapolation : une fréquence hors de la plage mesurée ne
        doit produire aucun point devine."""
        points = [MeasurementPoint(50.0, 0.0), MeasurementPoint(100.0, 5.0)]
        out = resample_linear(points, step_hz=10.0, f_min=0.0, f_max=150.0)
        freqs = [p.freq_hz for p in out]
        self.assertTrue(all(50.0 <= f <= 100.0 for f in freqs))
        self.assertNotIn(0.0, freqs)
        self.assertNotIn(150.0, freqs)

    def test_input_order_does_not_matter(self):
        """Les points d'entrée non triés doivent donner le même résultat
        qu'une entrée déjà triée."""
        sorted_points = [MeasurementPoint(0.0, 0.0), MeasurementPoint(10.0, 20.0)]
        shuffled_points = [MeasurementPoint(10.0, 20.0), MeasurementPoint(0.0, 0.0)]
        out_sorted = resample_linear(sorted_points, step_hz=5.0, f_min=0.0, f_max=10.0)
        out_shuffled = resample_linear(shuffled_points, step_hz=5.0, f_min=0.0, f_max=10.0)
        self.assertEqual(
            [(p.freq_hz, p.spl_db) for p in out_sorted],
            [(p.freq_hz, p.spl_db) for p in out_shuffled],
        )

    def test_output_sorted_by_increasing_frequency(self):
        points = [MeasurementPoint(f, 0.0) for f in (30.0, 10.0, 20.0)]
        out = resample_linear(points, step_hz=5.0, f_min=10.0, f_max=30.0)
        freqs = [p.freq_hz for p in out]
        self.assertEqual(freqs, sorted(freqs))


if __name__ == "__main__":
    unittest.main()
