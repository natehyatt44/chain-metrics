FROM python:3.11-slim

WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire backend directory
COPY backend/ /app/

EXPOSE 8080

# Use the correct Python module path
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"] 