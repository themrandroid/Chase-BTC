# ./bot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY bot/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY bot/ /app/

ENV PYTHONUNBUFFERED=1

CMD ["python", "bot.py"]