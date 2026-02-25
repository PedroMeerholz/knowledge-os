from nicegui import run, ui

from app.config import MAX_CHATS
from app.services import tool_service
from app.storage import (
    count_chats, delete_chat, get_chat, load_chats, save_chat, update_chat,
)
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

BOT_NAME = 'Gandalf-RAG'
BOT_AVATAR = '/static/gandalf-avatar.png'


# ---------------------------------------------------------------------------
# Pagina principal
# ---------------------------------------------------------------------------
@ui.page('/chat')
def knowledge_chat_page():
    create_sidebar()

    current_chat_id = None
    chat_history = []

    with ui.column().classes('w-full p-4').style('height: calc(100vh - 4rem)'):
        ui.label('Assistente Virtual').classes('text-h4 q-mb-md')

        with ui.row().classes('w-full flex-grow gap-4') \
                .style('min-height: 0'):

            # ---- LEFT: Chat Sidebar ----
            with ui.column().classes('min-w-0 border-r q-pr-sm flex-[3]') \
                    .style('min-height: 0'):

                with ui.row().classes('w-full items-center q-pa-sm'):
                    ui.label('Conversas') \
                        .classes('text-subtitle1 font-bold flex-grow')
                    chat_count_label = ui.label(
                        f'{count_chats()}/{MAX_CHATS}'
                    ).classes('text-caption text-grey-6')

                ui.button(
                    'Novo Chat', icon='add',
                    on_click=lambda: handle_new_chat(),
                ).classes('w-full q-mb-sm') \
                    .props('outline dense color=primary no-caps')

                ui.separator()

                with ui.scroll_area().classes('flex-grow w-full'):
                    sidebar_list = ui.column().classes('w-full gap-1 q-pa-xs')

            # ---- CENTER: Chat ----
            with ui.column().classes('min-w-0 flex-[7]') \
                    .style('min-height: 0'):
                with ui.scroll_area() \
                        .classes('flex-grow w-full border rounded-lg '
                                 'bg-grey-1') as scroll:
                    messages = ui.column().classes('w-full q-pa-md gap-2')

                with ui.row().classes('w-full gap-2 q-mt-sm items-center'):
                    msg_input = ui.input(
                        placeholder='Digite uma mensagem...',
                    ).classes('flex-grow').props('outlined dense')

                    async def send():
                        nonlocal current_chat_id
                        text = (msg_input.value or '').strip()
                        if not text:
                            return

                        if current_chat_id is None \
                                and len(chat_history) == 0:
                            if count_chats() >= MAX_CHATS:
                                ui.notify(
                                    f'Limite de {MAX_CHATS} conversas '
                                    'atingido! Exclua uma conversa antes '
                                    'de iniciar uma nova.',
                                    type='warning',
                                )
                                return

                        chat_history.append(
                            {'role': 'user', 'content': text},
                        )

                        with messages:
                            ui.chat_message(
                                text, name='Voce', sent=True,
                            )
                        msg_input.value = ''

                        with messages:
                            loading_msg = ui.row() \
                                .classes('items-center gap-2 q-pa-sm')
                            with loading_msg:
                                ui.spinner(
                                    'dots', size='2em', color='primary',
                                )
                                ui.label(
                                    'Buscando nas suas notas...',
                                ).classes('text-grey-7 text-caption')
                        scroll.scroll_to(percent=1.0)

                        msg_input.props('disable')
                        send_btn.props('disable')

                        try:
                            result = await run.io_bound(
                                tool_service.chat_with_tools,
                                chat_history,
                            )
                        except Exception as e:
                            result = {
                                'answer': 'Erro inesperado ao consultar '
                                          f'a base de conhecimento: {e}',
                                'sources': [],
                                'llm_available': False,
                                'tool_used': False,
                            }

                        chat_history.append({
                            'role': 'assistant',
                            'content': result['answer'],
                            'sources': list(result['sources']),
                        })

                        messages.remove(loading_msg)
                        with messages:
                            with ui.chat_message(
                                name=BOT_NAME, avatar=BOT_AVATAR,
                            ):
                                ui.markdown(result['answer'])
                            if result['sources']:
                                response_sources = list(result['sources'])

                                def _show_sources(
                                    sources=response_sources,
                                ):
                                    _open_sources_dialog(sources)

                                ui.button(
                                    'Ver Fontes', icon='source',
                                    on_click=_show_sources,
                                ).props(
                                    'flat dense size=sm color=primary',
                                )
                        scroll.scroll_to(percent=1.0)

                        msg_input.props(remove='disable')
                        send_btn.props(remove='disable')
                        msg_input.run_method('focus')

                        # ---- AUTO-SAVE ----
                        if current_chat_id is None:
                            title = chat_history[0]['content'][:50]
                            new_chat = save_chat(
                                title, list(chat_history),
                            )
                            if new_chat is not None:
                                current_chat_id = new_chat['id']
                            else:
                                ui.notify(
                                    f'Limite de {MAX_CHATS} conversas '
                                    'atingido. Conversa nao foi salva.',
                                    type='warning',
                                )
                        else:
                            update_chat(
                                current_chat_id, list(chat_history),
                            )
                        render_chat_sidebar()

                    send_btn = ui.button(icon='send', on_click=send) \
                        .props('round color=primary')
                    msg_input.on('keydown.enter', send)

    # -------------------------------------------------------------------
    # Helper functions (closures over UI containers)
    # -------------------------------------------------------------------

    def render_chat_sidebar():
        """Re-render the conversations list in the sidebar."""
        sidebar_list.clear()
        chats = load_chats()
        chat_count_label.text = f'{len(chats)}/{MAX_CHATS}'

        if not chats:
            with sidebar_list:
                ui.label('Nenhuma conversa salva.').classes(
                    'text-caption text-grey-6 q-pa-md text-center w-full',
                )
            return

        with sidebar_list:
            for chat in chats:
                is_active = (chat['id'] == current_chat_id)
                bg_class = 'bg-blue-1' if is_active else ''

                with ui.card() \
                        .classes(f'w-full q-pa-xs cursor-pointer {bg_class}') \
                        .props('flat bordered') as card:
                    with ui.row().classes('items-center w-full no-wrap'):
                        with ui.column() \
                                .classes('flex-grow gap-0 overflow-hidden'):
                            ui.label(chat['title']).classes(
                                'text-body2 font-bold',
                            ).style(
                                'white-space: nowrap; overflow: hidden; '
                                'text-overflow: ellipsis;',
                            )
                            ui.label(chat['updated_at'][:10]).classes(
                                'text-caption text-grey-6',
                            )

                        def _make_delete(cid=chat['id'], ctitle=chat['title']):
                            def _do():
                                confirm_delete_chat(cid, ctitle)
                            return _do

                        ui.button(
                            icon='close',
                        ).on(
                            'click.stop', _make_delete(),
                        ).props('flat round dense size=sm color=negative')

                    def _make_load(cid=chat['id']):
                        return lambda: load_conversation(cid)

                    card.on('click', _make_load())

    def render_messages():
        """Clear and re-render all messages from chat_history."""
        messages.clear()
        with messages:
            ui.chat_message(
                "Ola! Eu sou o Gandalf-RAG, assistente do Knowledge OS. "
                "Me pergunte qualquer coisa sobre suas notas.",
                name=BOT_NAME,
                avatar=BOT_AVATAR,
                stamp='agora',
            )
            for msg in chat_history:
                if msg['role'] == 'user':
                    ui.chat_message(msg['content'], name='Voce', sent=True)
                elif msg['role'] == 'assistant':
                    with ui.chat_message(
                        name=BOT_NAME, avatar=BOT_AVATAR,
                    ):
                        ui.markdown(msg['content'])
                    sources = msg.get('sources', [])
                    if sources:
                        def _show(s=list(sources)):
                            _open_sources_dialog(s)

                        ui.button(
                            'Ver Fontes', icon='source',
                            on_click=_show,
                        ).props('flat dense size=sm color=primary')
        scroll.scroll_to(percent=1.0)

    def handle_new_chat():
        nonlocal current_chat_id
        if count_chats() >= MAX_CHATS:
            ui.notify(
                f'Limite de {MAX_CHATS} conversas atingido! '
                'Exclua uma conversa antes de criar uma nova.',
                type='warning',
            )
            return
        current_chat_id = None
        chat_history.clear()
        render_messages()
        render_chat_sidebar()

    def load_conversation(chat_id: str):
        nonlocal current_chat_id
        chat = get_chat(chat_id)
        if chat is None:
            ui.notify('Conversa nao encontrada.', type='negative')
            return
        current_chat_id = chat['id']
        chat_history.clear()
        chat_history.extend(chat['messages'])
        render_messages()
        render_chat_sidebar()

    def confirm_delete_chat(chat_id: str, chat_title: str):
        nonlocal current_chat_id

        with ui.dialog() as dlg, ui.card():
            ui.label(f'Excluir "{chat_title}"?').classes('text-h6')
            ui.label('Esta acao nao pode ser desfeita.')
            with ui.row().classes('q-mt-md gap-2'):
                ui.button('Cancelar', on_click=dlg.close).props('flat')

                def do_delete():
                    nonlocal current_chat_id
                    delete_chat(chat_id)
                    dlg.close()
                    if current_chat_id == chat_id:
                        current_chat_id = None
                        chat_history.clear()
                        render_messages()
                    render_chat_sidebar()

                ui.button(
                    'Excluir', color='negative', on_click=do_delete,
                ).props('flat')
        dlg.open()

    # Initial render
    render_messages()
    render_chat_sidebar()


def _open_sources_dialog(sources: list[dict]):
    """Abre um dialog popup minimalista exibindo as fontes usadas na resposta."""
    with ui.dialog() as dialog, \
            ui.card().classes('q-pa-md').style('min-width: 320px'):
        ui.label('Fontes') \
            .classes('text-subtitle1 text-weight-medium q-mb-sm')
        ui.separator()
        for src in sources:
            with ui.row().classes('items-center gap-2 q-py-xs'):
                icon = TYPE_ICONS.get(src.get('source_type', ''), 'lightbulb')
                ui.icon(icon, color='grey-7').classes('text-sm')
                title = src.get('title', 'Sem titulo')
                source_name = src.get('source_name', '')
                label = f'{title} — {source_name}' if source_name else title
                ui.label(label).classes('text-body2 text-grey-9')
        ui.separator().classes('q-mt-xs')
        with ui.row().classes('w-full justify-end q-mt-sm'):
            ui.button('Fechar', on_click=dialog.close) \
                .props('flat dense size=sm')
    dialog.open()
