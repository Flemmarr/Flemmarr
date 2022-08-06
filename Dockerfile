FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install -r requirements.txt

COPY src/ ./

CMD python run.py
