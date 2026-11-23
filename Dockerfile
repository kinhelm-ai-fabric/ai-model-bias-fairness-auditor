FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory
RUN mkdir -p /app/data/uploads

# Expose port
EXPOSE 5000

# Run with gunicorn
CMD ["gunicorn", "--config", "gunicorn.conf.py", "wsgi:app"]
