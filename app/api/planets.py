from fastapi import APIRouter, HTTPException
from app.services.planet_service import load_planets, get_planet_by_id

router = APIRouter(prefix="/api/planets", tags=["planets"])


@router.get("/")
async def list_planets():
    return load_planets()


@router.get("/{planet_id}")
async def get_planet(planet_id: str):
    planet = get_planet_by_id(planet_id)
    if not planet:
        raise HTTPException(status_code=404, detail="Planet not found")
    return planet
