from nicegui import app, ui

# Importa os modulos de paginas para registrar as rotas via @ui.page
from pages import home         # noqa: F401
from pages import note_form  # noqa: F401
from pages import notes_db   # noqa: F401
from pages import tags        # noqa: F401
from pages import fontmap     # noqa: F401
from pages import reports     # noqa: F401
from pages import knowledge_chat  # noqa: F401

# Tema global
app.colors(
    primary='#1a1a2e',
    secondary='#16213e',
    accent='#0f3460',
    positive='#53d769',
    negative='#ff4757',
    warning='#ffa502',
)

ui.run(title='Knowledge OS', host='0.0.0.0', port=7860, reload=False)
