# jobpilot

Автоматический мониторинг вакансий с AI-скорингом. Парсит hh.ru, оценивает каждую вакансию через LLM и отправляет подходящие на email или в Google Sheets.

## Как работает

Два n8n воркфлоу:

**jobpilot-settings** - форма для настройки:
```
n8n Form (query, threshold, notify_via)
    ↓
Google Sheets (лист settings)
```

**jobpilot** - основной поиск (каждые 6 часов):
```
Schedule → Google Sheets (читает настройки)
    ↓
Python сервис (парсинг hh.ru + AI скоринг)
    ↓
IF → есть вакансии с нужным score?
    ↓
Switch → email → Gmail
              → sheets → Google Sheets
```

## Стек

- n8n - оркестрация воркфлоу
- FastAPI - Python сервис парсинга
- BeautifulSoup - парсинг hh.ru
- Ollama + qwen2.5:7b - AI скоринг вакансий
- Gmail - отправка уведомлений
- Google Sheets - хранение настроек и результатов
- Docker Compose - n8n + FastAPI в одной команде

## Запуск

```bash
git clone https://github.com/hitprim/jobpilot
cd jobpilot

docker-compose up -d
```

Ollama должна быть запущена локально с моделью qwen2.5:7b:
```bash
ollama pull qwen2.5:7b
```

- n8n: `http://localhost:5678`
- API: `http://localhost:8000/docs`

Настройки поиска задаются через форму в n8n.

## Структура

```
jobpilot/
├── app/
│   └── main.py           # FastAPI сервис парсинга + AI скоринг
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```