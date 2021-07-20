FROM python:3.9-slim

EXPOSE 8000
WORKDIR /app

COPY requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

COPY app.py /app/

CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]