from typing import AsyncIterator
from openai import AsyncOpenAI
from app.config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, OPENAI_TEMPERATURE
from app.models.planet import Planet

client = AsyncOpenAI(api_key=OPENAI_API_KEY)

_DESCRIPTION_CACHE: dict[str, str] = {}
_COMPARISON_CACHE: dict[str, str] = {}

_SYSTEM_PROMPT = (
    "You are an enthusiastic astronomy teacher explaining planets and exoplanets to "
    "curious students aged 12-16. Use simple language, vivid comparisons, and exciting "
    "facts. Always relate things to everyday life when possible. Keep responses to 3-4 "
    "paragraphs."
)


def _fmt(value: float | None, unit: str) -> str:
    if value is None:
        return "unknown"
    return f"{value:g} {unit}"


def clear_description_cache() -> None:
    _DESCRIPTION_CACHE.clear()
    _COMPARISON_CACHE.clear()


async def describe_planet(planet: Planet) -> AsyncIterator[str]:
    if planet.id in _DESCRIPTION_CACHE:
        yield _DESCRIPTION_CACHE[planet.id]
        return

    user_prompt = f"""Tell me about the planet {planet.name}.
Key facts to work with:
- Mass: {_fmt(planet.mass, 'Jupiter masses')}
- Radius: {_fmt(planet.radius, 'Earth radii')}
- Orbital period: {_fmt(planet.period, 'days')}
- Semi-major axis: {_fmt(planet.semi_major_axis, 'AU')}
- Temperature: {_fmt(planet.temperature, 'K')}
- Distance from Earth: {_fmt(planet.distance_light_year, 'light years')}
- Host star mass: {_fmt(planet.host_star_mass, 'solar masses')}
- Host star temperature: {_fmt(planet.host_star_temperature, 'K')}

Make it exciting and educational for a student who has never studied planets before."""

    stream = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
        max_tokens=OPENAI_MAX_TOKENS,
        temperature=OPENAI_TEMPERATURE,
    )
    chunks: list[str] = []
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            chunks.append(delta)
            yield delta

    _DESCRIPTION_CACHE[planet.id] = "".join(chunks)


async def compare_planets(planets: list[Planet]) -> AsyncIterator[str]:
    cache_key = "+".join(sorted(p.id for p in planets))

    if cache_key in _COMPARISON_CACHE:
        yield _COMPARISON_CACHE[cache_key]
        return

    planet_summaries = "\n\n".join(
        f"{p.name}:\n"
        f"  Mass: {_fmt(p.mass, 'Jupiter masses')}\n"
        f"  Radius: {_fmt(p.radius, 'Earth radii')}\n"
        f"  Orbital period: {_fmt(p.period, 'days')}\n"
        f"  Semi-major axis: {_fmt(p.semi_major_axis, 'AU')}\n"
        f"  Temperature: {_fmt(p.temperature, 'K')}\n"
        f"  Distance: {_fmt(p.distance_light_year, 'light years')}\n"
        f"  Host star mass: {_fmt(p.host_star_mass, 'solar masses')}\n"
        f"  Host star temperature: {_fmt(p.host_star_temperature, 'K')}"
        for p in planets
    )

    names = ", ".join(p.name for p in planets)
    user_prompt = f"""Compare and contrast these planets: {names}.

Here are their key characteristics:

{planet_summaries}

Highlight the most interesting similarities and differences between them. \
What makes each one unique? Make it educational and easy to understand."""

    stream = await client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        stream=True,
        max_tokens=OPENAI_MAX_TOKENS,
        temperature=OPENAI_TEMPERATURE,
    )
    chunks: list[str] = []
    async for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            chunks.append(delta)
            yield delta

    _COMPARISON_CACHE[cache_key] = "".join(chunks)
