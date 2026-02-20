---
title: Knowledge OS
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Knowledge OS | [Acessar Plataforma](https://huggingface.co/spaces/pedromeerholz/knowledge-os)

Sistema pessoal de gestao de conhecimento construido com Python e NiceGUI.

**Descrição do problema e da solução proposta**

O que o sistema faz? 
Qual problema resolve? 
Como a IA será integrada no futuro?

## O Problema

Quem estuda por diferentes fontes -- livros, videos, artigos, podcasts, cursos -- acaba com anotacoes espalhadas em cadernos, apps e arquivos soltos. Com o tempo, fica dificil:

- **Reencontrar** uma anotacao especifica feita meses atras
- **Saber de onde veio** cada informacao (qual livro, qual video, qual autor)
- **Enxergar padroes** nos proprios estudos (que tipo de fonte voce mais consome? quais temas domina?)
- **Descobrir lacunas** e receber sugestoes de novas fontes para estudar

## A Solucao (O que o sistema faz)

O Knowledge OS centraliza todas as suas anotacoes em um unico lugar com metadados ricos (fonte, autor, tipo, tags) e oferece ferramentas visuais para explorar e consultar sua base de conhecimento.

### Funcionalidades

| Pagina | Descricao |
|--------|-----------|
| **Nova Nota** | Formulario para criar notas com titulo, conteudo, tipo de fonte, nome da fonte, autor e tags |
| **Banco de Notas** | Lista todas as notas com busca por texto e filtro por tipo de fonte. Permite editar e excluir notas |
| **Gerenciar Tags** | Criacao e exclusao de tags para categorizar suas notas |
| **Mapa de Fontes** | Graficos (rosca e barras) mostrando a distribuicao dos tipos de fontes e tabela com todas as fontes utilizadas |
| **Chat & Recomendacoes** | Interface dividida: chat para consultar suas notas (lado esquerdo) e painel de recomendacoes de fontes geradas com base na sua pergunta (lado direito). Modulo de IA pendente — conteudo placeholder por enquanto |
| **Relatórios** | Gerar relatórios com IA com base nas notas cadastradas pelo usuário. O sistema requer pelo menos 10 notas por área de conhecimento para gerar o relatório |

## Arquitetura

```
knowledge-os/
├── main.py                # Ponto de entrada: importa paginas, define tema, inicia servidor
├── components.py          # Barra lateral de navegacao compartilhada
├── models.py              # Tipos de fonte e dataclass Note
├── storage.py             # Operacoes CRUD em JSON (notas e tags)
├── requirements.txt       # Dependencia: nicegui>=2.0.0
├── data/
│   ├── notes.json         # Banco de dados de notas (criado automaticamente)
│   └── tags.json          # Banco de dados de tags (criado automaticamente)
└── pages/
    ├── note_form.py       # Pagina: criar nova nota
    ├── notes_db.py        # Pagina: listar, buscar, editar e excluir notas
    ├── tags.py            # Pagina: gerenciar tags
    ├── fontmap.py         # Pagina: graficos e tabela de fontes
    └── knowledge_chat.py  # Pagina: chat + recomendacoes de fontes
```

### Stack Tecnica

- **Interface**: [NiceGUI](https://nicegui.io/) (Python, baseado em Vue.js/Quasar/FastAPI)
- **Banco de dados**: Arquivos JSON locais
- **Graficos**: Apache ECharts (via NiceGUI)

## Perguntas e Respostas

**Escolhas de design**
| Pergunta | Resposta |
| -------- | -------- |
| Por que essa arquitetura? | Optei por estas tecnologias por ter maior conhecimento técnico e experiência. Dessa forma, caso fosse necessário a intervenção manual no código, a manutenção seria mais eficaz | 
| Por que esses componentes de UI? | A escolha dos componentes foi realizada com base na premissa de manter o sistema com uma interface gráfica minimalista e intuitiva | 
| Que alternativas foram consideradas? | Considerei utilizar outros frameworks para criar a interface gráfica, como React e Vue.js. Porém, para manter todo o projeto em linguagem Python, optei por usar a biblioteca NiceGUI |

**O que funcionou?**
| Pergunta | Resposta |
| -------- | -------- |
| Quais partes o agente de codificação gerou bem? | O agente fez uma boa codificação ao criar as funcionalidades da interface gráfica |
| Onde a experiência foi positiva? | Desenvolvimento rápido e preciso |
| Exemplos específicos de prompts que deram bons resultados | Merge the chat page and recomendation page. On the left side, I want the chat and in the right side I want the recomendation system. Then, refactor the recomendation to be connected with the chat. When the user ask a question, the recommendation system search in web for knowledgements fonts to complement the user question. Each recommendation needs to have a short summary to help user to understand why the recommendation is available for him. |

**Evidência de Prompt (/data/readme)**

![Prompt inicial](/data/readme/Notes%20Claude%20Evidence.png "Optional title")

**O que não funcionou** 
| Pergunta | Resposta |
| -------- | -------- |
| Onde o agente falhou? | O agente apresentou alguns problemas de entendimento a respeito da construção de alguns elementos da interface gráfica, precisando refazer alguns componentes eventualmente | 
| O que precisou de intervenção manual? | Os nomes das páginas precisaram passar por uma revisão após a tradução para PT-BR, já que algumas não foram traduzidas corretamente ou poderiam recber nomes mais adequados ao contexto do sistema | 
| Quais limitações foram encontradas? O que seria feito diferente? | Acredito que prompts mais detalhados no momento da criação da interface gráfica poderiam ter ajudado o modelo a desempenhar melhor neste momento |

## Proximos Passos

- Integracao com LLM para o Chat de Conhecimento (busca semantica nas notas)
- Integracao com LLM + busca na web para Recomendacoes (analise da pergunta do usuario para sugerir fontes reais)
- Exportacao de notas (PDF, Markdown)
