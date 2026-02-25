from nicegui import run, ui

from app.services import tool_service
from app.ui.components import create_sidebar

# ---------------------------------------------------------------------------
# Icones por tipo de fonte
# ---------------------------------------------------------------------------
TYPE_ICONS = {
    'livro': 'menu_book',
    'video': 'play_circle',
    'artigo': 'article',
    'podcast': 'podcasts',
    'curso': 'school',
    'outro': 'lightbulb',
}


# ---------------------------------------------------------------------------
# Pagina principal
# ---------------------------------------------------------------------------
@ui.page('/chat')
def knowledge_chat_page():
    create_sidebar()

    with ui.column().classes('w-full p-4').style('height: calc(100vh - 4rem)'):
        ui.label('Assistente Virtual').classes('text-h4 q-mb-md')

        chat_history = []

        with ui.row().classes('w-full flex-grow gap-4') \
                .style('min-height: 0'):

            # ---- LADO ESQUERDO: Chat ----
            with ui.column().classes('flex-[3] min-w-0') \
                    .style('height: 100%'):
                with ui.scroll_area() \
                        .classes('flex-grow w-full border rounded-lg bg-grey-1') as scroll:
                    messages = ui.column().classes('w-full q-pa-md gap-2')
                    with messages:
                        ui.chat_message(
                            "Ola! Eu sou o assistente do Knowledge OS. "
                            "Me pergunte qualquer coisa sobre suas notas — "
                            "ao lado, voce vera as fontes mais relevantes "
                            "encontradas na sua base de conhecimento.",
                            name='KnowledgeBot',
                            stamp='agora',
                        )

                with ui.row().classes('w-full gap-2 q-mt-sm items-center'):
                    msg_input = ui.input(placeholder='Digite uma mensagem...') \
                        .classes('flex-grow').props('outlined dense')

                    async def send():
                        text = (msg_input.value or '').strip()
                        if not text:
                            return

                        chat_history.append({'role': 'user', 'content': text})

                        with messages:
                            ui.chat_message(text, name='Voce', sent=True)
                        msg_input.value = ''

                        with messages:
                            loading_msg = ui.row().classes('items-center gap-2 q-pa-sm')
                            with loading_msg:
                                ui.spinner('dots', size='2em', color='primary')
                                ui.label('Buscando nas suas notas...') \
                                    .classes('text-grey-7 text-caption')
                        scroll.scroll_to(percent=1.0)

                        msg_input.props('disable')
                        send_btn.props('disable')

                        try:
                            result = await run.io_bound(
                                tool_service.chat_with_tools, chat_history,
                            )
                        except Exception as e:
                            result = {
                                'answer': f'Erro inesperado ao consultar a base de conhecimento: {e}',
                                'sources': [],
                                'llm_available': False,
                                'tool_used': False,
                            }

                        chat_history.append({
                            'role': 'assistant',
                            'content': result['answer'],
                        })

                        messages.remove(loading_msg)
                        with messages:
                            ui.chat_message(result['answer'], name='KnowledgeBot')
                        scroll.scroll_to(percent=1.0)

                        msg_input.props(remove='disable')
                        send_btn.props(remove='disable')
                        msg_input.run_method('focus')

                        _update_sources(result['sources'], result['llm_available'])

                    send_btn = ui.button(icon='send', on_click=send) \
                        .props('round color=primary')
                    msg_input.on('keydown.enter', send)

            # ---- LADO DIREITO: Fontes Relacionadas ----
            with ui.column().classes('flex-[2] min-w-0') \
                    .style('height: 100%'):
                ui.label('Fontes Relacionadas').classes('text-h6 q-mb-sm')

                status_container = ui.column().classes('w-full')

                rec_scroll = ui.scroll_area().classes('flex-grow w-full')
                rec_container = ui.column().classes('w-full gap-2 q-pa-xs')
                rec_scroll.content = rec_container

                with rec_container:
                    ui.label('Faca uma pergunta para ver fontes relacionadas.') \
                        .classes('text-caption text-grey-6 q-pa-md text-center w-full')

    def _update_sources(sources: list[dict], llm_available: bool):
        status_container.clear()
        if not llm_available:
            with status_container:
                with ui.element('div').classes(
                    'w-full rounded-lg q-pa-sm q-mb-sm flex items-start gap-2'
                ).style('background-color: #e3f2fd; border: 1px solid #90caf9;'):
                    ui.icon('info', color='blue-7').classes('text-xl mt-1')
                    ui.label(
                        'O modelo de IA (Ollama) esta offline. '
                        'As respostas usam apenas busca nas notas.'
                    ).classes('text-caption text-blue-9')

        rec_container.clear()
        with rec_container:
            if sources:
                _render_sources(sources)
            else:
                ui.label('Nenhuma fonte relacionada encontrada.') \
                    .classes('text-caption text-grey-6 q-pa-md text-center w-full')


def _render_sources(sources: list[dict]):
    """Renderiza cards de fontes recuperadas pelo RAG."""
    for src in sources:
        icon = TYPE_ICONS.get(src.get('source_type', ''), 'lightbulb')
        with ui.card().classes('w-full q-pa-sm'):
            with ui.row().classes('items-start gap-3 w-full'):
                ui.icon(icon, color='primary').classes('text-2xl mt-1')
                with ui.column().classes('flex-grow gap-0'):
                    ui.label(src.get('title', 'Sem titulo')) \
                        .classes('text-subtitle1 font-bold')
                    with ui.row().classes('gap-2 items-center'):
                        source_type = src.get('source_type', '')
                        if source_type:
                            ui.chip(source_type, color='primary') \
                                .props('dense outline size=sm')
                        author = src.get('source_author', '')
                        if author:
                            ui.label(f"por {author}") \
                                .classes('text-caption text-grey-8')
                    source_name = src.get('source_name', '')
                    if source_name:
                        ui.label(source_name) \
                            .classes('text-caption text-grey-8 q-mt-xs')
                    tags = src.get('tags', [])
                    if tags:
                        with ui.row().classes('gap-1 q-mt-xs flex-wrap'):
                            for tag in tags:
                                ui.chip(tag, color='grey-4') \
                                    .props('dense outline size=sm')
