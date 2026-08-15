FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir \
    --index-url https://download.pytorch.org/whl/cpu \
    torch==2.5.1+cpu \
    torchvision==0.20.1+cpu

RUN pip install --no-cache-dir \
    ultralytics==8.3.0 \
    opencv-python-headless \
    pillow \
    azureml-inference-server-http==1.5.1

COPY model ./model
COPY inference ./inference

ENV MODEL_PATH=/app/model
ENV YOLO_CONFIG_DIR=/tmp/Ultralytics

EXPOSE 5001

CMD ["azmlinfsrv", "--entry_script", "/app/inference/score.py", "--model_dir", "/app/model", "--port", "5001"]
