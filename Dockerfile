FROM python:3.12-slim

ENV PORT=3000

COPY . app/
WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install gunicorn

CMD gunicorn -w 2 -b 0.0.0.0:${PORT} app:app
