# ./bot/Dockerfile
FROM python:3.10-slim

WORKDIR /app

# Copy requirements first and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all bot files
COPY . .

# Ensure logs are streamed immediately
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "bot.py"]