# pdf-api/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# System deps if you need fonts or freetype; uncomment if PIL complains
# RUN apt-get update && apt-get install -y --no-install-recommends \
#     libfreetype6-dev libjpeg-dev zlib1g-dev && \
#     rm -rf /var/lib/apt/lists/*

# Install fonts
RUN apt-get update && apt-get install -y \
    fonts-dejavu-core \
    && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy your app and fretboard code
COPY app.py ./
COPY fretboard_module.py ./
COPY Arial.ttf ./

EXPOSE 8000

CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:8000", "--workers", "1"]

