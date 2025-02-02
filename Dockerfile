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
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Google Chrome
RUN wget -q "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" \
    && dpkg -i google-chrome-stable_current_amd64.deb \
    && apt-get -fy install \
    && rm google-chrome-stable_current_amd64.deb

# Install ChromeDriver (compatible with your Chrome version)
RUN CHROME_VERSION=$(google-chrome-stable --version | sed 's/Google Chrome //') \
    && DRIVER_VERSION=$(wget -qO- "https://chromedriver.storage.googleapis.com/LATEST_RELEASE_$CHROME_VERSION") \
    && wget -q "https://chromedriver.storage.googleapis.com/$DRIVER_VERSION/chromedriver_linux64.zip" \
    && unzip chromedriver_linux64.zip \
    && mv chromedriver /usr/local/bin/ \
    && chmod +x /usr/local/bin/chromedriver \
    && rm chromedriver_linux64.zip

# Set environment variables
ENV PATH="/usr/local/bin/chromedriver:${PATH}"
ENV GOOGLE_CHROME_BIN="/usr/bin/google-chrome-stable"
ENV CHROME_BIN="/usr/bin/google-chrome-stable"
ENV DISPLAY=:99  # Set display variable for Xvfb

# Install Python dependencies
WORKDIR /app/src
COPY . /app
RUN pip install --no-cache-dir -r /app/requirements.txt

# Start Xvfb (virtual display for Chrome in headless mode)
CMD ["xvfb-run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
