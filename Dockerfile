# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.10-alpine
ARG APP=unwordle
LABEL maintainer="mshade@mshade.org"

# Some python housekeeping
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Install pip requirements
COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY *.py /app

RUN adduser -u 5678 --disabled-password --gecos "" ${APP} && chown -R ${APP} /app
USER ${APP}

# Grab the wordlist from wordle main.js
RUN python fetchdict.py

ENTRYPOINT ["python", "unwordle.py"]
