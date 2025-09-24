# Use official lightweight Python image
FROM python:3.12-slim

# Set work directory inside container
WORKDIR /app

# Prevent Python from writing pyc files + force unbuffered output
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system deps (for psycopg2 & Pillow)
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files into container
COPY . .

# Run Django server by default
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
