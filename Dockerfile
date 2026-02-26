FROM python:3.10-slim

WORKDIR /app

# Устанавливаем системные зависимости
RUN apt-get update && apt-get install -y \
    git \
    ffmpeg \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Клонируем репозиторий FaceFusion (последняя версия)
RUN git clone https://github.com/facefusion/facefusion.git /facefusion

# Устанавливаем зависимости Python для FaceFusion
WORKDIR /facefusion
RUN pip install --no-cache-dir -r requirements.txt

# Возвращаемся в рабочую директорию приложения
WORKDIR /app

# Копируем файлы нашего API
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Порт, который будет использовать FastAPI
EXPOSE 7860

# Запускаем сервер
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
