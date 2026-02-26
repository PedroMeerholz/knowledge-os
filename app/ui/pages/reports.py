from collections import Counter

from nicegui import ui

from app.ui.components import create_sidebar
from app.storage import load_notes, load_tags

MIN_NOTES_PER_TAG = 10

# ---------------------------------------------------------------------------
# Relatórios mockados por tag (usados quando a tag atinge o mínimo de notas)
# ---------------------------------------------------------------------------
MOCK_REPORTS = {
    'leadership': {
        'title': 'Relatório: Lideranca',
        'summary': (
            'Com base nas suas anotações sobre lideranca, identificamos que você tem '
            'explorado principalmente os conceitos de lideranca servidora e gestão de '
            'equipes. Suas fontes combinam livros clássicos com conteúdos em vídeo, '
            'indicando uma abordagem diversificada de aprendizado.'
        ),
        'insights': [
            'Tema recorrente: a importância da escuta ativa e empatia na gestão de pessoas.',
            'Fontes mais utilizadas: livros e vídeos, com predominância de autores norte-americanos.',
            'Lacuna identificada: poucas notas sobre lideranca em contextos de tecnologia e startups.',
        ],
        'suggestion': (
            'Considere explorar conteúdos sobre lideranca técnica e gestão de equipes ágeis '
            'para complementar sua base de conhecimento atual.'
        ),
    },
    'programacao': {
        'title': 'Relatório: Programação',
        'summary': (
            'Suas notas sobre programação cobrem boas práticas de código, arquitetura de '
            'software e carreira em tecnologia. Há uma concentracao em fontes do tipo vídeo '
            'e livro, com menor presenca de artigos técnicos.'
        ),
        'insights': [
            'Foco principal: clean code, principios SOLID e boas práticas de engenharia.',
            'Fontes diversificadas entre livros, vídeos e cursos online.',
            'Pouca cobertura de tópicos como testes automatizados e DevOps.',
        ],
        'suggestion': (
            'Ampliar o estudo com artigos técnicos e documentacao oficial pode trazer '
            'uma perspectiva mais pratica e atualizada.'
        ),
    },
    'psicologia': {
        'title': 'Relatório: Psicologia',
        'summary': (
            'O conjunto de notas sobre psicologia abrange comportamento humano, '
            'neurociência aplicada e técnicas de aprendizado. Você demonstra interesse '
            'em entender como o cérebro processa informacoes e forma hábitos.'
        ),
        'insights': [
            'Tema central: conexão entre psicologia cognitiva e produtividade pessoal.',
            'Boa variedade de fontes: podcasts, vídeos e livros acadêmicos.',
            'Oportunidade: explorar psicologia organizacional e dinâmicas de grupo.',
        ],
        'suggestion': (
            'Aprofundar em psicologia comportamental aplicada ao trabalho pode '
            'conectar esses aprendizados com suas notas sobre lideranca.'
        ),
    },
}

# Relatório generico para tags sem mock especifico
DEFAULT_MOCK_REPORT = {
    'summary': (
        'Este relatório foi gerado com base nas suas anotações sobre o tema "{tag}". '
        'A análise identificou padrões nas fontes utilizadas, temas recorrentes e '
        'possibilidades de aprofundamento.'
    ),
    'insights': [
        'As notas cobrem diferentes tipos de fonte, indicando aprendizado diversificado.',
        'Foram identificados subtemas que se conectam com outras areas do seu conhecimento.',
        'Há espaco para explorar fontes complementares como artigos e cursos especializados.',
    ],
    'suggestion': (
        'Considere revisar suas notas mais antigas sobre "{tag}" e buscar fontes '
        'atualizadas para manter seu conhecimento relevante.'
    ),
}


def _count_notes_per_tag(notes: list[dict]) -> dict[str, int]:
    """Retorna um dicionario com a contagem de notas por tag."""
    counts: dict[str, int] = Counter()
    for note in notes:
        for tag in note.get('tags', []):
            counts[tag] += 1
    return dict(counts)


def _get_mock_report(tag: str) -> dict:
    """Retorna o relatório mockado para uma tag."""
    if tag in MOCK_REPORTS:
        return MOCK_REPORTS[tag]
    return {
        'title': f'Relatório: {tag.capitalize()}',
        'summary': DEFAULT_MOCK_REPORT['summary'].format(tag=tag),
        'insights': list(DEFAULT_MOCK_REPORT['insights']),
        'suggestion': DEFAULT_MOCK_REPORT['suggestion'].format(tag=tag),
    }


@ui.page('/reports')
def reports_page():
    create_sidebar()

    notes = load_notes()
    tag_counts = _count_notes_per_tag(notes)
    all_tags = sorted(tag_counts.keys())

    with ui.column().classes('w-full max-w-4xl mx-auto p-6 gap-6'):
        ui.label('Relatórios').classes('text-h4 q-mb-md')

        # --- Banner explicativo ---
        with ui.element('div').classes(
            'w-full rounded-lg q-pa-md flex items-start gap-3'
        ).style('background-color: #fff3cd; border: 1px solid #ffc107;'):
            ui.icon('warning', color='orange-9').classes('text-2xl mt-1')
            with ui.column().classes('gap-1'):
                ui.label('Em desenvolvimento').classes(
                    'text-subtitle1 font-bold text-orange-9'
                )
                ui.label(
                    'Futuramente, esta página usara IA (LLM) para analisar suas notas '
                    'e gerar relatórios de conhecimento automaticamente. O modelo irá ler '
                    'o conteúdo completo das suas notas agrupadas por tag, identificar '
                    'padrões, temas recorrentes, lacunas e sugerir próximos passos de '
                    'estudo. Por enquanto, os relatórios abaixo são ilustrativos.'
                ).classes('text-body2 text-orange-10')

        # --- Como funciona ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Como funciona').classes('text-h6 q-mb-sm')
            ui.separator()
            with ui.column().classes('gap-2 q-mt-sm'):
                steps = [
                    ('looks_one', f'Cada tag precisa ter no mínimo {MIN_NOTES_PER_TAG} notas para desbloquear a geração de relatório.'),
                    ('looks_two', 'Ao clicar em "Gerar Relatório", a IA analisa todas as notas daquela tag.'),
                    ('looks_3', 'O relatório apresenta um resumo, insights principais e sugestões de estudo.'),
                    ('looks_4', 'Você pode gerar relatórios para diferentes tags e acompanhar sua evolução.'),
                ]
                for icon, text in steps:
                    with ui.row().classes('items-start gap-2'):
                        ui.icon(icon, color='primary').classes('text-xl mt-1')
                        ui.label(text).classes('text-body2')

        # --- Status das tags ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Status das Tags').classes('text-h6 q-mb-sm')
            ui.separator()

            if not all_tags:
                ui.label(
                    'Nenhuma tag encontrada. Crie tags e adicione notas para desbloquear relatórios.'
                ).classes('text-body2 text-grey-6 italic q-mt-md')
            else:
                with ui.column().classes('w-full gap-3 q-mt-md'):
                    for tag in all_tags:
                        count = tag_counts[tag]
                        available = count >= MIN_NOTES_PER_TAG
                        progress = min(count / MIN_NOTES_PER_TAG, 1.0)

                        with ui.row().classes('w-full items-center gap-3'):
                            ui.chip(tag, color='positive' if available else 'grey-5') \
                                .props('dense outline' if not available else 'dense')
                            with ui.column().classes('flex-grow gap-0'):
                                ui.linear_progress(
                                    value=progress,
                                    color='positive' if available else 'grey-5',
                                ).props('rounded size=8px')
                                ui.label(
                                    f'{count}/{MIN_NOTES_PER_TAG} notas'
                                ).classes('text-caption text-grey-7')
                            if available:
                                def make_generate(t):
                                    def generate():
                                        _show_report_dialog(t)
                                    return generate
                                ui.button('Gerar Relatório', icon='description',
                                          on_click=make_generate(tag)) \
                                    .props('color=primary size=sm no-caps')
                            else:
                                ui.icon('lock', color='grey-5').classes('text-xl') \
                                    .tooltip(f'Faltam {MIN_NOTES_PER_TAG - count} notas para desbloquear')

        # --- Relatório placeholder de exemplo ---
        with ui.card().classes('w-full q-pa-lg'):
            ui.label('Exemplo de Relatório').classes('text-h6 q-mb-sm')
            ui.separator()
            ui.label(
                'Abaixo está um exemplo do formato de relatório que será gerado pela IA '
                'quando o módulo estiver conectado.'
            ).classes('text-caption text-grey-7 q-mt-xs q-mb-md')
            _render_report(_get_mock_report('leadership'))


def _show_report_dialog(tag: str):
    """Abre um dialog com o relatório mockado da tag."""
    report = _get_mock_report(tag)
    with ui.dialog() as dialog, ui.card().classes('w-full max-w-2xl q-pa-lg'):
        _render_report(report)
        ui.separator().classes('q-my-md')
        ui.label(
            'Este relatório é apenas um exemplo ilustrativo. '
            'Quando o módulo de IA for integrado, o conteúdo será gerado '
            'automaticamente com base nas suas notas.'
        ).classes('text-caption text-grey-6 italic')
        ui.button('Fechar', icon='close', on_click=dialog.close) \
            .classes('q-mt-md').props('color=primary no-caps')
    dialog.open()


def _render_report(report: dict):
    """Renderiza o conteúdo de um relatório dentro do container atual."""
    ui.label(report['title']).classes('text-h6 font-bold text-primary')

    # Resumo
    with ui.row().classes('items-start gap-2 q-mt-md'):
        ui.icon('summarize', color='primary').classes('text-xl mt-1')
        with ui.column().classes('gap-0'):
            ui.label('Resumo').classes('text-subtitle2 font-bold')
            ui.label(report['summary']).classes('text-body2 text-grey-8')

    # Insights
    with ui.row().classes('items-start gap-2 q-mt-md'):
        ui.icon('lightbulb', color='warning').classes('text-xl mt-1')
        with ui.column().classes('gap-1'):
            ui.label('Insights Principais').classes('text-subtitle2 font-bold')
            for insight in report['insights']:
                with ui.row().classes('items-start gap-1'):
                    ui.label('•').classes('text-body2')
                    ui.label(insight).classes('text-body2 text-grey-8')

    # Sugestão
    with ui.row().classes('items-start gap-2 q-mt-md'):
        ui.icon('trending_up', color='positive').classes('text-xl mt-1')
        with ui.column().classes('gap-0'):
            ui.label('Sugestão de Próximo Passo').classes('text-subtitle2 font-bold')
            ui.label(report['suggestion']).classes('text-body2 text-grey-8')
