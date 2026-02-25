"""
Knowledge OS application package.
Importing this module configures the NiceGUI theme and registers all page routes.
"""
from nicegui import app

from app.config import THEME_COLORS, PROJECT_ROOT

# Apply global theme
app.colors(**THEME_COLORS)

# Serve static files (avatars, images, etc.)
app.add_static_files('/static', str(PROJECT_ROOT / 'data' / 'assets' / 'static'))

# Import page modules to register their @ui.page() routes
from app.ui.pages import home          # noqa: F401, E402
from app.ui.pages import note_form     # noqa: F401, E402
from app.ui.pages import notes_db      # noqa: F401, E402
from app.ui.pages import tags          # noqa: F401, E402
from app.ui.pages import fontmap       # noqa: F401, E402
from app.ui.pages import reports       # noqa: F401, E402
from app.ui.pages import knowledge_chat  # noqa: F401, E402
