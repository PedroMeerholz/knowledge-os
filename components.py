from nicegui import ui


def create_sidebar():
    """Barra lateral compartilhada com header e navegacao. Chamar dentro de cada @ui.page."""
    with ui.header().classes('bg-[#1a1a2e] items-center'):
        ui.button(icon='menu', on_click=lambda: drawer.toggle()) \
            .props('flat round color=white')
        ui.label('Knowledge OS').classes('text-h6 text-white q-ml-sm')

    drawer = ui.left_drawer(top_corner=True, bottom_corner=True, value=True) \
        .classes('bg-[#16213e]').style('width: 250px')

    with drawer:
        ui.label('MENU').classes('text-overline text-grey-5 q-pa-md')

        nav_items = [
            ('/', 'Nova Nota', 'add_circle'),
            ('/notes', 'Banco de Notas', 'library_books'),
            ('/tags', 'Gerenciar Tags', 'sell'),
            ('/fontmap', 'Mapa de Fontes', 'pie_chart'),
            ('/chat', 'Assistente Virtual', 'auto_awesome'),
        ]
        for path, label, icon in nav_items:
            ui.button(label, icon=icon,
                      on_click=lambda p=path: ui.navigate.to(p)) \
                .classes('w-full justify-start text-white q-my-xs') \
                .props('flat no-caps align=left')

    return drawer
