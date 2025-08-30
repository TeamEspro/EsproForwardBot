FROM python:3.10-slim-bullseye

RUN mkdir /app && chmod 777 /app
WORKDIR /app

ENV DEBIAN_FRONTEND=noninteractive

# install required packages
RUN apt-get -qq update && apt-get -qq install -y \
    git \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install --no-cache-dir -r requirements.txt

CMD ["bash","bash.sh"]
