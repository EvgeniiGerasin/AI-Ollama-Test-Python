from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import ollama

app = FastAPI(title="Test Case Generator API",
              description="API для генерации тест-кейсов с помощью Ollama")

# Инициализация клиента Ollama
ollama_client = ollama.Client(host='http://127.0.0.1:11434')


# Настройки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "chrome-extension://ifilkkfhbldegbjggdapmcbcogcpllfd",  # Замените на ID вашего расширения
        "http://localhost",  # Для тестирования из браузера
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RequirementRequest(BaseModel):
    requirement: str
    model: str = "mistral:latest"


@app.post("/generate-test-cases/", summary="Генерация тест-кейсов по требованию")
async def generate_test_cases(request: RequirementRequest):
    """
    Генерирует тест-кейсы для заданного требования к функционалу ПО.

    Параметры:
    - requirement: Текстовое описание требования
    - model: Модель Ollama для использования (по умолчанию mistral:latest)
    """
    try:
        prompt = f"""
        Напиши подробные тест-кейсы для следующего требования к функционалу ПО:
        {request.requirement}
        
        Формат вывода:
        1. Название тест-кейса
        - Предусловия
        - Шаги выполнения
        - Ожидаемый результат
        
        Сгенерируй как можно больше тест-кейсов разного типа (позитивные, негативные, граничные случаи) ::
        Разметка ответа в формате Markdown
        """

        response = ollama_client.generate(
            model=request.model,
            prompt=prompt,
        )

        return {
            "requirement": request.requirement,
            "test_cases": response['response'],
            "model": request.model
        }

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
