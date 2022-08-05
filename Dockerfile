FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

COPY src/ ./
RUN pip install -r requirements.txt

CMD python run.py
