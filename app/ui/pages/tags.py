from nicegui import ui

from app.ui.components import create_sidebar
from app.storage import load_tags, save_tag, delete_tag


@ui.page('/tags')
def tags_page():
    create_sidebar()

    with ui.column().classes('w-full max-w-3xl mx-auto p-6'):
        ui.label('Gerenciar Tags').classes('text-h4 q-mb-md')

        # --- Criar nova tag ---
        with ui.card().classes('w-full q-pa-lg q-mb-lg'):
            ui.label('Criar Nova Tag').classes('text-h6 q-mb-sm')
            with ui.row().classes('w-full gap-2 items-end'):
                tag_input = ui.input('Nome da tag', placeholder='Ex: python, neurociencia, historia') \
                    .classes('flex-grow').props('outlined dense')

                def handle_create():
                    val = (tag_input.value or '').strip()
                    if not val:
                        ui.notify('O nome da tag e obrigatório', type='warning')
                        return
                    result = save_tag(val)
                    if result is None:
                        ui.notify(f'A tag "{val.lower()}" já existe', type='warning')
                        return
                    ui.notify(f'Tag "{result["name"]}" criada com sucesso!', type='positive')
                    tag_input.value = ''
                    render_tags()

                ui.button('Criar', icon='add', on_click=handle_create) \
                    .props('color=positive dense')
                tag_input.on('keydown.enter', handle_create)

        # --- Lista de tags existentes ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Tags Existentes').classes('text-h6 q-mb-sm')
            tags_container = ui.column().classes('w-full gap-2')

        def render_tags():
            tags_container.clear()
            tags = load_tags()

            if not tags:
                with tags_container:
                    ui.label('Nenhuma tag criada ainda.').classes('text-subtitle1 text-grey')
                return

            with tags_container:
                with ui.row().classes('gap-2 flex-wrap'):
                    for tag in sorted(tags, key=lambda t: t['name']):
                        with ui.card().classes('q-pa-sm'):
                            with ui.row().classes('items-center gap-2'):
                                ui.icon('label', color='primary').classes('text-lg')
                                ui.label(tag['name']).classes('text-body1')

                                def make_delete(tid, tname):
                                    def do_delete():
                                        with ui.dialog() as dialog, ui.card():
                                            ui.label(f'Excluir tag "{tname}"?').classes('text-h6')
                                            ui.label('Isso não removerá a tag das notas existentes.')
                                            with ui.row().classes('q-mt-md gap-2'):
                                                ui.button('Cancelar', on_click=dialog.close).props('flat')
                                                ui.button('Excluir', color='negative',
                                                          on_click=lambda: (delete_tag(tid), dialog.close(), render_tags())) \
                                                    .props('flat')
                                        dialog.open()
                                    return do_delete

                                ui.button(icon='close', on_click=make_delete(tag['id'], tag['name'])) \
                                    .props('flat round dense size=sm color=negative')

        render_tags()
