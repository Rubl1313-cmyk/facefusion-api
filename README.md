---
title: FaceFusion API
emoji: 🎨
colorFrom: blue
colorTo: purple
sdk: docker
pinned: false
license: mit
---

# FaceFusion API

Этот Space предоставляет API для замены лиц с помощью FaceFusion.

## Эндпоинты

- `GET /health` — проверка работоспособности
- `POST /swap` — замена лица. Принимает multipart/form-data с полями `source` (фото лица) и `target` (целевое изображение). Возвращает JPEG.

Пример использования:
```python
import requests

url = "https://твой-username-facefusion-api.hf.space/swap"
files = {
    "source": open("face.jpg", "rb"),
    "target": open("image.jpg", "rb")
}
resp = requests.post(url, files=files)
with open("output.jpg", "wb") as f:
    f.write(resp.content)
