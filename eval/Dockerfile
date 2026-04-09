FROM python:3.11-slim

RUN pip install --no-cache-dir python-dotenv
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
WORKDIR /app

COPY app.py .

CMD ["python", "app.py"]