"""Entry point for the Knowledge OS application."""
import logging

from nicegui import ui

import app  # noqa: F401 -- triggers theme + route registration

from app.config import APP_TITLE, APP_HOST, APP_PORT, LOG_DIR, AGENT_LOG_FILE

# --- Configure agent tracking logger ---
LOG_DIR.mkdir(parents=True, exist_ok=True)

agent_logger = logging.getLogger('agent_tracking')
agent_logger.setLevel(logging.INFO)
agent_logger.propagate = False

_file_handler = logging.FileHandler(AGENT_LOG_FILE, encoding='utf-8')
_file_handler.setFormatter(logging.Formatter('%(asctime)s | %(message)s'))
agent_logger.addHandler(_file_handler)

ui.run(title=APP_TITLE, host=APP_HOST, port=APP_PORT, reload=False)
