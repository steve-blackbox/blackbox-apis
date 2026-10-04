"""
Tests unitaires du module de lecture de courbes depuis une capture d'écran
(`image_reader.py`). Utilise des images synthétiques construites en mémoire
avec Pillow (pas de vraie capture Dirac dans le dépôt — données client hors
dépôt) pour couvrir deux bugs réels trouvés et corrigés en extrayant les 8
vraies courbes de Steve (voir la docstring d'en-tête de `image_reader.py`
pour le détail) :
  1. Un label de texte épais de couleur proche de la courbe cible ne doit
     pas fausser le centre calculé (régression du bug "centre min/max
     global").
  2. Une ligne de grille de couleur stable mais proche par coïncidence de
     la couleur de courbe doit être exclue explicitement.

Lancer depuis le dossier PROJETS_FUTURS_calibrage_audio :
    python3 -m unittest discover -s tests -t .
"""

from __future__ import annotations

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PIL import Image

from image_reader import (
    AxisCalibration,
    UI_GRIDLINE_RGB,
    UI_RANGE_INDICATOR_RGB,
    detect_curve_color,
    detect_horizontal_gridlines,
    extract_curve_points,
    validate_calibration_against_gridlines,
)

BACKGROUND_RGB = (20, 24, 34)
CURVE_RGB = (200, 50, 50)

# Calibration simple : image 200x150, axe X log de 10 Hz à 1000 Hz sur
# toute la largeur, axe Y linéaire de +20 dB à -30 dB sur toute la hauteur.
SIMPLE_CALIBRATION = AxisCalibration(
    x_pixel_a=0.0, x_freq_hz_a=10.0,
    x_pixel_b=199.0, x_freq_hz_b=1000.0,
    y_pixel_a=0.0, y_db_a=20.0,
    y_pixel_b=149.0, y_db_b=-30.0,
)


def _blank_image(width: int = 200, height: int = 150) -> Image.Image:
    return Image.new("RGB", (width, height), BACKGROUND_RGB)


def _draw_diagonal_line(img: Image.Image, y_left: int, y_right: int, rgb) -> None:
    """Trait diagonal simple d'une colonne à l'autre, 1px d'épaisseur."""
    width, _ = img.size
    px = img.load()
    for x in range(width):
        t = x / (width - 1)
        y = round(y_left + t * (y_right - y_left))
        px[x, y] = rgb


class ExtractCurvePointsTests(unittest.TestCase):
    def test_simple_diagonal_line_extracted_without_noise(self):
        """Cas nominal : une ligne propre sans parasite doit être retrouvée
        fidèlement, sans trou significatif."""
        img = _blank_image()
        _draw_diagonal_line(img, y_left=100, y_right=50, rgb=CURVE_RGB)
        path = "/tmp/test_image_reader_simple.png"
        img.save(path)

        points = extract_curve_points(path, SIMPLE_CALIBRATION, CURVE_RGB, color_tolerance=20)

        self.assertGreater(len(points), 90)  # ~100 colonnes scannées (step=2 par défaut sur 200px)
        first, last = points[0], points[-1]
        self.assertAlmostEqual(first.freq_hz, 10.0, delta=1.0)
        self.assertAlmostEqual(last.freq_hz, 1000.0, delta=20.0)
        # y=100 -> db = 20 + (100/149)*(-50) = -13.6 ; y=50 -> db = 20 + (50/149)*(-50) = +3.2
        self.assertAlmostEqual(first.spl_db, -13.6, delta=1.0)
        self.assertAlmostEqual(last.spl_db, 3.2, delta=1.0)
        os.remove(path)

    def test_thick_label_does_not_distort_curve(self):
        """Régression du bug réel trouvé sur 'Surround Back Left' : un label
        de texte épais, de couleur proche de la courbe, placé en haut à
        gauche (loin de la vraie position de la courbe à ces colonnes), ne
        doit PAS faire dévier le résultat vers le label."""
        img = _blank_image()
        # vraie courbe : diagonale basse (y grand = dB bas), jamais proche du label
        _draw_diagonal_line(img, y_left=120, y_right=90, rgb=CURVE_RGB)
        px = img.load()
        # label épais (comme "+2,8 dB") en haut à gauche, couleur très proche
        # de la courbe (distance < color_tolerance), bloc de 15px de haut
        label_rgb = (205, 53, 53)
        for x in range(5, 35):
            for y in range(5, 20):
                px[x, y] = label_rgb
        path = "/tmp/test_image_reader_label.png"
        img.save(path)

        points = extract_curve_points(path, SIMPLE_CALIBRATION, CURVE_RGB, color_tolerance=20)

        # Les tout premiers points (sous le label, x=5..34) doivent rester
        # proches de la VRAIE courbe (y~118-120, db très négatif), pas du
        # label (y~5-20, db très positif ~+18 à +20 dB).
        early_points = [p for p in points if p.freq_hz <= SIMPLE_CALIBRATION.pixel_to_freq(34)]
        self.assertTrue(early_points, "aucun point extrait sous la zone du label")
        for p in early_points:
            self.assertLess(
                p.spl_db, 0.0,
                f"point à {p.freq_hz}Hz = {p.spl_db}dB semble avoir suivi le label, pas la courbe",
            )
        os.remove(path)

    def test_gridline_color_excluded_even_if_close_to_target(self):
        """Régression du bug réel trouvé sur 'Surround Right' : une ligne de
        grille de couleur UI_GRIDLINE_RGB, à une distance proche de la
        tolérance d'une couleur de courbe donnée, ne doit pas être prise
        pour la courbe mesurée (sinon extraction plate fausse)."""
        # couleur de courbe choisie à une distance d'environ 59.6 de
        # UI_GRIDLINE_RGB=(62,68,83), comme le cas réel rencontré.
        target_rgb = (41, 54, 137)
        img = _blank_image()
        # ligne de grille HORIZONTALE sur toute la largeur, à y=10 (jamais
        # la position de la vraie courbe tracée plus bas)
        px = img.load()
        width, _ = img.size
        for x in range(width):
            px[x, 10] = UI_GRIDLINE_RGB
        _draw_diagonal_line(img, y_left=120, y_right=80, rgb=target_rgb)
        path = "/tmp/test_image_reader_gridline.png"
        img.save(path)

        points = extract_curve_points(path, SIMPLE_CALIBRATION, target_rgb, color_tolerance=60)

        self.assertTrue(points, "aucun point extrait")
        # Aucun point ne doit être resté bloqué sur la grille (y=10 -> très
        # haut en dB, pixel_to_db(10) ~= +16.6 dB).
        stuck_on_grid = [p for p in points if p.spl_db > 10.0]
        self.assertEqual(
            stuck_on_grid, [],
            f"{len(stuck_on_grid)} points semblent être restés sur la ligne de grille",
        )
        os.remove(path)

    def test_min_saturation_filters_desaturated_interface_pixels(self):
        """Un pixel faiblement saturé (comme un dégradé d'interface) doit
        pouvoir être écarté explicitement via `min_saturation`, même s'il
        matche `target_rgb` en distance de couleur brute."""
        target_rgb = (41, 54, 137)
        desaturated_rgb = (70, 78, 137)  # saturation ~0.49, proche de target_rgb
        img = _blank_image()
        px = img.load()
        width, _ = img.size
        for x in range(width):
            px[x, 30] = desaturated_rgb
        _draw_diagonal_line(img, y_left=120, y_right=80, rgb=target_rgb)
        path = "/tmp/test_image_reader_saturation.png"
        img.save(path)

        points = extract_curve_points(
            path, SIMPLE_CALIBRATION, target_rgb, color_tolerance=40, min_saturation=0.55,
        )

        stuck_on_band = [p for p in points if abs(p.spl_db - SIMPLE_CALIBRATION.pixel_to_db(30)) < 0.5]
        self.assertEqual(
            stuck_on_band, [],
            "des points semblent avoir suivi la bande désaturée plutôt que la courbe",
        )
        os.remove(path)


class DetectCurveColorTests(unittest.TestCase):
    def test_finds_saturated_curve_color_ignoring_background_and_ui(self):
        img = _blank_image()
        _draw_diagonal_line(img, y_left=100, y_right=50, rgb=CURVE_RGB)
        px = img.load()
        # bandeau UI_RANGE_INDICATOR_RGB présent ailleurs dans la zone
        for x in range(0, 20):
            px[x, 140] = UI_RANGE_INDICATOR_RGB
        path = "/tmp/test_image_reader_detect_color.png"
        img.save(path)

        color = detect_curve_color(path, 0, 199, 0, 149)

        self.assertEqual(color, CURVE_RGB)
        os.remove(path)


# Positions pixel des 6 graduations dB (+20 à -30, pas de 10 dB) selon
# SIMPLE_CALIBRATION, arrondies à l'entier le plus proche (149px / 50dB).
SIMPLE_GRIDLINE_ROWS_PX = [0, 30, 60, 89, 119, 149]


def _draw_horizontal_gridlines(img: Image.Image, rows_px: list[int], rgb) -> None:
    width, height = img.size
    px = img.load()
    for y in rows_px:
        if 0 <= y < height:
            for x in range(width):
                px[x, y] = rgb


class GridlineValidationTests(unittest.TestCase):
    """Garde-fou de sécurité (04/10) : une `AxisCalibration` figée pour une
    résolution/zoom donnés ne doit jamais être appliquée silencieusement à
    une capture différente (risque de Hz/dB faux -> recommandation de
    réglage dangereuse). Ces tests couvrent `detect_horizontal_gridlines`
    et `validate_calibration_against_gridlines` sur des images
    synthétiques avec des lignes de grille à des positions connues."""

    def test_detect_horizontal_gridlines_finds_known_rows(self):
        img = _blank_image()
        _draw_horizontal_gridlines(img, SIMPLE_GRIDLINE_ROWS_PX, UI_GRIDLINE_RGB)
        path = "/tmp/test_image_reader_gridlines_detect.png"
        img.save(path)

        rows = detect_horizontal_gridlines(path, 0, 199, 0, 149)

        self.assertEqual(len(rows), len(SIMPLE_GRIDLINE_ROWS_PX))
        for expected, found in zip(SIMPLE_GRIDLINE_ROWS_PX, rows):
            self.assertAlmostEqual(expected, found, delta=1.0)
        os.remove(path)

    def test_matching_calibration_raises_no_warning(self):
        """Cas nominal : la calibration correspond réellement à l'image
        (comme sur les vraies captures de Steve) -> aucune alerte."""
        img = _blank_image()
        _draw_horizontal_gridlines(img, SIMPLE_GRIDLINE_ROWS_PX, UI_GRIDLINE_RGB)
        path = "/tmp/test_image_reader_gridlines_ok.png"
        img.save(path)

        warnings = validate_calibration_against_gridlines(SIMPLE_CALIBRATION, path, 0, 199, 0, 149)

        self.assertEqual(warnings, [])
        os.remove(path)

    def test_mismatched_calibration_raises_warning(self):
        """Cas dangereux à détecter : une capture d'une autre résolution/
        zoom utilisée avec une calibration figée pour une AUTRE capture —
        les lignes de grille réelles ne tombent alors plus sur des
        multiples de 10 dB une fois converties, et une alerte doit être
        levée plutôt que de laisser un diagnostic silencieusement faux."""
        img = _blank_image()
        _draw_horizontal_gridlines(img, SIMPLE_GRIDLINE_ROWS_PX, UI_GRIDLINE_RGB)
        path = "/tmp/test_image_reader_gridlines_mismatch.png"
        img.save(path)

        # Calibration incompatible : mêmes pixels de référence, mais une
        # plage dB différente (+20 à -20 au lieu de +20 à -30) — simule
        # une capture avec un zoom/plage différents de ceux calibrés.
        wrong_calibration = AxisCalibration(
            x_pixel_a=0.0, x_freq_hz_a=10.0,
            x_pixel_b=199.0, x_freq_hz_b=1000.0,
            y_pixel_a=0.0, y_db_a=20.0,
            y_pixel_b=149.0, y_db_b=-20.0,
        )

        warnings = validate_calibration_against_gridlines(wrong_calibration, path, 0, 199, 0, 149)

        self.assertTrue(warnings, "une calibration incompatible aurait dû lever au moins une alerte")
        os.remove(path)

    def test_no_gridlines_detected_raises_explicit_warning(self):
        """Zone de tracé ou couleur de grille mal renseignées : le message
        doit être explicite plutôt qu'un résultat vide silencieux."""
        img = _blank_image()  # aucune ligne de grille tracée
        path = "/tmp/test_image_reader_gridlines_none.png"
        img.save(path)

        warnings = validate_calibration_against_gridlines(SIMPLE_CALIBRATION, path, 0, 199, 0, 149)

        self.assertEqual(len(warnings), 1)
        self.assertIn("Aucune ligne de grille", warnings[0])
        os.remove(path)


if __name__ == "__main__":
    unittest.main()
