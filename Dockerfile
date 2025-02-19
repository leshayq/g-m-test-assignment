FROM python:3.12-alpine

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir -r requirements.txt

RUN apk add --no-cache \
    chromium \
    chromium-chromedriver \
    gcc \
    musl-dev \
    python3-dev

ENV PATH="/usr/lib/chromium/:${PATH}"

CMD ["python", "main.py"]