# Use Python base image
FROM python:3.10

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    firefox-esr \
    xvfb \
    libgtk-3-0 \
    && wget -q --tries=3 --retry-connrefused "https://github.com/mozilla/geckodriver/releases/download/v0.32.0/geckodriver-v0.32.0-linux64.tar.gz" \
    && tar -xvzf geckodriver-v0.32.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV MOZ_HEADLESS=1
ENV PATH="/usr/local/bin/geckodriver:${PATH}"

# Set working directory
WORKDIR /app/src
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
