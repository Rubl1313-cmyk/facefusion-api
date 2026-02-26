#!/usr/bin/env python3
"""FaceFusion API для Hugging Face Spaces — использует FaceFusion для замены лиц"""

import os
import tempfile
import subprocess
import logging
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import Response
import shutil
import uuid

logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FaceFusion API")

# Путь, куда будет установлен FaceFusion (внутри контейнера)
FACEFUSION_DIR = "/facefusion"
FACEFUSION_SCRIPT = os.path.join(FACEFUSION_DIR, "facefusion.py")  # может отличаться

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/swap")
async def swap_face(source: UploadFile = File(...), target: UploadFile = File(...)):
    """
    Принимает два изображения: source (фото с лицом) и target (целевое изображение).
    Возвращает обработанное изображение с заменённым лицом.
    """
    # Создаём временные файлы
    temp_dir = tempfile.mkdtemp()
    source_path = os.path.join(temp_dir, f"source_{uuid.uuid4().hex}.jpg")
    target_path = os.path.join(temp_dir, f"target_{uuid.uuid4().hex}.jpg")
    output_path = os.path.join(temp_dir, f"output_{uuid.uuid4().hex}.jpg")

    try:
        # Сохраняем загруженные файлы
        with open(source_path, "wb") as f:
            f.write(await source.read())
        with open(target_path, "wb") as f:
            f.write(await target.read())

        # Запускаем FaceFusion
        # Предполагается, что facefusion.py принимает аргументы:
        # --source SOURCE --target TARGET --output OUTPUT [другие параметры]
        cmd = [
            "python", FACEFUSION_SCRIPT,
            "--source", source_path,
            "--target", target_path,
            "--output", output_path,
            "--headless"  # если есть такой флаг
        ]
        logger.info(f"Запуск команды: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            logger.error(f"FaceFusion ошибка: {result.stderr}")
            raise HTTPException(status_code=500, detail="FaceFusion processing failed")

        # Проверяем, создался ли выходной файл
        if not os.path.exists(output_path):
            raise HTTPException(status_code=500, detail="Output file not created")

        # Читаем и возвращаем результат
        with open(output_path, "rb") as f:
            image_data = f.read()

        return Response(content=image_data, media_type="image/jpeg")

    except subprocess.TimeoutExpired:
        logger.error("FaceFusion превысил лимит времени")
        raise HTTPException(status_code=504, detail="Processing timeout")
    except Exception as e:
        logger.exception("Ошибка при обработке")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # Удаляем временные файлы
        shutil.rmtree(temp_dir, ignore_errors=True)
