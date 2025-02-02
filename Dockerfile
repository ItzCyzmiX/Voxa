# Use Python base image
FROM python:3.10

# Install dependencies
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    firefox-esr \
    xvfb \
    && wget -q "https://github.com/mozilla/geckodriver/releases/latest/download/geckodriver-linux64.tar.gz" \
    && tar -xvzf geckodriver-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/geckodriver

# Set environment variables
ENV MOZ_HEADLESS=1
ENV PATH="/usr/local/bin/geckodriver:${PATH}"

# Set working directory
WORKDIR /app
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Start FastAPI app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
