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
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RequirementRequest(BaseModel):
    requirement: str
    model: str = "deepseek-r1"


@app.post("/generate_check_list/", summary="Генерация чек-листа по требованию")
async def generate_check_list(request: RequirementRequest):
    """
    Генерирует чек-листа для заданного требования к функционалу ПО.

    Параметры:
    - requirement: Текстовое описание требования
    - model: Модель Ollama для использования (по умолчанию deepseek-r1:latest )
    """
    try:
        prompt = """
        Ты senior-тестировщик ПО. Напиши максимально подробный чек-лист проверок для следующего требования к функционалу ПО на русском языке:
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


@app.post("/generate_test_case/", summary="Генерация тест-кейсов по требованию")
async def generate_test_case(request: RequirementRequest):
    """
    Сгенерирует тест-кейсов для заданного требования к функционалу ПО.

    Параметры:
    - requirement: Текстовое описание требования
    - model: Модель Ollama для использования (по умолчанию deepseek-r1:latest )
    """
    try:
        prompt = """
        Напиши максимально подробные тест-кейсы проверок для следующего требования к функционалу ПО на русском языке:
        {}
        
        Формат вывода:
        'номер тест-кейса': 'Название тест-кейса. Шаги. Ожидаемый результат' 

        Пример:
        '1', 'Поле отображается на странице. 1.Ввести данные. 2 Нажать кнопку сохранить. Ожидаемый результат: данные сохранены', '2', 'Поле отображается на странице неверно. 1.Ввести неверные данные. 2 Нажать кнопку сохранить. Ожидаемый результат: данные не сохранены',

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
    - model: Модель Ollama для использования (по умолчанию deepseek-r1:latest )
    """
    json_result = json.loads(example_response)
    result = ''
    for _, value in json_result.items():
        result += value + '\n'
    try:
        return json_result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
