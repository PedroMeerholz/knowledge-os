import os
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"
PLANETS_FILE = DATA_DIR / "planets.json"

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_MAX_TOKENS = 600
OPENAI_TEMPERATURE = 0.7

PLANETS_PER_PAGE = 24

# Image URLs for known Solar System planets (Wikimedia Commons, public domain)
KNOWN_PLANET_IMAGES: dict[str, str] = {
    "Mercury": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4a/Mercury_in_true_color.jpg/800px-Mercury_in_true_color.jpg",
    "Venus": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/08/Venus_from_Mariner_10.jpg/800px-Venus_from_Mariner_10.jpg",
    "Earth": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/cb/The_Blue_Marble_%28remastered%29.jpg/800px-The_Blue_Marble_%28remastered%29.jpg",
    "Mars": "https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Mars_-_August_30_2021_-_Flipped.jpg/800px-Mars_-_August_30_2021_-_Flipped.jpg",
    "Jupiter": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2b/Jupiter_and_its_shrunken_Great_Red_Spot.jpg/800px-Jupiter_and_its_shrunken_Great_Red_Spot.jpg",
    "Saturn": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c7/Saturn_during_Equinox.jpg/800px-Saturn_during_Equinox.jpg",
    "Uranus": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/48/Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png/800px-Uranus_as_seen_by_NASA%27s_Voyager_2_%28remastered%29.png",
    "Neptune": "https://upload.wikimedia.org/wikipedia/commons/thumb/6/63/Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg/800px-Neptune_-_Voyager_2_%2829347980845%29_flatten_crop.jpg",
    "Pluto": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/ef/Pluto_in_True_Color_-_High-Res.jpg/800px-Pluto_in_True_Color_-_High-Res.jpg",
}

PLACEHOLDER_IMAGE = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/be/SolarSystem_OrdersOfMagnitude_Sun-Jupiter-Earth-Moon.jpg/800px-SolarSystem_OrdersOfMagnitude_Sun-Jupiter-Earth-Moon.jpg"


def get_color_for_temperature(temp: float | None) -> str:
    """Return a hex color based on planet temperature (Kelvin)."""
    if temp is None:
        return "#9E9E9E"  # grey for unknown
    if temp > 500:
        return "#E53935"  # red - hot
    if temp > 300:
        return "#FF9800"  # orange - warm
    if temp > 150:
        return "#29B6F6"  # blue - cool
    return "#3F51B5"  # deep blue - cold
