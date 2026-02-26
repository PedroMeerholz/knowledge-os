"""
guardrail_agent.py
Agente de guardrail que verifica se a resposta do LLM e coerente
com a pergunta do usuario e se nao contem conteudo perigoso ou sensivel.
Usa LangChain LCEL com ChatOpenAI.
"""

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI

from app.config import (
    OPENAI_API_KEY,
    GUARDRAIL_MODEL,
    OPENAI_TIMEOUT,
)
from prompts.guardrail_prompt import GUARDRAIL_PROMPT_TEMPLATE
from agents.logging_callback import AgentLoggingCallback

logger = logging.getLogger(__name__)


def check_coherence(
    user_question: str,
    llm_answer: str,
    interaction_id: str | None = None,
) -> bool:
    """
    Verifica se a resposta do LLM e coerente com a pergunta do usuario
    e se nao contem conteudo perigoso ou sensivel.

    Args:
        user_question: A pergunta original do usuario.
        llm_answer: A resposta gerada pelo LLM.
        interaction_id: UUID opcional para rastreamento no log.

    Returns:
        True se a resposta e coerente e segura ("Sim"), False caso contrario ("Nao").
        Retorna True (skip guardrail) em caso de erro na avaliacao.
    """
    try:
        llm = ChatOpenAI(
            api_key=OPENAI_API_KEY,
            model=GUARDRAIL_MODEL,
            timeout=OPENAI_TIMEOUT,
        )
        prompt = PromptTemplate(
            input_variables=['question', 'answer'],
            template=GUARDRAIL_PROMPT_TEMPLATE,
        )
        chain = prompt | llm | StrOutputParser()

        invoke_config = {}
        if interaction_id:
            callback = AgentLoggingCallback(interaction_id, 'guardrail')
            invoke_config = {'callbacks': [callback]}

        raw_result = chain.invoke(
            {'question': user_question, 'answer': llm_answer},
            config=invoke_config,
        )
        verdict = _parse_verdict(raw_result)
        logger.info(
            'Guardrail resultado: %s (raw: %s)',
            'coerente' if verdict else 'incoerente',
            raw_result.strip()[:50],
        )
        return verdict
    except Exception as e:
        logger.warning(
            'Guardrail indisponivel, pulando verificacao: %s', e,
        )
        return True


def _parse_verdict(raw: str) -> bool:
    """
    Extrai o veredito do texto retornado pelo LLM.

    Procura por "Sim" ou "Nao" no inicio da resposta (case-insensitive).
    Retorna True para "Sim", False para "Nao".
    Em caso de resposta ambigua, retorna True (assume coerente).
    """
    cleaned = raw.strip().lower()
    first_token = cleaned.split()[0] if cleaned else ''
    first_token = first_token.rstrip('.,;:!').strip()

    if first_token in ('sim', 'yes'):
        return True
    if first_token in ('não', 'nao', 'no'):
        return False

    if ('não' in cleaned or 'nao' in cleaned or 'incoerente' in cleaned
            or 'perigoso' in cleaned or 'sensível' in cleaned
            or 'sensivel' in cleaned or 'inseguro' in cleaned):
        return False

    logger.warning(
        'Guardrail retornou resposta ambigua: "%s". Assumindo coerente.',
        raw.strip()[:80],
    )
    return True
