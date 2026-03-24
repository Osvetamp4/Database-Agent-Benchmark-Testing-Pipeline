FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements if you have one, else install langchain directly
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt || pip install --no-cache-dir langchain

# Copy the rest of your code
COPY . .

# Set the entrypoint to run main.py
CMD ["python", "main.py"]