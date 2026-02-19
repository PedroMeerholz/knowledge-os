from nicegui import ui
from app.services.planet_service import load_planets
from app.services.llm_service import compare_planets
from app.ui.layout import create_layout


def _fmt(value: float | None, fmt: str = "g") -> str:
    if value is None:
        return "N/A"
    return f"{value:{fmt}}"


def comparison_page() -> None:
    create_layout("/comparison")
    all_planets = load_planets()
    selected_ids: list[str] = []

    compare_fields = [
        ("Mass (Jupiter masses)",    lambda p: _fmt(p.mass)),
        ("Radius (Earth radii)",     lambda p: _fmt(p.radius)),
        ("Orbital Period (days)",    lambda p: _fmt(p.period)),
        ("Semi-major Axis (AU)",     lambda p: _fmt(p.semi_major_axis)),
        ("Temperature (K)",          lambda p: _fmt(p.temperature)),
        ("Distance (ly)",            lambda p: _fmt(p.distance_light_year)),
        ("Host Star Mass (solar)",   lambda p: _fmt(p.host_star_mass)),
        ("Host Star Temp (K)",       lambda p: _fmt(p.host_star_temperature)),
    ]

    planet_name_to_id = {p.name: p.id for p in all_planets}

    with ui.column().classes("w-full max-w-7xl mx-auto p-6 gap-6"):
        ui.label("Planet Comparison Table").classes("text-3xl font-bold text-indigo-900 mb-1")
        ui.label(
            "Search and select planets, then click Compare to see "
            "their characteristics side by side with an AI-powered analysis."
        ).classes("text-gray-600 mb-2")

        selector = ui.select(
            list(planet_name_to_id.keys()),
            multiple=True,
            label="Search and select planets to compare",
            value=[],
        ).classes("w-full max-w-xl").props("use-input use-chips input-debounce=300")

        compare_btn = ui.button(
            "Compare",
            icon="compare_arrows",
        ).props("color=indigo no-caps").classes("mt-2")

        table_container = ui.column().classes("w-full overflow-x-auto mt-4")
        ai_container = ui.column().classes("w-full mt-4")

        def rebuild_table() -> None:
            selected_ids.clear()
            for name in (selector.value or []):
                pid = planet_name_to_id.get(name)
                if pid:
                    selected_ids.append(pid)

            table_container.clear()
            ai_container.clear()
            selected = [p for p in all_planets if p.id in selected_ids]
            if len(selected) < 2:
                with table_container:
                    ui.label("Select at least 2 planets to compare.").classes(
                        "text-gray-400 italic mt-4"
                    )
                return

            columns = [
                {
                    "name": "property",
                    "label": "Property",
                    "field": "property",
                    "align": "left",
                }
            ]
            for p in selected:
                columns.append(
                    {"name": p.id, "label": p.name, "field": p.id, "align": "center"}
                )

            rows = []
            for label, extractor in compare_fields:
                row: dict[str, str] = {"property": label}
                for p in selected:
                    row[p.id] = extractor(p)
                rows.append(row)

            with table_container:
                ui.table(columns=columns, rows=rows).classes(
                    "w-full border rounded-lg shadow-sm"
                ).props("flat bordered")

            # AI comparison section
            with ai_container:
                ui.label("AI Comparison").classes(
                    "text-xl font-semibold text-indigo-800 mt-2"
                )
                ui.separator()
                spinner = ui.spinner(size="lg").classes("mt-4")
                description_label = ui.label("").classes(
                    "text-base leading-relaxed whitespace-pre-wrap text-gray-800"
                )

            async def load_comparison() -> None:
                spinner.visible = True
                description_label.set_text("")
                async for chunk in compare_planets(selected):
                    description_label.set_text(description_label.text + chunk)
                spinner.visible = False

            ui.timer(0.05, load_comparison, once=True)

        compare_btn.on_click(rebuild_table)
        rebuild_table()
