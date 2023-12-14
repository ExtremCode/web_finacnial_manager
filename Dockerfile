FROM python:3.9-slim

WORKDIR /app

COPY application/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY application/* ./

ENTRYPOINT [ "waitress-serve", "app:app"]
