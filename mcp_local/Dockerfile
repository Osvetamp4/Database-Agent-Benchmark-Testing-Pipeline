FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY base_mcp_tools.py decider.py ./
COPY adapters ./adapters

EXPOSE 8000

CMD ["python", "-u", "decider.py"]
