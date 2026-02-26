"""
ollama_service.py
Utilities for checking Ollama availability using the langchain-ollama ecosystem.
"""

from ollama import Client

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL


def is_available() -> bool:
    """Verifica se o servidor Ollama esta acessivel e o modelo esta disponivel."""
    try:
        client = Client(host=OLLAMA_BASE_URL)
        response = client.list()
        model_names = [m.model for m in response.models]
        return any(
            name == OLLAMA_MODEL or name.startswith(f'{OLLAMA_MODEL}:')
            for name in model_names
        )
    except Exception:
        return False
