from nicegui import ui
from app.config import PLANETS_PER_PAGE
from app.services.planet_service import search_planets
from app.ui.components.planet_card import planet_card
from app.ui.layout import create_layout


def home_page() -> None:
    create_layout("/")
    state = {"query": "", "page": 1}

    with ui.column().classes("w-full max-w-7xl mx-auto p-6"):
        ui.label("Explore the Universe").classes("text-3xl font-bold text-indigo-900 mb-2")
        ui.label(
            "Browse over 2,000 planets and exoplanets. "
            "Use the search bar to find a planet by name, then click 'Learn more' for details."
        ).classes("text-gray-600 mb-6")

        search_input = ui.input(
            placeholder="Search planets by name...",
        ).classes("w-full max-w-md mb-4").props("outlined dense clearable")

        cards_container = ui.row().classes("flex-wrap justify-start gap-6 w-full")
        pagination_container = ui.row().classes("justify-center items-center gap-4 mt-6 w-full")

        def refresh() -> None:
            planets, total = search_planets(state["query"], state["page"], PLANETS_PER_PAGE)
            total_pages = max(1, -(-total // PLANETS_PER_PAGE))  # ceil division

            cards_container.clear()
            with cards_container:
                if not planets:
                    ui.label("No planets found.").classes("text-gray-400 italic")
                else:
                    for planet in planets:
                        planet_card(planet)

            pagination_container.clear()
            with pagination_container:
                ui.button(
                    "Previous",
                    on_click=lambda: go_page(state["page"] - 1),
                ).props("flat color=indigo no-caps").set_enabled(state["page"] > 1)
                ui.label(f"Page {state['page']} of {total_pages} ({total} planets)").classes(
                    "text-gray-600"
                )
                ui.button(
                    "Next",
                    on_click=lambda: go_page(state["page"] + 1),
                ).props("flat color=indigo no-caps").set_enabled(state["page"] < total_pages)

        def on_search(_) -> None:
            state["query"] = search_input.value or ""
            state["page"] = 1
            refresh()

        def go_page(page: int) -> None:
            state["page"] = page
            refresh()

        search_input.on("update:model-value", on_search)
        search_input.on("clear", lambda _: on_search(None))
        refresh()
