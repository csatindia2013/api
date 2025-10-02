# Use Python 3.11 base
FROM python:3.11-slim

# Install Chromium (lighter than Chrome) and dependencies
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    wget \
    && rm -rf /var/lib/apt/lists/*

# Set Chrome/Chromium paths
ENV CHROME_BIN=/usr/bin/chromium
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 5000

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "180", "--workers", "2", "app:app"]

