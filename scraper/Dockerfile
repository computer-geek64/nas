# Dockerfile
FROM python:3.10
WORKDIR /code

RUN apt-get update --fix-missing
RUN apt-get install -y firefox-esr

RUN wget -q https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-linux64.tar.gz
RUN tar -xzf geckodriver-v0.30.0-linux64.tar.gz -C /usr/local/bin
RUN rm geckodriver-v0.30.0-linux64.tar.gz

RUN pip install --upgrade pip
COPY requirements.txt .
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "-m", "scraper"]

COPY src .
