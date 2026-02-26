"""
Centralized configuration for the Knowledge OS application.
All paths resolve relative to the project root (one level above this file).
"""
import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

# Project root: the directory containing main.py and data/
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# --- Data paths ---
DATA_DIR = PROJECT_ROOT / 'data'
NOTES_FILE = DATA_DIR / 'notes.json'
TAGS_FILE = DATA_DIR / 'tags.json'
CHATS_FILE = DATA_DIR / 'chats.json'
MAX_CHATS = 10
FAISS_INDEX_DIR: str = os.environ.get(
    'FAISS_INDEX_DIR',
    str(DATA_DIR / 'faiss_index'),
)

# --- OpenAI settings ---
OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '')
CHAT_MODEL: str = os.environ.get('CHAT_MODEL', 'gpt-4o')
GUARDRAIL_MODEL: str = os.environ.get('GUARDRAIL_MODEL', 'gpt-4o-mini')
OPENAI_TIMEOUT: float = float(os.environ.get('OPENAI_TIMEOUT', '120'))

# --- RAG settings ---
EMBEDDING_MODEL_NAME: str = os.environ.get('EMBEDDING_MODEL_NAME', 'all-MiniLM-L6-v2')
RAG_TOP_K: int = int(os.environ.get('RAG_TOP_K', '5'))

# --- Tool calling settings ---
TOOL_CALLING_MAX_ROUNDS: int = int(os.environ.get('TOOL_CALLING_MAX_ROUNDS', '5'))

# --- Guardrail settings ---
GUARDRAIL_MAX_RETRIES: int = int(os.environ.get('GUARDRAIL_MAX_RETRIES', '2'))

# --- Logging settings ---
LOG_DIR = PROJECT_ROOT / 'logs'
AGENT_LOG_FILE = LOG_DIR / 'agent_tracking.log'

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
