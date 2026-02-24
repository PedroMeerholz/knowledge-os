"""Entry point for the Knowledge OS application."""
from nicegui import ui

import app  # noqa: F401 -- triggers theme + route registration

from app.config import APP_TITLE, APP_HOST, APP_PORT

ui.run(title=APP_TITLE, host=APP_HOST, port=APP_PORT, reload=False)
