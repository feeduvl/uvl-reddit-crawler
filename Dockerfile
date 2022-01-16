FROM python:3.8-slim-buster

WORKDIR /app
COPY . .

RUN pip3 install --no-cache-dir --upgrade pip -r requirements.txt


CMD [ "python3", "./app.py" ]