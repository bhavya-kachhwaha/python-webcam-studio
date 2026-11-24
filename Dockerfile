FROM python:3.12-slim-bookworm

WORKDIR /studio
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates libegl1 libgl1 libgles2 libglib2.0-0 libgomp1 \
    && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN python -m pip install --no-cache-dir -r requirements.txt
COPY *.py ./
COPY web ./web
RUN python download_models.py

ENV PORT=7860
EXPOSE 7860
CMD ["sh", "-c", "exec python -m uvicorn web_server:app --host 0.0.0.0 --port $PORT --ws websockets --ws-max-size 524288 --ws-max-queue 1"]
