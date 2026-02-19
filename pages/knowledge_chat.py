import random

from nicegui import ui

from components import create_sidebar
from storage import load_notes

# ---------------------------------------------------------------------------
# Respostas placeholder do chat
# ---------------------------------------------------------------------------
PLACEHOLDER_RESPONSES = [
    "Otima pergunta! Eu sou um bot placeholder -- nenhum backend de IA esta conectado ainda.",
    "Pensamento interessante! Em uma versao futura, eu poderia buscar nas suas notas por informacoes relevantes.",
    "Anotei sua pergunta. Quando um modelo de IA for conectado, vou te dar respostas reais.",
    "Boa ideia! Por enquanto, sou apenas um placeholder. Sua base de conhecimento tem {count} notas.",
    "Hmm, deixa eu pensar nisso... Brincadeira, sou um placeholder! Mas suas notas estao seguras.",
    "Isso parece fascinante! Quando o modulo de IA estiver pronto, vou poder te ajudar a explorar seu conhecimento.",
    "Otima pergunta! No momento so consigo responder com placeholders, mas suas notas estao sendo armazenadas.",
]

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
# Pool de recomendacoes estaticas
# ---------------------------------------------------------------------------
RECOMMENDATION_POOL = [
    {
        'title': 'O Poder do Habito',
        'author': 'Charles Duhigg',
        'type': 'livro',
        'reason': 'Explora como habitos moldam decisoes e produtividade no dia a dia.',
        'categories': ['habito', 'produtividade', 'comportamento'],
    },
    {
        'title': 'Deep Work',
        'author': 'Cal Newport',
        'type': 'livro',
        'reason': 'Tecnicas de concentracao e trabalho focado para aprendizado profundo.',
        'categories': ['produtividade', 'foco', 'aprendizado'],
    },
    {
        'title': 'Huberman Lab Podcast',
        'author': 'Andrew Huberman',
        'type': 'podcast',
        'reason': 'Pesquisas cientificas acessiveis sobre neurociencia e funcionamento do cerebro.',
        'categories': ['neurociencia', 'cerebro', 'ciencia', 'saude'],
    },
    {
        'title': 'Crash Course - Psychology',
        'author': 'Hank Green',
        'type': 'video',
        'reason': 'Introducao completa a psicologia com linguagem acessivel.',
        'categories': ['psicologia', 'comportamento', 'cerebro'],
    },
    {
        'title': 'O Projeto Aristoteles (Google)',
        'author': 'Google re:Work',
        'type': 'artigo',
        'reason': 'Pesquisa sobre o que torna equipes eficazes e produtivas.',
        'categories': ['lideranca', 'equipe', 'gestao'],
    },
    {
        'title': 'Atomic Habits',
        'author': 'James Clear',
        'type': 'livro',
        'reason': 'Metodo pratico para construir bons habitos e eliminar os ruins.',
        'categories': ['habito', 'produtividade', 'comportamento'],
    },
    {
        'title': 'O Monge e o Executivo',
        'author': 'James C. Hunter',
        'type': 'livro',
        'reason': 'Uma fabula sobre lideranca servidora e gestao de pessoas.',
        'categories': ['lideranca', 'gestao', 'equipe'],
    },
    {
        'title': 'TED Talk: How Great Leaders Inspire Action',
        'author': 'Simon Sinek',
        'type': 'video',
        'reason': 'Explica o conceito do Golden Circle e como lideres inspiram.',
        'categories': ['lideranca', 'comunicacao', 'inspiracao'],
    },
    {
        'title': 'O Gene Egoista',
        'author': 'Richard Dawkins',
        'type': 'livro',
        'reason': 'Visao evolutiva sobre comportamento e cooperacao entre seres vivos.',
        'categories': ['ciencia', 'biologia', 'comportamento'],
    },
    {
        'title': 'Lex Fridman Podcast',
        'author': 'Lex Fridman',
        'type': 'podcast',
        'reason': 'Conversas aprofundadas sobre tecnologia, IA, ciencia e filosofia.',
        'categories': ['tecnologia', 'ia', 'ciencia', 'filosofia'],
    },
    {
        'title': 'Se Trumbica na Programacao',
        'author': 'Fabio Akita',
        'type': 'video',
        'reason': 'Videos sobre carreira em tecnologia, programacao e aprendizado.',
        'categories': ['tecnologia', 'programacao', 'carreira'],
    },
    {
        'title': 'Clean Code',
        'author': 'Robert C. Martin',
        'type': 'livro',
        'reason': 'Principios e boas praticas para escrever codigo limpo e legivel.',
        'categories': ['programacao', 'tecnologia', 'engenharia'],
    },
    {
        'title': 'Coursera - Learning How to Learn',
        'author': 'Barbara Oakley',
        'type': 'curso',
        'reason': 'Curso sobre tecnicas de aprendizado baseadas em neurociencia.',
        'categories': ['aprendizado', 'neurociencia', 'produtividade'],
    },
    {
        'title': 'Sapiens: Uma Breve Historia da Humanidade',
        'author': 'Yuval Noah Harari',
        'type': 'livro',
        'reason': 'Panorama da historia humana conectando biologia, cultura e sociedade.',
        'categories': ['historia', 'filosofia', 'ciencia'],
    },
    {
        'title': 'Como Fazer Amigos e Influenciar Pessoas',
        'author': 'Dale Carnegie',
        'type': 'livro',
        'reason': 'Principios classicos de comunicacao e relacionamento interpessoal.',
        'categories': ['comunicacao', 'lideranca', 'comportamento'],
    },
    {
        'title': 'Podcast Naruhodo!',
        'author': 'B9',
        'type': 'podcast',
        'reason': 'Explora curiosidades cientificas e como o cerebro funciona.',
        'categories': ['ciencia', 'cerebro', 'curiosidade'],
    },
    {
        'title': 'Se Trumbica na Programacao',
        'author': 'Fabio Akita',
        'type': 'video',
        'reason': 'Conteudo tecnico sobre arquitetura de software e boas praticas.',
        'categories': ['programacao', 'tecnologia', 'engenharia'],
    },
    {
        'title': 'O Dilema da Inovacao',
        'author': 'Clayton Christensen',
        'type': 'livro',
        'reason': 'Analisa por que empresas bem-sucedidas podem falhar frente a inovacoes.',
        'categories': ['inovacao', 'gestao', 'tecnologia'],
    },
    {
        'title': 'Artigo: Spaced Repetition',
        'author': 'Gwern Branwen',
        'type': 'artigo',
        'reason': 'Analise detalhada sobre repeticao espacada como tecnica de memorizacao.',
        'categories': ['aprendizado', 'memoria', 'produtividade'],
    },
    {
        'title': 'Mindset: A Nova Psicologia do Sucesso',
        'author': 'Carol Dweck',
        'type': 'livro',
        'reason': 'Pesquisa sobre mentalidade fixa vs. de crescimento e impacto no desempenho.',
        'categories': ['psicologia', 'aprendizado', 'comportamento'],
    },
]

# ---------------------------------------------------------------------------
# Mapeamento de palavras-chave para categorias
# ---------------------------------------------------------------------------
KEYWORD_MAP = {
    'lider': 'lideranca',
    'lideranca': 'lideranca',
    'gestao': 'gestao',
    'gerenciar': 'gestao',
    'equipe': 'equipe',
    'time': 'equipe',
    'habito': 'habito',
    'rotina': 'habito',
    'produtividade': 'produtividade',
    'foco': 'foco',
    'concentracao': 'foco',
    'cerebro': 'cerebro',
    'neuro': 'neurociencia',
    'neurociencia': 'neurociencia',
    'psicologia': 'psicologia',
    'comportamento': 'comportamento',
    'ciencia': 'ciencia',
    'programacao': 'programacao',
    'codigo': 'programacao',
    'software': 'programacao',
    'tecnologia': 'tecnologia',
    'ia': 'ia',
    'inteligencia artificial': 'ia',
    'aprendizado': 'aprendizado',
    'aprender': 'aprendizado',
    'estudar': 'aprendizado',
    'estudo': 'aprendizado',
    'comunicacao': 'comunicacao',
    'historia': 'historia',
    'filosofia': 'filosofia',
    'inovacao': 'inovacao',
    'memoria': 'memoria',
    'livro': 'livro',
    'podcast': 'podcast',
    'video': 'video',
    'curso': 'curso',
    'saude': 'saude',
    'biologia': 'biologia',
}


def generate_placeholder_recommendations(message: str) -> list[dict]:
    """Gera recomendacoes placeholder baseadas em palavras-chave da mensagem."""
    text = message.lower()
    matched_categories = set()
    for keyword, category in KEYWORD_MAP.items():
        if keyword in text:
            matched_categories.add(category)

    if matched_categories:
        scored = []
        for rec in RECOMMENDATION_POOL:
            overlap = len(matched_categories & set(rec['categories']))
            if overlap > 0:
                scored.append((overlap, rec))
        scored.sort(key=lambda x: x[0], reverse=True)
        results = [r for _, r in scored[:5]]
        if results:
            return results

    return random.sample(RECOMMENDATION_POOL, min(4, len(RECOMMENDATION_POOL)))


# ---------------------------------------------------------------------------
# Pagina principal
# ---------------------------------------------------------------------------
@ui.page('/chat')
def knowledge_chat_page():
    create_sidebar()

    with ui.column().classes('w-full p-4').style('height: calc(100vh - 4rem)'):
        ui.label('Assitente Virtual').classes('text-h4 q-mb-md')

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
                            "ao lado, voce vera recomendacoes de fontes relacionadas a sua pergunta. "
                            "(Aviso: A IA ainda nao esta conectada — as respostas sao placeholders.)",
                            name='KnowledgeBot',
                            stamp='agora',
                        )

                with ui.row().classes('w-full gap-2 q-mt-sm items-center'):
                    msg_input = ui.input(placeholder='Digite uma mensagem...') \
                        .classes('flex-grow').props('outlined dense')

                    def send():
                        text = (msg_input.value or '').strip()
                        if not text:
                            return

                        with messages:
                            ui.chat_message(text, name='Voce', sent=True)

                        msg_input.value = ''

                        count = len(load_notes())
                        response = random.choice(PLACEHOLDER_RESPONSES).format(count=count)
                        with messages:
                            ui.chat_message(response, name='KnowledgeBot')

                        scroll.scroll_to(percent=1.0)

                        update_recommendations(text)

                    ui.button(icon='send', on_click=send) \
                        .props('round color=primary')
                    msg_input.on('keydown.enter', send)

            # ---- LADO DIREITO: Recomendacoes ----
            with ui.column().classes('flex-[2] min-w-0') \
                    .style('height: 100%'):
                ui.label('Recomendacoes').classes('text-h6 q-mb-sm')

                # Banner de aviso
                with ui.element('div').classes(
                    'w-full rounded-lg q-pa-sm q-mb-sm flex items-start gap-2'
                ).style('background-color: #fff3cd; border: 1px solid #ffc107;'):
                    ui.icon('warning', color='orange-9').classes('text-xl mt-1')
                    with ui.column().classes('gap-0'):
                        ui.label('Em desenvolvimento').classes(
                            'text-subtitle2 font-bold text-orange-9'
                        )
                        ui.label(
                            'Futuramente, este painel usara IA para '
                            'recomendar fontes de estudo com base na sua pergunta. '
                            'Por enquanto, as recomendacoes abaixo sao ilustrativas.'
                        ).classes('text-caption text-orange-10')

                rec_scroll = ui.scroll_area().classes('flex-grow w-full')
                rec_container = ui.column().classes('w-full gap-2 q-pa-xs')
                rec_scroll.content = rec_container

                with rec_container:
                    _render_recommendations(
                        random.sample(RECOMMENDATION_POOL,
                                      min(4, len(RECOMMENDATION_POOL)))
                    )

    def update_recommendations(text: str):
        recs = generate_placeholder_recommendations(text)
        rec_container.clear()
        with rec_container:
            _render_recommendations(recs)


def _render_recommendations(recs: list[dict]):
    """Renderiza cards de recomendacao dentro do container atual."""
    for rec in recs:
        icon = TYPE_ICONS.get(rec['type'], 'lightbulb')
        with ui.card().classes('w-full q-pa-sm'):
            with ui.row().classes('items-start gap-3 w-full'):
                ui.icon(icon, color='primary').classes('text-2xl mt-1')
                with ui.column().classes('flex-grow gap-0'):
                    ui.label(rec['title']).classes('text-subtitle1 font-bold')
                    with ui.row().classes('gap-2 items-center'):
                        ui.chip(rec['type'], color='primary') \
                            .props('dense outline size=sm')
                        ui.label(f"por {rec['author']}") \
                            .classes('text-caption text-grey-8')
                    ui.label(rec['reason']) \
                        .classes('text-caption text-grey-8 q-mt-xs')
