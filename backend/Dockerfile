# Use official Python slim image
FROM python:3.11-slim

# Install dependencies for Firefox and geckodriver
RUN apt-get update && apt-get install -y \
    firefox-esr \
    wget \
    curl \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libu2f-udev \
    libvulkan1 \
    libx11-xcb1 \
    libxcb-dri3-0 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpangocairo-1.0-0 \
    libpangoft2-1.0-0 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libgtk-3-0 \
    --no-install-recommends && \
    rm -rf /var/lib/apt/lists/*

# Install GeckoDriver (version 0.36.0 for Firefox 140.*)
RUN GECKODRIVER_VERSION=v0.36.0 && \
    wget -q "https://github.com/mozilla/geckodriver/releases/download/$GECKODRIVER_VERSION/geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz" && \
    tar -xzf geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz -C /usr/local/bin && \
    rm geckodriver-$GECKODRIVER_VERSION-linux64.tar.gz

# Set display port for headless mode
ENV DISPLAY=:99

# Create working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend source code
COPY . .

# Expose port
EXPOSE 8000

# Run app with Gunicorn and Uvicorn worker
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app:app", "--bind", "0.0.0.0:8000", "--workers", "2"]
