"""
search_knowledge.py
Ferramenta de busca na base de conhecimento filtrada por tag.
"""

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.services import rag_service
from app.storage import load_tags


# ---------------------------------------------------------------------------
# Input schema da ferramenta
# ---------------------------------------------------------------------------
class SearchKnowledgeInput(BaseModel):
    tag: str = Field(description='A tag para filtrar as notas.')
    question: str = Field(description='A pergunta do usuário para buscar nas notas.')


def _get_available_tag_names() -> list[str]:
    """Retorna a lista de nomes de tags registradas no sistema."""
    tags = load_tags()
    return [t['name'] for t in tags]


def create_search_knowledge_tool(sources_collector: list[dict]) -> StructuredTool:
    """
    Cria e retorna a ferramenta search_knowledge.

    Args:
        sources_collector: Lista mutável onde as fontes encontradas serão
                          acumuladas a cada invocação da ferramenta.

    Returns:
        StructuredTool configurada para buscar notas por tag.
    """

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
        sources_collector.extend(result['sources'])
        return result['context']

    available_tags = _get_available_tag_names()
    tags_description = (
        ', '.join(available_tags) if available_tags
        else '(nenhuma tag cadastrada)'
    )

    return StructuredTool.from_function(
        func=_search_knowledge_fn,
        name='search_knowledge',
        description=(
            'Busca notas na base de conhecimento do usuario filtradas '
            'por uma tag específica. '
            f'Tags disponiveis: {tags_description}'
        ),
        args_schema=SearchKnowledgeInput,
    )
