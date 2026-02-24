from nicegui import ui

from app.ui.components import create_sidebar
from app.models import SOURCE_TYPES
from app.storage import load_notes, delete_note, update_note, load_tags


@ui.page('/notes')
def notes_page():
    create_sidebar()

    with ui.column().classes('w-full max-w-5xl mx-auto p-6'):
        ui.label('Banco de Notas').classes('text-h4 q-mb-md')

        with ui.row().classes('w-full gap-4 q-mb-md items-end'):
            search_input = ui.input('Buscar', placeholder='Buscar por titulo, conteudo ou tags') \
                .classes('flex-grow').props('outlined clearable dense')
            filter_select = ui.select(
                ['Todos'] + SOURCE_TYPES,
                value='Todos',
                label='Filtrar por fonte',
            ).classes('w-48').props('outlined dense')

        notes_container = ui.column().classes('w-full gap-2')

        def open_edit_dialog(note):
            edit_tags: list[str] = list(note.get('tags', []))

            with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl'):
                ui.label('Editar Nota').classes('text-h5 q-mb-md')

                edit_title = ui.input('Titulo', value=note['title']) \
                    .classes('w-full').props('outlined')

                edit_content = ui.textarea('Conteudo', value=note.get('content', '')) \
                    .classes('w-full').props('outlined autogrow input-style="min-height: 150px"')

                edit_source_type = ui.select(
                    SOURCE_TYPES,
                    value=note.get('source_type', 'artigo'),
                    label='Tipo de Fonte',
                ).classes('w-full').props('outlined')

                edit_source_name = ui.input('Nome da Fonte', value=note.get('source_name', '')) \
                    .classes('w-full').props('outlined')

                edit_source_author = ui.input('Autor da Fonte', value=note.get('source_author', '')) \
                    .classes('w-full').props('outlined')

                # --- Secao de Tags ---
                ui.separator().classes('q-my-sm')
                ui.label('Tags').classes('text-subtitle2 font-bold')

                ui.label('Selecionadas:').classes('text-caption text-grey q-mt-xs')
                selected_container = ui.row().classes('gap-1 flex-wrap min-h-[32px]')

                ui.label('Selecione das tags existentes:').classes('text-caption text-grey q-mt-xs')
                existing_container = ui.row().classes('gap-1 flex-wrap min-h-[32px]')

                def refresh_edit_selected():
                    selected_container.clear()
                    if not edit_tags:
                        with selected_container:
                            ui.label('Nenhuma tag selecionada').classes('text-caption text-grey-5 italic')
                        return
                    for tag_name in sorted(edit_tags):
                        with selected_container:
                            ui.chip(tag_name, icon='check', color='positive',
                                    removable=True, on_value_change=lambda ev, t=tag_name:
                                        (edit_tags.remove(t), refresh_edit_selected(), refresh_edit_existing())
                                        if not ev.value else None)

                def refresh_edit_existing():
                    existing_container.clear()
                    all_tags = load_tags()
                    available = [t for t in all_tags if t['name'] not in edit_tags]
                    if not available:
                        with existing_container:
                            label_text = 'Todas as tags selecionadas' if all_tags else 'Nenhuma tag disponivel'
                            ui.label(label_text).classes('text-caption text-grey-5 italic')
                        return
                    for tag in sorted(available, key=lambda t: t['name']):
                        with existing_container:
                            def make_select(t):
                                def select():
                                    if t not in edit_tags:
                                        edit_tags.append(t)
                                        refresh_edit_selected()
                                        refresh_edit_existing()
                                return select
                            ui.chip(tag['name'], icon='add', color='primary',
                                    on_click=make_select(tag['name'])) \
                                .props('clickable outline')

                refresh_edit_selected()
                refresh_edit_existing()

                ui.separator().classes('q-my-sm')

                # --- Botoes de acao ---
                with ui.row().classes('w-full justify-end gap-2 q-mt-md'):
                    ui.button('Cancelar', on_click=dialog.close).props('flat')
                    def handle_save():
                        if not edit_title.value or not edit_title.value.strip():
                            ui.notify('O titulo e obrigatorio', type='warning')
                            return
                        if not edit_content.value or not edit_content.value.strip():
                            ui.notify('O conteudo e obrigatorio', type='warning')
                            return
                        update_note(
                            note_id=note['id'],
                            title=edit_title.value,
                            content=edit_content.value,
                            source_type=edit_source_type.value,
                            source_name=edit_source_name.value or '',
                            source_author=edit_source_author.value or '',
                            tags=list(edit_tags),
                        )
                        ui.notify('Nota atualizada com sucesso!', type='positive')
                        dialog.close()
                        render_notes()

                    ui.button('Salvar', icon='save', on_click=handle_save) \
                        .props('color=positive')

            dialog.open()

        def render_notes():
            notes_container.clear()
            notes = load_notes()
            query = (search_input.value or '').lower().strip()
            source_filter = filter_select.value

            filtered = []
            for note in reversed(notes):  # mais recentes primeiro
                if query:
                    searchable = f"{note['title']} {note['content']} {' '.join(note.get('tags', []))}".lower()
                    if query not in searchable:
                        continue
                if source_filter != 'Todos' and note.get('source_type') != source_filter:
                    continue
                filtered.append(note)

            if not filtered:
                with notes_container:
                    ui.label('Nenhuma nota encontrada.').classes('text-subtitle1 text-grey q-pa-lg')
                return

            for note in filtered:
                with notes_container:
                    caption = f"{note.get('source_type', '')} | {', '.join(note.get('tags', []))} | {note.get('created_at', '')[:10]}"
                    with ui.expansion(
                        text=note['title'],
                        caption=caption,
                        icon='description',
                    ).classes('w-full bg-grey-1'):
                        ui.markdown(note.get('content', '')).classes('q-pa-md')

                        with ui.row().classes('q-pa-sm gap-4'):
                            ui.label(f"Fonte: {note.get('source_name') or 'N/A'}") \
                                .classes('text-caption text-grey-8')
                            ui.label(f"Autor: {note.get('source_author') or 'N/A'}") \
                                .classes('text-caption text-grey-8')
                            ui.label(f"Tipo: {note.get('source_type', '')}") \
                                .classes('text-caption text-grey-8')
                            ui.label(f"Criado em: {note.get('created_at', '')}") \
                                .classes('text-caption text-grey-8')

                        if note.get('tags'):
                            with ui.row().classes('gap-1 q-pa-sm'):
                                for tag in note['tags']:
                                    ui.chip(tag, color='primary').props('dense outline')

                        with ui.row().classes('q-pa-sm gap-2'):
                            def make_edit(n):
                                return lambda: open_edit_dialog(n)

                            ui.button('Editar', icon='edit', color='primary',
                                      on_click=make_edit(note)).props('flat dense')

                            def make_delete(nid):
                                def do_delete():
                                    with ui.dialog() as dlg, ui.card():
                                        ui.label('Excluir esta nota?').classes('text-h6')
                                        ui.label('Esta acao nao pode ser desfeita.')
                                        with ui.row().classes('q-mt-md gap-2'):
                                            ui.button('Cancelar', on_click=dlg.close).props('flat')
                                            ui.button('Excluir', color='negative',
                                                      on_click=lambda: (delete_note(nid), dlg.close(), render_notes())) \
                                                .props('flat')
                                    dlg.open()
                                return do_delete

                            ui.button('Excluir', icon='delete', color='negative',
                                      on_click=make_delete(note['id'])).props('flat dense')

        search_input.on('update:model-value', lambda _: render_notes())
        filter_select.on('update:model-value', lambda _: render_notes())

        render_notes()
