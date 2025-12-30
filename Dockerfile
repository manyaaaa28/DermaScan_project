# Use a lightweight Python image
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your app code
COPY . .

# Hugging Face expects apps on port 7860
EXPOSE 7860

# Run with Gunicorn for better performance
CMD ["gunicorn", "--bind", "0.0.0.0:7860", "app:app"]