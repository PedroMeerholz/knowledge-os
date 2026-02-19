import json
import re
from app.config import (
    PLANETS_FILE,
    KNOWN_PLANET_IMAGES,
    PLACEHOLDER_IMAGE,
    get_color_for_temperature,
)
from app.models.planet import Planet

_CACHE: list[Planet] | None = None


def _slugify(name: str) -> str:
    """Convert a planet name into a URL-safe id."""
    slug = name.lower().strip()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    return slug.strip("-")


def load_planets() -> list[Planet]:
    global _CACHE
    if _CACHE is None:
        raw = json.loads(PLANETS_FILE.read_text(encoding="utf-8"))
        planets: list[Planet] = []
        for entry in raw:
            name = entry["name"]
            planets.append(
                Planet(
                    id=_slugify(name),
                    name=name,
                    mass=entry.get("mass"),
                    radius=entry.get("radius"),
                    period=entry.get("period"),
                    semi_major_axis=entry.get("semi_major_axis"),
                    temperature=entry.get("temperature"),
                    distance_light_year=entry.get("distance_light_year"),
                    host_star_mass=entry.get("host_star_mass"),
                    host_star_temperature=entry.get("host_star_temperature"),
                    image_url=KNOWN_PLANET_IMAGES.get(name, PLACEHOLDER_IMAGE),
                    color_hex=get_color_for_temperature(entry.get("temperature")),
                )
            )
        _CACHE = planets
    return _CACHE


def get_planet_by_id(planet_id: str) -> Planet | None:
    return next((p for p in load_planets() if p.id == planet_id), None)


def search_planets(
    query: str = "",
    page: int = 1,
    per_page: int = 24,
) -> tuple[list[Planet], int]:
    """Return a page of planets filtered by name query.

    Returns (page_results, total_matching).
    """
    planets = load_planets()
    if query:
        q = query.lower()
        planets = [p for p in planets if q in p.name.lower()]
    total = len(planets)
    start = (page - 1) * per_page
    return planets[start : start + per_page], total
