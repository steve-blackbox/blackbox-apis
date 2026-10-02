"""
Tests unitaires de specs_database.py — la base PERSISTANTE de fiches
techniques constructeur qui s'enrichit client après client (demande de
Steve, voir le docstring d'en-tête de specs_database.py).

Important : chaque test utilise un fichier JSON TEMPORAIRE (tempfile),
jamais le vrai fichier data/manufacturer_specs_db.json du projet — pour
ne jamais polluer la vraie base avec des données de test.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import specs_database as db
from models import ManufacturerSpecSheet


class TestSpecsDatabase(unittest.TestCase):
    def setUp(self) -> None:
        fd, self.tmp_path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        os.remove(self.tmp_path)  # load_db doit le recréer lui-même (bootstrap)

    def tearDown(self) -> None:
        if os.path.exists(self.tmp_path):
            os.remove(self.tmp_path)

    def test_first_load_bootstraps_from_knowledge_base(self) -> None:
        specs = db.load_db(self.tmp_path)
        self.assertGreaterEqual(len(specs), 5)
        self.assertTrue(os.path.exists(self.tmp_path))
        brands = {s.brand for s in specs}
        self.assertIn("Elipson", brands)

    def test_find_existing_spec_case_insensitive(self) -> None:
        db.load_db(self.tmp_path)  # déclenche le bootstrap
        found = db.find_spec("elipson", "legacy 3220", self.tmp_path)
        self.assertIsNotNone(found)
        self.assertEqual(found.brand, "Elipson")

    def test_find_unknown_spec_returns_none(self) -> None:
        db.load_db(self.tmp_path)
        self.assertIsNone(db.find_spec("MarqueInconnue", "ModeleX", self.tmp_path))

    def test_add_spec_persists_across_reload(self) -> None:
        db.load_db(self.tmp_path)
        new_spec = ManufacturerSpecSheet(
            brand="TestBrand",
            model="TestModel",
            role_in_system="Test",
            source_url="https://example.com",
            specs={"Puissance": "100W"},
            verification="Test unitaire",
        )
        added = db.add_spec(new_spec, self.tmp_path)
        self.assertTrue(added)

        reloaded = db.load_db(self.tmp_path)
        self.assertTrue(any(s.brand == "TestBrand" for s in reloaded))

    def test_add_spec_does_not_overwrite_existing(self) -> None:
        db.load_db(self.tmp_path)
        spec = ManufacturerSpecSheet(
            brand="TestBrand", model="TestModel", role_in_system="",
            source_url="", specs={}, verification="",
        )
        self.assertTrue(db.add_spec(spec, self.tmp_path))
        self.assertFalse(db.add_spec(spec, self.tmp_path))  # 2e ajout refusé

    def test_update_spec_replaces_existing(self) -> None:
        db.load_db(self.tmp_path)
        spec = ManufacturerSpecSheet(
            brand="TestBrand", model="TestModel", role_in_system="v1",
            source_url="", specs={}, verification="",
        )
        db.add_spec(spec, self.tmp_path)
        updated_spec = ManufacturerSpecSheet(
            brand="TestBrand", model="TestModel", role_in_system="v2",
            source_url="", specs={}, verification="",
        )
        self.assertTrue(db.update_spec(updated_spec, self.tmp_path))
        found = db.find_spec("TestBrand", "TestModel", self.tmp_path)
        self.assertEqual(found.role_in_system, "v2")

    def test_update_spec_on_unknown_model_returns_false(self) -> None:
        db.load_db(self.tmp_path)
        spec = ManufacturerSpecSheet(
            brand="Inconnu", model="Inconnu", role_in_system="",
            source_url="", specs={}, verification="",
        )
        self.assertFalse(db.update_spec(spec, self.tmp_path))


if __name__ == "__main__":
    unittest.main()
