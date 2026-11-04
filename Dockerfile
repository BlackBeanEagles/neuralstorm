FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.15.0 torchvision==0.29.2 \
    && pip install --no-cache-dir -r requirements.txt

COPY app.py ./
COPY binwise ./binwise
COPY config ./config
COPY models ./models
COPY static ./static

EXPOSE 7860
CMD ["python", "-m", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "7860"]
