from nicegui import ui


def create_layout(current_path: str = "/") -> None:
    nav_items = [
        ("home",       "/",           "Planet List"),
        ("psychology", "/overview",   "LLM Overview"),
        ("compare",    "/similarity", "Similarity"),
        ("table_view", "/comparison", "Compare Table"),
    ]

    with ui.header().classes("bg-indigo-900 text-white shadow-md"):
        with ui.row().classes("items-center gap-4 p-3 w-full max-w-7xl mx-auto"):
            ui.label("AstroMetrics").classes("text-2xl font-bold tracking-wide")
            ui.space()
            for icon, path, label in nav_items:
                ui.button(
                    label,
                    icon=icon,
                    on_click=lambda p=path: ui.navigate.to(p),
                ).classes("text-white").props("flat no-caps")
