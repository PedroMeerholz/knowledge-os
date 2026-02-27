"""
rag_service.py
RAG (Retrieval-Augmented Generation) service para o Knowledge OS.
Usa LangChain com FAISS para armazenamento vetorial e OpenAI para geracao.
"""

import logging
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

from app.config import (
    FAISS_INDEX_DIR,
    EMBEDDING_MODEL_NAME,
    RAG_TOP_K,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Estado do modulo (inicializacao lazy)
# ---------------------------------------------------------------------------
_embeddings = None
_vectorstore = None
_initialized = False


# ---------------------------------------------------------------------------
# Funcoes internas
# ---------------------------------------------------------------------------
def _get_embeddings():
    """Retorna a instancia compartilhada de HuggingFaceEmbeddings."""
    global _embeddings
    if _embeddings is None:
        try:
            _embeddings = HuggingFaceEmbeddings(
                model_name=EMBEDDING_MODEL_NAME,
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True},
            )
        except Exception as e:
            logger.error('Falha ao carregar modelo de embeddings: %s', e)
            raise RuntimeError(
                f'não foi possivel carregar o modelo "{EMBEDDING_MODEL_NAME}". '
                f'Verifique se sentence-transformers esta instalado. Erro: {e}'
            ) from e
    return _embeddings


def _get_vectorstore():
    """Retorna a instancia compartilhada do FAISS vectorstore, carregando do disco se existir."""
    global _vectorstore
    if _vectorstore is None:
        embeddings = _get_embeddings()
        index_path = Path(FAISS_INDEX_DIR)
        if (index_path / 'index.faiss').exists():
            _vectorstore = FAISS.load_local(
                FAISS_INDEX_DIR,
                embeddings,
                allow_dangerous_deserialization=True,
            )
            logger.info('índice FAISS carregado de %s', FAISS_INDEX_DIR)
        else:
            logger.info('Nenhum índice FAISS encontrado, sera criado no primeiro uso')
    return _vectorstore


def _save_vectorstore():
    """Persiste o vectorstore FAISS no disco."""
    if _vectorstore is not None:
        Path(FAISS_INDEX_DIR).parent.mkdir(parents=True, exist_ok=True)
        _vectorstore.save_local(FAISS_INDEX_DIR)
        logger.info('índice FAISS salvo em %s', FAISS_INDEX_DIR)


def _build_document(note: dict) -> Document:
    """Converte um dict de nota em um LangChain Document com metadados."""
    page_content = f"{note['title']}\n\n{note['content']}"
    tags = note.get('tags', [])
    metadata = {
        'note_id': note['id'],
        'title': note['title'],
        'source_type': note.get('source_type', ''),
        'source_name': note.get('source_name', ''),
        'source_author': note.get('source_author', ''),
        'tags': '|' + '|'.join(tags) + '|' if tags else '',
        'created_at': note.get('created_at', ''),
    }
    return Document(page_content=page_content, metadata=metadata)


def _rebuild_index(notes: list[dict]) -> None:
    """Reconstroi o índice FAISS do zero a partir de uma lista de notas."""
    global _vectorstore
    if not notes:
        _vectorstore = None
        # Limpar arquivos do índice se existirem
        index_path = Path(FAISS_INDEX_DIR)
        for f in ('index.faiss', 'index.pkl'):
            fpath = index_path / f
            if fpath.exists():
                fpath.unlink()
        return

    embeddings = _get_embeddings()
    docs = [_build_document(note) for note in notes]
    ids = [note['id'] for note in notes]
    _vectorstore = FAISS.from_documents(docs, embeddings, ids=ids)
    _save_vectorstore()


# ---------------------------------------------------------------------------
# Gerenciamento do índice
# ---------------------------------------------------------------------------
def ensure_index() -> int:
    """
    Reconcilia o vector store com as notas atuais no storage.
    Reconstroi o índice completo para garantir consistencia.
    Retorna o numero de documentos no índice.
    """
    global _initialized
    from app.storage import load_notes

    notes = load_notes()
    _rebuild_index(notes)
    _initialized = True
    logger.info('índice FAISS reconciliado com %d notas', len(notes))
    return len(notes)


def add_note(note: dict) -> None:
    """Adiciona uma nota ao vector store."""
    global _vectorstore
    try:
        embeddings = _get_embeddings()
        doc = _build_document(note)
        if _vectorstore is None:
            _vectorstore = FAISS.from_documents([doc], embeddings, ids=[note['id']])
        else:
            _vectorstore.add_documents([doc], ids=[note['id']])
        _save_vectorstore()
        logger.info('Nota %s adicionada ao vector store', note['id'])
    except Exception as e:
        logger.error('Falha ao adicionar nota ao vector store: %s', e)


def update_note(note_id: str, note: dict) -> None:
    """Atualiza uma nota no vector store (reconstroi o índice)."""
    try:
        from app.storage import load_notes
        notes = load_notes()
        _rebuild_index(notes)
        logger.info('Nota %s atualizada no vector store (índice reconstruido)', note_id)
    except Exception as e:
        logger.error('Falha ao atualizar nota no vector store: %s', e)


def delete_note(note_id: str) -> None:
    """Remove uma nota do vector store (reconstroi o índice)."""
    try:
        from app.storage import load_notes
        notes = load_notes()
        _rebuild_index(notes)
        logger.info('Nota %s removida do vector store (índice reconstruido)', note_id)
    except Exception as e:
        logger.error('Falha ao remover nota do vector store: %s', e)


# ---------------------------------------------------------------------------
# Recuperacao de notas (sem geracao LLM)
# ---------------------------------------------------------------------------
def retrieve(question: str, source_type: str = '', tags: list[str] | None = None,
             top_k: int = RAG_TOP_K) -> dict:
    """
    Recupera notas relevantes da base de conhecimento sem chamar o LLM.

    Args:
        question: A pergunta do usuário para busca semantica.
        source_type: Filtro opcional por tipo de fonte (ex: 'livro', 'video').
        tags: Filtro opcional por tags (notas que contenham QUALQUER uma das tags).
        top_k: Numero de documentos a recuperar.

    Returns:
        dict com:
            'context': str - Contexto formatado das notas encontradas.
            'sources': list[dict] - Metadados das notas recuperadas.
    """
    global _initialized
    if not _initialized:
        ensure_index()

    vs = _get_vectorstore()
    if vs is None:
        return {'context': '', 'sources': []}

    has_filter = bool(source_type or tags)
    fetch_k = top_k * 3 if has_filter else top_k

    try:
        results = vs.similarity_search(question, k=fetch_k)
    except Exception as e:
        logger.error('Falha na busca vetorial: %s', e)
        return {'context': '', 'sources': []}

    if has_filter:
        filtered = []
        for doc in results:
            meta = doc.metadata
            if source_type and meta.get('source_type', '') != source_type:
                continue
            if tags:
                doc_tags = meta.get('tags', '')
                if not any(f'|{t}|' in doc_tags for t in tags):
                    continue
            filtered.append(doc)
        results = filtered[:top_k]
    else:
        results = results[:top_k]

    if not results:
        return {'context': '', 'sources': []}

    context_parts = []
    sources = []
    for i, doc in enumerate(results, 1):
        meta = doc.metadata
        context_parts.append(
            f"[Nota {i}] Titulo: {meta.get('title', 'Sem titulo')}\n"
            f"Fonte: {meta.get('source_name', 'N/A')} ({meta.get('source_type', '')})\n"
            f"Autor: {meta.get('source_author', 'N/A')}\n"
            f"Tags: {meta.get('tags', '').replace('|', ', ').strip(', ')}\n"
            f"Conteudo:\n{doc.page_content}\n"
        )
        raw_tags = meta.get('tags', '')
        parsed_tags = [t for t in raw_tags.split('|') if t]
        sources.append({
            'note_id': meta.get('note_id', ''),
            'title': meta.get('title', ''),
            'source_type': meta.get('source_type', ''),
            'source_name': meta.get('source_name', ''),
            'source_author': meta.get('source_author', ''),
            'tags': parsed_tags,
        })

    context = '\n---\n'.join(context_parts)
    return {'context': context, 'sources': sources}
