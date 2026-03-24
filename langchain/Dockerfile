# Use a slim, stable 2026 Python base
FROM python:3.11-slim

WORKDIR /app

# Install only what we need
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY app.py .

# Run the script when the container starts
CMD ["python", "app.py"]