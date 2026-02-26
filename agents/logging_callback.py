"""
logging_callback.py
Custom LangChain callback handler para rastrear acoes do modelo
e do agente guardrail em arquivo de log com interaction_id compartilhado.
"""

import logging
from typing import Any
from uuid import UUID

from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

logger = logging.getLogger('agent_tracking')


class AgentLoggingCallback(BaseCallbackHandler):
    """
    Callback handler que loga eventos do LangChain em arquivo.

    Cada instancia e associada a um interaction_id (UUID da interacao)
    e um agent_name ('model' ou 'guardrail') para correlacionar
    chamadas do modelo principal com avaliacoes do guardrail.
    """

    def __init__(self, interaction_id: str, agent_name: str) -> None:
        self.interaction_id = interaction_id
        self.agent_name = agent_name

    def _log(self, event: str, data: str) -> None:
        logger.info(
            '%s | %-10s | %-12s | %s',
            self.interaction_id,
            self.agent_name,
            event,
            data,
        )

    def on_llm_start(
        self,
        serialized: dict[str, Any] | None,
        prompts: list[str],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        model = (serialized or {}).get('kwargs', {}).get('model', 'unknown')
        prompt_preview = (prompts[0][:100] + '...') if prompts else ''
        self._log('llm_start', f'model={model} | prompt={prompt_preview}')

    def on_llm_end(
        self,
        response: LLMResult,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        text = ''
        if response.generations:
            first = response.generations[0]
            if first:
                text = first[0].text[:150]
        self._log('llm_end', f'response={text}')

    def on_llm_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        self._log('llm_error', f'error={error}')

    def on_chain_start(
        self,
        serialized: dict[str, Any] | None,
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        serialized = serialized or {}
        chain_name = serialized.get('name', serialized.get('id', ['unknown'])[-1])
        input_preview = str(inputs)[:150]
        self._log('chain_start', f'chain={chain_name} | input={input_preview}')

    def on_chain_end(
        self,
        outputs: dict[str, Any] | None,
        *,
        run_id: UUID,
        **kwargs: Any,
    ) -> None:
        output_preview = str(outputs)[:150]
        self._log('chain_end', f'output={output_preview}')
