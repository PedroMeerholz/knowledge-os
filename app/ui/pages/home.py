from collections import Counter

from nicegui import ui

from app.ui.components import create_sidebar
from app.models import SOURCE_TYPES
from app.storage import load_notes, load_tags


@ui.page('/')
def home_page():
    create_sidebar()

    notes = load_notes()
    tags = load_tags()
    total_notes = len(notes)
    total_tags = len(tags)

    # Contar tipos de fontes
    type_counts = Counter(n.get('source_type', 'outro') for n in notes)
    # Fontes unicas
    unique_sources = {n.get('source_name', '') for n in notes if n.get('source_name', '').strip()}

    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-6'):

        # --- Cabecalho ---
        with ui.column().classes('w-full items-center text-center gap-2 q-mb-lg'):
            ui.icon('school', color='primary').classes('text-6xl')
            ui.label('Knowledge OS').classes('text-h3 font-bold')
            ui.label(
                'Seu sistema pessoal de gestao do conhecimento'
            ).classes('text-subtitle1 text-grey-7')

        # --- O que e ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Sobre o Sistema').classes('text-h5 q-mb-sm')
            ui.separator()
            ui.label(
                'O Knowledge OS e uma ferramenta pessoal para organizar, consultar e '
                'expandir o seu conhecimento. Ele resolve o problema de ter anotacoes '
                'espalhadas em diferentes lugares, sem conexao entre si e dificeis de '
                'recuperar. Com ele, voce centraliza suas notas, categoriza por tags e '
                'tipos de fonte, e visualiza padroes no seu aprendizado.'
            ).classes('text-body1 q-mt-sm')

        # --- Objetivos ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Objetivos').classes('text-h5 q-mb-sm')
            ui.separator()

            objectives = [
                ('edit_note', 'Registrar conhecimento',
                 'Salvar notas estruturadas com titulo, conteudo, fonte, autor e tags para nunca perder uma anotacao importante.'),
                ('search', 'Recuperar informacoes',
                 'Buscar e filtrar notas por texto, tipo de fonte ou tags, encontrando rapidamente o que voce precisa.'),
                ('pie_chart', 'Visualizar padroes',
                 'Entender quais tipos de fontes voce mais utiliza e identificar oportunidades de diversificar seu aprendizado.'),
                ('sell', 'Categorizar com tags',
                 'Criar e gerenciar tags para organizar suas notas por tema, facilitando a navegacao e a conexao entre assuntos.'),
                ('auto_awesome', 'Receber recomendacoes',
                 'Obter sugestoes de novas fontes de estudo com base nas suas perguntas e interesses (em desenvolvimento).'),
            ]

            for icon, title, description in objectives:
                with ui.row().classes('items-start gap-3 q-mt-md'):
                    ui.icon(icon, color='primary').classes('text-2xl mt-1')
                    with ui.column().classes('gap-0'):
                        ui.label(title).classes('text-subtitle1 font-bold')
                        ui.label(description).classes('text-body2 text-grey-8')

        # --- Estatisticas rapidas ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Resumo da Base').classes('text-h5 q-mb-sm')
            ui.separator()

            with ui.row().classes('w-full justify-around q-mt-md'):
                _stat_card('library_books', str(total_notes), 'Notas')
                _stat_card('sell', str(total_tags), 'Tags')
                _stat_card('source', str(len(unique_sources)), 'Fontes Unicas')
                _stat_card('category', str(len(type_counts)), 'Tipos de Fonte')



def _stat_card(icon: str, value: str, label: str):
    """Renderiza um card de estatistica."""
    with ui.column().classes('items-center gap-1'):
        ui.icon(icon, color='primary').classes('text-3xl')
        ui.label(value).classes('text-h4 font-bold')
        ui.label(label).classes('text-caption text-grey-7')
