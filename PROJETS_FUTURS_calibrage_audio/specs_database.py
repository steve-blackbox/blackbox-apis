"""
specs_database.py — Base de données PERSISTANTE de fiches techniques
constructeur, qui s'enrichit client après client.

Contexte (demande de Steve) : "quand le client va nous lister son
matériel il faudra qu'on soit en mesure d'en connaître toutes les
caractéristiques. Au fur et à mesure des clients nous aurons une source
de data qui s'étoffera." Avant ce module, les 5 fiches déjà sourcées
(`knowledge_base.CITED_MANUFACTURER_SPECS`, section 15) étaient une
simple liste Python codée en dur, valable uniquement pour le matériel de
Steve — rien ne persistait d'un client à l'autre.

Principe : un fichier JSON (`specs_db/manufacturer_specs_db.json`) sert de
base vivante. Au premier appel, il est initialisé avec les fiches déjà
connues de `knowledge_base.py` (pour ne rien perdre de ce qui a déjà été
sourcé et vérifié). Ensuite, chaque nouvelle fiche trouvée pour un
nouveau client (marque/modèle absent de la base) peut y être ajoutée via
`add_spec()`, et sera disponible immédiatement pour tous les clients
suivants qui ont le même matériel — sans qu'il faille re-chercher la
fiche sur le site du fabricant à chaque fois.

Ce module ne fait AUCUNE recherche web lui-même : il se contente de
stocker/retrouver des `ManufacturerSpecSheet` déjà construites (par
exemple après une recherche faite via le navigateur intégré, comme pour
les 5 fiches d'origine — voir knowledge_base.py section 15).
"""

from __future__ import annotations

import json
import os
from dataclasses import asdict

import knowledge_base as kb
from models import ManufacturerSpecSheet

DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "specs_db", "manufacturer_specs_db.json")


def _spec_to_dict(spec: ManufacturerSpecSheet) -> dict:
    return asdict(spec)


def _spec_from_dict(data: dict) -> ManufacturerSpecSheet:
    return ManufacturerSpecSheet(
        brand=data["brand"],
        model=data["model"],
        role_in_system=data.get("role_in_system", ""),
        source_url=data.get("source_url", ""),
        specs=data.get("specs", {}),
        verification=data.get("verification", ""),
    )


def _bootstrap_specs() -> list[ManufacturerSpecSheet]:
    """Fiches de départ : celles déjà sourcées et vérifiées dans
    knowledge_base.py (section 15), pour ne rien perdre de ce qui existe
    déjà au moment de la création de ce module."""
    return list(kb.CITED_MANUFACTURER_SPECS)


def load_db(path: str = DEFAULT_DB_PATH) -> list[ManufacturerSpecSheet]:
    """Charge la base depuis le fichier JSON. Si le fichier n'existe pas
    encore (premier lancement), l'initialise avec les fiches déjà
    connues de knowledge_base.py et le sauvegarde immédiatement."""
    if not os.path.exists(path):
        specs = _bootstrap_specs()
        save_db(specs, path)
        return specs

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)
    return [_spec_from_dict(d) for d in raw]


def save_db(specs: list[ManufacturerSpecSheet], path: str = DEFAULT_DB_PATH) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump([_spec_to_dict(s) for s in specs], f, ensure_ascii=False, indent=2)


def find_spec(
    brand: str, model: str, path: str = DEFAULT_DB_PATH
) -> ManufacturerSpecSheet | None:
    """Recherche insensible à la casse. Retourne None si cette marque/
    modèle n'est encore dans la base d'AUCUN client précédent — ce n'est
    PAS une confirmation que le matériel n'existe pas, juste qu'il reste
    à chercher une première fois (voir add_spec)."""
    brand_norm = brand.strip().casefold()
    model_norm = model.strip().casefold()
    for spec in load_db(path):
        if spec.brand.casefold() == brand_norm and spec.model.casefold() == model_norm:
            return spec
    return None


def add_spec(spec: ManufacturerSpecSheet, path: str = DEFAULT_DB_PATH) -> bool:
    """Ajoute une nouvelle fiche à la base persistante, pour qu'elle soit
    disponible immédiatement pour tous les clients suivants ayant le
    même matériel. Retourne False sans rien écraser si une fiche pour
    cette marque/modèle existe déjà (mettre à jour une fiche existante
    doit être un choix explicite, pas un écrasement silencieux) —
    utiliser update_spec() pour ce cas."""
    specs = load_db(path)
    if find_spec(spec.brand, spec.model, path) is not None:
        return False
    specs.append(spec)
    save_db(specs, path)
    return True


def update_spec(spec: ManufacturerSpecSheet, path: str = DEFAULT_DB_PATH) -> bool:
    """Remplace une fiche existante (même marque/modèle) par une version
    mise à jour. Retourne False si aucune fiche existante ne correspond
    (utiliser add_spec() dans ce cas)."""
    specs = load_db(path)
    brand_norm = spec.brand.strip().casefold()
    model_norm = spec.model.strip().casefold()
    for i, existing in enumerate(specs):
        if existing.brand.casefold() == brand_norm and existing.model.casefold() == model_norm:
            specs[i] = spec
            save_db(specs, path)
            return True
    return False


def all_specs(path: str = DEFAULT_DB_PATH) -> list[ManufacturerSpecSheet]:
    return load_db(path)


def known_brands(path: str = DEFAULT_DB_PATH) -> list[str]:
    return sorted({s.brand for s in load_db(path)})
