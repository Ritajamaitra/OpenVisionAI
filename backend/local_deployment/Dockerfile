FROM python:3.11-slim

WORKDIR /app

# System libraries required by OpenCV / Ultralytics
RUN apt-get update && apt-get install -y --no-install-recommends \
    libglib2.0-0 \
    libgl1 \
    libsm6 \
    libxext6 \
    libxrender1 \
    libxcb1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY model ./model
COPY inference ./inference

ENV MODEL_PATH=/app/model/best.pt
ENV AZUREML_MODEL_DIR=/app/model

EXPOSE 5001

CMD ["azmlinfsrv", "--entry_script", "/app/inference/score.py", "--model_dir", "/app/model", "--port", "5001"]
