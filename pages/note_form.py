from datetime import datetime

from nicegui import ui

from components import create_sidebar
from models import SOURCE_TYPES
from storage import save_note, load_tags


@ui.page('/')
def index():
    create_sidebar()

    with ui.column().classes('w-full max-w-2xl mx-auto p-6'):
        ui.label('Criar Nova Nota').classes('text-h4 q-mb-md')

        with ui.card().classes('w-full q-pa-lg'):
            title_input = ui.input('Titulo', placeholder='Titulo da nota') \
                .classes('w-full').props('outlined')

            content_input = ui.textarea('Conteudo', placeholder='Escreva sua nota...') \
                .classes('w-full').props('outlined autogrow input-style="min-height: 200px"')

            source_type_select = ui.select(
                SOURCE_TYPES,
                value='artigo',
                label='Tipo de Fonte',
            ).classes('w-full').props('outlined')

            source_name_input = ui.input(
                'Nome da Fonte',
                placeholder='Ex: Titulo do livro, URL, nome do canal',
            ).classes('w-full').props('outlined')

            source_author_input = ui.input(
                'Autor da Fonte',
                placeholder='Ex: Nome do autor, criador, instrutor',
            ).classes('w-full').props('outlined')

            # --- Secao de Tags ---
            ui.separator().classes('q-my-md')
            ui.label('Tags').classes('text-subtitle1 font-bold')

            selected_tags: list[str] = []

            # Tags selecionadas
            ui.label('Selecionadas:').classes('text-caption text-grey q-mt-sm')
            selected_container = ui.row().classes('gap-1 flex-wrap min-h-[32px]')

            def refresh_selected():
                selected_container.clear()
                if not selected_tags:
                    with selected_container:
                        ui.label('Nenhuma tag selecionada').classes('text-caption text-grey-5 italic')
                    return
                for tag_name in sorted(selected_tags):
                    with selected_container:
                        def make_deselect(t):
                            def deselect():
                                selected_tags.remove(t)
                                refresh_selected()
                                refresh_existing()
                            return deselect
                        ui.chip(tag_name, icon='check', color='positive',
                                removable=True, on_value_change=lambda ev, t=tag_name:
                                    (selected_tags.remove(t), refresh_selected(), refresh_existing())
                                    if not ev.value else None)

            # Tags existentes para selecionar
            ui.label('Selecione das tags existentes:').classes('text-caption text-grey q-mt-sm')
            existing_container = ui.row().classes('gap-1 flex-wrap min-h-[32px]')

            def refresh_existing():
                existing_container.clear()
                all_tags = load_tags()
                available = [t for t in all_tags if t['name'] not in selected_tags]
                if not available:
                    with existing_container:
                        label_text = 'Todas as tags selecionadas' if all_tags else 'Nenhuma tag ainda — crie em Gerenciar Tags'
                        ui.label(label_text).classes('text-caption text-grey-5 italic')
                    return
                for tag in sorted(available, key=lambda t: t['name']):
                    with existing_container:
                        def make_select(t):
                            def select():
                                if t not in selected_tags:
                                    selected_tags.append(t)
                                    refresh_selected()
                                    refresh_existing()
                            return select
                        ui.chip(tag['name'], icon='add', color='primary',
                                on_click=make_select(tag['name'])) \
                            .props('clickable outline')

            # Renderizacao inicial
            refresh_selected()
            refresh_existing()

            ui.separator().classes('q-my-md')

            ui.label(f'Data: {datetime.now().strftime("%d/%m/%Y %H:%M")}') \
                .classes('text-caption text-grey q-mt-sm')

            def handle_save():
                if not title_input.value or not title_input.value.strip():
                    ui.notify('O titulo e obrigatorio', type='warning')
                    return
                if not content_input.value or not content_input.value.strip():
                    ui.notify('O conteudo e obrigatorio', type='warning')
                    return

                save_note(
                    title=title_input.value,
                    content=content_input.value,
                    source_type=source_type_select.value,
                    source_name=source_name_input.value or '',
                    source_author=source_author_input.value or '',
                    tags=list(selected_tags),
                )
                ui.notify('Nota salva com sucesso!', type='positive')

                # Limpar formulario
                title_input.value = ''
                content_input.value = ''
                source_type_select.value = 'artigo'
                source_name_input.value = ''
                source_author_input.value = ''
                selected_tags.clear()
                refresh_selected()
                refresh_existing()

            ui.button('Salvar Nota', icon='save', on_click=handle_save) \
                .classes('q-mt-md').props('color=positive size=lg')
