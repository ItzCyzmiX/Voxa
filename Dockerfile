# Use Python base image
FROM python:3.10

# Install dependencies for Chrome and Xvfb
RUN apt-get update && apt-get install -y \
    wget \
    unzip \
    curl \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libgdk-pixbuf2.0-0 \
    libnspr4 \
    libnss3 \
    libxss1 \
    xdg-utils \
    libgtk-3-0 \
    libx11-xcb1 \
    xvfb \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*


# Set environment variables
ENV PATH="/usr/local/bin/chromedriver:${PATH}"
ENV GOOGLE_CHROME_BIN="/usr/bin/google-chrome-stable"
ENV CHROME_BIN="/usr/bin/google-chrome-stable"
ENV DISPLAY=:99 

# Install Python dependencies
WORKDIR /app/src
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Start Xvfb (virtual display for Chrome in headless mode)
CMD ["xvfb-run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
