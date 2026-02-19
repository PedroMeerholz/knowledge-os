from pydantic import BaseModel


class Planet(BaseModel):
    id: str
    name: str
    mass: float | None = None
    radius: float | None = None
    period: float | None = None
    semi_major_axis: float | None = None
    temperature: float | None = None
    distance_light_year: float | None = None
    host_star_mass: float | None = None
    host_star_temperature: float | None = None
    image_url: str
    color_hex: str


class SimilarityResult(BaseModel):
    planet: Planet
    score: float
