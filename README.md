# jobpilot

**Automated lead/candidate monitoring pipeline.** Scrapes listings on a schedule, scores each one against configurable criteria with an LLM, and routes only the qualifying results to email or Google Sheets - no manual board-checking, no manual triage.

## The manual process it eliminates

Checking a job board every few hours, opening each posting, reading it, and deciding which ones are worth acting on. jobpilot turns that recurring manual loop into a hands-off pipeline that runs itself and only surfaces what matters.

## How it works (process -> automation -> optimization -> scale)

Two n8n workflows:

**jobpilot-settings** - a form to configure the run (no code needed to retune):
```
n8n Form (query, threshold, notify_via)
    -> Google Sheets (settings sheet)
```

**jobpilot** - the main run, every 6 hours:
```
Schedule -> Google Sheets (reads settings)
    -> Python service (scrape + LLM scoring)
    -> IF (any results above the score threshold?)
    -> Switch -> email  -> Gmail
              -> sheets -> Google Sheets
```

The data source, the scoring model, and the delivery channel are all decoupled - swapping any of them is a configuration change, not a rewrite. That is the scale path: the same pipeline shape works for sales leads, candidates, listings, or any "monitor a source, score it, route the good ones" job.

## Stack

- **n8n** - workflow orchestration (schedule, branching, routing)
- **FastAPI** - Python service for scraping + scoring
- **BeautifulSoup** - listing parser
- **LLM scoring** - Ollama + qwen2.5:7b locally; swappable for the OpenAI / Claude API with a single client change
- **Gmail API** - notifications
- **Google Sheets API** - settings storage and results
- **Docker Compose** - n8n + FastAPI in one command

## Run

```bash
git clone https://github.com/hitprim/jobpilot
cd jobpilot
docker-compose up -d
```

Ollama must be running locally with the model pulled:
```bash
ollama pull qwen2.5:7b
```

- n8n: `http://localhost:5678`
- API: `http://localhost:8000/docs`

Search settings are configured through the n8n form.

## Structure

```
jobpilot/
├── app/
│   └── main.py           # FastAPI service: scraping + LLM scoring
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```
