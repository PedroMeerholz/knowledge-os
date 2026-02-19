from dotenv import load_dotenv

load_dotenv()  # must be before any service imports that read env vars

from nicegui import ui, app as nicegui_app  # noqa: E402

from app.api.planets import router as planets_router  # noqa: E402
from app.api.similarity import router as similarity_router  # noqa: E402
from app.services.llm_service import clear_description_cache  # noqa: E402
from app.ui.pages.home import home_page  # noqa: E402
from app.ui.pages.overview import overview_page  # noqa: E402
from app.ui.pages.similarity import similarity_page  # noqa: E402
from app.ui.pages.comparison import comparison_page  # noqa: E402

# Attach REST API routers to NiceGUI's internal FastAPI instance
nicegui_app.include_router(planets_router)
nicegui_app.include_router(similarity_router)

# Clear LLM description cache on shutdown
nicegui_app.on_shutdown(clear_description_cache)

# Register NiceGUI pages
ui.page("/")(home_page)
ui.page("/overview")(overview_page)
ui.page("/similarity")(similarity_page)
ui.page("/comparison")(comparison_page)

if __name__ in {"__main__", "__mp_main__"}:
    ui.run(
        title="AstroMetrics",
        port=8080,
        reload=False,
        favicon="🪐",
    )
