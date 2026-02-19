# AstroMetrics

An interactive web application for students to explore and learn about the planets of our solar system. Built with NiceGUI and FastAPI, it features AI-powered descriptions, planet similarity analysis, and side-by-side comparisons.

---

## Features

### 1. Planet List
Browse all 9 planets (Mercury through Pluto) displayed as interactive cards. Each card shows the planet's image, type, diameter, moon count, and temperature range.

### 2. LLM Planet Overview
Select any planet to receive an AI-generated description written in simple, engaging language for students. Powered by OpenAI's `gpt-4o-mini` model, the description streams in real time.

### 3. Planet Similarity
Choose a planet and discover which others are most physically similar. Similarity is computed using cosine similarity across 7 numerical features: mass, diameter, distance from the Sun, moon count, minimum/maximum temperature, and orbital period.

### 4. Comparative Table
Select two or more planets and compare their characteristics side by side in a dynamic table covering type, mass, diameter, distance, moons, rings, temperatures, orbital period, and atmosphere.

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | [NiceGUI](https://nicegui.io/) 3.x |
| API | [FastAPI](https://fastapi.tiangolo.com/) (via NiceGUI's internal app) |
| AI | [OpenAI Python SDK](https://github.com/openai/openai-python) (`gpt-4o-mini`) |
| Similarity | [scikit-learn](https://scikit-learn.org/) — MinMaxScaler + cosine_similarity |
| Data | Local JSON file (`data/planets.json`) |
| Runtime | Python 3.13, uvicorn |

---

## Setup

### 1. Clone the repository

```bash
git clone <repo-url>
cd planet-start
```

### 2. Create and activate the virtual environment

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure your OpenAI API key

Edit the `.env` file and replace the placeholder with your real key:

```
OPENAI_API_KEY=your-key-here
```

You can get an API key at [platform.openai.com](https://platform.openai.com/api-keys).

### 5. Run the application

```bash
python main.py
```

Open your browser at **http://localhost:8080**.

---

## Project Structure

```
planet-start/
├── main.py                  # Application entry point
├── requirements.txt         # Python dependencies
├── .env                     # API key (not committed)
├── data/
│   └── planets.json         # Planet data (9 planets)
└── app/
    ├── config.py            # Settings and constants
    ├── models/
    │   └── planet.py        # Pydantic data models
    ├── services/
    │   ├── planet_service.py    # Load planets from JSON
    │   ├── llm_service.py       # OpenAI streaming
    │   └── similarity_service.py # Cosine similarity
    ├── api/
    │   ├── planets.py       # REST: GET /api/planets
    │   └── similarity.py    # REST: GET /api/similarity/{id}
    └── ui/
        ├── layout.py        # Shared header & navigation
        ├── components/
        │   └── planet_card.py   # Reusable planet card
        └── pages/
            ├── home.py      # Planet list (/)
            ├── overview.py  # LLM overview (/overview)
            ├── similarity.py # Similarity (/similarity)
            └── comparison.py # Compare table (/comparison)
```

---

## REST API

The app also exposes a REST API you can query directly:

| Endpoint | Description |
|----------|-------------|
| `GET /api/planets` | List all planets |
| `GET /api/planets/{id}` | Get a single planet by ID (e.g. `earth`) |
| `GET /api/similarity/{id}` | Get top-N similar planets for a given planet |
| `GET /api/similarity/{id}?top_n=5` | Control how many similar planets are returned |
