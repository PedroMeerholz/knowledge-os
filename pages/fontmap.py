from collections import Counter

from nicegui import ui

from components import create_sidebar
from storage import load_notes


@ui.page('/fontmap')
def fontmap_page():
    create_sidebar()

    with ui.column().classes('w-full max-w-5xl mx-auto p-6'):
        ui.label('Mapa de Fontes').classes('text-h4 q-mb-md')

        notes = load_notes()

        if not notes:
            with ui.card().classes('w-full q-pa-xl text-center'):
                ui.icon('info', size='xl', color='grey')
                ui.label('Nenhuma nota ainda. Crie algumas notas primeiro!') \
                    .classes('text-subtitle1 text-grey q-mt-md')
            return

        # Calcular agregacoes
        type_counts = Counter(n.get('source_type', 'outro') for n in notes)
        source_counts = Counter(
            (n.get('source_name', 'Desconhecido') or 'Desconhecido', n.get('source_type', 'outro'))
            for n in notes
        )

        # Linha de graficos
        with ui.row().classes('w-full gap-4 q-mb-lg flex-wrap'):
            # Grafico de rosca
            with ui.card().classes('flex-1 min-w-[300px]'):
                ui.label('Notas por Tipo de Fonte').classes('text-h6 q-pa-sm')
                ui.echart({
                    'tooltip': {'trigger': 'item', 'formatter': '{b}: {c} ({d}%)'},
                    'legend': {'orient': 'vertical', 'left': 'left'},
                    'series': [{
                        'name': 'Tipo de Fonte',
                        'type': 'pie',
                        'radius': ['40%', '70%'],
                        'avoidLabelOverlap': False,
                        'itemStyle': {
                            'borderRadius': 10,
                            'borderColor': '#fff',
                            'borderWidth': 2,
                        },
                        'label': {'show': True, 'formatter': '{b}: {c}'},
                        'data': [
                            {'value': count, 'name': stype}
                            for stype, count in type_counts.items()
                        ],
                    }],
                }).classes('w-full h-64')

            # Grafico de barras
            with ui.card().classes('flex-1 min-w-[300px]'):
                ui.label('Quantidade por Tipo de Fonte').classes('text-h6 q-pa-sm')
                sorted_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)
                ui.echart({
                    'tooltip': {'trigger': 'axis'},
                    'xAxis': {
                        'type': 'category',
                        'data': [t[0] for t in sorted_types],
                        'axisLabel': {'rotate': 30},
                    },
                    'yAxis': {'type': 'value', 'minInterval': 1},
                    'series': [{
                        'type': 'bar',
                        'data': [t[1] for t in sorted_types],
                        'itemStyle': {'borderRadius': [4, 4, 0, 0]},
                        'colorBy': 'data',
                    }],
                }).classes('w-full h-64')

        # Tabela de fontes
        ui.label('Todas as Fontes').classes('text-h6 q-mb-sm')
        source_rows = [
            {'source_name': name, 'source_type': stype, 'count': count}
            for (name, stype), count in sorted(source_counts.items(), key=lambda x: x[1], reverse=True)
        ]
        columns = [
            {'name': 'source_name', 'label': 'Nome da Fonte', 'field': 'source_name', 'align': 'left', 'sortable': True},
            {'name': 'source_type', 'label': 'Tipo', 'field': 'source_type', 'align': 'left', 'sortable': True},
            {'name': 'count', 'label': 'Qtd de Notas', 'field': 'count', 'align': 'center', 'sortable': True},
        ]
        ui.table(columns=columns, rows=source_rows, row_key='source_name') \
            .classes('w-full')
