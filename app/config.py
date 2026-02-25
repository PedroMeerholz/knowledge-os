"""
Centralized configuration for the Knowledge OS application.
All paths resolve relative to the project root (one level above this file).
"""
import os
from pathlib import Path

# Project root: the directory containing main.py and data/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Data paths ---
DATA_DIR = PROJECT_ROOT / 'data'
NOTES_FILE = DATA_DIR / 'notes.json'
TAGS_FILE = DATA_DIR / 'tags.json'
FAISS_INDEX_DIR: str = os.environ.get(
    'FAISS_INDEX_DIR',
    str(DATA_DIR / 'faiss_index'),
)

# --- Ollama settings ---
OLLAMA_BASE_URL: str = os.environ.get('OLLAMA_BASE_URL', 'http://localhost:11434')
OLLAMA_MODEL: str = os.environ.get('OLLAMA_MODEL', 'ministral-3:3b')
OLLAMA_TIMEOUT: float = float(os.environ.get('OLLAMA_TIMEOUT', '120'))

# --- RAG settings ---
EMBEDDING_MODEL_NAME: str = os.environ.get('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
RAG_TOP_K: int = int(os.environ.get('RAG_TOP_K', '5'))

# --- Tool calling settings ---
TOOL_CALLING_MAX_ROUNDS: int = int(os.environ.get('TOOL_CALLING_MAX_ROUNDS', '5'))

# --- NiceGUI settings ---
APP_TITLE = 'Knowledge OS'
APP_HOST = '0.0.0.0'
APP_PORT = 7860

# --- Theme colors ---
THEME_COLORS = {
    'primary': '#1a1a2e',
    'secondary': '#16213e',
    'accent': '#0f3460',
    'positive': '#53d769',
    'negative': '#ff4757',
    'warning': '#ffa502',
}
