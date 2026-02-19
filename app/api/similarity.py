from fastapi import APIRouter, HTTPException
from app.services.similarity_service import get_similar_planets
from app.services.planet_service import load_planets

router = APIRouter(prefix="/api/similarity", tags=["similarity"])


@router.get("/{planet_id}")
async def planet_similarity(planet_id: str, top_n: int = 3):
    valid_ids = [p.id for p in load_planets()]
    if planet_id not in valid_ids:
        raise HTTPException(status_code=404, detail="Planet not found")
    return get_similar_planets(planet_id, top_n)
