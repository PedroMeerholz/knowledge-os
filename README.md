---
title: Knowledge OS
emoji: 🚀
colorFrom: blue
colorTo: indigo
sdk: docker
pinned: false
---

# Knowledge OS

Sistema pessoal de gestão de conhecimento construído com Python e NiceGUI.

## O Problema

Quem estuda por diferentes fontes -- livros, vídeos, artigos, podcasts, cursos -- acaba com anotacoes espalhadas em cadernos, apps e arquivos soltos. Com o tempo, fica difícil:

- **Reencontrar** uma anotação específica feita meses atrás
- **Saber de onde veio** cada informação (qual livro, qual vídeo, qual autor)
- **Enxergar padrões** nos proprios estudos (que tipo de fonte você mais consome? quais temas domina?)
- **Descobrir lacunas** e receber sugestões de novas fontes para estudar

## A Solucao (O que o sistema faz)

O Knowledge OS centraliza todas as suas anotacoes em um único lugar com metadados ricos (fonte, autor, tipo, tags) e oferece ferramentas visuais para explorar e consultar sua base de conhecimento.

### Funcionalidades

| Página | Descrição |
|--------|-----------|
| **Nova Nota** | Formulário para criar notas com título, conteúdo, tipo de fonte, nome da fonte, autor e tags |
| **Banco de Notas** | Lista todas as notas com busca por texto e filtro por tipo de fonte. Permite editar e excluir notas |
| **Gerenciar Tags** | Criação e exclusão de tags para categorizar suas notas |
| **Mapa de Fontes** | Gráficos (rosca e barras) mostrando a distribuição dos tipos de fontes e tabela com todas as fontes utilizadas |
| **Chat & Recomendações** | Interface dividida: chat para consultar suas notas (lado esquerdo) e painel de recomendações de fontes geradas com base na sua pergunta (lado direito). Módulo de IA pendente — conteúdo placeholder por enquanto |
| **Relatórios** | Gerar relatórios com IA com base nas notas cadastradas pelo usuário. O sistema requer pelo menos 10 notas por área de conhecimento para gerar o relatório |

### Stack Técnica

- **Interface**: [NiceGUI](https://nicegui.io/) (Python, baseado em Vue.js/Quasar/FastAPI)
- **Banco de dados**: Arquivos JSON locais
- **Gráficos**: Apache ECharts (via NiceGUI)

## Utilização de Agentes de IA para Criação da Interface Gráfica

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

## Frameworks e Arquitetura do Sistema
**1. Escolha de framework: Por que Langchain?**

O framework me permite integrar com vários modelos diferentes, criar o RAG e as ferramentas facilmente, eliminando a necessidade de criar tudo do zero. Utilizar o SDK da empresa fornecedora do modelo, iria restingir o projeto ao uso dos modelos desta empresa e ainda assim seria necessário de uma biblioteca que ajudasse na construção do RAG, para reduzir a quantidade e a complexidade do código.

**2. Conteúdo, estrutura e estratégias de prompt**

Todos os prompts foram desenvolvidos separadamente, pensando no cenário em que cada um deles seria utilizado. No entanto, a utilização de tags para delimitar onde uma determinada informação relevante está contida, foi utilizada em mais de um prompt tendo em vista que isto pode vir a melhorar o desempenho do modelo.

**3. Parâmetros do modelo: Por que modelos da OpenAI?**

Inicialmente os teste foram realizados de forma local com o modelo ministral-3:8b via Ollama. Este modelo apresentou capacidade de responder as perguntas de forma adequada e de fazer o uso correto das ferramentas. No entanto, por conta de restrições do hardware local o modelo tinha um tempo de resposta muito alto. Em resumo, modelos mais simples poderiam ser utilizados desde que o tempo de resposta não fosse um problema.

Dessa forma, visando diminuir o tempo de resposta, foi realizada a mudança para os modelos da OpenAI. O modelo usado para o chat foi o gpt-4o e para o guardrail, o modelo gpt-4o-mini.

Referente aos parâmetros do modelo, foram utilizados os parâmetros padrão, tendo em vista que apresentaram um resultado satisfatório durante os testes.

**4. Ferramentas disponibilizadas**

search_knowledge: Responsável para encontrar e filtrar as informações dentro do banco vetorial.

**5. RAG**

Esta técnica foi utilizada por conta das frequência de atualização dos dados. No sistema o usuário pode cadastrar informações textuais sempre que achar necessário, requerendo a necessidade de uma arquitetura que suporte mudanças frequentes e radicais sem que o modelo utilizado perca precisão. Neste cenário, realizar o fine-tuning de um modelo com pesos abertos não faria sentido, pois como não se tem previsibilidade do contúdo escrito pelo usuário, não seria possível realizar uma boa otimização deste modelo.

Para criar o banco de dados vetorial, foi utilizada a biblioteca FAISS. Apesar do ChromaDB ser uma boa opção e possuir filtro de metadados de forma nativa (o que reduziria a complexidade do código), enfrentei problemas de integração com a minha versão do Python. Dessa forma, como o FAISS não apresentou problemas de integração, optei por prosseguir com esta opção.

**6. Guardrail**

Para tratar eventuais falhas do modelo de linguagem, onde traz informações irrelevantes ou sensíveis em suas respostas, foi criado um guardrail. Este guardrail é um agente que recebe a pergunta do usuário e a resposta do modelo e valida se a resposta está coerente com o que o usuário pediu, assim como realiza algumas verificações de segurança.

## Proximos Passos

- Integracao com LLM + busca na web para Recomendações (analise da pergunta do usuario para sugerir fontes reais)
- Exportacao de notas (PDF, Markdown)
