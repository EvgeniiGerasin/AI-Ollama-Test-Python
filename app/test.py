import ollama


app = ollama.Client(host='http://127.0.0.1:11434')

r = app.generate(
    model='mistral:latest',
    prompt='Напиши мне промпт для создания нейросетью тест-кейсов по заданному требованию к функционалу ПО',)
print(r.message)
