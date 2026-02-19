import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics.pairwise import cosine_similarity
from app.services.planet_service import load_planets
from app.models.planet import Planet, SimilarityResult

FEATURE_KEYS = [
    "mass",
    "radius",
    "period",
    "semi_major_axis",
    "temperature",
    "distance_light_year",
    "host_star_mass",
    "host_star_temperature",
]


def _build_matrix() -> tuple[list[Planet], np.ndarray]:
    planets = load_planets()
    raw = np.array(
        [
            [getattr(p, k) if getattr(p, k) is not None else float("nan") for k in FEATURE_KEYS]
            for p in planets
        ],
        dtype=float,
    )
    # Replace NaN with column median so nulls don't dominate similarity
    col_medians = np.nanmedian(raw, axis=0)
    for col_idx in range(raw.shape[1]):
        mask = np.isnan(raw[:, col_idx])
        raw[mask, col_idx] = col_medians[col_idx]
    scaler = MinMaxScaler()
    normalized = scaler.fit_transform(raw)
    return planets, normalized


def get_similar_planets(target_id: str, top_n: int = 3) -> list[SimilarityResult]:
    planets, matrix = _build_matrix()
    ids = [p.id for p in planets]
    target_idx = ids.index(target_id)
    target_vec = matrix[target_idx].reshape(1, -1)
    scores = cosine_similarity(target_vec, matrix)[0]
    ranked = sorted(
        [(planets[i], float(scores[i])) for i in range(len(planets)) if i != target_idx],
        key=lambda x: x[1],
        reverse=True,
    )
    return [SimilarityResult(planet=p, score=round(s, 4)) for p, s in ranked[:top_n]]
