from nicegui import ui
from app.models.planet import Planet


def planet_card(planet: Planet) -> None:
    with ui.card().classes(
        "w-64 cursor-pointer hover:shadow-2xl transition-shadow duration-200 overflow-hidden"
    ).style(f"border-top: 4px solid {planet.color_hex}"):
        ui.image(planet.image_url).classes("w-full h-40 object-cover")
        with ui.card_section().classes("pb-1"):
            ui.label(planet.name).classes("text-xl font-bold")
        with ui.card_section().classes("pt-1 text-sm text-gray-600 space-y-1"):
            mass_str = f"{planet.mass:g} Mj" if planet.mass is not None else "N/A"
            ui.label(f"Mass: {mass_str}")
            temp_str = f"{planet.temperature:g} K" if planet.temperature is not None else "N/A"
            ui.label(f"Temp: {temp_str}")
            dist_str = f"{planet.distance_light_year:g} ly" if planet.distance_light_year is not None else "N/A"
            ui.label(f"Distance: {dist_str}")
        with ui.card_actions().classes("justify-end"):
            ui.button(
                "Learn more",
                on_click=lambda p=planet: ui.navigate.to(f"/overview?id={p.id}"),
            ).props("flat color=indigo no-caps")
