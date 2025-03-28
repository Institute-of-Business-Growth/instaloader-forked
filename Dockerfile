FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py .

# Set environment variables
ENV PORT=8000
ENV FLASK_ENV=production

# Expose the port
EXPOSE 8000

# Use Gunicorn as the production server
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "instagram_server:app"] 