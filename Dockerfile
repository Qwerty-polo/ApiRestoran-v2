# Використовуємо легкий Python 3.11
FROM python:3.11-slim

# Налаштування, щоб Python не створював зайві файли .pyc і виводив логи одразу
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Встановлюємо залежності
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копіюємо весь код проекту
COPY . .

# Створюємо папку для картинок (якщо її немає)
RUN mkdir -p static/images

# Відкриваємо порт
EXPOSE 8000

# Запускаємо сервер
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]