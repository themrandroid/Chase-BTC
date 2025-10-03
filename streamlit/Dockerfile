# ./streamlit/Dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY streamlit/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY streamlit/ /app/

ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false
ENV STREAMLIT_SERVER_PORT=8501
ENV PYTHONUNBUFFERED=1

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]