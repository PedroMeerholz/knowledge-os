from nicegui import ui
from app.services.planet_service import load_planets
from app.services.similarity_service import get_similar_planets
from app.ui.layout import create_layout


def similarity_page() -> None:
    create_layout("/similarity")
    planets = load_planets()

    with ui.column().classes("w-full max-w-5xl mx-auto p-6 gap-6"):
        ui.label("Planet Similarity Explorer").classes("text-3xl font-bold text-indigo-900 mb-1")
        ui.label(
            "Select a planet to discover which other planets are most similar based on "
            "physical characteristics like mass, radius, temperature, and orbital period."
        ).classes("text-gray-600 mb-4")

        planet_options = {p.name: p.id for p in planets}
        selected_name = ui.select(
            list(planet_options.keys()),
            value=planets[0].name,
            label="Choose a planet",
        ).classes("w-80").props("use-input fill-input hide-selected input-debounce=300")

        top_n_select = ui.select(
            {10: "Top 10", 25: "Top 25", 50: "Top 50"},
            value=10,
            label="Results to show",
        ).classes("w-40")

        results_container = ui.column().classes("w-full gap-4 mt-4")

        def show_similarity() -> None:
            results_container.clear()
            pid = planet_options.get(selected_name.value)
            if pid is None:
                return
            source = next((p for p in planets if p.id == pid), None)
            if source is None:
                return

            n = top_n_select.value or 10
            results = get_similar_planets(pid, top_n=n)

            with results_container:
                ui.label(
                    f"Planets most similar to {source.name}"
                ).classes("text-xl font-semibold text-indigo-800")
                ui.separator()

                for result in results:
                    p = result.planet
                    pct = int(result.score * 100)
                    with ui.card().classes("w-full p-4"):
                        with ui.row().classes("items-center gap-4 w-full"):
                            ui.image(p.image_url).classes("w-20 h-16 object-cover rounded")
                            with ui.column().classes("flex-1 gap-1"):
                                with ui.row().classes("items-center justify-between w-full"):
                                    ui.label(p.name).classes("text-lg font-bold")
                                    ui.badge(
                                        f"{pct}% similar",
                                        color="green" if pct >= 80 else "orange" if pct >= 50 else "red",
                                    )
                                ui.linear_progress(value=result.score).classes("w-full")
                                mass_str = f"{p.mass:g} Mj" if p.mass is not None else "N/A"
                                temp_str = f"{p.temperature:g} K" if p.temperature is not None else "N/A"
                                dist_str = f"{p.distance_light_year:g} ly" if p.distance_light_year is not None else "N/A"
                                ui.label(
                                    f"Mass: {mass_str} | Temp: {temp_str} | "
                                    f"Dist: {dist_str}"
                                ).classes("text-sm text-gray-500")
                            ui.button(
                                "View",
                                on_click=lambda pid=p.id: ui.navigate.to(
                                    f"/overview?id={pid}"
                                ),
                            ).props("flat color=indigo no-caps")

        selected_name.on("update:model-value", lambda _: show_similarity())
        top_n_select.on("update:model-value", lambda _: show_similarity())
        show_similarity()
