from nicegui import ui
from app.services.planet_service import get_planet_by_id, load_planets
from app.services.llm_service import describe_planet
from app.services.similarity_service import get_similar_planets
from app.ui.layout import create_layout


def _fmt(value: float | None, unit: str) -> str:
    if value is None:
        return "N/A"
    return f"{value:g} {unit}"


def overview_page() -> None:
    create_layout("/overview")

    planet_id = ui.context.client.request.query_params.get("id", "earth")
    planet = get_planet_by_id(planet_id)

    if planet is None:
        planet = load_planets()[0]

    with ui.column().classes("w-full max-w-4xl mx-auto p-6 gap-6"):
        # Header row: image + quick facts
        with ui.row().classes("gap-6 items-start flex-wrap"):
            ui.image(planet.image_url).classes("w-56 h-48 object-cover rounded-xl shadow")
            with ui.column().classes("gap-2"):
                ui.label(planet.name).classes("text-4xl font-bold text-indigo-900")
                ui.separator()
                ui.label(f"Mass: {_fmt(planet.mass, 'Jupiter masses')}").classes("text-gray-700")
                ui.label(f"Radius: {_fmt(planet.radius, 'Earth radii')}").classes("text-gray-700")
                ui.label(f"Orbital Period: {_fmt(planet.period, 'days')}").classes("text-gray-700")
                ui.label(f"Semi-major Axis: {_fmt(planet.semi_major_axis, 'AU')}").classes(
                    "text-gray-700"
                )
                ui.label(f"Temperature: {_fmt(planet.temperature, 'K')}").classes("text-gray-700")
                ui.label(f"Distance: {_fmt(planet.distance_light_year, 'light years')}").classes(
                    "text-gray-700"
                )
                ui.label(f"Host Star Mass: {_fmt(planet.host_star_mass, 'solar masses')}").classes(
                    "text-gray-700"
                )
                ui.label(f"Host Star Temp: {_fmt(planet.host_star_temperature, 'K')}").classes(
                    "text-gray-700"
                )

        # LLM description section
        ui.label("AI Description").classes("text-xl font-semibold text-indigo-800 mt-2")
        ui.separator()

        spinner = ui.spinner(size="lg").classes("mt-4")
        description_label = ui.label("").classes(
            "text-base leading-relaxed whitespace-pre-wrap text-gray-800"
        )

        async def load_description() -> None:
            spinner.visible = True
            description_label.set_text("")
            async for chunk in describe_planet(planet):
                description_label.set_text(description_label.text + chunk)
            spinner.visible = False

        ui.timer(0.05, load_description, once=True)

        # Similar planets section
        ui.label("Similar Planets").classes("text-xl font-semibold text-indigo-800 mt-6")
        ui.separator()
        try:
            similar = get_similar_planets(planet.id, top_n=5)
            with ui.row().classes("flex-wrap gap-2"):
                for result in similar:
                    pct = int(result.score * 100)
                    ui.button(
                        f"{result.planet.name} ({pct}%)",
                        on_click=lambda pid=result.planet.id: ui.navigate.to(
                            f"/overview?id={pid}"
                        ),
                    ).props("outline color=indigo no-caps").classes("text-sm")
        except ValueError:
            ui.label("No similarity data available.").classes("text-gray-400 italic")

        # Back to list
        ui.button(
            "Back to Planet List",
            icon="arrow_back",
            on_click=lambda: ui.navigate.to("/"),
        ).props("flat color=indigo no-caps").classes("mt-4")
