from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import ollama
import json

from test_data import example_response

app = FastAPI(title="Test Case Generator API",
              description="API для генерации тест-кейсов с помощью Ollama")

# Инициализация клиента Ollama
ollama_client = ollama.Client(host='http://127.0.0.1:11434')


# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://ingflainldpdigbnkbmlglinefminhpn",  # Замените на ID вашего расширения
        "http://localhost",  # Для тестирования из браузера
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequirementRequest(BaseModel):
    requirement: str
    model: str = "mistral:latest"


@app.post("/generate_check_list/", summary="Генерация чек-листа по требованию")
async def generate_check_list(request: RequirementRequest):
    """
    Генерирует чек-листа для заданного требования к функционалу ПО.

    Параметры:
    - requirement: Текстовое описание требования
    - model: Модель Ollama для использования (по умолчанию mistral:latest)
    """
    try:
        prompt = """
        Напиши максимально подробный чек-лист проверок для следующего требования к функционалу ПО на русском языке:
        {}
        
        Формат вывода:
        'номер проверки': 'название проверки или ее суть' 

        Пример:
        '1', 'Поле отображается на странице', '2': 'Поле отображается и выводит значение'

        """.format(request.requirement)

        response = ollama_client.generate(
            model=request.model,
            prompt=prompt,
            format='json',
            stream=False
        )

        json_result = json.loads(response['response'].strip("'"))

        return json_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/", summary="Тестовый метод для предоставления ответа")
async def for_test(request: RequirementRequest):
    """
    Тестовый метод для предоставления ответа по генерации

    Параметры:
    - requirement: Текстовое описание требования
    - model: Модель Ollama для использования (по умолчанию mistral:latest)
    """
    json_result = json.loads(example_response)
    result = ''
    for _, value in json_result.items():
        result += value + '\n'
    try:
        return json_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/available-models/", summary="Получить список доступных моделей")
async def get_available_models():
    """Возвращает список моделей, доступных в Ollama"""
    try:
        models = ollama_client.list()
        return {"available_models": [model['model'] for model in models['models']]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
