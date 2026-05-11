import httpx
from fastapi import FastAPI
from pydantic import BaseModel
from bs4 import BeautifulSoup

app = FastAPI()

PROFILE = """
Python разработчик с опытом в AI системах.
Навыки: Python, FastAPI, PostgreSQL, Docker, RAG, LLM, LangGraph, n8n.
Ищу: AI Engineer, Backend Developer с AI фокусом.
"""

PROMPT_TEMPLATE = """Оцени насколько подходит вакансия для кандидата.

Профиль кандидата:
{profile}

Вакансия:
Название: {name}
Компания: {employer}
Требования: {description}

Поставь оценку от 1 до 10. Ответь ТОЛЬКО числом."""


class SearchRequest(BaseModel):
    query: str = "AI engineer Python"
    threshold: int = 7
    notify_via: str = "email"


class Vacancy(BaseModel):
    id: str
    name: str
    employer: str
    url: str
    score: int
    notify_via: str


@app.post("/api/v1/search")
async def search(request: SearchRequest):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://hh.ru/search/vacancy",
            params={
                "text": request.query,
                "area": 1,
                "order_by": "publication_time",
            },
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
                "Accept-Language": "ru-RU,ru;q=0.9",
            },
            follow_redirects=True,
        )

    print(f"Статус hh.ru: {response.status_code}")
    soup = BeautifulSoup(response.text, "lxml")

    # Находим карточки вакансий
    cards = soup.find_all("div", {"data-qa": "vacancy-serp__vacancy"})
    print(f"Найдено карточек: {len(cards)}")

    result = []

    async with httpx.AsyncClient() as client:
        for card in cards[:10]:
            try:
                title_tag = card.find("a", {"data-qa": "serp-item__title"})
                employer_tag = card.find("a", {"data-qa": "vacancy-serp__vacancy-employer"})
                snippet_tag = card.find("div", {"data-qa": "vacancy-serp__vacancy_snippet"})

                if not title_tag:
                    continue

                name = title_tag.text.strip()
                url = title_tag["href"].split("?")[0]
                vacancy_id = url.split("/")[-1]
                employer = employer_tag.text.strip() if employer_tag else "Не указано"
                description = snippet_tag.text.strip() if snippet_tag else ""

                print(f"Обрабатываем: {name} - {employer}")

                prompt = PROMPT_TEMPLATE.format(
                    profile=PROFILE,
                    name=name,
                    employer=employer,
                    description=description,
                )

                ollama_response = await client.post(
                    "http://host.docker.internal:11434/api/generate",
                    json={
                        "model": "qwen2.5:7b",
                        "prompt": prompt,
                        "stream": False,
                    },
                    timeout=30.0,
                )
                score_text = ollama_response.json()["response"].strip()
                print(f"Score: {score_text}")
                score = int("".join(filter(str.isdigit, score_text[:2])))
                score = max(1, min(10, score))

            except Exception as e:
                print(f"Ошибка: {e}")
                score = 5
                name = "unknown"
                employer = "unknown"
                url = ""
                vacancy_id = "0"

            if score >= request.threshold:
                result.append(Vacancy(
                    id=vacancy_id,
                    name=name,
                    employer=employer,
                    url=url,
                    score=score,
                    notify_via=request.notify_via,
                ))

    return {"vacancies": [v.dict() for v in result], "total": len(result)}


@app.get("/health")
async def health():
    return {"status": "ok"}