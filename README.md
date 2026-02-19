# Knowledge OS

Sistema pessoal de gestao de conhecimento construido com Python e NiceGUI.

## O Problema

Quem estuda por diferentes fontes -- livros, videos, artigos, podcasts, cursos -- acaba com anotacoes espalhadas em cadernos, apps e arquivos soltos. Com o tempo, fica dificil:

- **Reencontrar** uma anotacao especifica feita meses atras
- **Saber de onde veio** cada informacao (qual livro, qual video, qual autor)
- **Enxergar padroes** nos proprios estudos (que tipo de fonte voce mais consome? quais temas domina?)
- **Descobrir lacunas** e receber sugestoes de novas fontes para estudar

## A Solucao

O Knowledge OS centraliza todas as suas anotacoes em um unico lugar com metadados ricos (fonte, autor, tipo, tags) e oferece ferramentas visuais para explorar e consultar sua base de conhecimento.

### Funcionalidades

| Pagina | Descricao |
|--------|-----------|
| **Nova Nota** | Formulario para criar notas com titulo, conteudo, tipo de fonte, nome da fonte, autor e tags |
| **Banco de Notas** | Lista todas as notas com busca por texto e filtro por tipo de fonte. Permite editar e excluir notas |
| **Gerenciar Tags** | Criacao e exclusao de tags para categorizar suas notas |
| **Mapa de Fontes** | Graficos (rosca e barras) mostrando a distribuicao dos tipos de fontes e tabela com todas as fontes utilizadas |
| **Recomendacoes** | Pagina para recomendacoes de novas fontes geradas por IA (em desenvolvimento -- conteudo estatico por enquanto) |
| **Chat de Conhecimento** | Interface de chat estilo ChatGPT para consultar suas notas via linguagem natural (interface pronta, modulo de IA pendente) |

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
    ├── recommendations.py # Pagina: recomendacoes de fontes (estatico)
    └── chat.py            # Pagina: chat de conhecimento (placeholder)
```

### Stack Tecnica

- **Interface**: [NiceGUI](https://nicegui.io/) (Python, baseado em Vue.js/Quasar/FastAPI)
- **Banco de dados**: Arquivos JSON locais
- **Graficos**: Apache ECharts (via NiceGUI)
- **Dependencias externas**: Apenas `nicegui`

## Como Executar

### Pre-requisitos

- Python 3.10 ou superior

### Instalacao

```bash
# Clonar ou acessar o diretorio do projeto
cd knowledge-os

# Criar ambiente virtual
python -m venv venv

# Ativar ambiente virtual (Windows)
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Execucao

```bash
python main.py
```

O sistema estara disponivel em **http://localhost:3000**.

## Estrutura dos Dados

### Nota (`data/notes.json`)

```json
{
  "id": "uuid",
  "title": "Titulo da nota",
  "content": "Conteudo em texto",
  "source_type": "livro|video|artigo|podcast|curso|outro",
  "source_name": "Nome da fonte",
  "source_author": "Autor da fonte",
  "tags": ["tag1", "tag2"],
  "created_at": "2026-02-19T14:30:00"
}
```

### Tag (`data/tags.json`)

```json
{
  "id": "uuid",
  "name": "nome-da-tag"
}
```

## Proximos Passos

- Integracao com LLM para o Chat de Conhecimento (busca semantica nas notas)
- Integracao com LLM para Recomendacoes (analise das ultimas 100 notas para sugerir novas fontes)
- Exportacao de notas (PDF, Markdown)
