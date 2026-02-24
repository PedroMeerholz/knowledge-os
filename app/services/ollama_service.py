"""
ollama_service.py
Modulo standalone de integracao com o Ollama local.
Conecta ao servidor Ollama via API REST e utiliza o modelo ministral:8b.
"""

import httpx

from app.config import OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_TIMEOUT


# ---------------------------------------------------------------------------
# Verificacao de disponibilidade
# ---------------------------------------------------------------------------
def is_available() -> bool:
    """Verifica se o servidor Ollama esta acessivel e o modelo esta disponivel."""
    try:
        response = httpx.get(f'{OLLAMA_BASE_URL}/api/tags', timeout=10)
        response.raise_for_status()
        models = response.json().get('models', [])
        model_names = [m.get('name', '') for m in models]
        return any(
            name == OLLAMA_MODEL or name.startswith(f'{OLLAMA_MODEL}:')
            for name in model_names
        )
    except (httpx.HTTPError, httpx.ConnectError, Exception):
        return False


# ---------------------------------------------------------------------------
# Geracao de texto (prompt unico)
# ---------------------------------------------------------------------------
def generate(prompt: str, system: str = '') -> str:
    """
    Gera texto a partir de um prompt usando POST /api/generate.

    Args:
        prompt: O texto de entrada para geracao.
        system: Instrucao de sistema opcional para guiar o comportamento do modelo.

    Returns:
        O texto gerado pelo modelo.

    Raises:
        httpx.ConnectError: Se o servidor Ollama nao estiver acessivel.
        httpx.HTTPStatusError: Se o servidor retornar um erro HTTP.
    """
    payload = {
        'model': OLLAMA_MODEL,
        'prompt': prompt,
        'stream': False,
    }
    if system:
        payload['system'] = system

    response = httpx.post(
        f'{OLLAMA_BASE_URL}/api/generate',
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get('response', '')


# ---------------------------------------------------------------------------
# Chat multi-turno
# ---------------------------------------------------------------------------
def chat(messages: list[dict], system: str = '') -> str:
    """
    Envia uma conversa multi-turno usando POST /api/chat.

    Args:
        messages: Lista de dicts com 'role' ('user', 'assistant') e 'content'.
                  Exemplo: [{'role': 'user', 'content': 'Ola'}]
        system: Instrucao de sistema opcional. Se fornecida, e adicionada como
                a primeira mensagem com role='system'.

    Returns:
        O texto da resposta do assistente.

    Raises:
        httpx.ConnectError: Se o servidor Ollama nao estiver acessivel.
        httpx.HTTPStatusError: Se o servidor retornar um erro HTTP.
    """
    all_messages = list(messages)
    if system:
        all_messages.insert(0, {'role': 'system', 'content': system})

    payload = {
        'model': OLLAMA_MODEL,
        'messages': all_messages,
        'stream': False,
    }

    response = httpx.post(
        f'{OLLAMA_BASE_URL}/api/chat',
        json=payload,
        timeout=OLLAMA_TIMEOUT,
    )
    response.raise_for_status()
    return response.json().get('message', {}).get('content', '')
