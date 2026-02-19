from nicegui import ui

from components import create_sidebar

# Conteudo estatico de exemplo (sera substituido por uma LLM futuramente)
STATIC_RECOMMENDATIONS = [
    {
        'title': 'O Poder do Habito',
        'author': 'Charles Duhigg',
        'type': 'livro',
        'reason': 'Baseado nas suas notas sobre lideranca e comportamento, este livro complementa '
                  'seus estudos sobre como habitos moldam decisoes e produtividade.',
    },
    {
        'title': 'Deep Work: Rules for Focused Success in a Distracted World',
        'author': 'Cal Newport',
        'type': 'livro',
        'reason': 'Suas anotacoes mostram interesse em produtividade e aprendizado. '
                  'Este livro aprofunda tecnicas de concentracao e trabalho focado.',
    },
    {
        'title': 'Huberman Lab Podcast',
        'author': 'Andrew Huberman',
        'type': 'podcast',
        'reason': 'Com base no seu interesse em neurociencia e aprendizado, este podcast '
                  'traz pesquisas cientificas acessiveis sobre o funcionamento do cerebro.',
    },
    {
        'title': 'Crash Course - Psychology',
        'author': 'Hank Green',
        'type': 'video',
        'reason': 'Seus temas de estudo incluem comportamento humano. Esta serie de videos '
                  'oferece uma introducao completa a psicologia.',
    },
    {
        'title': 'O Projeto Aristoteles (Google)',
        'author': 'Google re:Work',
        'type': 'artigo',
        'reason': 'Suas notas sobre lideranca se conectam com esta pesquisa do Google sobre '
                  'o que torna equipes eficazes.',
    },
]

TYPE_ICONS = {
    'livro': 'menu_book',
    'video': 'play_circle',
    'artigo': 'article',
    'podcast': 'podcasts',
    'curso': 'school',
    'outro': 'lightbulb',
}


@ui.page('/recommendations')
def recommendations_page():
    create_sidebar()

    with ui.column().classes('w-full max-w-4xl mx-auto p-6'):
        ui.label('Recomendacoes').classes('text-h4 q-mb-md')

        # Banner de aviso
        with ui.element('div').classes(
            'w-full rounded-lg q-pa-md q-mb-lg flex items-start gap-3'
        ).style('background-color: #fff3cd; border: 1px solid #ffc107;'):
            ui.icon('warning', color='orange-9').classes('text-2xl mt-1')
            with ui.column().classes('gap-1'):
                ui.label('Pagina em desenvolvimento').classes('text-subtitle1 font-bold text-orange-9')
                ui.label(
                    'Esta pagina exibira recomendacoes personalizadas geradas por uma IA com base nas suas '
                    'ultimas 100 notas. O modulo de IA ainda nao esta conectado, entao o conteudo abaixo '
                    'e apenas ilustrativo para demonstrar o layout. Quando a integracao estiver pronta, '
                    'as recomendacoes serao geradas automaticamente analisando suas fontes, tags e temas '
                    'mais frequentes.'
                ).classes('text-body2 text-orange-10')

        # Lista de recomendacoes estaticas
        for rec in STATIC_RECOMMENDATIONS:
            icon = TYPE_ICONS.get(rec['type'], 'lightbulb')
            with ui.card().classes('w-full q-pa-md q-mb-sm'):
                with ui.row().classes('items-start gap-4 w-full'):
                    ui.icon(icon, color='primary').classes('text-3xl mt-1')
                    with ui.column().classes('flex-grow gap-1'):
                        ui.label(rec['title']).classes('text-h6')
                        with ui.row().classes('gap-3'):
                            ui.chip(rec['type'], color='primary').props('dense outline')
                            ui.label(f"por {rec['author']}").classes('text-caption text-grey-8')
                        ui.label(rec['reason']).classes('text-body2 text-grey-8 q-mt-xs')
