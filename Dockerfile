FROM python:3.10-alpine

ENV PYTHONUNBUFFERED=1

COPY src/requirements.txt ./
RUN pip install -r requirements.txt

COPY src/api.py src/run.py ./

CMD python run.py
