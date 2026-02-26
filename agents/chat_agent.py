"""
chat_agent.py
Agente de chat que orquestra o loop de tool calling (function calling) do LLM
no Knowledge OS. Usa LangChain para definir a ferramenta 'search_knowledge'
e gerenciar o loop de tool calling entre o modelo OpenAI e o sistema RAG.
"""

import logging

from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langchain_openai import ChatOpenAI

from app.config import (
    OPENAI_API_KEY,
    CHAT_MODEL,
    OPENAI_TIMEOUT,
    TOOL_CALLING_MAX_ROUNDS,
)
from prompts.tool_prompt import TOOL_SYSTEM_PROMPT
from agents.logging_callback import AgentLoggingCallback
from tools.search_knowledge import create_search_knowledge_tool

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
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
            'llm_available': bool - Se o modelo participou da geracao.
            'tool_used': bool - Se a ferramenta search_knowledge foi invocada.
    """
    # Coletor de fontes via closure
    all_sources: list[dict] = []

    search_tool = create_search_knowledge_tool(all_sources)

    tools = [search_tool]
    tools_by_name = {t.name: t for t in tools}

    # Criar modelo com ferramentas vinculadas
    llm = ChatOpenAI(
        api_key=OPENAI_API_KEY,
        model=CHAT_MODEL,
        timeout=OPENAI_TIMEOUT,
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
            logger.error('Erro na chamada ao OpenAI (round %d): %s', round_num, e)
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
