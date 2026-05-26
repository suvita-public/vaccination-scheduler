FROM python:3.11-slim

ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y \
    curl \
    wget \
    gnupg \
    ca-certificates \
    fonts-noto \
    fonts-noto-cjk \
    fonts-noto-color-emoji \
    fonts-noto-mono \
    fonts-dejavu-core \
    fonts-liberation \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxi6 \
    libxtst6 \
    libxrandr2 \
    libasound2 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxss1 \
    libxdamage1 \
    libgdk-pixbuf2.0-0 \
    libgtk-3-0 \
    libgbm1 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN apt-get update && apt-get install -y chromium chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN chromium --version

WORKDIR /app

COPY . /app

RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

COPY start_services.sh /start_services.sh
RUN chmod +x /start_services.sh

CMD ["/start_services.sh"]
