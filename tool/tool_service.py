"""
tool_service.py
Camada de orquestracao para tool calling (function calling) do LLM no Knowledge OS.
Usa LangChain para definir a ferramenta 'search_knowledge' e gerenciar o loop
de tool calling entre o modelo Ollama e o sistema RAG.
"""

import logging

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_core.tools import StructuredTool
from langchain_ollama import ChatOllama
from pydantic import BaseModel, Field

from app.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    TOOL_CALLING_MAX_ROUNDS,
)
from app.services import ollama_service, rag_service
from app.storage import load_tags
from prompts.tool_prompt import TOOL_SYSTEM_PROMPT
from agents.logging_callback import AgentLoggingCallback

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Input schema da ferramenta
# ---------------------------------------------------------------------------
class SearchKnowledgeInput(BaseModel):
    tag: str = Field(description='A tag para filtrar as notas.')
    question: str = Field(description='A pergunta do usuário para buscar nas notas.')


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _get_available_tag_names() -> list[str]:
    """Retorna a lista de nomes de tags registradas no sistema."""
    tags = load_tags()
    return [t['name'] for t in tags]


def _to_langchain_messages(messages: list[dict]) -> list:
    """Converte dicts {role, content} em objetos de mensagem LangChain."""
    lc_messages: list = [SystemMessage(content=TOOL_SYSTEM_PROMPT)]
    for msg in messages:
        role = msg.get('role', '')
        content = msg.get('content', '')
        if role == 'user':
            lc_messages.append(HumanMessage(content=content))
        elif role == 'assistant':
            lc_messages.append(AIMessage(content=content))
    return lc_messages


# ---------------------------------------------------------------------------
# Loop de orquestracao
# ---------------------------------------------------------------------------
def chat_with_tools(messages: list[dict], interaction_id: str | None = None) -> dict:
    """
    Executa o loop de tool calling completo usando LangChain.

    Args:
        messages: Historico de mensagens do chat (role/content dicts).
        interaction_id: UUID opcional para rastreamento no log.

    Returns:
        dict com:
            'answer': str - A resposta final do modelo.
            'sources': list[dict] - Fontes das notas encontradas.
            'llm_available': bool - Se o Ollama participou da geracao.
            'tool_used': bool - Se a ferramenta search_knowledge foi invocada.
    """
    if not ollama_service.is_available():
        return {
            'answer': 'O modelo de IA (Ollama) não está disponível no momento.',
            'sources': [],
            'llm_available': False,
            'tool_used': False,
        }

    # Coletor de fontes via closure
    all_sources: list[dict] = []

    def _search_knowledge_fn(tag: str, question: str) -> str:
        """Busca notas na base de conhecimento filtradas por tag."""
        available_tags = _get_available_tag_names()
        if tag not in available_tags:
            return (
                f'Erro: A tag "{tag}" não existe no sistema. '
                f'Tags disponíveis: {", ".join(available_tags)}'
            )
        result = rag_service.retrieve(question=question, tags=[tag])
        if not result['sources']:
            return (
                f'Nenhuma nota encontrada com a tag "{tag}" '
                f'relevante para a pergunta.'
            )
        all_sources.extend(result['sources'])
        return result['context']

    # Construir ferramenta com descricao dinamica (tags atuais)
    available_tags = _get_available_tag_names()
    tags_description = (
        ', '.join(available_tags) if available_tags
        else '(nenhuma tag cadastrada)'
    )
    search_tool = StructuredTool.from_function(
        func=_search_knowledge_fn,
        name='search_knowledge',
        description=(
            'Busca notas na base de conhecimento do usuario filtradas '
            'por uma tag específica. '
            f'Tags disponiveis: {tags_description}'
        ),
        args_schema=SearchKnowledgeInput,
    )

    tools = [search_tool]
    tools_by_name = {t.name: t for t in tools}

    # Criar modelo com ferramentas vinculadas
    llm = ChatOllama(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        timeout=OLLAMA_TIMEOUT,
    ).bind_tools(tools)

    lc_messages = _to_langchain_messages(messages)
    tool_was_used = False

    invoke_config = {}
    if interaction_id:
        callback = AgentLoggingCallback(interaction_id, 'model')
        invoke_config = {'callbacks': [callback]}

    for round_num in range(TOOL_CALLING_MAX_ROUNDS):
        try:
            response: AIMessage = llm.invoke(lc_messages, config=invoke_config)
        except Exception as e:
            logger.error('Erro na chamada ao Ollama (round %d): %s', round_num, e)
            return {
                'answer': f'Erro ao comunicar com o modelo de IA: {e}',
                'sources': all_sources,
                'llm_available': False,
                'tool_used': tool_was_used,
            }

        # Se nao ha tool calls, o modelo produziu a resposta final
        if not response.tool_calls:
            return {
                'answer': response.content,
                'sources': all_sources,
                'llm_available': True,
                'tool_used': tool_was_used,
            }

        # Adicionar resposta do assistente ao historico
        lc_messages.append(response)

        # Executar cada tool call
        for tool_call in response.tool_calls:
            tool_name = tool_call['name']
            tool_args = tool_call['args']

            logger.info(
                'Tool call round %d: %s(%s)', round_num, tool_name, tool_args,
            )

            selected_tool = tools_by_name.get(tool_name)
            if selected_tool:
                tool_result = selected_tool.invoke(tool_args)
            else:
                tool_result = f'Erro: Ferramenta desconhecida "{tool_name}".'

            tool_was_used = True

            lc_messages.append(
                ToolMessage(content=tool_result, tool_call_id=tool_call['id'])
            )

    # Se atingiu o limite de rounds
    logger.warning(
        'Tool calling loop atingiu o limite de %d rounds',
        TOOL_CALLING_MAX_ROUNDS,
    )
    return {
        'answer': (
            'Desculpe, não consegui processar completamente sua pergunta. '
            'Tente reformulá-la.'
        ),
        'sources': all_sources,
        'llm_available': True,
        'tool_used': tool_was_used,
    }
