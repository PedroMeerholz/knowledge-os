import random

from nicegui import ui

from components import create_sidebar
from storage import load_notes

PLACEHOLDER_RESPONSES = [
    "Otima pergunta! Eu sou um bot placeholder -- nenhum backend de IA esta conectado ainda.",
    "Pensamento interessante! Em uma versao futura, eu poderia buscar nas suas notas por informacoes relevantes.",
    "Anotei sua pergunta. Quando um modelo de IA for conectado, vou te dar respostas reais.",
    "Boa ideia! Por enquanto, sou apenas um placeholder. Sua base de conhecimento tem {count} notas.",
    "Hmm, deixa eu pensar nisso... Brincadeira, sou um placeholder! Mas suas notas estao seguras.",
    "Isso parece fascinante! Quando o modulo de IA estiver pronto, vou poder te ajudar a explorar seu conhecimento.",
    "Otima pergunta! No momento so consigo responder com placeholders, mas suas notas estao sendo armazenadas.",
]


@ui.page('/chat')
def chat_page():
    create_sidebar()

    with ui.column().classes('w-full max-w-3xl mx-auto p-6') \
            .style('height: calc(100vh - 4rem)'):
        ui.label('Chat de Conhecimento').classes('text-h4 q-mb-md')

        with ui.scroll_area().classes('flex-grow w-full border rounded-lg bg-grey-1') as scroll:
            messages = ui.column().classes('w-full q-pa-md gap-2')
            with messages:
                ui.chat_message(
                    "Ola! Eu sou o assistente do Knowledge OS. "
                    "Me pergunte qualquer coisa sobre suas notas. "
                    "(Aviso: A IA ainda nao esta conectada -- as respostas sao placeholders.)",
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

            send_btn = ui.button(icon='send', on_click=send) \
                .props('round color=primary')
            msg_input.on('keydown.enter', send)
